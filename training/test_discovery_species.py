import csv
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from discover_inaturalist_candidates import (
    FIELDS, GROUPS, SPECIES, LICENSES, _candidate_from_observation, discover,
)
from audit_inaturalist_candidates import audit as audit_candidates
from dataset_groups import (
    GROUP_LABELS, SPECIES_TO_GROUP, balanced_quotas, balanced_taxon_quotas,
)


def make_observations(species, count=200, start=1):
    records = []
    for index in range(count):
        observation_id = start + index
        photo_id = start * 100000 + index
        records.append({
            "id": observation_id,
            "quality_grade": "research",
            "taxon": {"name": species},
            "user": {"login": "research-photographer", "name": "Research Photographer"},
            "photos": [{
                "id": photo_id,
                "license_code": "cc0",
                "attribution": "Research Photographer, no rights reserved (CC0)",
                "url": f"https://static.inaturalist.org/photos/{photo_id}/square.jpg",
            }],
        })
    return records


class SpeciesAndQuotaTests(unittest.TestCase):
    def test_candidate_metadata_separates_creator_and_attribution_and_passes_audit(self):
        observation = make_observations("Vespa velutina", count=1)[0]
        candidate = _candidate_from_observation(
            observation, "Vespa velutina", set(), set()
        )
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["creator"], "Research Photographer")
        self.assertEqual(candidate["creator_login"], "research-photographer")
        self.assertEqual(candidate["license_notice"], "Research Photographer, no rights reserved (CC0)")
        self.assertEqual(candidate["attribution"], "Research Photographer, no rights reserved (CC0)")

        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "candidates.csv"
            with queue.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerow(candidate)
            report = audit_candidates(queue)
        self.assertEqual(report["metadata_errors"], [])
        self.assertEqual(report["approved_training_images"], 0)

    def test_cc_by_candidate_keeps_source_attribution_and_unverified_license(self):
        observation = make_observations("Vespa velutina", count=1)[0]
        photo = observation["photos"][0]
        photo["license_code"] = "cc-by"
        photo["attribution"] = "© Research Photographer, some rights reserved (CC-BY)"
        candidate = _candidate_from_observation(
            observation, "Vespa velutina", set(), set()
        )
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["license"], "CC-BY-VERSION-UNVERIFIED")
        self.assertEqual(candidate["license_url"], "")
        self.assertEqual(candidate["creator"], "Research Photographer")
        self.assertEqual(candidate["creator_login"], "research-photographer")
        self.assertEqual(candidate["attribution"], photo["attribution"])
        self.assertEqual(candidate["license_notice"], photo["attribution"])

    def test_missing_observer_identity_is_rejected(self):
        observation = make_observations("Vespa velutina", count=1)[0]
        observation.pop("user")
        self.assertIsNone(_candidate_from_observation(
            observation, "Vespa velutina", set(), set()
        ))

    def test_non_research_grade_observation_is_rejected(self):
        observation = make_observations("Vespa velutina", count=1)[0]
        observation["quality_grade"] = "needs_id"
        self.assertIsNone(_candidate_from_observation(
            observation, "Vespa velutina", set(), set()
        ))
    def test_five_dataset_groups_and_all_scientific_taxa_are_explicit(self):
        self.assertEqual(len(GROUPS), 5)
        self.assertEqual(set(GROUPS), set(GROUP_LABELS))
        self.assertEqual(len(SPECIES), 7)
        self.assertEqual(len(SPECIES), len(set(SPECIES)))
        for species in (
            "Vespa velutina", "Vespa crabro", "Vespula vulgaris",
            "Vespula germanica", "Apis mellifera",
            "Bombus terrestris", "Bombus lapidarius",
        ):
            self.assertIn(species, SPECIES_TO_GROUP)

    def test_default_target_is_200_per_group(self):
        quotas = balanced_quotas(1000)
        self.assertEqual(set(quotas.values()), {200})
        self.assertEqual(sum(quotas.values()), 1000)

    def test_bumblebee_and_wasp_subtaxa_get_balanced_shares(self):
        self.assertEqual(
            balanced_taxon_quotas("bumblebees", 200),
            {"Bombus terrestris": 100, "Bombus lapidarius": 100},
        )
        self.assertEqual(
            balanced_taxon_quotas("wasps", 200),
            {"Vespula vulgaris": 100, "Vespula germanica": 100},
        )

    def test_candidate_discovery_returns_exactly_200_per_group_when_available(self):
        start = 10
        fixtures = {}
        for species in SPECIES:
            fixtures[species] = make_observations(species, 200, start)
            start += 1000

        with patch("discover_inaturalist_candidates.fetch_observations",
                   side_effect=lambda species, page: fixtures[species] if page == 1 else []):
            rows = discover(1000, max_pages=2, pause=0)

        counts = Counter(row["dataset_group"] for row in rows)
        self.assertEqual(len(rows), 1000)
        self.assertEqual(counts, {group: 200 for group in GROUPS})
        self.assertTrue(all(row["review_status"] == "UNREVIEWED" for row in rows))
        self.assertTrue(all(row["image_url"].endswith("/original.jpg") for row in rows))
        species_counts = Counter(row["species_candidate"] for row in rows)
        self.assertEqual(species_counts["Bombus terrestris"], 100)
        self.assertEqual(species_counts["Bombus lapidarius"], 100)
        self.assertEqual(species_counts["Vespula vulgaris"], 100)
        self.assertEqual(species_counts["Vespula germanica"], 100)

    def test_group_shortfall_is_backfilled_by_other_taxa_in_same_group(self):
        start = 100
        fixtures = {}
        for species in SPECIES:
            if species in {"Bombus lapidarius", "Vespula germanica"}:
                fixtures[species] = []
            else:
                fixtures[species] = make_observations(species, 200, start)
            start += 1000

        with patch("discover_inaturalist_candidates.fetch_observations",
                   side_effect=lambda species, page: fixtures[species] if page == 1 else []):
            rows = discover(1000, max_pages=2, pause=0)

        counts = Counter(row["dataset_group"] for row in rows)
        self.assertEqual(counts, {group: 200 for group in GROUPS})
        species_counts = Counter(row["species_candidate"] for row in rows)
        self.assertEqual(species_counts["Bombus terrestris"], 200)
        self.assertEqual(species_counts["Bombus lapidarius"], 0)
        self.assertEqual(species_counts["Vespula vulgaris"], 200)
        self.assertEqual(species_counts["Vespula germanica"], 0)

    def test_license_candidate_code_does_not_upgrade_cc_by_rights(self):
        self.assertEqual(LICENSES["cc-by"][0], "CC-BY-VERSION-UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
