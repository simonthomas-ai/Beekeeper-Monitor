import csv
import json
import tempfile
import unittest
from pathlib import Path

try:
    from training.prepare_species_review import prepare
except ModuleNotFoundError:
    from prepare_species_review import prepare


class SpeciesReviewGroupTests(unittest.TestCase):
    def test_scientific_taxa_are_kept_separate_but_share_the_right_group(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.csv"
            target = root / "review.csv"
            fields = ["source_id", "source_url", "image_url", "creator", "license", "license_url",
                      "attribution", "observation_id", "photo_id", "species_candidate", "dataset_group", "review_status"]
            rows = []
            for index, species in enumerate(("Bombus terrestris", "Bombus lapidarius"), start=1):
                rows.append({
                    "source_id": f"inat:{index}", "source_url": f"https://www.inaturalist.org/observations/{index}",
                    "image_url": f"https://static.inaturalist.org/photos/{index}/original.jpg",
                    "creator": "Creator", "license": "CC0-1.0",
                    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                    "attribution": "Creator", "observation_id": str(index), "photo_id": str(index),
                    "species_candidate": species, "dataset_group": "bumblebees", "review_status": "UNREVIEWED",
                })
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            prepare(source, target)
            with target.open(newline="", encoding="utf-8") as stream:
                output = list(csv.DictReader(stream))
            self.assertEqual({row["species_candidate"] for row in output}, {"Bombus terrestris", "Bombus lapidarius"})
            self.assertEqual({row["review_group"] for row in output}, {"bumblebees"})
            self.assertEqual({row["dataset_group"] for row in output}, {"bumblebees"})
            summary = json.loads(target.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(summary["dataset_group_counts"], {"bumblebees": 2})
            self.assertEqual(summary["approved_for_training"], 0)

    def test_species_group_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "input.csv"
            target = root / "review.csv"
            fields = ["source_id", "source_url", "image_url", "creator", "license", "license_url",
                      "attribution", "observation_id", "photo_id", "species_candidate", "dataset_group", "review_status"]
            row = {
                "source_id": "inat:1", "source_url": "https://www.inaturalist.org/observations/1",
                "image_url": "https://static.inaturalist.org/photos/1/original.jpg", "creator": "Creator",
                "license": "CC0-1.0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "attribution": "Creator", "observation_id": "1", "photo_id": "1",
                "species_candidate": "Vespa velutina", "dataset_group": "honey_bee", "review_status": "UNREVIEWED",
            }
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow(row)
            with self.assertRaises(ValueError):
                prepare(source, target)


if __name__ == "__main__":
    unittest.main()
