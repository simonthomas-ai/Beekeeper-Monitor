"""Real HTTP end-to-end tests for the camera outbox -> source API -> bridge -> Monitor."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

from integrations.local_ingest import BoundedThreadingHTTPServer, make_handler as make_monitor_handler, make_server
from integrations.event_store import SQLiteEventStore

TOKEN = "e2e-only-secret-token-not-for-production-87654321"
SOURCE_KEY = "e2e-source-api-key-not-for-production-987654321"
CURSOR_SECRET = "e2e-cursor-signing-secret-not-for-production-123456789"


@unittest.skipUnless(
    os.environ.get("BEEKEEPER_BRIDGE_ENTRY") and shutil.which("node"),
    "requires companion Node bridge path and Node.js",
)
class BridgeReceiverEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_path = os.path.join(cls.tmp.name, "bridge-e2e.sqlite3")
        cls.store = SQLiteEventStore(cls.db_path)
        cls.server = make_server(TOKEN, cls.store, port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.tmp.cleanup()

    def _run_node(self, script, extra_env=None):
        env = os.environ.copy()
        env["BEEKEEPER_BRIDGE_ENTRY"] = str(Path(os.environ["BEEKEEPER_BRIDGE_ENTRY"]).resolve())
        env["BEEKEEPER_MONITOR_INGEST_URL"] = (
            f"http://127.0.0.1:{self.server.server_port}/api/v1/events"
        )
        env["BEEKEEPER_MONITOR_INGEST_TOKEN"] = TOKEN
        env["BRIDGE_STATE_FILE"] = os.path.join(self.tmp.name, "bridge-state.json")
        if extra_env:
            env.update(extra_env)
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        return result.stdout

    def test_bridge_event_is_persisted_and_replay_is_deduplicated(self):
        script = r"""
import { pathToFileURL } from 'node:url';
const { forwardBatch } = await import(pathToFileURL(process.env.BEEKEEPER_BRIDGE_ENTRY).href);
const event = {
  id: 'e2e-event-0001',
  observed_at: '2026-11-20T08:00:00Z',
  station_id: 'integration-test-station',
  species: 'vespa_velutina',
  confidence: 0.91,
  origin: 'camera',
  status: 'unverified',
  image_path: '/must/not/be/transmitted.jpg',
  latitude: 51.2,
  longitude: 6.8
};
const send = () => forwardBatch([event], new Set());
console.log('first=' + await send());
console.log('replay=' + await send());
"""
        output = self._run_node(script)
        self.assertIn("first=1", output)
        self.assertIn("replay=1", output)
        self.assertEqual(self.store.count(), 1)
        row = self.store.list_events()[0]
        payload = row["event"]["payload"]
        self.assertEqual(payload["verification_status"], "unverified")
        self.assertNotIn("image_path", payload)
        self.assertNotIn("latitude", payload)
        self.assertNotIn("longitude", payload)
        self.assertEqual(SQLiteEventStore(self.db_path).count(), 1)


@unittest.skipUnless(
    os.environ.get("BEEKEEPER_BRIDGE_ENTRY") and shutil.which("node"),
    "requires companion BeeKeeper source API, Node bridge and Node.js",
)
class FullSourceBridgeMonitorEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.companion_root = Path(os.environ["BEEKEEPER_BRIDGE_ENTRY"]).resolve().parent.parent
        if str(cls.companion_root) not in sys.path:
            sys.path.insert(0, str(cls.companion_root))

        from network.source_api import BoundedSourceHTTPServer, make_handler as make_source_handler
        from network.source_event_store import SQLiteSourceEventStore
        from camera.contracts import Detection, make_source_event
        from camera.outbox import SQLiteOutbox
        from camera.runtime import CameraRuntimeError, LocalCameraRuntime
        from camera.source_client import SourceApiClient

        cls.Detection = Detection
        cls.make_source_event = staticmethod(make_source_event)
        cls.SQLiteOutbox = SQLiteOutbox
        cls.CameraRuntimeError = CameraRuntimeError
        cls.LocalCameraRuntime = LocalCameraRuntime
        cls.BoundedSourceHTTPServer = BoundedSourceHTTPServer
        cls.SQLiteSourceEventStore = SQLiteSourceEventStore
        cls.make_source_handler = make_source_handler

        cls.tmp = tempfile.TemporaryDirectory()
        cls.monitor_db = os.path.join(cls.tmp.name, "monitor-events.sqlite3")
        cls.source_db = os.path.join(cls.tmp.name, "source-events.sqlite3")
        cls.camera_outbox_db = os.path.join(cls.tmp.name, "camera-outbox.sqlite3")
        cls.monitor_store = SQLiteEventStore(cls.monitor_db)
        cls.source_store = SQLiteSourceEventStore(
            cls.source_db, retention_days=30, max_rows=1000
        )

        handler = cls.make_source_handler(
            SOURCE_KEY, CURSOR_SECRET, cls.source_store, rate_limit=1000
        )
        cls.source_server = cls.BoundedSourceHTTPServer(
            ("127.0.0.1", 0), handler
        )
        cls.source_thread = threading.Thread(
            target=cls.source_server.serve_forever, daemon=True
        )
        cls.source_thread.start()
        camera_client = SourceApiClient(
            f"http://127.0.0.1:{cls.source_server.server_port}", SOURCE_KEY
        )
        cls.camera_outbox = cls.SQLiteOutbox(cls.camera_outbox_db, max_rows=1000)

        # Production inference is deliberately disabled. This end-to-end test
        # exercises only the durable outbox and drain-only transport path.
        cls.camera_runtime = cls.LocalCameraRuntime(
            detector=None,
            outbox=cls.camera_outbox,
            client=camera_client,
            station_id="integration-station-north",
            source="drain-only-test-fixture",
        )

        monitor_handler = make_monitor_handler(
            TOKEN, cls.monitor_store, rate_limit=1000
        )
        cls.monitor_server = BoundedThreadingHTTPServer(
            ("127.0.0.1", 0), monitor_handler
        )
        cls.monitor_thread = threading.Thread(
            target=cls.monitor_server.serve_forever, daemon=True
        )
        cls.monitor_thread.start()

    @classmethod
    def tearDownClass(cls):
        for name in ("source_server", "monitor_server"):
            server = getattr(cls, name, None)
            if server is not None:
                server.shutdown()
                server.server_close()
        for name in ("source_thread", "monitor_thread"):
            thread = getattr(cls, name, None)
            if thread is not None:
                thread.join(timeout=3)
        if hasattr(cls, "tmp"):
            cls.tmp.cleanup()

    def _run_node(self, script, extra_env=None):
        env = os.environ.copy()
        env["BEEKEEPER_BRIDGE_ENTRY"] = str(
            Path(os.environ["BEEKEEPER_BRIDGE_ENTRY"]).resolve()
        )
        env["BEEKEEPER_MONITOR_INGEST_URL"] = (
            f"http://127.0.0.1:{self.monitor_server.server_port}/api/v1/events"
        )
        env["BEEKEEPER_MONITOR_INGEST_TOKEN"] = TOKEN
        env["BRIDGE_STATE_FILE"] = os.path.join(
            self.tmp.name, "full-source-bridge-state.json"
        )
        if extra_env:
            env.update(extra_env)
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            env=env,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        return result.stdout

    def _queue_synthetic_candidate_event(self, index):
        # Synthetic metadata enters the outbox directly; no frame, detector or
        # inference is exercised. The runtime is drain-only by design.
        event = self.make_source_event(
            station_id="integration-station-north",
            detection=self.Detection(
                "Vespa velutina", 0.87, prey_detected=(index % 2 == 0)
            ),
        )
        self.assertTrue(self.camera_outbox.enqueue(event))
        self.assertEqual(self.camera_outbox.count(), 1)
        self.assertEqual(self.camera_runtime.drain_outbox(), 1)
        self.assertEqual(self.camera_outbox.count(), 0)

    def test_drain_only_runtime_rejects_camera_frame_inference(self):
        with self.assertRaisesRegex(self.CameraRuntimeError, "drain-only"):
            self.camera_runtime.process_frame(1)

    def test_205_synthetic_outbox_events_cross_source_api_bridge_and_monitor(self):
        for index in range(1, 206):
            self._queue_synthetic_candidate_event(index)
        self.assertEqual(self.source_store.count(), 205)

        state_path = os.path.join(self.tmp.name, "full-bridge-state.json")
        script = r"""
