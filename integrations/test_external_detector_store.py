"""End-to-end metadata adapter -> validated contract -> durable SQLite store."""
import tempfile
import unittest
from pathlib import Path

from integrations.external_detector_adapter import adapt_detection
from integrations.event_contracts import HiveEvent
from integrations.event_store import SQLiteEventStore


class ExternalDetectorStoreTests(unittest.TestCase):
    def test_candidate_persists_and_replay_is_idempotent(self):
        record = {
            "taxon": "vespa_velutina",
            "confidence": 0.83,
            "timestamp": "2026-11-21T17:00:00Z",
            "event_id": "detector-123",
        }
        event = adapt_detection(record, device_id="station_01", source="external_camera")
        with tempfile.TemporaryDirectory() as root:
            store = SQLiteEventStore(str(Path(root) / "private" / "events.sqlite3"))
            self.assertTrue(store(HiveEvent.from_json(event.to_json())))
            self.assertFalse(store(HiveEvent.from_json(event.to_json())))
            self.assertEqual(store.count(), 1)
            stored = store.list_events(limit=1)[0]["event"]
            self.assertEqual(stored["payload"]["verification_status"], "unverified")
            self.assertEqual(stored["payload"]["label"], "vespa_velutina")
            self.assertEqual(stored["payload"]["origin_event_id"], "detector-123")
            self.assertNotIn("image", stored["payload"])
            self.assertNotIn("gps", stored["payload"])
            # Reopen SQLite to verify durable replay protection across restarts.
            reopened = SQLiteEventStore(str(Path(root) / "private" / "events.sqlite3"))
            self.assertFalse(reopened(HiveEvent.from_json(event.to_json())))
            self.assertEqual(reopened.count(), 1)
            self.assertTrue(reopened.delete(reopened.list_events(limit=1)[0]["event_id"]))
            self.assertEqual(reopened.count(), 0)

    def test_unreviewed_label_cannot_reach_store(self):
        with tempfile.TemporaryDirectory() as root:
            store = SQLiteEventStore(str(Path(root) / "private" / "events.sqlite3"))
            with self.assertRaises(ValueError):
                store(adapt_detection({
                    "taxon": "unreviewed_species", "confidence": 0.95,
                    "timestamp": "2026-11-21T17:00:00Z", "event_id": "bad-1"
                }, device_id="station_01", source="external_camera"))
            self.assertEqual(store.count(), 0)


if __name__ == "__main__":
    unittest.main()
