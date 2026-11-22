import csv
import json
import tempfile
import unittest
from pathlib import Path

from training.prepare_gbif_review_gallery import gallery, prepare_items


BASE = {
    "source_id": "gbif-media-6129883437-e078882a11650421",
    "source_url": "https://www.gbif.org/occurrence/6129883437",
    "image_url": "https://inaturalist-open-data.s3.amazonaws.com/photos/607770528/original.jpg",
    "media_license": "CC-BY-4.0",
    "media_license_url": "https://creativecommons.org/licenses/by/4.0/",
    "media_creator": "Carl Ramirez",
    "rights_holder": "Carl Ramirez",
    "publisher": "iNaturalist",
    "format": "image/jpeg",
    "occurrence_id": "6129883437",
    "occurrence_license": "CC-BY-4.0",
    "occurrence_license_url": "https://creativecommons.org/licenses/by/4.0/",
    "occurrence_rights_holder": "Carl Ramirez",
    "dataset_key": "50c9509d-22c7-4a22-a47d-8c48425ef4a7",
    "scientific_name": "Vespa velutina",
    "species_key": "1311477",
    "review_status": "UNREVIEWED_MEDIA_RIGHTS_AND_IMAGE",
}


class GbifReviewGalleryTests(unittest.TestCase):
    def write_rows(self, path, rows):
        fields = list(BASE)
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_allowlisted_original_is_embedded_and_bytes_are_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            output = Path(tmp) / "gallery.html"
            self.write_rows(source, [dict(BASE)])
            result = gallery(source, output)
            page = output.read_text(encoding="utf-8")
            self.assertEqual(result["records"], 1)
            self.assertEqual(result["inline_originals"], 1)
            self.assertEqual(result["images_embedded_as_bytes"], 0)
            self.assertIn("inaturalist-open-data.s3.amazonaws.com/photos/607770528/original.jpg", page)
            self.assertIn("UNREVIEWED_MEDIA_RIGHTS_AND_IMAGE", page)
            self.assertIn("Media licence", page) if "Media licence" in page else None
            self.assertIn("media_license", page)
            self.assertIn("occurrence_license", page)
            self.assertIn("training_eligible:false", page)
            self.assertNotIn("data:image/", page)

    def test_external_host_is_not_auto_embedded(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            output = Path(tmp) / "gallery.html"
            row = dict(BASE, source_id="gbif-media-100", occurrence_id="100",
                       source_url="https://www.gbif.org/occurrence/100",
                       image_url="https://11.ilstatic.hu/images/2026-02/r1770649967656_xl.webp",
                       format="image/webp")
            self.write_rows(source, [row])
            result = gallery(source, output)
            page = output.read_text(encoding="utf-8")
            self.assertEqual(result["inline_originals"], 0)
            self.assertEqual(result["external_or_unverified_hosts"], 1)
            self.assertIn("Externer oder nicht eindeutig originaler Medienhost", page)
            self.assertNotIn('src:"https://11.ilstatic.hu', page)
            self.assertNotIn('src="https://11.ilstatic.hu', page)

    def test_thumbnail_variant_is_not_auto_embedded(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            row = dict(BASE, image_url="https://inaturalist-open-data.s3.amazonaws.com/photos/607770528/square.jpg")
            self.write_rows(source, [row])
            item = prepare_items(source)[0]
            self.assertFalse(item["inline_allowed"])
            self.assertIsNone(item["inline_image_url"])

    def test_original_with_mismatched_media_format_is_not_auto_embedded(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            row = dict(BASE, format="image/webp")
            self.write_rows(source, [row])
            item = prepare_items(source)[0]
            self.assertFalse(item["inline_allowed"])

    def test_image_url_with_query_parameters_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            row = dict(BASE, image_url=BASE["image_url"] + "?redirect=https://evil.example/")
            self.write_rows(source, [row])
            with self.assertRaisesRegex(ValueError, "query parameters"):
                prepare_items(source)

    def test_gallery_limits_queue_size_to_500(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            self.write_rows(source, [
                dict(BASE, source_id=f"gbif-media-{i}", occurrence_id=str(i),
                     source_url=f"https://www.gbif.org/occurrence/{i}")
                for i in range(501)
            ])
            with self.assertRaisesRegex(ValueError, "500-row"):
                prepare_items(source)

    def test_rejects_unreviewed_state_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            row = dict(BASE, review_status="APPROVED")
            self.write_rows(source, [row])
            with self.assertRaisesRegex(ValueError, "unreviewed state"):
                prepare_items(source)

    def test_rejects_nonapproved_occurrence_license(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            row = dict(BASE, occurrence_license="CC-BY-NC-4.0",
                       occurrence_license_url="https://creativecommons.org/licenses/by-nc/4.0/")
            self.write_rows(source, [row])
            with self.assertRaisesRegex(ValueError, "unsupported media or occurrence licence"):
                prepare_items(source)

    def test_rejects_missing_cc_by_occurrence_rights_holder(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            row = dict(BASE, occurrence_rights_holder="")
            self.write_rows(source, [row])
            with self.assertRaisesRegex(ValueError, "CC-BY occurrence rights holder"):
                prepare_items(source)

    def test_rejects_source_url_occurrence_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            row = dict(BASE, source_url="https://www.gbif.org/occurrence/999")
            self.write_rows(source, [row])
            with self.assertRaisesRegex(ValueError, "does not bind"):
                prepare_items(source)

    def test_untrusted_metadata_cannot_close_inline_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            output = Path(tmp) / "gallery.html"
            hostile = "</script><script>alert('xss')</script>"
            row = dict(BASE, media_creator=hostile)
            self.write_rows(source, [row])
            gallery(source, output)
            page = output.read_text(encoding="utf-8")
            self.assertIn(r"\u003c/script\u003e", page)
            self.assertNotIn(hostile, page)
            self.assertEqual(page.count("</script>"), 1)

    def test_duplicates_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "queue.csv"
            duplicate = dict(BASE)
            self.write_rows(source, [BASE, duplicate])
            with self.assertRaisesRegex(ValueError, "duplicate GBIF source ID"):
                prepare_items(source)


if __name__ == "__main__":
    unittest.main()
