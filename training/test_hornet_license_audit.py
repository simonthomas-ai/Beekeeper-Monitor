"""Regression tests: source metadata alone must never approve training images."""
import io
import json
import unittest
from unittest.mock import patch
from verify_inaturalist_photo_metadata import verify
from prepare_hornet_visual_review import original_url


class _Response:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return io.BytesIO(json.dumps(self.data).encode("utf-8"))

    def __exit__(self, *args):
        return False


class HornetLicenseAuditTests(unittest.TestCase):
    def setUp(self):
        self.row = {
            "observation_id": "123", "photo_id": "456",
            "species_candidate": "Vespa velutina", "license": "CC0-1.0",
            "source_url": "https://www.inaturalist.org/observations/123",
        }
        self.payload = {"results": [{
            "taxon": {"name": "Vespa velutina"}, "quality_grade": "research",
            "photos": [{"id": 456, "license_code": "cc0",
                        "attribution": "Author", "url": "https://static.inaturalist.org/photos/456/square.jpg"}],
        }]}

    def test_matching_cc0_is_only_metadata_not_approval(self):
        with patch("verify_inaturalist_photo_metadata.urllib.request.urlopen",
                   return_value=_Response(self.payload)):
            result = verify(self.row)
        self.assertEqual(result["license_metadata_match"], "YES")
        self.assertEqual(result["api_photo_url"], "https://static.inaturalist.org/photos/456/original.jpg")
        self.assertEqual(result["review_status"], "UNREVIEWED")
        self.assertNotIn("training_approved", result)

    def test_changed_license_fails_closed(self):
        self.payload["results"][0]["photos"][0]["license_code"] = "cc-by"
        with patch("verify_inaturalist_photo_metadata.urllib.request.urlopen",
                   return_value=_Response(self.payload)):
            result = verify(self.row)
        self.assertEqual(result["license_metadata_match"], "NO")
        self.assertEqual(result["review_status"], "UNREVIEWED")

    def test_missing_photo_fails_closed(self):
        self.payload["results"][0]["photos"][0]["id"] = 999
        with patch("verify_inaturalist_photo_metadata.urllib.request.urlopen",
                   return_value=_Response(self.payload)):
            result = verify(self.row)
        self.assertEqual(result["api_photo_found"], "NO")
        self.assertTrue(result["error"])

    def test_invalid_ids_make_no_network_request(self):
        with patch("verify_inaturalist_photo_metadata.urllib.request.urlopen") as call:
            result = verify({**self.row, "observation_id": "123/../../"})
        call.assert_not_called()
        self.assertEqual(result["license_metadata_match"], "NO")

    def test_original_url_rejects_external_hosts(self):
        self.assertEqual(original_url("https://evil.example/photos/456/square.jpg"), "")
        self.assertEqual(original_url("https://static.inaturalist.org.evil.example/photos/456/square.jpg"), "")
        self.assertEqual(original_url("http://static.inaturalist.org/photos/456/square.jpg"), "")
        self.assertEqual(original_url("https://static.inaturalist.org/photos/456/square.jpg"),
                         "https://static.inaturalist.org/photos/456/original.jpg")


if __name__ == "__main__":
    unittest.main()
