import hashlib
import tempfile
import unittest
from pathlib import Path
from scripts.verify_varroa_source_blob import verify


class BlobVerificationTests(unittest.TestCase):
    def test_exact_bytes_and_digest(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "model.pt"
            p.write_bytes(b"test-weights")
            content = p.read_bytes()
            manifest = {"bytes": len(content), "git_blob_sha1": hashlib.sha1(b"blob " + str(len(content)).encode() + bytes([0]) + content).hexdigest()}
            result = verify(p, manifest)
            self.assertEqual(result["local_sha256"], hashlib.sha256(content).hexdigest())
            self.assertFalse(result["model_validated"])

    def test_rejects_modified_bytes_same_size(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "model.pt"
            p.write_bytes(b"other-weights")
            content = b"test--weights"
            manifest = {"bytes": len(content), "git_blob_sha1": hashlib.sha1(b"blob " + str(len(content)).encode() + bytes([0]) + content).hexdigest()}
            with self.assertRaises(ValueError):
                verify(p, manifest)

    def test_rejects_missing_file(self):
        with self.assertRaises(ValueError):
            verify(Path("/nonexistent/varroa-weights.pt"), {"bytes": 10, "git_blob_sha1": "0" * 40})


if __name__ == "__main__":
    unittest.main()
