import os
import sqlite3
import stat
import tempfile
import unittest
from pathlib import Path

from integrations.event_contracts import HiveEvent
from integrations.event_store import SQLiteEventStore
from integrations.store_backup import (
    backup_database,
    restore_database,
    verify_database,
)


class SQLiteBackupRestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source_dir = self.root / "source"
        self.backup_dir = self.root / "private-backups"
        self.restore_dir = self.root / "restored"
        self.source_dir.mkdir(mode=0o700)
        self.source = self.source_dir / "events.sqlite3"
        self.store = SQLiteEventStore(str(self.source), retention_days=90, max_rows=1000)
        self.event = HiveEvent(
            "camera_detection",
            "yard-camera",
            "2026-11-20T09:00:00Z",
            {"label": "unverified_candidate:vespa_velutina", "confidence": 0.87},
        )
        self.store(self.event)

    def tearDown(self):
        self.tmp.cleanup()

    def test_backup_is_consistent_and_verifiable(self):
        backup = backup_database(self.source, self.backup_dir / "events-backup.sqlite3")
        result = verify_database(backup)
        self.assertEqual(result, {"valid": True, "events": 1, "integrity": "ok"})
        snapshot = SQLiteEventStore(str(backup))
        self.assertEqual(snapshot.count(), 1)
        self.assertEqual(
            snapshot.list_events()[0]["event"]["payload"]["label"],
            "unverified_candidate:vespa_velutina",
        )

    def test_restore_to_new_path_preserves_events(self):
        backup = backup_database(self.source, self.backup_dir / "events-backup.sqlite3")
        restored = restore_database(backup, self.restore_dir / "events-restored.sqlite3")
        self.assertEqual(verify_database(restored)["events"], 1)
        self.assertEqual(SQLiteEventStore(str(restored)).count(), 1)

    def test_refuses_to_overwrite_existing_backup_or_restore_target(self):
        backup = backup_database(self.source, self.backup_dir / "events-backup.sqlite3")
        with self.assertRaises(FileExistsError):
            backup_database(self.source, backup)
        target = self.restore_dir / "must-not-overwrite.sqlite3"
        target.parent.mkdir(mode=0o700)
        target.write_bytes(b"KEEP EXISTING DATA")
        with self.assertRaises(FileExistsError):
            restore_database(backup, target)
        self.assertEqual(target.read_bytes(), b"KEEP EXISTING DATA")

    def test_rejects_same_source_and_destination(self):
        with self.assertRaises(ValueError):
            backup_database(self.source, self.source)

    def test_corrupt_backup_is_rejected_and_not_repaired(self):
        self.backup_dir.mkdir(mode=0o700)
        corrupt = self.backup_dir / "corrupt.sqlite3"
        corrupt.write_bytes(b"NOT SQLITE")
        with self.assertRaises(sqlite3.DatabaseError):
            verify_database(corrupt)
        restore_target = self.restore_dir / "restore.sqlite3"
        with self.assertRaises(sqlite3.DatabaseError):
            restore_database(corrupt, restore_target)
        self.assertFalse(restore_target.exists())
        self.assertEqual(corrupt.read_bytes(), b"NOT SQLITE")

    def test_wrong_schema_is_rejected(self):
        self.backup_dir.mkdir(mode=0o700)
        wrong = self.backup_dir / "wrong-schema.sqlite3"
        with sqlite3.connect(wrong) as db:
            db.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
        with self.assertRaises(sqlite3.DatabaseError):
            verify_database(wrong)

    def test_backup_files_and_directory_are_private_on_posix(self):
        backup = backup_database(self.source, self.backup_dir / "events-backup.sqlite3")
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(self.backup_dir.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o600)

    def test_refuses_shared_backup_directory_on_posix(self):
        if os.name != "posix":
            self.skipTest("POSIX directory mode validation")
        shared = self.root / "shared-backups"
        shared.mkdir(mode=0o755)
        os.chmod(shared, 0o755)
        with self.assertRaises(PermissionError):
            backup_database(self.source, shared / "events.sqlite3")
        self.assertEqual(stat.S_IMODE(shared.stat().st_mode), 0o755)


if __name__ == "__main__":
    unittest.main()
