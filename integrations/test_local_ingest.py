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

    def send(self, path="/api/v1/events", token=TOKEN, data=None, content_type="application/json"):
        if data is None:
            data = HiveEvent("hive_telemetry", "sensor-1", "2026-11-19T19:00:00Z",
                             {"temperature_c": 21.5, "humidity_pct": 45}).to_json()
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Authorization": "Bearer " + token, "Content-Type": content_type}
        conn.request("POST", path, data, headers)
        resp = conn.getresponse()
        status = resp.status
        resp.read()
        conn.close()
        return status

    def test_valid_real_transport(self):
        before = len(self.events)
        self.assertEqual(self.send(), 202)
        self.assertEqual(len(self.events), before + 1)

    def test_bad_token(self):
        self.assertEqual(self.send(token="wrong"), 401)

    def test_unknown_endpoint(self):
        self.assertEqual(self.send(path="/bad"), 404)

    def test_invalid_data(self):
        self.assertEqual(self.send(data='{"invalid":true}'), 400)

    def test_untrusted_approval(self):
        data = json.loads(HiveEvent("varroa_count", "v1", "2026-11-19T19:00:00Z",
                                   {"mites": 1, "bees_examined": 10}).to_json())
        data["payload"]["training_approved"] = True
        self.assertEqual(self.send(data=json.dumps(data)), 400)

    def test_oversized_body_rejected(self):
        self.assertEqual(self.send(data="x" * 32769), 413)

    def test_non_json_content_type_rejected(self):
        self.assertEqual(self.send(content_type="text/plain"), 415)

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

    def test_invalid_page_size_rejected(self):
        with self.assertRaises(ValueError):
            self.store.list_events(501)

    def test_delete_is_explicit_and_idempotent(self):
        event = self.event()
        self.store(event)
        event_id = self.store.list_events()[0]["event_id"]
        self.assertTrue(self.store.delete(event_id))
        self.assertFalse(self.store.delete(event_id))
        self.assertEqual(self.store.count(), 0)


class AuthenticatedStoreApiTests(unittest.TestCase):
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

    def request(self, method, path, token=TOKEN, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Authorization": "Bearer " + token}
        if body is not None:
            headers["Content-Type"] = "application/json"
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        payload = response.read()
        status = response.status
        conn.close()
        return status, json.loads(payload) if payload else None

    def test_authenticated_list_and_delete(self):
        event = HiveEvent("hive_telemetry", "sensor-api", "2026-11-19T19:00:00Z",
                          {"temperature_c": 22.0, "humidity_pct": 44})
        self.store(event)
        status, payload = self.request("GET", "/api/v1/events?limit=10")
        self.assertEqual(status, 200)
        self.assertEqual(payload["count"], 1)
        event_id = payload["events"][0]["event_id"]
        status, payload = self.request("DELETE", "/api/v1/events/" + event_id)
        self.assertEqual(status, 200)
        self.assertTrue(payload["deleted"])
        self.assertEqual(self.store.count(), 0)

    def test_event_api_requires_authentication(self):
        status, _ = self.request("GET", "/api/v1/events", token="wrong")
        self.assertEqual(status, 401)


if __name__ == "__main__":
    unittest.main()