import { pathToFileURL } from 'node:url';
const { pollOnce, readState, writeState } = await import(
  pathToFileURL(process.env.BEEKEEPER_BRIDGE_ENTRY).href
);
const stateFile = process.env.BRIDGE_STATE_FILE;
const saveState = state => writeState(state, stateFile);
const options = {
  sourceUrl: process.env.E2E_SOURCE_URL,
  sourceKey: process.env.E2E_SOURCE_KEY,
  endpoint: process.env.BEEKEEPER_MONITOR_INGEST_URL,
  token: process.env.BEEKEEPER_MONITOR_INGEST_TOKEN,
  requireCursor: true,
  saveState,
  sleep: async () => {},
  timeoutMs: 5000
};
const state = await readState(stateFile);
const first = await pollOnce(state, options);
console.log('first=' + first);
const persisted = await readState(stateFile);
const afterRestart = await pollOnce(persisted, options);
console.log('afterRestart=' + afterRestart);
const replayState = new Set();
replayState.cursor = null;
const replay = await pollOnce(replayState, { ...options, saveState: async () => {} });
console.log('replay=' + replay);
"""
        output = self._run_node(script, {
            "BRIDGE_STATE_FILE": state_path,
            "E2E_SOURCE_URL": f"http://127.0.0.1:{self.source_server.server_port}",
            "E2E_SOURCE_KEY": SOURCE_KEY,
        })
        self.assertIn("first=205", output)
        self.assertIn("afterRestart=0", output)
        self.assertIn("replay=205", output)

        self.assertEqual(self.monitor_store.count(), 205)
        rows = self.monitor_store.list_events(500)
        self.assertEqual(len(rows), 205)
        origin_ids = {
            row["event"]["payload"]["origin_event_id"]
            for row in rows
        }
        self.assertEqual(len(origin_ids), 205)
        for row in rows:
            event = row["event"]
            payload = event["payload"]
            self.assertEqual(event["kind"], "camera_detection")
            self.assertEqual(payload["label"], "unverified_candidate:vespa_velutina")
            self.assertEqual(payload["verification_status"], "unverified")
            self.assertNotIn("latitude", payload)
            self.assertNotIn("longitude", payload)
            self.assertNotIn("image", payload)
            self.assertNotIn("audio", payload)
        self.assertEqual(SQLiteEventStore(self.monitor_db).count(), 205)


if __name__ == "__main__":
    unittest.main()
