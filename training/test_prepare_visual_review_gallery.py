"""Regression tests for high-resolution iNaturalist gallery output."""
import csv
import tempfile
import unittest
from pathlib import Path

from prepare_visual_review_gallery import gallery


class VisualReviewGalleryTests(unittest.TestCase):
    def test_inaturalist_square_url_is_upgraded_and_pixel_dimensions_are_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "in.csv"
            output = Path(folder) / "gallery.html"
            fields = ["photo_id", "observation_id", "species_candidate", "image_url",
                      "source_url", "license", "creator"]
            row = {"photo_id":"763034625", "observation_id":"414481366",
                   "species_candidate":"Vespa velutina",
                   "image_url":"https://inaturalist-open-data.s3.amazonaws.com/photos/763034625/square.jpg",
                   "source_url":"https://www.inaturalist.org/observations/414481366",
                   "license":"CC0-1.0", "creator":"no rights reserved"}
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow(row)
            gallery(source, output)
            result = output.read_text(encoding="utf-8")
            self.assertIn("/photos/763034625/original.jpg", result)
            self.assertNotIn("/photos/763034625/square.jpg", result)
            self.assertIn("naturalWidth", result)
            self.assertIn("naturalHeight", result)
            self.assertIn("2048 px", result)


if __name__ == "__main__":
    unittest.main()
