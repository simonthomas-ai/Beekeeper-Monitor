"""Offline regression tests for paginated CC0 candidate discovery."""
import unittest
from unittest.mock import patch
from training.discover_cc0_candidates import discover, SPECIES

def obs(oid, pid, species, license_code="cc0"):
    return {"id": oid, "quality_grade": "research", "taxon": {"name": species},
            "user": {"login": "test-observer", "name": "Test Observer"},
            "photos": [{"id": pid, "url": f"https://static.inaturalist.org/photos/{pid}/square.jpg",
                        "license_code": license_code,
                        "attribution": "no rights reserved" if license_code == "cc0" else "some rights reserved"}]}

class PaginationTests(unittest.TestCase):
    def test_multiple_pages_and_only_cc0(self):
        calls = []
        def api(url):
            calls.append(url)
            if "taxa/autocomplete" in url:
                species = next(s for s in SPECIES if s.replace(" ", "+") in url)
                return {"results": [{"name": species, "id": SPECIES.index(species)+1}]}
            if "taxon_id=1" in url and "page=1" in url:
                return {"results": [obs(i, i, SPECIES[0], "cc-by") for i in range(200)]}
            if "taxon_id=1" in url and "page=2" in url:
                return {"results": [obs(1000, 1000, SPECIES[0])]}
            return {"results": []}
        with patch("training.discover_cc0_candidates.get_json", side_effect=api), patch("training.discover_cc0_candidates.time.sleep"):
            rows = discover(50, 2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["species_candidate"], SPECIES[0])
        self.assertEqual(rows[0]["review_status"], "UNREVIEWED")
        self.assertEqual(rows[0]["image_url"], f"https://static.inaturalist.org/photos/1000/original.jpg")
        self.assertEqual(rows[0]["dataset_group"], "asian_hornet")
        self.assertEqual(rows[0]["creator"], "Test Observer")
        self.assertEqual(rows[0]["creator_login"], "test-observer")
        self.assertEqual(rows[0]["license_notice"], "no rights reserved")
        self.assertEqual(rows[0]["attribution"], "Test Observer, no rights reserved (CC0)")
        self.assertTrue(any("taxon_id=1" in x and "page=2" in x for x in calls))

if __name__ == "__main__":
    unittest.main()
