"""Regression tests: unknown CC BY version must never become approved 4.0."""
import unittest
from discover_inaturalist_candidates import LICENSES

class LicenseMappingTest(unittest.TestCase):
    def test_cc_by_version_is_unverified(self):
        license_id, license_url = LICENSES["cc-by"]
        self.assertEqual(license_id, "CC-BY-VERSION-UNVERIFIED")
        self.assertEqual(license_url, "")
        self.assertNotEqual(license_id, "CC-BY-4.0")

    def test_cc0_is_explicit(self):
        self.assertEqual(LICENSES["cc0"][0], "CC0-1.0")

if __name__ == "__main__":
    unittest.main()
