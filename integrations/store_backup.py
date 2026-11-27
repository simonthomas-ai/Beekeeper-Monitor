"""Consistent, integrity-checked SQLite backup and restore for local event storage.

Backups contain station metadata and must be treated as sensitive. This module
never overwrites an existing backup or restore target.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import stat
import subprocess
import tempfile
from pathlib import Path

_REQUIRED_COLUMNS = {
    "event_id", "kind", "device_id", "event_timestamp", "received_at", "event_json"
}


def _database_uri(path: Path) -> str:
    return path.resolve().as_uri() + "?mode=ro"


_WINDOWS_FULL_CONTROL_MASK = 0x1F01FF
_WINDOWS_ACL_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
$path = $env:BEEKEEPER_BACKUP_ACL_PATH
if ([string]::IsNullOrWhiteSpace($path)) { throw 'Backup ACL path is missing.' }
$acl = Get-Acl -LiteralPath $path
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
if ($null -eq $identity.User) { throw 'Current Windows user SID is unavailable.' }
$rules = @(
    $acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]) |
    ForEach-Object {
        [pscustomobject]@{
            sid = $_.IdentityReference.Value
            type = $_.AccessControlType.ToString()
            rights = [int]$_.FileSystemRights
        }
    }
)
[pscustomobject]@{
    owner_sid = $acl.GetOwner([Security.Principal.SecurityIdentifier]).Value
    current_user_sid = $identity.User.Value
    rules = $rules
} | ConvertTo-Json -Compress -Depth 4
"""


def _check_windows_private_directory(directory: Path) -> None:
    """Fail closed unless NTFS grants access only to the current user/SYSTEM/admins."""
    environment = os.environ.copy()
    environment["BEEKEEPER_BACKUP_ACL_PATH"] = str(directory)
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", _WINDOWS_ACL_SCRIPT],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PermissionError("cannot verify Windows backup-directory ACL; refusing backup") from exc
    if result.returncode != 0:
        raise PermissionError("Windows backup-directory ACL verification failed; refusing backup")
    try:
        payload = json.loads(result.stdout.lstrip("\ufeff"))
        owner_sid = payload["owner_sid"]
        current_sid = payload["current_user_sid"]
        rules = payload["rules"]
        if isinstance(rules, dict):
            rules = [rules]
        if not isinstance(rules, list) or not rules or owner_sid != current_sid:
            raise ValueError("invalid owner or ACL rules")
        allowed_sids = {current_sid, "S-1-5-18", "S-1-5-32-544"}
        rights_by_sid = {}
        for rule in rules:
            sid = rule["sid"]
            if sid not in allowed_sids or rule["type"] != "Allow":
                raise ValueError("unexpected Windows ACL principal or deny rule")
            rights = int(rule["rights"])
            if rights < 0 or rights & ~_WINDOWS_FULL_CONTROL_MASK:
                raise ValueError("unexpected Windows filesystem rights")
            rights_by_sid[sid] = rights_by_sid.get(sid, 0) | rights
        for sid in (current_sid, "S-1-5-18"):
            if rights_by_sid.get(sid, 0) & _WINDOWS_FULL_CONTROL_MASK != _WINDOWS_FULL_CONTROL_MASK:
                raise ValueError("current user and SYSTEM must have FullControl")
        if "S-1-5-32-544" in rights_by_sid and (
            rights_by_sid["S-1-5-32-544"] & _WINDOWS_FULL_CONTROL_MASK
        ) != _WINDOWS_FULL_CONTROL_MASK:
            raise ValueError("Administrators ACL must be FullControl when present")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise PermissionError("Windows backup-directory ACL is not restricted to trusted principals") from exc


def _check_private_directory(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name == "nt":
        _check_windows_private_directory(directory)
        return
    if os.name != "posix":
        raise PermissionError("unsupported platform; refusing to create an unverified backup")
    info = directory.stat()
    if info.st_uid != os.getuid():
        raise PermissionError("backup directory must be owned by the current service account")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise PermissionError("backup directory must be private (POSIX mode 0700)")


def verify_database(path: str | os.PathLike) -> dict:
    """Verify SQLite integrity and the Beekeeper Monitor event schema."""
    database = Path(path).expanduser().resolve()
    if not database.is_file():
        raise FileNotFoundError(f"SQLite database not found: {database}")
    connection = sqlite3.connect(_database_uri(database), uri=True, timeout=5)
    try:
        result = connection.execute("PRAGMA quick_check").fetchone()
        if not result or result[0] != "ok":
            raise sqlite3.DatabaseError("SQLite quick_check failed")
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(events)").fetchall()
        }
        if not _REQUIRED_COLUMNS.issubset(columns):
            raise sqlite3.DatabaseError("database does not contain the expected Beekeeper events schema")
        count = int(connection.execute("SELECT COUNT(*) FROM events").fetchone()[0])
        return {"valid": True, "events": count, "integrity": "ok"}
    finally:
        connection.close()


