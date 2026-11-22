import unittest
from training.discover_gbif_media_candidates import (
    BASE, normalize_license, media_candidate, match_species, discover
)


class GBIFMediaCandidateTests(unittest.TestCase):
    def test_only_exact_cc0_and_cc_by_4_are_accepted(self):
        self.assertEqual(normalize_license("http://creativecommons.org/publicdomain/zero/1.0/")[0], "CC0-1.0")
        self.assertEqual(normalize_license("https://creativecommons.org/licenses/by/4.0/")[0], "CC-BY-4.0")
        for denied in ("CC-BY-NC-4.0", "CC BY 3.0", "", None, "all rights reserved"):
            self.assertIsNone(normalize_license(denied))

    def test_media_license_is_checked_independently_from_occurrence_license(self):
        occurrence = {"key": 42, "speciesKey": 123, "species": "Vespa velutina",
                      "license": "CC0_1_0", "datasetKey": "dataset-1"}
        denied = {"type":"StillImage", "identifier":"https://images.example/1.jpg",
                  "license":"CC BY-NC 4.0", "creator":"Photographer"}
        self.assertIsNone(media_candidate(denied, occurrence, "Vespa velutina", expected_species_key=123))
        accepted = {"type":"StillImage", "identifier":"https://images.example/2.jpg",
                    "license":"https://creativecommons.org/licenses/by/4.0/",
                    "creator":"Photographer", "format":"image/jpeg"}
        row = media_candidate(accepted, occurrence, "Vespa velutina", expected_species_key=123)
        self.assertEqual(row["media_license"], "CC-BY-4.0")
        self.assertEqual(row["occurrence_license"], "CC0-1.0")
        self.assertEqual(row["species_key"], 123)
        self.assertEqual(row["review_status"], "UNREVIEWED_MEDIA_RIGHTS_AND_IMAGE")

    def test_rejects_unknown_or_noncommercial_occurrence_license_even_when_media_is_cc0(self):
        media = {"type":"StillImage", "identifier":"https://images.example/10.jpg", "license":"CC0-1.0"}
        for license_value in ("CC-BY-NC-4.0", "", None, "all rights reserved"):
            occurrence = {"key": 10, "speciesKey": 123, "species": "Vespa velutina",
                          "license": license_value}
            with self.subTest(license=license_value):
                self.assertIsNone(media_candidate(media, occurrence, "Vespa velutina", expected_species_key=123))

    def test_cc_by_occurrence_requires_rights_holder_attribution(self):
        occurrence = {"key": 11, "speciesKey": 123, "species": "Vespa velutina",
                      "license":"CC BY 4.0"}
        media = {"type":"StillImage", "identifier":"https://images.example/11.jpg", "license":"CC0-1.0"}
        self.assertIsNone(media_candidate(media, occurrence, "Vespa velutina", expected_species_key=123))
        occurrence["rightsHolder"] = "Dataset rights holder"
        self.assertEqual(media_candidate(media, occurrence, "Vespa velutina", expected_species_key=123)["occurrence_license"], "CC-BY-4.0")

    def test_cc_by_requires_attribution_identity(self):
        media = {"type":"StillImage", "identifier":"https://images.example/3.jpg",
                 "license":"CC BY 4.0"}
        occurrence = {"key": 4, "speciesKey": 456, "species": "Apis mellifera", "license": "CC0_1_0"}
        self.assertIsNone(media_candidate(media, occurrence, "Apis mellifera", expected_species_key=456))

    def test_exact_species_match_required(self):
        def fetch(url):
            return {"matchType":"FUZZY", "rank":"SPECIES", "canonicalName":"Vespa velutina", "usageKey":123}
        self.assertIsNone(match_species("Vespa velutina", fetch=fetch))

    def test_rejects_descendant_taxon_even_when_media_license_is_allowed(self):
        occurrence = {
            "key": 77, "speciesKey": 456, "species": "Vespula germanica",
            "license": "CC0_1_0", "datasetKey": "dataset-1",
        }
        media = {
            "type": "StillImage",
            "identifier": "https://images.example/subspecies.jpg",
            "license": "CC0_1_0",
        }
        self.assertIsNone(
            media_candidate(media, occurrence, "Vespa velutina", expected_species_key=123)
        )

    def test_rejects_missing_interpreted_species_key(self):
        occurrence = {"key": 78, "species": "Vespa velutina", "license": "CC0_1_0"}
        media = {
            "type": "StillImage", "identifier": "https://images.example/no-key.jpg",
            "license": "CC0_1_0",
        }
        self.assertIsNone(
            media_candidate(media, occurrence, "Vespa velutina", expected_species_key=123)
        )

    def test_rejects_species_name_key_conflict(self):
        occurrence = {"key": 79, "speciesKey": 123, "species": "Vespula germanica",
                      "license": "CC0_1_0"}
        media = {
            "type": "StillImage", "identifier": "https://images.example/conflict.jpg",
            "license": "CC0_1_0",
        }
        self.assertIsNone(
            media_candidate(media, occurrence, "Vespa velutina", expected_species_key=123)
        )

    def test_discovery_reports_only_candidate_metadata(self):
        def fetch(url):
            if "/species/match?" in url:
                return {"matchType":"EXACT", "rank":"SPECIES", "canonicalName":"Vespa velutina", "usageKey":1}
            if "/occurrence/search?" in url:
                return {"results":[{"key":9,"speciesKey":1,"species":"Vespa velutina",
                    "license":"CC0_1_0","datasetKey":"d",
                    "media":[{"type":"StillImage","identifier":"https://images.example/9.jpg",
                    "license":"CC0_1_0"}]}]}
            raise AssertionError("Unexpected endpoint: " + url)
        # Run a single target; the quota means only the first species is queried.
        rows, status = discover(target=1, max_pages=1, limit=10, pause=0.5, fetch=fetch)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["scientific_name"], "Vespa velutina")
        self.assertEqual(rows[0]["species_key"], 1)
        self.assertFalse(status["media_downloaded"])
        self.assertFalse(status["training_performed"])


if __name__ == "__main__":
    unittest.main()
