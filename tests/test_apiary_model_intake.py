import tempfile
import unittest
from pathlib import Path
from scripts.apiary_model_intake import inspect_artifact

class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "model.onnx"
        self.path.write_bytes(b"fixture only; not a real ONNX model")
        self.kw = dict(source_url="https://example.org/model.onnx", license_spdx="UNKNOWN",
                       attribution="Test fixture", module="varroa_board")
    def test_never_approves_model(self):
        r = inspect_artifact(self.path, **self.kw)
        self.assertFalse(r["approved_for_inference"])
        self.assertEqual(len(r["sha256"]), 64)
    def test_reject_http(self):
        with self.assertRaises(ValueError):
            inspect_artifact(self.path, **{**self.kw,"source_url":"http://example.org/model"})
    def test_reject_unknown_module(self):
        with self.assertRaises(ValueError):
            inspect_artifact(self.path, **{**self.kw,"module":"other"})
    def test_reject_missing_attribution(self):
        with self.assertRaises(ValueError):
            inspect_artifact(self.path, **{**self.kw,"attribution":""})
    def test_reject_non_onnx(self):
        self.path.rename(self.path.with_suffix(".pt"))
        with self.assertRaises(ValueError):
            inspect_artifact(self.path.with_suffix(".pt"), **self.kw)

if __name__ == "__main__":
    unittest.main()
