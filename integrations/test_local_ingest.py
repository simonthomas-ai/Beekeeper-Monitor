import http.client
import json
import os
import socket
import sqlite3
import stat
import tempfile
import threading
import unittest

from datetime import datetime, timedelta, timezone

from integrations.local_ingest import make_handler, make_server, retention_maintenance
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

    def _raw_status(self, raw_request):
        with socket.create_connection(("127.0.0.1", self.server.server_port), timeout=3) as client:
            client.settimeout(3)
            client.sendall(raw_request)
            response = client.recv(4096)
        return response.split(b"\r\n", 1)[0]

    def test_duplicate_negative_and_oversized_content_lengths_rejected(self):
        prefix = (
            b"POST /api/v1/events HTTP/1.1\r\n"
            b"Host: localhost\r\n"
            b"Authorization: Bearer " + TOKEN.encode("ascii") + b"\r\n"
            b"Content-Type: application/json\r\n"
        )
        duplicate = prefix + b"Content-Length: 2\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{}"
        negative = prefix + b"Content-Length: -1\r\nConnection: close\r\n\r\n"
        too_large = prefix + b"Content-Length: 999999999999999999999999999999\r\nConnection: close\r\n\r\n"
        self.assertIn(b" 400 ", self._raw_status(duplicate))
        self.assertIn(b" 400 ", self._raw_status(negative))
        self.assertIn(b" 413 ", self._raw_status(too_large))

    def test_invalid_utf8_rejected(self):
        self.assertEqual(self.send(data=b"\xff", content_type="application/json"), 400)

    def test_slow_incomplete_body_returns_408(self):
        with socket.create_connection(("127.0.0.1", self.server.server_port), timeout=3) as client:
            client.settimeout(8)
            client.sendall(
                b"POST /api/v1/events HTTP/1.1\r\n"
                b"Host: localhost\r\n"
                b"Authorization: Bearer " + TOKEN.encode("ascii") + b"\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: 10\r\nConnection: close\r\n\r\nx"
            )
            response = client.recv(4096)
        self.assertIn(b" 408 ", response.split(b"\r\n", 1)[0])

    def test_worker_limit_rejects_extra_slow_connection(self):
        server = make_server(TOKEN, lambda _: None, port=0, max_workers=1)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        slow = socket.create_connection(("127.0.0.1", server.server_port), timeout=3)
        try:
            slow.sendall(
                b"POST /api/v1/events HTTP/1.1\r\n"
                b"Host: localhost\r\n"
                b"Authorization: Bearer " + TOKEN.encode("ascii") + b"\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: 10\r\nConnection: close\r\n\r\n"
            )
            with socket.create_connection(("127.0.0.1", server.server_port), timeout=3) as extra:
                extra.settimeout(3)
                extra.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
                response = extra.recv(4096)
            self.assertIn(b" 503 ", response.split(b"\r\n", 1)[0])
        finally:
            slow.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

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

    def test_invalid_retention_maintenance_interval_rejected(self):
        with self.assertRaises(ValueError):
            retention_maintenance(self.store, threading.Event(), interval_seconds=10)

    def test_expired_events_are_purged(self):
        event_json = self.event().to_json()
        old_received = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        with self.store._db() as db:
            db.execute(
                "INSERT INTO events (event_id, kind, device_id, event_timestamp, received_at, event_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                ("a" * 64, "hive_telemetry", "old-sensor", "2026-08-01T00:00:00Z",
                 old_received, event_json),
            )
        self.assertEqual(self.store.purge_expired(), 1)
        self.assertEqual(self.store.count(), 0)

    def test_private_sqlite_directory_and_file_modes(self):
        private_dir = os.path.join(self.tmp.name, "private-store")
        store = SQLiteEventStore(os.path.join(private_dir, "events.sqlite3"))
        store(self.event())
        if os.name == "posix":
            directory_mode = stat.S_IMODE(os.stat(private_dir).st_mode)
            file_mode = stat.S_IMODE(os.stat(store.path).st_mode)
            self.assertEqual(directory_mode, 0o700)
            self.assertEqual(file_mode, 0o600)

    def test_refuses_shared_directory_without_changing_its_permissions(self):
        if os.name != "posix":
            self.skipTest("POSIX directory mode check")
        shared_dir = os.path.join(self.tmp.name, "shared")
        os.mkdir(shared_dir, 0o755)
        os.chmod(shared_dir, 0o755)
        with self.assertRaises(PermissionError):
            SQLiteEventStore(os.path.join(shared_dir, "events.sqlite3"))
        self.assertEqual(stat.S_IMODE(os.stat(shared_dir).st_mode), 0o755)

    def test_corrupted_database_fails_closed_without_reinitializing(self):
        corrupt_path = os.path.join(self.tmp.name, "corrupt.sqlite3")
        with open(corrupt_path, "wb") as handle:
            handle.write(b"NOT A SQLITE DATABASE")
        with self.assertRaises(sqlite3.DatabaseError):
            SQLiteEventStore(corrupt_path)
        with open(corrupt_path, "rb") as handle:
            self.assertEqual(handle.read(), b"NOT A SQLITE DATABASE")

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
        if not payload:
            return status, None
        try:
            return status, json.loads(payload)
        except json.JSONDecodeError:
            return status, payload.decode("utf-8", errors="replace")

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

    def test_delete_requires_authentication_and_preserves_event(self):
        event = HiveEvent("hive_telemetry", "sensor-delete-auth", "2026-11-19T19:00:00Z",
                          {"temperature_c": 22.0, "humidity_pct": 44})
        self.store(event)
        event_id = self.store.list_events()[0]["event_id"]
        status, payload = self.request("DELETE", "/api/v1/events/" + event_id, token="wrong")
        self.assertEqual(status, 401)
        self.assertEqual(payload, {"error": "unauthorized"})
        self.assertEqual(self.store.count(), 1)
        self.assertEqual(self.store.list_events()[0]["event_id"], event_id)

    def test_event_api_requires_authentication(self):
        status, _ = self.request("GET", "/api/v1/events", token="wrong")
        self.assertEqual(status, 401)

    def test_station_event_export_is_authenticated_and_versioned(self):
        event = HiveEvent("hive_telemetry", "sensor-export", "2026-11-19T19:00:00Z",
                          {"temperature_c": 22.5, "humidity_pct": 43})
        self.store(event)
        status, payload = self.request("GET", "/api/v1/events/export?limit=10")
        self.assertEqual(status, 200)
        self.assertEqual(payload["export_version"], 1)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["events"][0]["event"]["device_id"], "sensor-export")

        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        conn.request("GET", "/api/v1/events/export?limit=10",
                     headers={"Authorization": "Bearer " + TOKEN})
        response = conn.getresponse()
        self.assertIn("attachment;", response.getheader("Content-Disposition", ""))
        response.read()
        conn.close()

    def test_station_event_export_requires_authentication(self):
        status, _ = self.request("GET", "/api/v1/events/export", token="wrong")
        self.assertEqual(status, 401)

    def test_local_pwa_is_served_on_same_origin(self):
        status, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn('id="station-events-form"', body)
        self.assertIn('id="station-events-export"', body)
        self.assertIn('integrations-ui.js', body)

    def test_private_source_files_are_not_served(self):
        for path in ("/integrations/local_ingest.py", "/integrations/event_store.py",
                     "/.gitignore", "/%2e%2e/integrations/local_ingest.py"):
            with self.subTest(path=path):
                status, _ = self.request("GET", path)
                self.assertEqual(status, 404)





