"""Real loopback HTTP integration: adapter -> authenticated receiver -> SQLite -> API.

Uses synthetic metadata only; does not claim a working camera or model.
"""
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from integrations.external_detector_adapter import adapt_detection
from integrations.event_store import SQLiteEventStore
from integrations.local_ingest import make_server

TOKEN = "test-only-http-bridge-token-please-replace"


class ExternalDetectorHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = SQLiteEventStore(str(Path(self.temp.name) / "private" / "events.sqlite3"))
        self.server = make_server(TOKEN, self.store, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.temp.cleanup()

    def request(self, method, path, body=None, token=TOKEN):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        headers = {"Authorization": "Bearer " + token}
        if body is not None:
            headers["Content-Type"] = "application/json"
        try:
            conn.request(method, path, body=body, headers=headers)
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def test_detector_to_http_sqlite_api_with_replay_and_privacy(self):
        event = adapt_detection({
            "taxon": "vespa_velutina", "confidence": 0.93,
            "timestamp": "2026-11-21T18:30:00Z", "event_id": "external-cam-001",
        }, device_id="station_01", source="external_camera")
        body = event.to_json()
        status, _ = self.request("POST", "/api/v1/events", body, token="wrong")
        self.assertEqual(status, 401)
        self.assertEqual(self.store.count(), 0)
        for _ in range(2):
            status, response = self.request("POST", "/api/v1/events", body)
            self.assertEqual(status, 202, response)
        self.assertEqual(self.store.count(), 1)
        status, response = self.request("GET", "/api/v1/events?limit=10")
        self.assertEqual(status, 200)
        self.assertEqual(response["count"], 1)
        row = response["events"][0]
        self.assertEqual(row["event"]["payload"]["label"], "vespa_velutina")
        self.assertEqual(row["event"]["payload"]["verification_status"], "unverified")
        self.assertEqual(row["event"]["payload"]["origin_event_id"], "external-cam-001")
        self.assertNotIn("image", json.dumps(row))
        self.assertNotIn("gps", json.dumps(row))
        status, _ = self.request("GET", "/api/v1/events", token="wrong")
        self.assertEqual(status, 401)
        status, response = self.request("DELETE", "/api/v1/events/" + row["event_id"])
        self.assertEqual(status, 200)
        self.assertTrue(response["deleted"])
        self.assertEqual(self.store.count(), 0)


if __name__ == "__main__":
    unittest.main()
