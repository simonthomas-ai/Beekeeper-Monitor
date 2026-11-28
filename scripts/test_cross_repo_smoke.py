#!/usr/bin/env python3
"""Exercise real local receiver HTTP with a BeeKeeper3000 bridge-generated event.

This tests the cross-repository event contract, not a physical camera or radio.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from integrations.event_store import SQLiteEventStore
from integrations.local_ingest import make_server

TOKEN = "cross-repository-test-token-32-characters"
ROOT = Path(__file__).resolve().parents[1]


class CrossRepositorySmoke(unittest.TestCase):
    def test_bridge_to_real_receiver_and_replay(self):
        bridge = ROOT.parent / "beekeeper3000" / "monitor-bridge" / "bridge.mjs"
        self.assertTrue(bridge.is_file(), "BeeKeeper3000 bridge checkout missing")
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteEventStore(str(Path(tmp) / "events.sqlite3"), retention_days=30, max_rows=100)
            server = make_server(TOKEN, store, port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/api/v1/events"
                node = r"""
const { forwardBatch } = await import(process.argv[1]);
const endpoint = process.argv[2], token = process.argv[3];
const event = {id:'contract-test-001',observed_at:new Date().toISOString(),station_id:'station_test',species:'Vespa velutina',confidence:0.82,prey_detected:false,origin:'camera'};
const state = new Set();
const options = {endpoint,token,saveState:async()=>{},maxAttempts:1};
const first = await forwardBatch([event],state,options);
const replay = await forwardBatch([event],new Set(),options);
if(first!==1 || replay!==1) throw new Error('Bridge delivery/replay failed');
console.log(JSON.stringify({first,replay}));
"""
                # The second attempt must receive a durable duplicate acknowledgement.
                result = subprocess.run(
                    ["node", "--input-type=module", "-e", node, bridge.as_uri(), url, TOKEN],
                    capture_output=True, text=True, timeout=40, check=False
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                request = Request(url + "?limit=10", headers={"Authorization": "Bearer " + TOKEN})
                with urlopen(request, timeout=5) as response:
                    data = json.load(response)
                self.assertEqual(data["count"], 1, "Replay must not create duplicate records")
                self.assertEqual(len(data["events"]), 1)
                self.assertEqual(store.count(), 1)
                event = data["events"][0]["event"]
                self.assertEqual(event["kind"], "camera_detection")
                self.assertEqual(event["payload"]["verification_status"], "unverified")
                self.assertTrue(event["payload"]["label"].startswith("unverified_candidate:"))
                self.assertNotIn("image", json.dumps(data))
                self.assertNotIn("latitude", json.dumps(data))
                with self.assertRaises(HTTPError) as unauthorized:
                    urlopen(Request(url + "?limit=10"), timeout=5)
                self.assertEqual(unauthorized.exception.code, 401)
                unauthorized.exception.close()
                malicious = dict(event)
                malicious["payload"] = dict(event["payload"], latitude=51.2)
                bad_request = Request(url, data=json.dumps(malicious).encode("utf-8"), method="POST", headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
                with self.assertRaises(HTTPError) as invalid:
                    urlopen(bad_request, timeout=5)
                self.assertEqual(invalid.exception.code, 400)
                invalid.exception.close()
                self.assertEqual(store.count(), 1, "Rejected payload must not alter durable storage")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
