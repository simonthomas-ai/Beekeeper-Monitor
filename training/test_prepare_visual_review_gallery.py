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
                      "source_url", "license", "creator", "creator_login",
                      "attribution", "license_notice"]
            row = {"photo_id":"763034625", "observation_id":"414481366",
                   "species_candidate":"Vespa velutina",
                   "image_url":"https://inaturalist-open-data.s3.amazonaws.com/photos/763034625/square.jpg",
                   "source_url":"https://www.inaturalist.org/observations/414481366",
                   "license":"CC0-1.0", "creator":"Test Observer",
                   "creator_login":"test-observer",
                   "attribution":"Test Observer, no rights reserved (CC0)",
                   "license_notice":"no rights reserved"}
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
            self.assertIn("iNaturalist-Originalvariante", result)
            self.assertIn('option value="asian_hornet"', result)
            self.assertIn('option value="bumblebees"', result)
            self.assertIn('option value="wasps"', result)
            self.assertIn("items[i].dataset_group===filter", result)
            self.assertIn("iNaturalist-Beobachter / Attributionsbasis", result)
            self.assertIn("label+\": \"+items.filter", result)
            self.assertNotIn(" / 200", result)
            self.assertIn("Unveränderte Originaldatei öffnen", result)
            self.assertIn('"dataset_group": "asian_hornet"', result)


    def test_untrusted_species_filter_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "Unsupported species filter"):
                gallery(
                    Path(folder) / "missing.csv",
                    Path(folder) / "gallery.html",
                    species="ALL</script><script>alert(1)</script>",
                )

    def test_external_creator_metadata_cannot_close_inline_script(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "in.csv"
            output = Path(folder) / "gallery.html"
            hostile = "</script><script>alert('xss')</script>"
            fields = ["photo_id", "observation_id", "species_candidate", "image_url",
                      "source_url", "license", "creator", "creator_login",
                      "attribution", "license_notice"]
            row = {
                "photo_id": "763034625",
                "observation_id": "414481366",
                "species_candidate": "Vespa velutina",
                "image_url": "https://static.inaturalist.org/photos/763034625/original.jpg",
                "source_url": "https://www.inaturalist.org/observations/414481366",
                "license": "CC0-1.0",
                "creator": hostile,
                "creator_login": "untrusted-login",
                "attribution": hostile + ", no rights reserved (CC0)",
                "license_notice": "no rights reserved",
            }
            self.write_rows(source, fields, [row])
            gallery(source, output, species="ALL")
            page = output.read_text(encoding="utf-8")
            self.assertIn(r"\u003c/script>", page)
            self.assertNotIn(hostile, page)
            self.assertEqual(page.count("</script>"), 1)

    def test_quality_screen_rejects_small_images_and_shows_metrics(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "screened.csv"
            output = Path(folder) / "gallery.html"
            fields = ["photo_id", "observation_id", "species_candidate", "image_url",
                      "source_url", "license", "creator", "creator_login",
                      "attribution", "license_notice", "dataset_group",
                      "image_width", "image_height", "image_megapixels",
                      "image_bytes", "sharpness_score", "image_quality_status",
                      "quality_rank", "quality_reason"]
            rows = [
                {"photo_id":"10", "observation_id":"20", "species_candidate":"Vespa velutina",
                 "dataset_group":"asian_hornet",
                 "image_url":"https://static.inaturalist.org/photos/10/original.jpg",
                 "source_url":"https://www.inaturalist.org/observations/20",
                 "license":"CC0-1.0", "creator":"Test Observer",
                 "creator_login":"test-observer",
                 "attribution":"Test Observer, no rights reserved (CC0)",
                 "license_notice":"no rights reserved",
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


    def test_gallery_prefers_local_unmodified_original_from_verified_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "screened.csv"
            output = root / "velutina.html"
            manifest = root / "images.csv"
            fields = ["photo_id", "observation_id", "species_candidate", "dataset_group",
                      "image_url", "source_url", "license", "creator", "creator_login",
                      "attribution", "license_notice", "image_width", "image_height",
                      "image_quality_status"]
            row = {"photo_id":"42", "observation_id":"99", "species_candidate":"Vespa velutina",
                   "dataset_group":"asian_hornet",
                   "image_url":"https://static.inaturalist.org/photos/42/original.jpg",
                   "source_url":"https://www.inaturalist.org/observations/99",
                   "license":"CC0-1.0", "creator":"Original author",
                   "creator_login":"original-author",
                   "attribution":"Original author, no rights reserved (CC0)",
                   "license_notice":"no rights reserved",
                   "image_width":"1920", "image_height":"1080", "image_quality_status":"PASS"}
            missing_original = dict(row, photo_id="43", observation_id="100",
                                    image_url="https://static.inaturalist.org/photos/43/original.jpg",
                                    source_url="https://www.inaturalist.org/observations/100")
            self.write_rows(source, fields, [row, missing_original])
            manifest_fields = ["photo_id", "observation_id", "species_candidate",
                               "source_url", "license", "creator", "creator_login",
                               "attribution", "license_notice", "source_image_url",
                               "local_image_path", "image_format", "image_width",
                               "image_height", "image_bytes", "sha256", "download_status"]
            asset = {"photo_id":"42", "observation_id":"99",
                     "species_candidate":"Vespa velutina",
                     "source_url":row["source_url"], "license":"CC0-1.0",
                     "creator":"Original author", "creator_login":"original-author",
                     "attribution":"Original author, no rights reserved (CC0)",
                     "license_notice":"no rights reserved",
                     "source_image_url":"https://static.inaturalist.org/photos/42/original.jpg",
                     "local_image_path":"images/velutina/42.jpg",
                     "image_format":"JPEG", "image_width":"1920",
                     "image_height":"1080", "image_bytes":"245678",
                     "sha256":"a"*64, "download_status":"DOWNLOADED_UNMODIFIED"}
            self.write_rows(manifest, manifest_fields, [asset])
            gallery(source, output, species="Vespa velutina", images_manifest=manifest)
            page = output.read_text(encoding="utf-8")
            self.assertIn('"image_url": "images/velutina/42.jpg"', page)
            self.assertNotIn('"photo_id": "43"', page)
            self.assertNotIn("/photos/43/original.jpg", page)
            self.assertNotIn('src item.image_url', page)
            self.assertIn('"image_delivery": "LOCAL_UNMODIFIED_ORIGINAL"', page)
            self.assertIn('"original_sha256": "' + "a"*64 + '"', page)
            self.assertIn("Unveränderte Originaldatei öffnen", page)

    def write_rows(self, path, fields, rows):
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
