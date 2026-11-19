import unittest
from discover_cc0_3d_models import candidates

class CC0ModelDiscoveryTests(unittest.TestCase):
    def test_no_beet_or_beef_false_positives(self):
        rows = [{"row": {"title": title, "license": "CC0-1.0", "media_usage_access": "CC0"}} for title in ("De la Fuente sugar beet knife", "Bully beef can opener")]
        self.assertEqual(candidates(rows), [])

    def test_only_cc0_and_no_approvals(self):
        rows = [
            {"row": {"package_id": "1", "title": "Vespa crabro", "license": "CC0-1.0", "media_usage_access": "CC0", "mesh_url": "https://example.org/model.glb"}},
            {"row": {"package_id": "2", "title": "Vespa velutina", "license": "CC-BY-NC", "media_usage_access": "Restricted"}},
            {"row": {"package_id": "3", "title": "Chair", "license": "CC0-1.0", "media_usage_access": "CC0"}},
        ]
        result = candidates(rows)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["package_id"], "1")
        self.assertEqual(result[0]["training_approved"], "NO")
        self.assertEqual(result[0]["species_verified"], "NO")
        self.assertEqual(result[0]["geometry_verified"], "NO")

if __name__ == "__main__":
    unittest.main()
