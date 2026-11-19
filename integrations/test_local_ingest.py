import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from integrations.local_ingest import make_handler
from integrations.event_contracts import HiveEvent

TOKEN = "testing-only-token-not-for-production-1234"

class LocalIngestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = []
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(TOKEN, cls.events.append))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def send(self, path="/api/v1/events", token=TOKEN, data=None):
        if data is None:
            data = HiveEvent("hive_telemetry", "sensor-1", "2026-11-19T19:00:00Z",
                             {"temperature_c": 21.5, "humidity_pct": 45}).to_json()
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
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

    def test_short_token_rejected(self):
        with self.assertRaises(ValueError):
            make_handler("weak", lambda _: None)

if __name__ == "__main__":
    unittest.main()
