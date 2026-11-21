"""Tests that original CC0 image bytes are saved without transformation."""
import csv
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from training.download_original_inaturalist_images import download_originals


class FakeResponse:
    def __init__(self, body, url):
        self.body = body
        self.url = url
        self.headers = {"Content-Type": "image/jpeg"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit=-1):
        return self.body[:limit]

    def geturl(self):
        return self.url


def jpeg_bytes():
    stream = io.BytesIO()
    Image.new("RGB", (1920, 1080), (12, 34, 56)).save(stream, format="JPEG", quality=88)
    return stream.getvalue()


class DownloadOriginalTests(unittest.TestCase):
    def write_csv(self, path, fields, rows):
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_original_bytes_are_saved_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            photo_url = "https://static.inaturalist.org/photos/42/original.jpg"
            source_url = "https://www.inaturalist.org/observations/99"
            body = jpeg_bytes()
            candidate = {
                "photo_id": "42", "observation_id": "99",
                "species_candidate": "Vespa velutina", "license": "CC0-1.0",
                "creator": "Test photographer", "creator_login": "test-photographer",
                "attribution": "Test photographer, no rights reserved (CC0)",
                "license_notice": "no rights reserved",
                "image_url": photo_url, "source_url": source_url,
                "image_quality_status": "PASS",
            }
            verified = {
                "photo_id": "42", "observation_id": "99",
                "species_candidate": "Vespa velutina", "source_url": source_url,
                "api_photo_found": "YES", "license_metadata_match": "YES",
                "api_photo_license": "cc0", "api_taxon": "Vespa velutina",
                "api_quality_grade": "research", "api_observer_name": "Test photographer",
                "api_observer_login": "test-photographer", "api_attribution": "no rights reserved",
                "api_attribution_statement": "Test photographer, no rights reserved (CC0)",
                "error": "",
            }
            input_csv = root / "quality.csv"
            verification_csv = root / "verified.csv"
            output_dir = root / "review" / "images" / "velutina"
            manifest = root / "review" / "manifest.csv"
            self.write_csv(input_csv, list(candidate), [candidate])
            self.write_csv(verification_csv, list(verified), [verified])

            with patch("training.download_original_inaturalist_images.urllib.request.urlopen",
                       return_value=FakeResponse(body, photo_url)):
                rows = download_originals(input_csv, verification_csv, "Vespa velutina",
                                          output_dir, manifest, pause=0)

            self.assertEqual(len(rows), 1)
            filename = output_dir / "42.jpg"
            self.assertEqual(filename.read_bytes(), body)
            self.assertEqual(hashlib.sha256(filename.read_bytes()).hexdigest(), hashlib.sha256(body).hexdigest())
            self.assertEqual(rows[0]["local_image_path"], "images/velutina/42.jpg")
            self.assertEqual(rows[0]["download_status"], "DOWNLOADED_UNMODIFIED")
            self.assertEqual(rows[0]["image_width"], 1920)
            self.assertEqual(rows[0]["image_height"], 1080)
            self.assertEqual(rows[0]["creator"], "Test photographer")
            self.assertEqual(rows[0]["creator_login"], "test-photographer")
            self.assertEqual(rows[0]["attribution"], "Test photographer, no rights reserved (CC0)")
            self.assertEqual(rows[0]["license_notice"], "no rights reserved")

    def test_rejects_candidate_without_exact_cc0_recheck(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            candidate = {
                "photo_id": "42", "observation_id": "99",
                "species_candidate": "Vespa velutina", "license": "CC0-1.0",
                "image_url": "https://static.inaturalist.org/photos/42/original.jpg",
                "source_url": "https://www.inaturalist.org/observations/99",
                "image_quality_status": "PASS",
            }
            verified = {
                "photo_id": "42", "observation_id": "99",
                "source_url": candidate["source_url"], "api_photo_found": "YES",
                "license_metadata_match": "NO", "api_photo_license": "cc-by",
                "api_taxon": "Vespa velutina", "api_quality_grade": "research",
                "api_observer_name": "Test photographer", "api_observer_login": "test-photographer",
                "api_attribution": "no rights reserved",
                "api_attribution_statement": "Test photographer, no rights reserved (CC0)",
                "error": "",
            }
            input_csv, verification_csv = root / "q.csv", root / "v.csv"
            self.write_csv(input_csv, list(candidate), [candidate])
            self.write_csv(verification_csv, list(verified), [verified])
            with self.assertRaisesRegex(ValueError, "No image passed"):
                download_originals(input_csv, verification_csv, "Vespa velutina",
                                   root / "images", root / "manifest.csv", pause=0)

    def test_rejects_non_original_redirect_without_writing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            photo_url = "https://static.inaturalist.org/photos/42/original.jpg"
            candidate = {
                "photo_id": "42", "observation_id": "99",
                "species_candidate": "Vespa velutina", "license": "CC0-1.0",
                "image_url": photo_url,
                "source_url": "https://www.inaturalist.org/observations/99",
                "image_quality_status": "PASS",
            }
            verified = {
                "photo_id": "42", "observation_id": "99",
                "source_url": candidate["source_url"], "api_photo_found": "YES",
                "license_metadata_match": "YES", "api_photo_license": "cc0",
                "api_taxon": "Vespa velutina", "api_quality_grade": "research", "error": "",
            }
            input_csv, verification_csv = root / "q.csv", root / "v.csv"
            self.write_csv(input_csv, list(candidate), [candidate])
            self.write_csv(verification_csv, list(verified), [verified])
            redirect = "https://static.inaturalist.org/photos/42/square.jpg"
            with patch("training.download_original_inaturalist_images.urllib.request.urlopen",
                       return_value=FakeResponse(jpeg_bytes(), redirect)):
                with self.assertRaisesRegex(RuntimeError, "No original files"):
                    download_originals(input_csv, verification_csv, "Vespa velutina",
                                       root / "images", root / "manifest.csv", pause=0)
            self.assertEqual(list((root / "images").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
