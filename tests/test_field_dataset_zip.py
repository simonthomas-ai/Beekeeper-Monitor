import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.validate_field_dataset_zip import validate


CLASS_SLUGS = [
    "vespa_velutina", "vespa_crabro", "other_vespidae",
    "apis_mellifera", "bombus_spp", "syrphidae", "other_insect",
]


class FieldDatasetZipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def make_zip(self, lines, extra=None):
        path = self.root / "field.zip"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, content in (extra or {}).items():
                archive.writestr(name, content)
            archive.writestr("images/positive.jpg", b"\xff\xd8image\xff\xd9")
            archive.writestr("images/negative.jpg", b"\xff\xd8negative\xff\xd9")
            archive.writestr("annotations.jsonl", "\n".join(
                json.dumps(line, ensure_ascii=False) for line in lines
            ) + "\n")
        return path

    def record(self, image, labels):
        return {
            "image": image,
            "labels": labels,
            "captured_at": "2026-11-23T08:00:00+01:00",
            "capture_session_id": "session-pseudonym-1",
            "labeler_id": "reviewer-1",
            "review_status": "approved",
            "rights": {
                "source": "Eigene Feldaufnahme",
                "basis": "Nutzerangabe; nicht unabhängig geprüft",
                "status": "training_approved",
            },
        }

    def test_accepts_multilabel_and_negative_contract(self):
        path = self.make_zip([
            self.record("images/positive.jpg", ["vespa_velutina", "apis_mellifera"]),
            self.record("images/negative.jpg", []),
        ])
        self.assertEqual(validate(path), [])

    def test_rejects_unapproved_and_unknown_labels(self):
        positive = self.record("images/positive.jpg", ["not_a_project_class"])
        positive["review_status"] = "pending_review"
        negative = self.record("images/negative.jpg", [])
        path = self.make_zip([positive, negative])
        errors = validate(path)
        self.assertTrue(any("unknown" in error.lower() or "unbekannte" in error.lower() for error in errors))
        self.assertTrue(any("approved" in error for error in errors))

    def test_rejects_gps_bbox_and_extra_root_entries(self):
        positive = self.record("images/positive.jpg", [CLASS_SLUGS[0]])
        positive["location"] = {"latitude": 53.0, "longitude": 10.0}
        positive["bbox"] = [1, 2, 3, 4]
        path = self.make_zip([positive, self.record("images/negative.jpg", [])],
                             extra={"notes.txt": "not part of the contract"})
        errors = validate(path)
        self.assertTrue(any("nicht unterstützte Felder" in error for error in errors))
        self.assertTrue(any("Unzulässiger ZIP-Pfad" in error for error in errors))

    def test_rejects_missing_or_duplicate_annotations(self):
        path = self.make_zip([
            self.record("images/positive.jpg", [CLASS_SLUGS[0]])
        ])
        errors = validate(path)
        self.assertTrue(any("Bilder ohne Annotation" in error for error in errors))

        path = self.make_zip([
            self.record("images/positive.jpg", [CLASS_SLUGS[0]]),
            self.record("images/positive.jpg", [CLASS_SLUGS[0]]),
            self.record("images/negative.jpg", []),
        ])
        errors = validate(path)
        self.assertTrue(any("mehrfach annotiert" in error for error in errors))

    def test_rights_are_bounded_free_text_and_only_supported_image_suffixes(self):
        long_source = self.record("images/positive.jpg", [CLASS_SLUGS[0]])
        long_source["rights"]["source"] = "x" * 201
        path = self.make_zip([long_source, self.record("images/negative.jpg", [])])
        errors = validate(path)
        self.assertTrue(any("rights.source" in error for error in errors))

        unsupported = self.root / "unsupported.zip"
        with zipfile.ZipFile(unsupported, "w") as archive:
            archive.writestr("images/photo.heic", b"fixture")
            archive.writestr("annotations.jsonl", "{}\n")
        errors = validate(unsupported)
        self.assertTrue(any("Unzulässiger ZIP-Pfad" in error for error in errors))

    def test_rejects_duplicate_image_bytes(self):
        path = self.root / "duplicate.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("images/one.jpg", b"same bytes")
            archive.writestr("images/two.jpg", b"same bytes")
            archive.writestr("annotations.jsonl", "\n".join([
                json.dumps(self.record("images/one.jpg", [CLASS_SLUGS[0]])),
                json.dumps(self.record("images/two.jpg", [CLASS_SLUGS[1]])),
            ]) + "\n")
        errors = validate(path)
        self.assertTrue(any("Duplizierter Bildinhalt" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
