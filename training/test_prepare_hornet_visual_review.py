"""Offline regression tests for the hornet visual-review queue."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import prepare_hornet_visual_review as review


class ReviewQueueTests(unittest.TestCase):
    def test_large_url_only_https_square(self):
        self.assertEqual(review.large_url("https://example.org/photos/1/square.jpg"),
                         "https://example.org/photos/1/large.jpg")
        self.assertEqual(review.large_url("http://example.org/photos/1/square.jpg"), "")
        self.assertEqual(review.large_url("https://example.org/photos/1/original.jpg"), "")

    def test_only_verified_metadata_and_never_approve(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "input.csv"
            target = Path(folder) / "output.csv"
            keys = ["observation_id", "photo_id", "api_photo_found",
                    "license_metadata_match", "api_photo_license",
                    "api_taxon", "api_photo_url", "error"]
            base = dict.fromkeys(keys, "")
            base.update(observation_id="1", photo_id="2", api_photo_found="YES",
                        license_metadata_match="YES", api_photo_license="cc0",
                        api_taxon="Vespa velutina",
                        api_photo_url="https://example.org/photos/2/square.jpg")
            invalid = dict(base, observation_id="3", error="API failed")
            with source.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows([base, invalid])
            with patch("sys.argv", ["review", "--input", str(source), "--output", str(target)]):
                review.main()
            with target.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["training_approved"], "NO")
            self.assertEqual(rows[0]["visual_species_verified"], "NO")
            self.assertEqual(rows[0]["rights_verified"], "NO")
            self.assertEqual(rows[0]["large_review_url"],
                             "https://example.org/photos/2/large.jpg")


if __name__ == "__main__":
    unittest.main()
