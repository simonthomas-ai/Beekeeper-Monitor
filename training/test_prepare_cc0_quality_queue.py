import copy
import unittest

from training.prepare_cc0_quality_queue import select_cc0_candidates


BASE = {
    "source_id": "inaturalist-photo-42",
    "source_url": "https://www.inaturalist.org/observations/99",
    "image_url": "https://static.inaturalist.org/photos/42/original.jpg",
    "creator": "Test Observer",
    "creator_login": "test-observer",
    "license": "CC0-1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    "license_notice": "no rights reserved",
    "attribution": "Test Observer, no rights reserved (CC0)",
    "observation_id": "99",
    "photo_id": "42",
    "species_candidate": "Vespa velutina",
    "dataset_group": "asian_hornet",
    "review_status": "UNREVIEWED",
}


class CC0QualityQueueTests(unittest.TestCase):
    def test_only_exact_cc0_rows_are_selected(self):
        unverified_by = dict(BASE, source_id="inat:43", photo_id="43",
                             image_url="https://static.inaturalist.org/photos/43/original.jpg",
                             observation_id="100", license="CC-BY-VERSION-UNVERIFIED",
                             license_url="")
        result = select_cc0_candidates([BASE, unverified_by])
        self.assertEqual(result, [BASE])

    def test_rejects_cc0_row_with_wrong_license_url(self):
        row = dict(BASE, license_url="https://creativecommons.org/licenses/by/4.0/")
        with self.assertRaisesRegex(ValueError, "incorrect CC0 license URL"):
            select_cc0_candidates([row])

    def test_rejects_missing_creator_identity(self):
        row = dict(BASE, creator="no rights reserved")
        with self.assertRaisesRegex(ValueError, "creator identity is missing"):
            select_cc0_candidates([row])

    def test_rejects_missing_observer_login(self):
        row = dict(BASE, creator_login="")
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            select_cc0_candidates([row])

    def test_rejects_forged_attribution(self):
        row = dict(BASE, attribution="Different person, no rights reserved (CC0)")
        with self.assertRaisesRegex(ValueError, "attribution does not match"):
            select_cc0_candidates([row])

    def test_rejects_missing_or_non_original_photo_variant(self):
        row = dict(BASE, image_url="https://static.inaturalist.org/photos/42/square.jpg")
        with self.assertRaisesRegex(ValueError, "not the exact photo-bound original"):
            select_cc0_candidates([row])

    def test_rejects_wrong_observation_source_binding(self):
        row = dict(BASE, source_url="https://www.inaturalist.org/observations/100")
        with self.assertRaisesRegex(ValueError, "source URL does not bind"):
            select_cc0_candidates([row])

    def test_rejects_wrong_species_group(self):
        row = dict(BASE, dataset_group="honey_bee")
        with self.assertRaisesRegex(ValueError, "species and dataset group"):
            select_cc0_candidates([row])

    def test_rejects_non_unreviewed_or_approved_record(self):
        row = dict(BASE, review_status="APPROVED")
        with self.assertRaisesRegex(ValueError, "remain UNREVIEWED"):
            select_cc0_candidates([row])

    def test_rejects_duplicate_photo_or_observation_ids(self):
        duplicate = copy.deepcopy(BASE)
        duplicate["source_id"] = "inaturalist-photo-42-copy"
        with self.assertRaisesRegex(ValueError, "duplicate photo or observation"):
            select_cc0_candidates([BASE, duplicate])

    def test_non_cc0_records_are_excluded_without_becoming_approved(self):
        by = dict(BASE, license="CC-BY-VERSION-UNVERIFIED", license_url="",
                  creator="CC-BY author", attribution="CC-BY author")
        self.assertEqual(select_cc0_candidates([by]), [])


if __name__ == "__main__":
    unittest.main()
