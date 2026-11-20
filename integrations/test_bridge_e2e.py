"""Real bridge-to-receiver integration test; activated in CI with BEEKEEPER_BRIDGE_ENTRY."""
import os
import shutil
import subprocess
import tempfile
import threading
import unittest

from integrations.local_ingest import make_server
from integrations.event_store import SQLiteEventStore

TOKEN = "e2e-only-secret-token-not-for-production-87654321"


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
        cls.server = make_server(TOKEN, cls.store)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.tmp.cleanup()

    def test_bridge_event_is_persisted_and_replay_is_deduplicated(self):
        env = os.environ.copy()
        env["BEEKEEPER_INGEST_URL"] = (
            f"http://127.0.0.1:{self.server.server_port}/api/v1/events"
        )
        env["BEEKEEPER_INGEST_TOKEN"] = TOKEN
        script = r"""
import { pathToFileURL } from 'node:url';
const { forwardBatch } = await import(pathToFileURL(process.env.BEEKEEPER_BRIDGE_ENTRY).href);
const event = {
  id: 'e2e-event-0001',
  observed_at: '2026-11-20T08:00:00Z',
  station_id: 'integration-test-station',
  species: 'vespa_velutina',
  confidence: 0.91,
  status: 'expert_confirmed',
  image_path: '/must/not/be/transmitted.jpg',
  latitude: 51.2,
  longitude: 6.8
};
const send = () => forwardBatch([event], new Set(), {
  endpoint: process.env.BEEKEEPER_INGEST_URL,
  token: process.env.BEEKEEPER_INGEST_TOKEN,
  saveState: async () => {}
});
console.log('first=' + await send());
console.log('replay=' + await send());
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        self.assertIn("first=1", result.stdout)
        self.assertIn("replay=1", result.stdout)
        self.assertEqual(self.store.count(), 1)
        row = self.store.list_events()[0]
        payload = row["event"]["payload"]
        self.assertEqual(payload["verification_status"], "unverified")
        self.assertNotIn("image_path", payload)
        self.assertNotIn("latitude", payload)
        self.assertNotIn("longitude", payload)
        self.assertEqual(SQLiteEventStore(self.db_path).count(), 1)


if __name__ == "__main__":
    unittest.main()