class StorageFailureTests(unittest.TestCase):
    def test_full_or_unavailable_store_never_returns_accepted(self):
        def failing_sink(_event):
            raise sqlite3.OperationalError("database or disk is full")

        server = make_server(TOKEN, failing_sink, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            event = HiveEvent(
                "hive_telemetry", "storage-failure-station", "2026-11-19T19:00:00Z",
                {"temperature_c": 21.0, "humidity_pct": 45},
            )
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
            conn.request(
                "POST", "/api/v1/events", body=event.to_json(),
                headers={
                    "Authorization": "Bearer " + TOKEN,
                    "Content-Type": "application/json",
                },
            )
            response = conn.getresponse()
            body = json.loads(response.read())
            conn.close()
            self.assertEqual(response.status, 503)
            self.assertEqual(body, {"error": "storage_unavailable"})
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)



class AdditionalContractSecurityTests(unittest.TestCase):
    def test_bridge_metadata_is_accepted_but_remains_unverified(self):
        event = HiveEvent(
            "camera_detection",
            "yard_cam_north",
            "2026-11-20T10:00:00+01:00",
            {
                "label": "unverified_candidate:vespa_velutina",
                "confidence": 0.83,
                "origin_event_id": "hornet-event-001",
                "verification_status": "unverified",
                "prey_detected": True,
            },
            source="hornet3000",
        )
        parsed = HiveEvent.from_json(event.to_json())
        self.assertEqual(parsed.payload["verification_status"], "unverified")

    def test_untrusted_coordinates_media_and_free_fields_are_rejected(self):
        valid = {
            "kind": "camera_detection",
            "device_id": "yard_cam_north",
            "timestamp": "2026-11-20T10:00:00+01:00",
            "source": "hornet3000",
            "schema_version": 1,
            "payload": {
                "label": "vespa_velutina",
                "confidence": 0.8,
                "latitude": 51.2,
                "image_base64": "not-accepted",
            },
        }
        with self.assertRaises(ValueError):
            HiveEvent.from_json(json.dumps(valid))

    def test_duplicate_json_keys_are_rejected(self):
        raw = (
            '{"kind":"hive_telemetry","device_id":"sensor-01",'
            '"timestamp":"2026-11-20T10:00:00Z","source":"station-01",'
            '"schema_version":1,"payload":{"temperature_c":21.5,'
            '"humidity_pct":45,"humidity_pct":99}}'
        )
        with self.assertRaises(ValueError):
            HiveEvent.from_json(raw)

    def test_explicit_timezone_offset_is_valid_but_naive_timestamp_is_not(self):
        offset_event = HiveEvent(
            "hive_telemetry", "sensor-01", "2026-11-20T10:00:00+01:00",
            {"temperature_c": 21.5, "humidity_pct": 45},
        )
        self.assertIsNone(offset_event.validate())
        naive_event = HiveEvent(
            "hive_telemetry", "sensor-01", "2026-11-20T10:00:00",
            {"temperature_c": 21.5, "humidity_pct": 45},
        )
        with self.assertRaises(ValueError):
            naive_event.validate()

    def test_extreme_numeric_overflow_is_rejected_as_invalid_input(self):
        event = HiveEvent(
            "camera_detection", "cam_overflow", "2026-11-20T10:00:00Z",
            {"label": "vespa_velutina", "confidence": 10 ** 1000},
        )
        with self.assertRaises(ValueError):
            event.validate()

    def test_boolean_schema_version_is_rejected(self):
        event = HiveEvent(
            "hive_telemetry", "sensor-01", "2026-11-20T10:00:00Z",
            {"temperature_c": 21.5, "humidity_pct": 45},
            schema_version=True,
        )
        with self.assertRaises(ValueError):
            event.validate()

    def test_capacity_fails_closed_and_keeps_existing_events_and_duplicate_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            store = SQLiteEventStore(
                os.path.join(directory, "events.sqlite3"),
                retention_days=90,
                max_rows=100,
            )
            first = None
            for index in range(100):
                event = HiveEvent(
                    "hive_telemetry",
                    f"sensor_{index:03d}",
                    "2026-11-20T10:00:00Z",
                    {"temperature_c": 20.0, "humidity_pct": 45},
                )
                store(event)
                if index == 0:
                    first = event
            self.assertEqual(store.count(), 100)
            self.assertFalse(store(first))
            overflow = HiveEvent(
                "hive_telemetry", "sensor_overflow", "2026-11-20T10:00:00Z",
                {"temperature_c": 20.0, "humidity_pct": 45},
            )
            with self.assertRaises(RuntimeError):
                store(overflow)
            self.assertEqual(store.count(), 100)
            self.assertEqual(
                store.list_events(500)[-1]["event"]["device_id"],
                "sensor_000",
            )

    def test_duplicate_authorization_headers_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = SQLiteEventStore(os.path.join(directory, "events.sqlite3"))
            server = make_server(TOKEN, store, port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                crlf = bytes((13, 10))
                raw = (
                    b"GET /api/v1/events HTTP/1.1" + crlf
                    + b"Host: localhost" + crlf
                    + b"Authorization: Bearer " + TOKEN.encode("ascii") + crlf
                    + b"Authorization: Bearer another-token-value-123456789" + crlf
                    + b"Connection: close" + crlf + crlf
                )
                with socket.create_connection(("127.0.0.1", server.server_port), timeout=3) as client:
                    client.sendall(raw)
                    response = client.recv(4096)
                self.assertIn(b" 401 ", response.split(crlf, 1)[0])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)

    def test_non_ascii_bearer_secret_is_rejected(self):
        with self.assertRaises(ValueError):
            make_handler("ä" * 24, lambda _: None)



if __name__ == "__main__":
    unittest.main()
