import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from scripts.download_verified_varroa import SOURCE_URL, download_verified


class FakeResponse(io.BytesIO):
    def geturl(self):
        return SOURCE_URL


def authorized_synthetic_manifest(data: bytes) -> dict:
    blob = hashlib.sha1(
        b"blob " + str(len(data)).encode() + bytes([0]) + data
    ).hexdigest()
    return {
        "bytes": len(data),
        "git_blob_sha1": blob,
        "weights_license_independently_confirmed": True,
        "download_authorized": True,
        "download_authorization_ref": "synthetic-test-only",
    }


class DownloadTests(unittest.TestCase):
    def test_exact_verified_bytes(self):
        data = b"synthetic test bytes, not a model"
        manifest = authorized_synthetic_manifest(data)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.pt"
            result = download_verified(
                path, manifest,
                opener=lambda request, timeout: FakeResponse(data),
            )
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(result["local_sha256"], hashlib.sha256(data).hexdigest())
            self.assertFalse(result["converted_to_onnx"])

    def test_unapproved_manifest_fails_before_network_access(self):
        data = b"synthetic test bytes, not a model"
        manifest = authorized_synthetic_manifest(data)
        manifest["weights_license_independently_confirmed"] = False
        manifest["download_authorized"] = False
        called = False

        def forbidden_opener(request, timeout):
            nonlocal called
            called = True
            raise AssertionError("network must not be accessed for an unapproved model")

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.pt"
            with self.assertRaisesRegex(ValueError, "license review is not confirmed"):
                download_verified(path, manifest, opener=forbidden_opener)
            self.assertFalse(called)
            self.assertFalse(path.exists())

    def test_missing_authorization_reference_fails_before_network_access(self):
        data = b"synthetic test bytes, not a model"
        manifest = authorized_synthetic_manifest(data)
        manifest["download_authorization_ref"] = None
        called = False

        def forbidden_opener(request, timeout):
            nonlocal called
            called = True
            raise AssertionError("network must not be accessed without a review reference")

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.pt"
            with self.assertRaisesRegex(ValueError, "review reference is required"):
                download_verified(path, manifest, opener=forbidden_opener)
            self.assertFalse(called)
            self.assertFalse(path.exists())

    def test_mismatched_bytes_fail_closed(self):
        data = b"synthetic test bytes, not a model"
        manifest = authorized_synthetic_manifest(data)
        manifest["git_blob_sha1"] = "0" * 40
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.pt"
            with self.assertRaises(ValueError):
                download_verified(
                    path, manifest,
                    opener=lambda request, timeout: FakeResponse(data),
                )
            self.assertFalse(path.exists())
            self.assertFalse(path.with_name("best.pt.partial").exists())

    def test_truncated_download_rejected(self):
        data = b"synthetic test bytes, not a model"
        manifest = authorized_synthetic_manifest(data)
        manifest["bytes"] += 8
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.pt"
            with self.assertRaises(ValueError):
                download_verified(
                    path, manifest,
                    opener=lambda request, timeout: FakeResponse(data),
                )
            self.assertFalse(path.exists())
            self.assertFalse(path.with_name("best.pt.partial").exists())

    def test_refuses_overwrite(self):
        data = b"synthetic test bytes, not a model"
        manifest = authorized_synthetic_manifest(data)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "best.pt"
            path.write_bytes(b"existing")
            with self.assertRaises(ValueError):
                download_verified(path, manifest)
            self.assertEqual(path.read_bytes(), b"existing")


if __name__ == "__main__":
    unittest.main()
