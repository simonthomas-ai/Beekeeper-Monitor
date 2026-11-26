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


def rights(basis="LicenseRef-ExplicitPermission", source="Eigene Feldaufnahme", **changes):
    result = {
        "source": source,
        "basis": basis,
        "status": "training_approved",
    }
    if basis == "CC0-1.0":
        result["evidence_url"] = "https://creativecommons.org/publicdomain/zero/1.0/"
    elif basis == "CC-BY-4.0":
        result["evidence_url"] = "https://creativecommons.org/licenses/by/4.0/"
        result["attribution"] = "Example photographer (CC BY 4.0)"
    elif basis == "LicenseRef-ExplicitPermission":
        result["permission_ref"] = "consent-record-test-001"
    result.update(changes)
    return result


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

    def record(self, image, labels, rights_data=None):
        return {
            "image": image,
            "labels": labels,
            "captured_at": "2026-11-23T08:00:00+01:00",
            "capture_session_id": "session-pseudonym-1",
            "labeler_id": "reviewer:field-0001",
            "review_status": "approved",
            "reviewed_by": "reviewer:field-reviewer-0001",
            "reviewed_at": "2026-11-23T08:30:00+01:00",
            "rights": rights_data or rights(),
        }

    def test_accepts_multilabel_and_negative_contract(self):
        path = self.make_zip([
            self.record("images/positive.jpg", ["vespa_velutina", "apis_mellifera"]),
            self.record("images/negative.jpg", []),
        ])
        self.assertEqual(validate(path), [])

    def test_accepts_each_supported_rights_basis(self):
        rows = [
            self.record("images/positive.jpg", ["vespa_velutina"], rights("CC0-1.0")),
            self.record(
                "images/negative.jpg", [],
                rights("CC-BY-4.0", "https://example.org/photos/negative"),
            ),
        ]
        path = self.make_zip(rows)
        self.assertEqual(validate(path), [])

    def test_rejects_non_pseudonymous_labeler_ids(self):
        for labeler_id in ("Simon Thomas", "simon@example.org", "https://example.org/reviewer", "reviewer:short"):
            with self.subTest(labeler_id=labeler_id):
                positive = self.record("images/positive.jpg", [CLASS_SLUGS[0]])
                positive["labeler_id"] = labeler_id
                path = self.make_zip([positive, self.record("images/negative.jpg", [])])
                errors = validate(path)
                self.assertTrue(any("labeler_id" in error for error in errors))

    def test_requires_pseudonymous_review_identity_and_separate_timezone_aware_time(self):
        invalid_rows = [
            ({"reviewed_by": "Simon Thomas"}, "reviewed_by muss reviewer:<opaque-id> verwenden"),
            ({"reviewed_by": "reviewer:short"}, "reviewed_by muss reviewer:<opaque-id> verwenden"),
            ({"reviewed_at": "2026-11-23T08:30:00"}, "reviewed_at ist kein ISO-8601-Zeitstempel"),
            ({"reviewed_at": "2026-11-23T06:59:59Z"}, "reviewed_at liegt vor captured_at"),
            ({"reviewed_at": None}, "reviewed_at ist kein ISO-8601-Zeitstempel"),
        ]
        for index, (changes, expected) in enumerate(invalid_rows):
            with self.subTest(index=index):
                positive = self.record("images/positive.jpg", [CLASS_SLUGS[0]])
                positive.update(changes)
                path = self.make_zip([
                    positive,
                    self.record("images/negative.jpg", []),
                ])
                errors = validate(path)
                self.assertTrue(any(expected in error for error in errors))

        missing = self.record("images/positive.jpg", [CLASS_SLUGS[0]])
        missing.pop("reviewed_by")
        path = self.make_zip([
            missing,
            self.record("images/negative.jpg", []),
        ])
        errors = validate(path)
        self.assertTrue(any("Pflichtfelder" in error for error in errors))

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

    def test_rejects_unknown_rights_basis_missing_evidence_and_long_values(self):
        long_source = self.record("images/positive.jpg", [CLASS_SLUGS[0]])
        long_source["rights"]["source"] = "x" * 201
        path = self.make_zip([long_source, self.record("images/negative.jpg", [])])
        errors = validate(path)
        self.assertTrue(any("rights.source" in error for error in errors))

        bad_basis = self.record(
            "images/positive.jpg", [CLASS_SLUGS[0]],
            rights("Nutzerangabe"),
        )
        missing_evidence = rights("CC0-1.0")
        missing_evidence.pop("evidence_url")
        path = self.make_zip([
            bad_basis,
            self.record("images/negative.jpg", [], missing_evidence),
        ])
        errors = validate(path)
        self.assertTrue(any("rights.basis" in error for error in errors))
        self.assertTrue(any("evidence_url fehlt" in error for error in errors))

        unsupported = self.root / "unsupported.zip"
        with zipfile.ZipFile(unsupported, "w") as archive:
            archive.writestr("images/photo.heic", b"fixture")
            archive.writestr("annotations.jsonl", "{}\n")
        errors = validate(unsupported)
        self.assertTrue(any("Unzulässiger ZIP-Pfad" in error for error in errors))

    def test_rejects_credentials_queries_fragments_and_unknown_rights_fields(self):
        invalid = [
            rights(source="http://example.org/photo"),
            rights(source="https://user:password@example.org/photo"),
            rights(source="https://example.org/photo?token=example"),
            rights(source="https://example.org/photo#private"),
            rights(private_note="must not be exported"),
            rights(publication_allowed=False),
        ]
        for index, item_rights in enumerate(invalid):
            with self.subTest(index=index):
                path = self.make_zip([
                    self.record("images/positive.jpg", [CLASS_SLUGS[0]], item_rights),
                    self.record("images/negative.jpg", []),
                ])
                errors = validate(path)
                self.assertTrue(any("rights.source" in error or "nicht unterstützte Felder" in error or
                                    "publication_allowed" in error for error in errors))

    def test_requires_cc_by_attribution_and_explicit_permission_reference(self):
        invalid = [
            rights("CC-BY-4.0", attribution=""),
            rights("LicenseRef-ExplicitPermission", permission_ref=""),
            rights("LicenseRef-ExplicitPermission", permission_ref="https://private.example/permission"),
            rights("LicenseRef-ExplicitPermission", private_note="sensitive"),
        ]
        for index, item_rights in enumerate(invalid):
            with self.subTest(index=index):
                path = self.make_zip([
                    self.record("images/positive.jpg", [CLASS_SLUGS[0]], item_rights),
                    self.record("images/negative.jpg", []),
                ])
                errors = validate(path)
                self.assertTrue(any("attribution" in error or "permission_ref" in error or
                                    "nicht unterstützte Felder" in error for error in errors))


    def test_rejects_duplicate_json_keys(self):
        path = self.root / "duplicate-keys.zip"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("images/positive.jpg", b"positive")
            archive.writestr("images/negative.jpg", b"negative")
            archive.writestr(
                "annotations.jsonl",
                '{"image":"images/positive.jpg","image":"images/negative.jpg"}\\n',
            )
        errors = validate(path)
        self.assertTrue(any("doppelter Schlüssel" in error for error in errors))

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
