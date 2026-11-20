"""Safe SQLite backup, verification and restore utilities.

Backups are not encrypted. Store them only on an encrypted volume with
access controls appropriate to the event metadata.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import stat
import sys
import tempfile
from pathlib import Path

REQUIRED_COLUMNS = {
    "event_id", "kind", "device_id", "event_timestamp", "received_at", "event_json"
}


def _open_readonly(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise FileNotFoundError(f"SQLite database not found: {path}")
    uri = path.resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=5)


def _verify_database(path: Path) -> int:
    with _open_readonly(path) as db:
        integrity = db.execute("PRAGMA integrity_check").fetchone()
        if not integrity or integrity[0] != "ok":
            raise sqlite3.DatabaseError("SQLite integrity_check failed")
        tables = {
            row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        if "events" not in tables:
            raise sqlite3.DatabaseError("Required events table is missing")
        columns = {
            row[1] for row in db.execute("PRAGMA table_info(events)").fetchall()
        }
        if not REQUIRED_COLUMNS.issubset(columns):
            raise sqlite3.DatabaseError("Event store schema is incomplete")
        count = int(db.execute("SELECT COUNT(*) FROM events").fetchone()[0])
        return count


def _secure_file(path: Path) -> None:
    if os.name == "posix":
        os.chmod(path, 0o600)


def _secure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name == "posix":
        info = path.parent.stat()
        if info.st_uid != os.getuid():
            raise PermissionError("Backup directory must be owned by the current user")
        if stat.S_IMODE(info.st_mode) & 0o077:
            raise PermissionError("Backup directory must be private (mode 0700)")


def _copy_exclusive(source: Path, destination: Path) -> None:
    """Copy a completed SQLite image without ever overwriting an existing file."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=True) as output, source.open("rb") as input_file:
            shutil.copyfileobj(input_file, output, length=1024 * 1024)
            output.flush()
            os.fsync(output.fileno())
        _secure_file(destination)
    except Exception:
        try:
            destination.unlink()
        except OSError:
            pass
        raise


def backup(source: str, destination: str) -> int:
    source_path = Path(source).expanduser().resolve()
    target = Path(destination).expanduser().resolve()
    if source_path == target:
        raise ValueError("Backup destination must differ from source")
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite: {target}")
    _secure_parent(target)
    # Build and validate a standalone snapshot in the target directory.
    fd, temp_name = tempfile.mkstemp(prefix=".beekeeper-backup-", suffix=".sqlite3", dir=target.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        with _open_readonly(source_path) as source_db:
            with sqlite3.connect(temp_path, timeout=5) as target_db:
                source_db.backup(target_db, pages=256, sleep=0.05)
                target_db.execute("PRAGMA journal_mode=DELETE")
        _secure_file(temp_path)
        count = _verify_database(temp_path)
        _copy_exclusive(temp_path, target)
        if _verify_database(target) != count:
            target.unlink(missing_ok=True)
            raise sqlite3.DatabaseError("Backup row count changed during finalization")
        return count
    finally:
        temp_path.unlink(missing_ok=True)


def verify(source: str) -> int:
    return _verify_database(Path(source).expanduser().resolve())


def restore(backup_path: str, destination: str) -> int:
    source_path = Path(backup_path).expanduser().resolve()
    target = Path(destination).expanduser().resolve()
    if source_path == target:
        raise ValueError("Restore destination must differ from backup")
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite: {target}")
    count = _verify_database(source_path)
    _secure_parent(target)
    fd, temp_name = tempfile.mkstemp(prefix=".beekeeper-restore-", suffix=".sqlite3", dir=target.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        with _open_readonly(source_path) as source_db:
            with sqlite3.connect(temp_path, timeout=5) as target_db:
                source_db.backup(target_db, pages=256, sleep=0.05)
                target_db.execute("PRAGMA journal_mode=DELETE")
        _secure_file(temp_path)
        restored_count = _verify_database(temp_path)
        if restored_count != count:
            raise sqlite3.DatabaseError("Restored database row count does not match backup")
        _copy_exclusive(temp_path, target)
        if _verify_database(target) != count:
            target.unlink(missing_ok=True)
            raise sqlite3.DatabaseError("Restored database failed final verification")
        return count
    finally:
        temp_path.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Verify and copy BeeKeeper local SQLite stores safely.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_backup = sub.add_parser("backup", help="Create a consistent backup without overwriting files")
    p_backup.add_argument("--source", required=True)
    p_backup.add_argument("--destination", required=True)
    p_verify = sub.add_parser("verify", help="Run integrity and schema checks")
    p_verify.add_argument("--source", required=True)
    p_restore = sub.add_parser("restore", help="Restore to a new destination without overwriting files")
    p_restore.add_argument("--backup", required=True)
    p_restore.add_argument("--destination", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "backup":
            count = backup(args.source, args.destination)
            print(f"Backup verified; {count} event(s) copied to {Path(args.destination).resolve()}")
        elif args.command == "verify":
            count = verify(args.source)
            print(f"SQLite integrity and schema OK; {count} event(s)")
        else:
            count = restore(args.backup, args.destination)
            print(f"Restore verified; {count} event(s) copied to {Path(args.destination).resolve()}")
        return 0
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
