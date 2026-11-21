import csv
import json
import tempfile
import unittest
from pathlib import Path

try:
    from training.prepare_annotation_tasks import prepare
except ModuleNotFoundError:
    from prepare_annotation_tasks import prepare


class AnnotationTaskGroupTests(unittest.TestCase):
    def test_annotation_tasks_preserve_group_and_species(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, target = root / "review.csv", root / "tasks.csv"
            fields = ["photo_id", "observation_id", "species_candidate", "dataset_group",
                      "image_url", "source_url", "creator", "license", "license_url",
                      "license_review", "taxon_review", "image_quality_review",
                      "bbox_annotation_review", "training_eligible"]
            rows = [
                {"photo_id": "1", "observation_id": "10", "species_candidate": "Bombus terrestris",
                 "dataset_group": "bumblebees", "image_url": "https://static.inaturalist.org/photos/1/original.jpg",
                 "source_url": "https://www.inaturalist.org/observations/10", "creator": "Creator",
                 "license": "CC0-1.0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                 "license_review": "PENDING", "taxon_review": "PENDING", "image_quality_review": "PENDING",
                 "bbox_annotation_review": "PENDING", "training_eligible": "NO"},
                {"photo_id": "2", "observation_id": "11", "species_candidate": "Bombus lapidarius",
                 "dataset_group": "bumblebees", "image_url": "https://static.inaturalist.org/photos/2/original.jpg",
                 "source_url": "https://www.inaturalist.org/observations/11", "creator": "Creator",
                 "license": "CC0-1.0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                 "license_review": "PENDING", "taxon_review": "PENDING", "image_quality_review": "PENDING",
                 "bbox_annotation_review": "PENDING", "training_eligible": "NO"},
            ]
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            prepare(source, target)
            with target.open(newline="", encoding="utf-8") as stream:
                tasks = list(csv.DictReader(stream))
            self.assertEqual({task["species_candidate"] for task in tasks},
                             {"Bombus terrestris", "Bombus lapidarius"})
            self.assertEqual({task["dataset_group"] for task in tasks}, {"bumblebees"})
            summary = json.loads(target.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(summary["by_dataset_group"], {"bumblebees": 2})
            self.assertEqual(summary["training_approved"], 0)

    def test_annotation_task_rejects_group_taxon_mismatch(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, target = root / "review.csv", root / "tasks.csv"
            fields = ["photo_id", "observation_id", "species_candidate", "dataset_group",
                      "image_url", "source_url", "creator", "license", "license_url",
                      "license_review", "taxon_review", "image_quality_review",
                      "bbox_annotation_review", "training_eligible"]
            row = {"photo_id": "1", "observation_id": "10", "species_candidate": "Vespa velutina",
                   "dataset_group": "honey_bee", "image_url": "https://static.inaturalist.org/photos/1/original.jpg",
                   "source_url": "https://www.inaturalist.org/observations/10", "creator": "Creator",
                   "license": "CC0-1.0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                   "license_review": "PENDING", "taxon_review": "PENDING", "image_quality_review": "PENDING",
                   "bbox_annotation_review": "PENDING", "training_eligible": "NO"}
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow(row)
            with self.assertRaises(ValueError):
                prepare(source, target)


if __name__ == "__main__":
    unittest.main()
