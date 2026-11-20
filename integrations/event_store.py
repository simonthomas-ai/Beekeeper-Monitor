"""Small local SQLite event store. Stores validated metadata only; never media or secrets."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import stat
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from integrations.event_contracts import HiveEvent


class SQLiteEventStore:
    """Durable, idempotent event sink with bounded retention."""

    def __init__(self, path: str, retention_days: int = 90, max_rows: int = 100_000):
        if not path:
            raise ValueError("A database path is required")
        if not 1 <= retention_days <= 3650 or not 100 <= max_rows <= 2_000_000:
            raise ValueError("Invalid retention bounds")
        target = Path(path).expanduser().resolve()
        self.path = str(target)
        self.retention_days = retention_days
        self.max_rows = max_rows
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if os.name == "posix":
            parent_stat = target.parent.stat()
            if parent_stat.st_uid != os.getuid():
                raise PermissionError("SQLite directory must be owned by the service account")
            if stat.S_IMODE(parent_stat.st_mode) & 0o077:
                raise PermissionError(
                    "SQLite directory must be private (mode 0700); choose a dedicated data directory"
                )
        self._initialize()
        self._secure_files()

    def _secure_files(self):
        """Restrict database and SQLite sidecars on POSIX systems."""
        if os.name != "posix":
            # Windows permissions must be established with explicit NTFS ACLs.
            return
        for candidate in (self.path, self.path + "-wal", self.path + "-shm"):
            try:
                os.chmod(candidate, 0o600)
            except FileNotFoundError:
                continue

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=5)
        try:
            self._secure_files()
            db.execute("PRAGMA busy_timeout=5000")
            db.execute("PRAGMA foreign_keys=ON")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
            self._secure_files()

    def _initialize(self):
        with self._db() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    event_timestamp TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    event_json TEXT NOT NULL
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_events_received ON events(received_at)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_events_device ON events(device_id)")

    def __call__(self, event: HiveEvent) -> bool:
        event.validate()
        event_json = event.to_json()
        event_id = hashlib.sha256(event_json.encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc)
        cutoff = (now - timedelta(days=self.retention_days)).isoformat()
        with self._db() as db:
            cursor = db.execute(
                "INSERT OR IGNORE INTO events "
                "(event_id, kind, device_id, event_timestamp, received_at, event_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (event_id, event.kind, event.device_id, event.timestamp, now.isoformat(), event_json),
            )
            db.execute("DELETE FROM events WHERE received_at < ?", (cutoff,))
            db.execute("""
                DELETE FROM events WHERE event_id IN (
                    SELECT event_id FROM events ORDER BY received_at DESC
                    LIMIT -1 OFFSET ?
                )
            """, (self.max_rows,))
            return cursor.rowcount == 1

    def list_events(self, limit: int = 100) -> list[dict]:
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        with self._db() as db:
            rows = db.execute(
                "SELECT event_id, received_at, event_json FROM events "
                "ORDER BY received_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [
            {"event_id": row[0], "received_at": row[1], "event": json.loads(row[2])}
            for row in rows
        ]

    def delete(self, event_id: str) -> bool:
        if not isinstance(event_id, str) or len(event_id) != 64 or any(ch not in "0123456789abcdef" for ch in event_id):
            raise ValueError("Invalid event ID")
        with self._db() as db:
            cursor = db.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
            return cursor.rowcount == 1

    def purge_expired(self) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=self.retention_days)).isoformat()
        with self._db() as db:
            cursor = db.execute("DELETE FROM events WHERE received_at < ?", (cutoff,))
            return cursor.rowcount

    def count(self) -> int:
        with self._db() as db:
            return int(db.execute("SELECT COUNT(*) FROM events").fetchone()[0])
