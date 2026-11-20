"""Offline unit tests: Commons importer must fail closed for licensing and image types."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import io
import json
import sys
import tempfile
from urllib.error import HTTPError

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/import_commons_candidates.py"
spec = importlib.util.spec_from_file_location("commons_import", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ImporterTests(unittest.TestCase):
    def test_class_configuration(self):
        self.assertEqual(set(module.CATEGORIES), set(module.FALLBACK_CATEGORIES))
        self.assertTrue({"velutina", "crabro", "apis", "bombus", "vespula"} <= set(module.CATEGORIES))

    def test_pagination_and_duplicate_url(self):
        candidate = lambda title: {"title": title, "imageinfo": [{"url": "https://upload.wikimedia.org/shared.jpg", "mime": "image/jpeg", "extmetadata": {"LicenseShortName": {"value": "CC0"}}}]}
        first = {"query": {"pages": {"1": candidate("File:First.jpg")}}, "continue": {"continue": "-||", "gcmcontinue": "next"}}
        second = {"query": {"pages": {"2": candidate("File:Duplicate.jpg")}}}
        with tempfile.TemporaryDirectory() as tmp, patch.object(module, "get_json", side_effect=[first, second]) as api, patch.object(sys, "argv", ["import", "--class-name", "apis", "--max-pages", "2", "--output", tmp]):
            module.main()
            data = json.loads((Path(tmp) / "apis" / "manifest.json").read_text())
        self.assertEqual(api.call_count, 2)
        self.assertEqual(len(data["items"]), 1)
        self.assertFalse(data["items"][0]["human_approved_for_training"])

    def test_rate_limit_retry(self):
        err = HTTPError("https://commons.wikimedia.org/w/api.php", 429, "Too Many Requests", {"Retry-After": "1"}, None)
        response = io.BytesIO(b'{"query":{"pages":{}}}')
        with patch.object(module, "urlopen", side_effect=[err, response]) as mocked, patch.object(module.time, "sleep") as pause:
            data = module.get_json({"action": "query"})
        self.assertIn("query", data)
        self.assertEqual(mocked.call_count, 2)
        pause.assert_called_once()

    def test_licenses(self):
        for license_name in ["CC0", "CC BY 4.0", "CC BY 3.0", "CC BY 2.0", "Public Domain"]:
            self.assertTrue(module.allowed(license_name), license_name)
        for license_name in ["", "CC BY-NC 4.0", "CC BY-SA 4.0", "All Rights Reserved", "CC BY-ND 4.0"]:
            self.assertFalse(module.allowed(license_name), license_name)

    def test_fallback_on_empty_category(self):
        empty = {"query": {"pages": {}}}
        candidate = {"query": {"pages": {"1": {"title": "File:Hornet.jpg",
            "imageinfo": [{"url": "https://upload.wikimedia.org/hornet.jpg",
            "mime": "image/jpeg", "extmetadata": {"LicenseShortName": {"value": "CC0"}}}]}}}}
        with tempfile.TemporaryDirectory() as tmp, patch.object(module, "get_json", side_effect=[empty, candidate]) as api, patch.object(sys, "argv", ["import", "--class-name", "velutina", "--output", tmp]):
            module.main()
            data = json.loads((Path(tmp) / "velutina" / "manifest.json").read_text())
        self.assertEqual(api.call_count, 2)
        self.assertEqual(len(data["items"]), 1)
        self.assertFalse(data["items"][0]["species_verified"])

    def test_metadata_only_no_download(self):
        response = {"query": {"pages": {
            "1": {"title": "File:Velutina.jpg", "imageinfo": [{"url": "https://upload.wikimedia.org/a.jpg", "mime": "image/jpeg", "extmetadata": {"LicenseShortName": {"value": "CC BY 4.0"}, "Artist": {"value": "Author"}}}]},
            "2": {"title": "File:Restricted.jpg", "imageinfo": [{"url": "https://upload.wikimedia.org/b.jpg", "mime": "image/jpeg", "extmetadata": {"LicenseShortName": {"value": "CC BY-NC 4.0"}}}]},
            "3": {"title": "File:Svg.svg", "imageinfo": [{"url": "https://upload.wikimedia.org/c.svg", "mime": "image/svg+xml", "extmetadata": {"LicenseShortName": {"value": "CC0"}}}]}
        }}}
        with tempfile.TemporaryDirectory() as tmp, patch.object(module, "get_json", return_value=response) as api, patch.object(sys, "argv", ["import", "--class-name", "velutina", "--output", tmp]):
            module.main()
            data = json.loads((Path(tmp) / "velutina" / "manifest.json").read_text())
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["license"], "CC BY 4.0")
        self.assertFalse(data["items"][0]["human_approved_for_training"])
        self.assertFalse(data["items"][0]["species_verified"])
        self.assertIsNone(data["items"][0]["local_file"])
        self.assertFalse(data["downloaded"])
        self.assertEqual(api.call_count, 1)

if __name__ == "__main__":
    unittest.main()
