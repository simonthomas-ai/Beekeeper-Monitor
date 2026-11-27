import json
import tempfile
import unittest
from pathlib import Path

from training.class_schema import CLASS_NAMES
from training.validate_reviewed_annotations import check


class ReviewedAnnotationTests(unittest.TestCase):
    def _record(self, class_id):
        return {
            "photo_id": "photo-001",
            "species": CLASS_NAMES[class_id] if 0 <= class_id < len(CLASS_NAMES) else "unknown",
            "license": "CC0-1.0",
            "license_verified": True,
            "species_verified": True,
            "image_quality_verified": True,
            "reviewer": "reviewer:field-0001",
            "reviewed_at": "2026-11-27T08:30:00Z",
            "source_url": "https://example.org/source/photo-001",
            "boxes": [{
                "class_id": class_id,
                "x": 0.5,
                "y": 0.5,
                "width": 0.2,
                "height": 0.3,
            }],
        }

    def _check(self, record):
        return self._check_payload({"records": [record]})

    def _check_payload(self, payload):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return check(path)

    def _check_raw(self, raw):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.json"
            path.write_text(raw, encoding="utf-8")
            return check(path)

    def test_seventh_class_other_insect_is_accepted(self):
        report = self._check(self._record(6))
        self.assertEqual(report["reviewed_records"], 1)
        self.assertEqual(report["validated_boxes"], 1)
        self.assertIn("Metadata/geometry only", report["limitations"])

    def test_first_class_is_accepted(self):
        report = self._check(self._record(0))
        self.assertEqual(report["validated_boxes"], 1)

    def test_class_id_after_schema_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid class_id"):
            self._check(self._record(7))

    def test_negative_class_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid class_id"):
            self._check(self._record(-1))

    def test_boolean_class_id_is_rejected(self):
        record = self._record(0)
        record["boxes"][0]["class_id"] = True
        with self.assertRaisesRegex(ValueError, "invalid class_id"):
            self._check(record)

    def test_rejects_reviewer_names_emails_and_urls(self):
        for reviewer in ("Simon Thomas", "person@example.org", "https://example.org/reviewer"):
            with self.subTest(reviewer=reviewer):
                record = self._record(0)
                record["reviewer"] = reviewer
                with self.assertRaisesRegex(ValueError, "reviewer:<opaque-id>"):
                    self._check(record)

    def test_rejects_missing_or_timezone_naive_review_timestamp(self):
        record = self._record(0)
        del record["reviewed_at"]
        with self.assertRaisesRegex(ValueError, "unknown or missing fields"):
            self._check(record)
        record = self._record(0)
        record["reviewed_at"] = "2026-11-27T08:30:00"
        with self.assertRaisesRegex(ValueError, "must include a timezone"):
            self._check(record)

    def test_rejects_malformed_review_timestamp(self):
        record = self._record(0)
        record["reviewed_at"] = "yesterday"
        with self.assertRaisesRegex(ValueError, "timezone-aware ISO-8601"):
            self._check(record)

    def test_rejects_source_url_credentials_query_and_fragment(self):
        for url in (
            "https://user:secret@example.org/photo",
            "https://example.org/photo?token=secret",
            "https://example.org/photo#private",
        ):
            with self.subTest(url=url):
                record = self._record(0)
                record["source_url"] = url
                with self.assertRaisesRegex(ValueError, "source_url"):
                    self._check(record)

    def test_rejects_non_opaque_photo_ids(self):
        for photo_id in ("person@example.org", "https://example.org/photo", "../photo.jpg"):
            with self.subTest(photo_id=photo_id):
                record = self._record(0)
                record["photo_id"] = photo_id
                with self.assertRaisesRegex(ValueError, "opaque identifier"):
                    self._check(record)

    def test_rejects_unknown_fields_that_could_carry_private_data(self):
        record = self._record(0)
        record["gps"] = "51.0,7.0"
        with self.assertRaisesRegex(ValueError, "unknown or missing fields"):
            self._check(record)

    def test_rejects_duplicate_json_keys(self):
        raw = '{"records":[],"records":[]}'
        with self.assertRaisesRegex(ValueError, "unique keys"):
            self._check_raw(raw)

    def test_rejects_extra_top_level_fields(self):
        with self.assertRaisesRegex(ValueError, "only a records array"):
            self._check_payload({"records": [self._record(0)], "reviewer_email": "private@example.org"})

    def test_shared_class_schema_has_seven_distinct_classes(self):
        self.assertEqual(len(CLASS_NAMES), 7)
        self.assertEqual(len(set(CLASS_NAMES)), 7)
        self.assertEqual(CLASS_NAMES[6], "other_insect")


if __name__ == "__main__":
    unittest.main()
