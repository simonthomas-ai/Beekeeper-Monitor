"""Practical CSV audit tests: real files, no fabricated training approval."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("audit_inaturalist_candidates.py")
spec = importlib.util.spec_from_file_location("candidate_audit", MODULE)
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)

BASE = {
    "source_id": "inat:1:11", "source_url": "https://www.inaturalist.org/observations/1",
    "image_url": "https://example.org/photo1.jpg", "creator": "Photographer",
    "license": "CC0-1.0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    "attribution": "Photographer", "observation_id": "1", "photo_id": "11",
    "species_candidate": "Vespa velutina", "review_status": "UNREVIEWED",
}

class CandidateAuditTests(unittest.TestCase):
    def check_rows(self, rows):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.csv"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(BASE))
                writer.writeheader()
                writer.writerows(rows)
            return audit_module.audit(path)

    def test_valid_metadata_is_not_approved(self):
        report = self.check_rows([BASE])
        self.assertEqual(report["metadata_errors"], [])
        self.assertEqual(report["approved_training_images"], 0)
        self.assertTrue(report["requires_human_review"])

    def test_duplicate_image_url_detected(self):
        duplicate = dict(BASE, source_id="inat:2:22", observation_id="2", photo_id="22")
        report = self.check_rows([BASE, duplicate])
        self.assertEqual(report["candidates"], 2)
        self.assertTrue(any("duplicate_image_url" in item["errors"] for item in report["metadata_errors"]))

    def test_embedded_url_credentials_rejected(self):
        report = self.check_rows([dict(BASE, image_url="https://secret:token@example.org/a.jpg")])
        self.assertIn("invalid_image_url", report["metadata_errors"][0]["errors"])

    def test_cc_by_version_unverified_remains_unapproved(self):
        report = self.check_rows([dict(BASE, license="CC-BY-VERSION-UNVERIFIED", license_url="https://creativecommons.org/licenses/by/4.0/")])
        self.assertEqual(report["approved_training_images"], 0)
        self.assertTrue(report["requires_human_review"])

    def test_square_inaturalist_thumbnail_is_flagged(self):
        row = dict(BASE, image_url="https://inaturalist-open-data.s3.amazonaws.com/photos/11/square.jpg")
        report = self.check_rows([row])
        self.assertIn("non_original_inaturalist_image_variant", report["metadata_errors"][0]["errors"])

if __name__ == "__main__":
    unittest.main()
