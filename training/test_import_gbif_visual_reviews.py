import copy
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from training.prepare_gbif_review_gallery import MAX_QUEUE_BYTES, prepare_items
from training.import_gbif_visual_reviews import (
    MAX_REVIEW_EXPORT_BYTES,
    load_review_export,
    validate_review_export,
    write_new_file,
)


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


class GbifReviewImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.queue = self.root / "queue.csv"
        rows = [
            dict(BASE),
            dict(BASE,
                 source_id="gbif-media-6129883438-e078882a11650422",
                 source_url="https://www.gbif.org/occurrence/6129883438",
                 occurrence_id="6129883438",
                 image_url="https://inaturalist-open-data.s3.amazonaws.com/photos/607770529/original.jpg"),
        ]
        with self.queue.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(BASE))
            writer.writeheader()
            writer.writerows(rows)
        self.expected = prepare_items(self.queue)

    def export(self, decisions=None):
        decisions = decisions or ["LIKELY", "REJECT"]
        return {
            "format": "beekeeper-gbif-unverified-review-v2",
            "source_queue_sha256": hashlib.sha256(self.queue.read_bytes()).hexdigest(),
            "training_eligible": False,
            "records": [
                {**copy.deepcopy(row), "review": {"decision": decision},
                 "training_eligible": False}
                for row, decision in zip(self.expected, decisions)
            ],
        }

    def validate(self, payload=None, reviewer="Reviewer Example",
                 recorded_at="2026-11-22T10:00:00+01:00"):
        return validate_review_export(
            self.queue, self.export() if payload is None else payload,
            reviewer=reviewer, recorded_at=recorded_at,
        )

    def test_valid_export_reconciles_all_records_without_approval(self):
        result = self.validate()
        self.assertEqual(result["source_queue_records"], 2)
        self.assertEqual(result["source_queue_sha256"], hashlib.sha256(self.queue.read_bytes()).hexdigest())
        self.assertEqual(result["review_records_reconciled"], 2)
        self.assertEqual(result["decision_counts"]["LIKELY"], 1)
        self.assertEqual(result["decision_counts"]["REJECT"], 1)
        self.assertEqual(result["expert_species_confirmations"], 0)
        self.assertEqual(result["bounding_boxes_created"], 0)
        self.assertEqual(result["training_labels_created"], 0)
        self.assertEqual(result["training_approvals"], 0)
        self.assertIs(result["training_eligible"], False)
        self.assertTrue(result["human_expert_review_still_required"])

    def test_records_reviewer_and_timezone_aware_timestamp(self):
        result = self.validate(reviewer="Entomology Reviewer",
                               recorded_at="2026-11-22T10:30:00Z")
        self.assertEqual(result["reviewer"], "Entomology Reviewer")
        self.assertEqual(result["recorded_at"], "2026-11-22T10:30:00+00:00")

    def test_queue_snapshot_parser_uses_bytes_and_rejects_duplicate_headers(self):
        self.assertEqual(prepare_items(self.queue.read_bytes()), self.expected)
        header, *body = self.queue.read_bytes().splitlines()
        fields = header.decode("utf-8").split(",")
        fields[1] = fields[0]
        malformed = (",".join(fields) + "\n").encode("utf-8") + b"\n".join(body) + b"\n"
        with self.assertRaisesRegex(ValueError, "duplicate column names"):
            prepare_items(malformed)

    def test_queue_snapshot_enforces_size_limit(self):
        with self.assertRaisesRegex(ValueError, "safety limit"):
            prepare_items(b"x" * (MAX_QUEUE_BYTES + 1))

    def test_review_json_loader_rejects_duplicate_keys_at_nested_levels(self):
        path = self.root / "duplicate-review.json"
        path.write_text(
            '{"format":"beekeeper-gbif-unverified-review-v2",'
            '"records":[{"review":{"decision":"PENDING","decision":"LIKELY"}}]}',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            load_review_export(path)

    def test_review_json_loader_enforces_size_limit(self):
        path = self.root / "oversized-review.json"
        path.write_bytes(b" " * (MAX_REVIEW_EXPORT_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "safety limit"):
            load_review_export(path)

    def test_rejects_review_export_bound_to_different_queue_bytes(self):
        payload = self.export()
        original = self.queue.read_bytes()
        # CRLF is semantically equivalent CSV but is a different source snapshot.
        self.queue.write_bytes(original.replace(b"\n", b"\r\n"))
        with self.assertRaisesRegex(ValueError, "source queue SHA-256"):
            self.validate(payload)

    def test_rejects_missing_queue_digest(self):
        payload = self.export()
        payload.pop("source_queue_sha256")
        with self.assertRaisesRegex(ValueError, "source_queue_sha256"):
            self.validate(payload)

    def test_rejects_forged_top_level_training_approval(self):
        payload = self.export()
        payload["training_eligible"] = True
        with self.assertRaisesRegex(ValueError, "training_eligible=false"):
            self.validate(payload)

    def test_rejects_forged_record_training_approval(self):
        payload = self.export()
        payload["records"][0]["training_eligible"] = True
        with self.assertRaisesRegex(ValueError, "training approval is forbidden"):
            self.validate(payload)

    def test_rejects_wrong_export_format(self):
        payload = self.export()
        payload["format"] = "arbitrary-training-labels-v1"
        with self.assertRaisesRegex(ValueError, "unsupported"):
            self.validate(payload)

    def test_rejects_media_license_tampering(self):
        payload = self.export()
        payload["records"][0]["media_license"] = "CC0-1.0"
        with self.assertRaisesRegex(ValueError, "media_license differs"):
            self.validate(payload)

    def test_rejects_occurrence_license_tampering(self):
        payload = self.export()
        payload["records"][0]["occurrence_license_url"] = "https://creativecommons.org/licenses/by-nc/4.0/"
        with self.assertRaisesRegex(ValueError, "occurrence_license_url differs"):
            self.validate(payload)

    def test_rejects_species_or_source_tampering(self):
        payload = self.export()
        payload["records"][0]["scientific_name"] = "Vespa crabro"
        with self.assertRaisesRegex(ValueError, "scientific_name differs"):
            self.validate(payload)

    def test_rejects_image_url_or_host_policy_tampering(self):
        payload = self.export()
        payload["records"][0]["inline_allowed"] = False
        with self.assertRaisesRegex(ValueError, "inline_allowed differs"):
            self.validate(payload)

    def test_rejects_added_boxes_or_class_labels(self):
        payload = self.export()
        payload["records"][0]["review"]["boxes"] = [{"x": 0.5, "y": 0.5, "width": 0.2, "height": 0.2}]
        with self.assertRaisesRegex(ValueError, "only a visual decision"):
            self.validate(payload)

    def test_rejects_unrecognized_decision(self):
        payload = self.export()
        payload["records"][0]["review"]["decision"] = "CONFIRMED_VESPA_VELUTINA"
        with self.assertRaisesRegex(ValueError, "unsupported decision"):
            self.validate(payload)

    def test_rejects_missing_or_duplicate_source_records(self):
        payload = self.export()
        payload["records"].pop()
        with self.assertRaisesRegex(ValueError, "every original GBIF queue record"):
            self.validate(payload)
        payload = self.export()
        payload["records"][1] = copy.deepcopy(payload["records"][0])
        with self.assertRaisesRegex(ValueError, "unknown or duplicate source_id"):
            self.validate(payload)

    def test_rejects_unknown_extra_record_fields(self):
        payload = self.export()
        payload["records"][0]["model_prediction"] = "Vespa velutina"
        with self.assertRaisesRegex(ValueError, "unexpected or missing metadata fields"):
            self.validate(payload)

    def test_rejects_missing_reviewer_or_timezone(self):
        with self.assertRaisesRegex(ValueError, "reviewer identity is required"):
            self.validate(reviewer="  ")
        with self.assertRaisesRegex(ValueError, "explicit timezone"):
            self.validate(recorded_at="2026-11-22T10:30:00")

    def test_output_file_is_never_overwritten(self):
        result = self.validate()
        output = self.root / "review-audit.json"
        write_new_file(output, result)
        before = output.read_bytes()
        with self.assertRaises(FileExistsError):
            write_new_file(output, {"training_eligible": True})
        self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
