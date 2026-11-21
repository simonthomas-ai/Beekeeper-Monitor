"""Real loopback HTTP integration: adapter -> authenticated receiver -> SQLite -> API.

Uses synthetic metadata only; does not claim a working camera or model.
"""
import http.client
import socket
import json
import subprocess
from datetime import datetime, timezone
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

    def test_lost_http_response_then_retry_is_idempotent(self):
        """A disconnected client must not create a second SQLite event."""
        event = adapt_detection({
            "taxon": "vespa_velutina", "confidence": 0.97,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": "reconnect-lost-response-001",
        }, device_id="station_01", source="external_camera")
        body = event.to_json().encode("utf-8")
        request = (
            b"POST /api/v1/events HTTP/1.1\\r\\n"
            b"Host: 127.0.0.1\\r\\n"
            + ("Authorization: Bearer " + TOKEN + "\\r\\n").encode("ascii")
            + b"Content-Type: application/json\\r\\n"
            + ("Content-Length: " + str(len(body)) + "\\r\\n").encode("ascii")
            + b"Connection: close\\r\\n\\r\\n" + body
        )
        # Send the complete request, then close without reading the response.
        with socket.create_connection(("127.0.0.1", self.server.server_port), timeout=4) as sock:
            sock.sendall(request)
            sock.shutdown(socket.SHUT_WR)
            # The server can still be processing; a client retry must be safe.
        status, response = self.request("POST", "/api/v1/events", body)
        self.assertEqual(status, 202, response)
        self.assertEqual(self.store.count(), 1)
        status, response = self.request("GET", "/api/v1/events?limit=10")
        self.assertEqual(status, 200)
        self.assertEqual(response["count"], 1)
        self.assertEqual(response["events"][0]["event"]["payload"]["origin_event_id"],
                         "reconnect-lost-response-001")

    def test_detector_to_http_sqlite_api_with_replay_and_privacy(self):
        event = adapt_detection({
            "taxon": "vespa_velutina", "confidence": 0.93,
            "timestamp": datetime.now(timezone.utc).isoformat(), "event_id": "external-cam-001",
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
        script = """
const fs=require('node:fs');
const rules=require('./alert-rules.js');
const row=JSON.parse(fs.readFileSync(0,'utf8'));
const cfg={enabled:true,thresholdPercent:90,cooldownSeconds:0};
const first=rules.selectAlerts([row],cfg,new Set(),Date.now());
if(first.alerts.length!==1)process.exit(11);
if(!rules.describe(first.alerts[0]).includes('unbestätigt'))process.exit(12);
if(rules.selectAlerts([row],cfg,new Set([row.event_id]),Date.now()).alerts.length)process.exit(13);
if(rules.selectAlerts([row],{enabled:false},new Set(),Date.now()).alerts.length)process.exit(14);
"""
        result = subprocess.run(
            ["node", "-e", script], input=json.dumps(row), text=True,
            capture_output=True, timeout=10, cwd=Path(__file__).resolve().parents[1],
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        status, _ = self.request("GET", "/api/v1/events", token="wrong")
        self.assertEqual(status, 401)
        status, response = self.request("DELETE", "/api/v1/events/" + row["event_id"])
        self.assertEqual(status, 200)
        self.assertTrue(response["deleted"])
        self.assertEqual(self.store.count(), 0)


if __name__ == "__main__":
    unittest.main()
