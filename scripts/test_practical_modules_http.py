"""Practical loopback HTTP tests for Varroa counts and unverified queen/swarm candidates.

Synthetic metadata only: no camera, model, mite counter or field validation.
"""
import json
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from integrations.event_store import SQLiteEventStore
from integrations.local_ingest import make_server

TOKEN = "practical-module-contract-test-token-32"


class PracticalModuleHttpTests(unittest.TestCase):
    def test_varroa_queen_swarm_persistence_replay_and_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteEventStore(str(Path(tmp) / "events.sqlite3"), retention_days=30, max_rows=100)
            server = make_server(TOKEN, store, port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            endpoint = f"http://127.0.0.1:{server.server_address[1]}/api/v1/events"
            timestamp = datetime.now(timezone.utc).isoformat()
            base = {"device_id": "hive_station_01", "timestamp": timestamp,
                    "source": "module_contract_test", "schema_version": 1}
            events = [
                dict(base, kind="varroa_count", payload={"mites": 7, "bees_examined": 200}),
                dict(base, kind="camera_detection", payload={"label": "unverified_candidate:queen", "confidence": 0.7, "verification_status": "unverified", "origin_event_id": "queen-001"}),
                dict(base, kind="camera_detection", payload={"label": "unverified_candidate:swarm", "confidence": 0.65, "verification_status": "unverified", "origin_event_id": "swarm-001"}),
            ]

            def post(event):
                req = Request(endpoint, data=json.dumps(event).encode("utf-8"), method="POST",
                              headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
                return urlopen(req, timeout=5)

            try:
                for event in events:
                    with post(event) as response:
                        self.assertEqual(response.status, 202)
                self.assertEqual(store.count(), 3)
                for event in events:
                    with post(event) as response:
                        self.assertEqual(response.status, 202)
                self.assertEqual(store.count(), 3, "Replays must not duplicate records")

                req = Request(endpoint + "?limit=10", headers={"Authorization": "Bearer " + TOKEN})
                with urlopen(req, timeout=5) as response:
                    data = json.load(response)
                self.assertEqual(data["count"], 3)
                stored = [item["event"] for item in data["events"]]
                self.assertEqual({e["kind"] for e in stored}, {"varroa_count", "camera_detection"})
                self.assertEqual({e["payload"].get("label") for e in stored if e["kind"] == "camera_detection"},
                                 {"unverified_candidate:queen", "unverified_candidate:swarm"})
                self.assertNotIn("latitude", json.dumps(data))
                self.assertNotIn("image", json.dumps(data))

                invalid = [
                    dict(base, kind="varroa_count", payload={"mites": -1, "bees_examined": 200}),
                    dict(base, kind="camera_detection", payload={"label": "queen", "confidence": 0.9, "verification_status": "verified"}),
                    dict(base, kind="camera_detection", payload={"label": "swarm", "confidence": 0.8, "latitude": 51.0}),
                ]
                for event in invalid:
                    with self.subTest(kind=event["kind"], payload=event["payload"]):
                        with self.assertRaises(HTTPError) as error:
                            post(event)
                        self.assertEqual(error.exception.code, 400)
                        error.exception.close()
                self.assertEqual(store.count(), 3, "Invalid data must not be stored")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
