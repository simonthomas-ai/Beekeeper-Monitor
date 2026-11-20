import unittest
from training.discover_sketchfab_insects import discover, normalize, TERMS


class SketchfabDiscoveryTests(unittest.TestCase):
    def test_cc0_is_review_only(self):
        item = {"uid": "abcdef1234567890", "name": "Vespa", "license": {"slug": "cc0"},
                "isDownloadable": True, "user": {"username": "creator"}}
        row = normalize(item, TERMS[0])
        self.assertEqual(row["training_approved"], "NO")
        self.assertEqual(row["species_verified"], "NO")
        self.assertEqual(row["rights_verified"], "NO")

    def test_noncommercial_and_missing_license_rejected(self):
        base = {"uid": "abcdef1234567890", "isDownloadable": True}
        for slug in ("cc-by-nc", "cc-by-nd", "", "proprietary"):
            self.assertIsNone(normalize(dict(base, license={"slug": slug}), TERMS[0]))

    def test_not_downloadable_rejected(self):
        self.assertIsNone(normalize({"uid": "abcdef1234567890",
                                   "license": {"slug": "cc0"}, "isDownloadable": False}, TERMS[0]))

    def test_deduplicates_and_limits_queries(self):
        item = {"uid": "abcdef1234567890", "license": {"slug": "cc-by"},
                "isDownloadable": True}
        calls = []
        def fetch(url):
            calls.append(url)
            return {"results": [item, item]}
        rows, errors = discover(fetch)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(calls), len(TERMS))
        self.assertEqual(errors, [])

    def test_upstream_failure_is_not_zero_candidates_claim(self):
        rows, errors = discover(lambda url: (_ for _ in ()).throw(OSError("offline")))
        self.assertEqual(rows, [])
        self.assertEqual(len(errors), len(TERMS))


if __name__ == "__main__":
    unittest.main()
