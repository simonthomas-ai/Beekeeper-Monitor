import json
import struct
import tempfile
import unittest
from pathlib import Path
from inspect_external_glb import inspect

class ExternalGLBTests(unittest.TestCase):
    def test_missing_assets_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            report = inspect(root / "bee.glb", root / "LICENSE.txt", root / "manifest.json")
            self.assertEqual(report["training_approved"], "NO")
            self.assertIn("GLB file missing", report["issues"])

    def test_valid_glb_still_requires_manual_review(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            payload = json.dumps({"asset": {"version": "2.0"}, "meshes": [{"primitives": []}]}).encode()
            payload += b" " * (-len(payload) % 4)
            glb = root / "bee.glb"
            glb.write_bytes(struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(payload)) + struct.pack("<I4s", len(payload), b"JSON") + payload)
            (root / "LICENSE.txt").write_text("CC0 1.0", encoding="utf-8")
            (root / "manifest.json").write_text('{"source":"example"}', encoding="utf-8")
            report = inspect(glb, root / "LICENSE.txt", root / "manifest.json")
            self.assertEqual(report["issues"], [])
            self.assertEqual(report["mesh_count"], 1)
            self.assertEqual(report["training_approved"], "NO")
            self.assertEqual(report["license_verified"], "NO")

    def test_reject_bad_header(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            glb = root / "bee.glb"
            glb.write_bytes(b"not a real GLB file")
            report = inspect(glb, root / "LICENSE.txt", root / "manifest.json")
            self.assertTrue(report["issues"])

if __name__ == "__main__":
    unittest.main()
