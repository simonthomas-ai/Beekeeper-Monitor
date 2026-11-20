import hashlib
import tempfile
import unittest
from pathlib import Path
from scripts.export_varroa_onnx import validate_export_request

class ExportGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.weights = Path(self.tmp.name) / "best.pt"
        self.weights.write_bytes(b"synthetic test only" * 100)
        self.digest = hashlib.sha256(self.weights.read_bytes()).hexdigest()
    def test_requires_review(self):
        with self.assertRaises(ValueError):
            validate_export_request(self.weights, self.digest, reviewed=False)
    def test_rejects_mismatch(self):
        with self.assertRaises(ValueError):
            validate_export_request(self.weights, "0"*64, reviewed=True)
    def test_rejects_missing_file(self):
        with self.assertRaises(ValueError):
            validate_export_request(Path(self.tmp.name)/"missing.pt", self.digest, reviewed=True)
    def test_rejects_wrong_format(self):
        p = self.weights.with_suffix(".onnx")
        self.weights.rename(p)
        with self.assertRaises(ValueError):
            validate_export_request(p, self.digest, reviewed=True)
    def test_verified_file_passes_without_deserialization(self):
        validate_export_request(self.weights, self.digest, reviewed=True)

if __name__ == "__main__":
    unittest.main()
