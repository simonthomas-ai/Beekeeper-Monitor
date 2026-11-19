import copy
import unittest
from training.stage_mobile_reviews import stage

SAMPLE = {
    "format": "vespaguard-unverified-mobile-review-v1",
    "species": "Vespa velutina",
    "records": [{
        "photo_id": "101", "observation_id": "202",
        "species_candidate": "Vespa velutina",
        "source_url": "https://www.inaturalist.org/observations/202",
        "image_url": "https://static.inaturalist.org/photos/101/medium.jpg",
        "license": "CC0-1.0", "creator": "observer",
        "training_eligible": False,
        "review": {"decision": "LIKELY", "boxes": [{"x": 0.5, "y": 0.5, "width": 0.2, "height": 0.3}]}
    }]
}

class MobileStageTests(unittest.TestCase):
    def test_likely_stays_unapproved(self):
        result = stage(copy.deepcopy(SAMPLE))
        self.assertFalse(result["training_eligible"])
        self.assertFalse(result["records"][0]["training_eligible"])
        self.assertEqual(result["records"][0]["mobile_decision"], "LIKELY")
        self.assertIn("verify_license_and_attribution", result["records"][0]["expert_checks_required"])

    def test_forged_training_approval_rejected(self):
        data = copy.deepcopy(SAMPLE)
        data["records"][0]["training_eligible"] = True
        with self.assertRaises(ValueError):
            stage(data)

    def test_out_of_bounds_box_rejected(self):
        data = copy.deepcopy(SAMPLE)
        data["records"][0]["review"]["boxes"][0]["x"] = 0.99
        with self.assertRaises(ValueError):
            stage(data)

    def test_duplicate_id_rejected(self):
        data = copy.deepcopy(SAMPLE)
        data["records"].append(copy.deepcopy(data["records"][0]))
        with self.assertRaises(ValueError):
            stage(data)

    def test_unknown_species_rejected(self):
        data = copy.deepcopy(SAMPLE)
        data["species"] = "Unverified species"
        with self.assertRaises(ValueError):
            stage(data)

    def test_pending_is_not_approved(self):
        data = copy.deepcopy(SAMPLE)
        data["records"][0]["review"] = {"decision": "PENDING", "boxes": []}
        self.assertFalse(stage(data)["records"][0]["training_eligible"])

if __name__ == "__main__":
    unittest.main()
