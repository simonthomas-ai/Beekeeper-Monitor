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
            "reviewer": "reviewer-pseudonym",
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
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.json"
            path.write_text(json.dumps({"records": [record]}), encoding="utf-8")
            return check(path)

    def test_seventh_class_other_insect_is_accepted(self):
        report = self._check(self._record(6))
        self.assertEqual(report["reviewed_records"], 1)
        self.assertEqual(report["validated_boxes"], 1)

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

    def test_shared_class_schema_has_seven_distinct_classes(self):
        self.assertEqual(len(CLASS_NAMES), 7)
        self.assertEqual(len(set(CLASS_NAMES)), 7)
        self.assertEqual(CLASS_NAMES[6], "other_insect")


if __name__ == "__main__":
    unittest.main()
