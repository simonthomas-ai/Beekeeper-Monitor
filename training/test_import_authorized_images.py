#!/usr/bin/env python3
"""Offline safety tests for authorized image importer. No network or training data."""
import csv
from email.message import Message
import hashlib
import importlib.util
import io
import pathlib
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

MODULE = pathlib.Path(__file__).with_name("import_authorized_images.py")
spec = importlib.util.spec_from_file_location("authorized_import", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ImportSafetyTests(unittest.TestCase):
    def test_approved_license_allowlist(self):
        self.assertEqual(mod.ALLOWED, {"CC0-1.0", "CC-BY-4.0"})
        self.assertNotIn("CC-BY-VERSION-UNVERIFIED", mod.ALLOWED)

    def test_audit_import_and_annotation_license_allowlists_are_identical(self):
        audit_path = pathlib.Path(__file__).with_name("audit_image_licenses.py")
        audit_spec = importlib.util.spec_from_file_location("image_license_audit", audit_path)
        audit = importlib.util.module_from_spec(audit_spec)
        audit_spec.loader.exec_module(audit)
        self.assertEqual(audit.ALLOWED, mod.ALLOWED)
        self.assertEqual(audit.ALLOWED, {"CC0-1.0", "CC-BY-4.0"})

    def test_canonical_license_references(self):
        self.assertEqual(mod.LICENSE_URLS["CC0-1.0"], "https://creativecommons.org/publicdomain/zero/1.0/")
        self.assertEqual(mod.LICENSE_URLS["CC-BY-4.0"], "https://creativecommons.org/licenses/by/4.0/")

    def test_provenance_manifest_retains_source_and_sanitized_hashes(self):
        for field in ("source_id", "source_url", "image_url", "requested_image_url",
                      "creator", "license", "license_url", "attribution", "source_sha256",
                      "sha256", "image_format", "width", "height", "exif_removed"):
            self.assertIn(field, mod.OUTPUT)

    def test_reject_non_https(self):
        for url in ("http://example.org/a.jpg", "file:///etc/passwd",
                    "https://user:pass@example.org/a.jpg", "https://localhost/a.jpg",
                    "https://example.org/a.jpg#fragment"):
            with self.assertRaises(ValueError):
                mod.public_https(url)

    def test_reject_private_resolved_addresses(self):
        for address in ("127.0.0.1", "10.1.2.3", "192.168.1.2", "::1", "169.254.169.254"):
            with self.subTest(address=address):
                with patch.object(mod.socket, "getaddrinfo", return_value=[
                    (None, None, None, None, (address, 443))
                ]):
                    with self.assertRaises(ValueError):
                        mod.public_https("https://example.org/a.jpg")

    def test_accept_public_resolved_address(self):
        with patch.object(mod.socket, "getaddrinfo", return_value=[
            (None, None, None, None, ("8.8.8.8", 443))
        ]):
            self.assertEqual(mod.public_https("https://example.org/a.jpg"), "https://example.org/a.jpg")

    def test_inaturalist_thumbnail_is_upgraded_before_authorized_download(self):
        row = {"source_id":"inat:photo:763034625",
               "source_url":"https://www.inaturalist.org/observations/414481366",
               "image_url":"https://inaturalist-open-data.s3.amazonaws.com/photos/763034625/square.jpg",
               "creator":"Creator","license":"CC0-1.0",
               "license_url":mod.LICENSE_URLS["CC0-1.0"],"attribution":"Creator"}
        with patch.object(mod, "public_https", side_effect=lambda url: url):
            prepared = mod.validate_rows([row])[0]
        self.assertEqual(prepared["requested_image_url"], row["image_url"])
        self.assertEqual(prepared["image_url"],
                         "https://inaturalist-open-data.s3.amazonaws.com/photos/763034625/original.jpg")

    def test_redirects_rejected(self):
        with self.assertRaises(ValueError):
            mod.NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://example.org/a.jpg")

    def _jpeg_with_exif(self):
        image = Image.new("RGB", (16, 12), (90, 120, 150))
        exif = Image.Exif()
        exif[0x010E] = "PRIVATE CAMERA METADATA"
        output = io.BytesIO()
        image.save(output, format="JPEG", exif=exif)
        return output.getvalue()

    def test_sanitizer_removes_exif_and_reencodes_valid_image(self):
        original = self._jpeg_with_exif()
        sanitized, suffix, image_format, width, height = mod.sanitize_image(original, "image/jpeg")
        self.assertEqual((suffix, image_format), (".jpg", "JPEG"))
        self.assertNotEqual(hashlib.sha256(original).digest(), hashlib.sha256(sanitized).digest())
        with Image.open(io.BytesIO(sanitized)) as result:
            result.load()
            self.assertEqual(result.size, (16, 12))
            self.assertEqual((width, height), (16, 12))
            self.assertEqual(dict(result.getexif()), {})

    def test_sanitizer_rejects_mime_mismatch_and_corrupt_image(self):
        original = self._jpeg_with_exif()
        with self.assertRaises(ValueError): mod.sanitize_image(original, "image/png")
        with self.assertRaises(ValueError): mod.sanitize_image(b"not an image", "image/jpeg")

    def test_sanitizer_enforces_pixel_limit(self):
        original = io.BytesIO()
        Image.new("RGB", (20, 20)).save(original, format="PNG")
        with patch.object(mod, "MAX_IMAGE_PIXELS", 100):
            with self.assertRaises(ValueError): mod.sanitize_image(original.getvalue(), "image/png")

    def test_preflight_rejects_duplicate_sources_and_noncommercial_rights(self):
        good = {"source_id":"image-1","source_url":"https://source.example/item/1",
                "image_url":"https://image.example/1.jpg","creator":"Creator",
                "license":"CC0-1.0","license_url":mod.LICENSE_URLS["CC0-1.0"],
                "attribution":"Creator / source"}
        with patch.object(mod, "public_https", side_effect=lambda url: url):
            self.assertEqual(len(mod.validate_rows([good])), 1)
            with self.assertRaises(ValueError): mod.validate_rows([good, good])
            with self.assertRaises(ValueError): mod.validate_rows([dict(good, license="CC-BY-NC-4.0")])

    def test_authorized_import_downloads_original_and_records_pixels(self):
        source = self._jpeg_with_exif()
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            queue = root / "queue.csv"
            row = {
                "source_id": "inat:photo:763034625",
                "source_url": "https://www.inaturalist.org/observations/414481366",
                "image_url": "https://inaturalist-open-data.s3.amazonaws.com/photos/763034625/square.jpg",
                "creator": "Creator",
                "license": "CC0-1.0",
                "license_url": mod.LICENSE_URLS["CC0-1.0"],
                "attribution": "Creator",
            }
            with queue.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=mod.FIELDS)
                writer.writeheader()
                writer.writerow(row)

            class FakeResponse:
                def __init__(self):
                    self.headers = Message()
                    self.headers["Content-Type"] = "image/jpeg"
                def __enter__(self): return self
                def __exit__(self, *args): return False
                def read(self, _limit): return source

            class FakeOpener:
                def __init__(self): self.requested_urls = []
                def open(self, request, **_kwargs):
                    self.requested_urls.append(request.full_url)
                    return FakeResponse()

            fake_opener = FakeOpener()
            dataset = root / "dataset"
            with patch.object(mod, "public_https", side_effect=lambda url: url), \
                 patch.object(mod.urllib.request, "build_opener", return_value=fake_opener):
                result = mod.import_candidates(queue, dataset)

            expected_url = "https://inaturalist-open-data.s3.amazonaws.com/photos/763034625/original.jpg"
            self.assertEqual(fake_opener.requested_urls, [expected_url])
            self.assertEqual(result["downloaded"], 1)
            self.assertEqual(result["training_approved"], 0)
            with (dataset / "licenses.csv").open(newline="", encoding="utf-8") as stream:
                manifest = next(csv.DictReader(stream))
            self.assertEqual(manifest["requested_image_url"], row["image_url"])
            self.assertEqual(manifest["image_url"], expected_url)
            self.assertEqual((manifest["width"], manifest["height"]), ("16", "12"))
            self.assertEqual(manifest["exif_removed"], "true")

    def test_existing_manifest_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            queue = root / "queue.csv"
            with queue.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=mod.FIELDS)
                writer.writeheader()
                writer.writerow({
                    "source_id": "photo-1",
                    "source_url": "https://source.example/photo-1",
                    "image_url": "https://image.example/photo-1.jpg",
                    "creator": "Creator",
                    "license": "CC0-1.0",
                    "license_url": mod.LICENSE_URLS["CC0-1.0"],
                    "attribution": "Creator / source",
                })
            dataset = root / "dataset"
            dataset.mkdir()
            manifest = dataset / "licenses.csv"
            manifest.write_text("do-not-overwrite\n", encoding="utf-8")
            with patch.object(mod, "public_https", side_effect=lambda url: url):
                with self.assertRaises(FileExistsError):
                    mod.import_candidates(queue, dataset)
            self.assertEqual(manifest.read_text(encoding="utf-8"), "do-not-overwrite\n")

    def test_existing_candidate_file_is_not_deleted(self):
        source = self._jpeg_with_exif()
        sanitized, suffix, _, _, _ = mod.sanitize_image(source, "image/jpeg")
        digest = hashlib.sha256(sanitized).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            queue = root / "queue.csv"
            with queue.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=mod.FIELDS)
                writer.writeheader()
                writer.writerow({
                    "source_id": "photo-1",
                    "source_url": "https://source.example/photo-1",
                    "image_url": "https://image.example/photo-1.jpg",
                    "creator": "Creator",
                    "license": "CC0-1.0",
                    "license_url": mod.LICENSE_URLS["CC0-1.0"],
                    "attribution": "Creator / source",
                })
            existing_dir = root / "dataset" / "unreviewed"
            existing_dir.mkdir(parents=True)
            existing = existing_dir / (digest + suffix)
            existing.write_bytes(b"pre-existing protected content")

            class FakeResponse:
                def __init__(self):
                    self.headers = Message()
                    self.headers["Content-Type"] = "image/jpeg"
                def __enter__(self): return self
                def __exit__(self, *args): return False
                def read(self, _limit): return source

            class FakeOpener:
                def open(self, *_args, **_kwargs): return FakeResponse()

            with patch.object(mod, "public_https", side_effect=lambda url: url), \
                 patch.object(mod.urllib.request, "build_opener", return_value=FakeOpener()):
                with self.assertRaises(FileExistsError):
                    mod.import_candidates(queue, root / "dataset")
            self.assertEqual(existing.read_bytes(), b"pre-existing protected content")


if __name__ == "__main__":
    unittest.main()
