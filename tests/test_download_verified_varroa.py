import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from scripts.download_verified_varroa import SOURCE_URL, download_verified


class FakeResponse(io.BytesIO):
    def geturl(self):
        return SOURCE_URL


class DownloadTests(unittest.TestCase):
    def test_exact_verified_bytes(self):
        data = b"test weights"
        manifest = {"bytes": len(data), "git_blob_sha1": hashlib.sha1(b"blob " + str(len(data)).encode() + bytes([0]) + data).hexdigest()}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.pt"
            result = download_verified(path, manifest, opener=lambda request, timeout: FakeResponse(data))
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(result["local_sha256"], hashlib.sha256(data).hexdigest())
            self.assertFalse(result["converted_to_onnx"])

    def test_mismatched_bytes_fail_closed(self):
        data = b"test weights"
        manifest = {"bytes": len(data), "git_blob_sha1": "0" * 40}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.pt"
            with self.assertRaises(ValueError):
                download_verified(path, manifest, opener=lambda request, timeout: FakeResponse(data))
            self.assertFalse(path.exists())
            self.assertFalse(path.with_name("best.pt.partial").exists())

    def test_truncated_download_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.pt"
            with self.assertRaises(ValueError):
                download_verified(path, {"bytes": 20, "git_blob_sha1": "0" * 40},
                                  opener=lambda request, timeout: FakeResponse(b"short"))
            self.assertFalse(path.exists())

    def test_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.pt"
            path.write_bytes(b"existing")
            with self.assertRaises(ValueError):
                download_verified(path, {"bytes": 5, "git_blob_sha1": "0" * 40})
            self.assertEqual(path.read_bytes(), b"existing")


if __name__ == "__main__":
    unittest.main()