def _snapshot_to_new_file(source_path: str | os.PathLike,
                          destination_path: str | os.PathLike) -> Path:
    source = Path(source_path).expanduser().resolve()
    destination = Path(destination_path).expanduser().resolve()
    if source == destination:
        raise ValueError("source and destination must be different files")
    if not source.is_file():
        raise FileNotFoundError(f"SQLite source not found: {source}")
    if destination.exists():
        raise FileExistsError(f"destination already exists; refusing to overwrite: {destination}")
    if destination.parent == source.parent and os.name == "posix":
        # A dedicated backup directory separates live WAL files from snapshots.
        pass

    _check_private_directory(destination.parent)
    verify_database(source)

    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".partial", dir=destination.parent
    )
    os.close(descriptor)
    temporary = Path(temp_name)
    published_placeholder = False
    try:
        if os.name == "posix":
            os.chmod(temporary, 0o600)
        source_connection = sqlite3.connect(_database_uri(source), uri=True, timeout=5)
        destination_connection = sqlite3.connect(str(temporary), timeout=5)
        try:
            source_connection.backup(destination_connection, pages=256, sleep=0.05)
            result = destination_connection.execute("PRAGMA quick_check").fetchone()
            if not result or result[0] != "ok":
                raise sqlite3.DatabaseError("snapshot integrity check failed")
            columns = {
                row[1] for row in destination_connection.execute(
                    "PRAGMA table_info(events)"
                ).fetchall()
            }
            if not _REQUIRED_COLUMNS.issubset(columns):
                raise sqlite3.DatabaseError("snapshot schema does not match the Monitor event store")
            destination_connection.commit()
        finally:
            destination_connection.close()
            source_connection.close()

        verify_database(temporary)
        with temporary.open("rb+") as handle:
            handle.flush()
            os.fsync(handle.fileno())

        # Reserve the final name with O_EXCL so another process cannot cause an
        # existing backup or live database to be overwritten by os.replace().
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        descriptor = os.open(destination, flags, 0o600)
        os.close(descriptor)
        published_placeholder = True
        os.replace(temporary, destination)
        if os.name == "posix":
            os.chmod(destination, 0o600)
        return destination
    except Exception:
        if published_placeholder:
            try:
                destination.unlink()
            except FileNotFoundError:
                pass
        raise
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def backup_database(source_path: str | os.PathLike,
                    backup_path: str | os.PathLike) -> Path:
    """Create a consistent SQLite online backup; never overwrite a previous file."""
    return _snapshot_to_new_file(source_path, backup_path)


def restore_database(backup_path: str | os.PathLike,
                     destination_path: str | os.PathLike) -> Path:
    """Restore a verified snapshot into a new, non-existing destination file."""
    verify_database(backup_path)
    return _snapshot_to_new_file(backup_path, destination_path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Back up, verify or restore the Beekeeper Monitor local SQLite event store."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup = subparsers.add_parser("backup", help="Create a consistent snapshot")
    backup.add_argument("--source", required=True, help="Path to the live events.sqlite3")
    backup.add_argument("--destination", required=True, help="New backup file path")

    verify = subparsers.add_parser("verify", help="Verify an existing snapshot or live database")
    verify.add_argument("--source", required=True, help="SQLite database path")

    restore = subparsers.add_parser("restore", help="Restore a verified snapshot to a new file")
    restore.add_argument("--backup", required=True, help="Path to the backup file")
    restore.add_argument("--destination", required=True, help="New destination path (must not exist)")

    args = parser.parse_args(argv)
    if args.command == "backup":
        path = backup_database(args.source, args.destination)
        print(f"Backup created and verified: {path}")
    elif args.command == "verify":
        result = verify_database(args.source)
        print(f"Database verified: integrity={result['integrity']}, events={result['events']}")
    else:
        path = restore_database(args.backup, args.destination)
        result = verify_database(path)
        print(f"Restore created and verified: {path} (events={result['events']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
