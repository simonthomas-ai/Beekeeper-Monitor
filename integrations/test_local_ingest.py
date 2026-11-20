import http.client
import json
import os
import tempfile
import threading
import unittest

from integrations.local_ingest import make_handler, make_server
from integrations.event_contracts import HiveEvent
from integrations.event_store import SQLiteEventStore

TOKEN = "testing-only-token-not-for-production-1234"


class LocalIngestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = []
        cls.server = make_server(TOKEN, cls.events.append)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def send(self, method="POST", path="/api/v1/events", token=TOKEN, data=None,
             content_type="application/json"):
        if method == "POST" and data is None:
            data = HiveEvent("hive_telemetry", "sensor-1", "2026-11-19T19:00:00Z",
                             {"temperature_c": 21.5, "humidity_pct": 45}).to_json()
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Authorization": "Bearer " + token}
        if method == "POST":
            headers["Content-Type"] = content_type
        conn.request(method, path, data, headers)
        resp = conn.getresponse()
        status = resp.status
        body = resp.read()
        conn.close()
        return status, body

    def test_valid_real_transport(self):
        before = len(self.events)
        status, _ = self.send()
        self.assertEqual(status, 202)
        self.assertEqual(len(self.events), before + 1)

    def test_bad_token(self):
        self.assertEqual(self.send(token="wrong")[0], 401)

    def test_unknown_endpoint(self):
        self.assertEqual(self.send(path="/bad")[0], 404)

    def test_invalid_data(self):
        self.assertEqual(self.send(data='{"invalid":true}')[0], 400)

    def test_extra_location_or_media_payload_is_rejected(self):
        data = HiveEvent("hive_telemetry", "sensor-1", "2026-11-19T19:00:00Z",
                         {"temperature_c": 21.5, "humidity_pct": 45}).to_json()
        obj = json.loads(data)
        obj["payload"]["latitude"] = 51.2
        self.assertEqual(self.send(data=json.dumps(obj))[0], 400)

    def test_oversized_body_rejected(self):
        self.assertEqual(self.send(data="x" * 32769)[0], 413)

    def test_non_json_content_type_rejected(self):
        self.assertEqual(self.send(data="{}", content_type="text/plain")[0], 415)

    def test_short_token_rejected(self):
        with self.assertRaises(ValueError):
            make_handler("weak", lambda _: None)


class SQLiteEventStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "events.sqlite3")
        self.store = SQLiteEventStore(self.path, retention_days=90, max_rows=100)

    def tearDown(self):
        self.tmp.cleanup()

    def event(self):
        return HiveEvent("hive_telemetry", "sensor-1", "2026-11-19T19:00:00Z",
                         {"temperature_c": 21.5, "humidity_pct": 45})

    def test_persists_and_reads_event(self):
        self.assertTrue(self.store(self.event()))
        self.assertEqual(self.store.count(), 1)
        self.assertEqual(self.store.list_events()[0]["event"]["device_id"], "sensor-1")

    def test_duplicate_delivery_is_idempotent(self):
        event = self.event()
        self.assertTrue(self.store(event))
        self.assertFalse(self.store(event))
        self.assertEqual(self.store.count(), 1)

    def test_explicit_delete(self):
        self.store(self.event())
        item = self.store.list_events()[0]
        self.assertTrue(self.store.delete(item["event_id"]))
        self.assertEqual(self.store.count(), 0)

    def test_invalid_page_size_rejected(self):
        with self.assertRaises(ValueError):
            self.store.list_events(501)


class ReadDeleteApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.store = SQLiteEventStore(os.path.join(cls.tmp.name, "api.sqlite3"))
        cls.server = make_server(TOKEN, cls.store)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.tmp.cleanup()

    def request(self, method, path, token=TOKEN):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request(method, path, headers={"Authorization": "Bearer " + token})
        resp = conn.getresponse()
        status, body = resp.status, resp.read()
        conn.close()
        return status, json.loads(body) if body else {}

    def setUp(self):
        for item in self.store.list_events(500):
            self.store.delete(item["event_id"])

    def test_authenticated_bounded_read_and_delete(self):
        event = HiveEvent("camera_detection", "cam-01", "2026-11-20T08:00:00Z",
                          {"label": "vespa_velutina", "confidence": 0.97})
        self.store(event)
        status, result = self.request("GET", "/api/v1/events?limit=10")
        self.assertEqual(status, 200)
        self.assertEqual(len(result["events"]), 1)
        event_id = result["events"][0]["event_id"]
        status, result = self.request("DELETE", "/api/v1/events/" + event_id)
        self.assertEqual(status, 200)
        self.assertTrue(result["deleted"])
        self.assertEqual(self.store.count(), 0)

    def test_read_requires_authentication(self):
        self.assertEqual(self.request("GET", "/api/v1/events", token="bad")[0], 401)

    def test_read_limit_is_bounded(self):
        self.assertEqual(self.request("GET", "/api/v1/events?limit=501")[0], 400)


if __name__ == "__main__":
    unittest.main()
