"""Offline tests for verified iNaturalist observer attribution."""
import json
import unittest
from unittest.mock import patch

from training.verify_inaturalist_photo_metadata import verify


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit=-1):
        return self.payload if limit is None or limit < 0 else self.payload[:limit]


def observation(login="test-observer", name="Test Observer"):
    return {
        "results": [{
            "id": 99,
            "quality_grade": "research",
            "taxon": {"name": "Vespa velutina"},
            "user": {"login": login, "name": name},
            "photos": [{
                "id": 42,
                "url": "https://static.inaturalist.org/photos/42/square.jpg",
                "license_code": "cc0",
                "attribution": "no rights reserved",
            }],
        }]
    }


class ObserverAttributionTests(unittest.TestCase):
    def setUp(self):
        self.row = {
            "observation_id": "99",
            "photo_id": "42",
            "species_candidate": "Vespa velutina",
            "license": "CC0-1.0",
            "source_url": "https://www.inaturalist.org/observations/99",
            "creator": "Test Observer",
            "creator_login": "test-observer",
            "license_notice": "no rights reserved",
        }

    def test_verifies_observer_identity_separately_from_cc0_notice(self):
        response = FakeResponse(observation())
        with patch("training.verify_inaturalist_photo_metadata.urllib.request.urlopen",
                   return_value=response):
            result = verify(self.row)
        self.assertEqual(result["api_photo_found"], "YES")
        self.assertEqual(result["api_observer_name"], "Test Observer")
        self.assertEqual(result["api_observer_login"], "test-observer")
        self.assertEqual(result["api_attribution"], "no rights reserved")
        self.assertEqual(
            result["api_attribution_statement"],
            "Test Observer, no rights reserved (CC0)",
        )
        self.assertEqual(result["license_metadata_match"], "YES")
        self.assertEqual(result["api_photo_url"],
                         "https://static.inaturalist.org/photos/42/original.jpg")
        self.assertEqual(result["error"], "")

    def test_rejects_observer_login_changed_since_discovery(self):
        response = FakeResponse(observation(login="different-user"))
        with patch("training.verify_inaturalist_photo_metadata.urllib.request.urlopen",
                   return_value=response):
            result = verify(self.row)
        self.assertEqual(result["api_observer_login"], "different-user")
        self.assertIn("differs from discovery metadata", result["error"])
        self.assertEqual(result["license_metadata_match"], "NO")


if __name__ == "__main__":
    unittest.main()
