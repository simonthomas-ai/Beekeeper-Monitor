"""Regression tests for high-resolution iNaturalist gallery output."""
import csv
import tempfile
import unittest
from pathlib import Path

try:
    from training.prepare_visual_review_gallery import gallery
except ModuleNotFoundError:
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
            gallery(source, output, species="ALL")
            result = output.read_text(encoding="utf-8")
            self.assertIn("/photos/763034625/original.jpg", result)
            self.assertNotIn("/photos/763034625/square.jpg", result)
            self.assertIn("naturalWidth", result)
            self.assertIn("naturalHeight", result)
            self.assertIn("2048 px", result)
            self.assertIn('option value="asian_hornet"', result)
            self.assertIn('option value="bumblebees"', result)
            self.assertIn('option value="wasps"', result)
            self.assertIn("items[i].dataset_group===filter", result)
            self.assertIn("label+\": \"+items.filter", result)
            self.assertNotIn(" / 200", result)
            self.assertIn("Bilddatei in Originalgröße öffnen", result)
            self.assertIn('"dataset_group": "asian_hornet"', result)


    def test_quality_screen_rejects_small_images_and_shows_metrics(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "screened.csv"
            output = Path(folder) / "gallery.html"
            fields = ["photo_id", "observation_id", "species_candidate", "image_url",
                      "source_url", "license", "creator", "dataset_group",
                      "image_width", "image_height", "image_megapixels",
                      "image_bytes", "sharpness_score", "image_quality_status",
                      "quality_rank", "quality_reason"]
            rows = [
                {"photo_id":"10", "observation_id":"20", "species_candidate":"Vespa velutina",
                 "dataset_group":"asian_hornet",
                 "image_url":"https://static.inaturalist.org/photos/10/original.jpg",
                 "source_url":"https://www.inaturalist.org/observations/20",
                 "license":"CC0-1.0", "creator":"creator",
                 "image_width":"1600", "image_height":"1200", "image_megapixels":"1.92",
                 "image_bytes":"200000", "sharpness_score":"42.1",
                 "image_quality_status":"PASS", "quality_rank":"1",
                 "quality_reason":"dimensions passed"},
                {"photo_id":"11", "observation_id":"21", "species_candidate":"Vespa velutina",
                 "dataset_group":"asian_hornet",
                 "image_url":"https://static.inaturalist.org/photos/11/original.jpg",
                 "source_url":"https://www.inaturalist.org/observations/21",
                 "license":"CC0-1.0", "creator":"creator",
                 "image_width":"320", "image_height":"240", "image_megapixels":"0.077",
                 "image_bytes":"5000", "sharpness_score":"2.0",
                 "image_quality_status":"REJECT_LOW_RESOLUTION", "quality_rank":"",
                 "quality_reason":"too small"},
            ]
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            gallery(source, output, species="Vespa velutina")
            result = output.read_text(encoding="utf-8")
            self.assertIn('\"photo_id\": \"10\"', result)
            self.assertNotIn('\"photo_id\": \"11\"', result)
            self.assertIn('\"image_width\": 1600', result)
            self.assertIn('\"sharpness_score\": \"42.1\"', result)
            self.assertIn("nur Sortierung", result)


if __name__ == "__main__":
    unittest.main()
