"""Offline regression tests for the CC0 discovery/audit schema contract."""
import csv
import tempfile
import unittest
from pathlib import Path

from training.audit_cc0_candidates import FIELDS, audit
from training.discover_cc0_candidates import FIELDS as DISCOVERY_FIELDS

BASE = {
    "source_id": "inat-photo-11",
    "source_url": "https://www.inaturalist.org/observations/1",
    "image_url": "https://static.inaturalist.org/photos/11/original.jpg",
    "creator": "Test Observer",
    "creator_login": "test-observer",
    "license": "CC0-1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    "license_notice": "no rights reserved",
    "attribution": "Test Observer, no rights reserved (CC0)",
    "observation_id": "1",
    "photo_id": "11",
    "species_candidate": "Vespa velutina",
    "dataset_group": "asian_hornet",
    "review_status": "UNREVIEWED",
}


class CC0CandidateAuditTests(unittest.TestCase):
    def write_rows(self, rows, fields=FIELDS):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "candidates.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_audit_schema_is_the_discovery_schema(self):
        self.assertEqual(tuple(FIELDS), tuple(DISCOVERY_FIELDS))

    def test_valid_metadata_passes_but_never_approves_training(self):
        report = audit(self.write_rows([BASE]))
        self.assertEqual(report["status"], "metadata_passed_human_review_required")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["total"], 1)
        self.assertEqual(report["approved"], 0)

    def test_rejects_unexpected_or_stale_csv_columns(self):
        report = audit(self.write_rows([BASE], fields=FIELDS[:-1]))
        self.assertEqual(report["status"], "blocked")
        self.assertIn("Unexpected CSV columns", report["errors"])

    def test_rejects_missing_creator_identity(self):
        row = dict(BASE, creator_login="")
        report = audit(self.write_rows([row]))
        self.assertTrue(any("creator login" in error for error in report["errors"]))

    def test_rejects_dataset_group_species_mismatch(self):
        row = dict(BASE, dataset_group="honey_bee")
        report = audit(self.write_rows([row]))
        self.assertTrue(any("dataset group/species mismatch" in error for error in report["errors"]))

    def test_rejects_unreviewed_status_changes(self):
        row = dict(BASE, review_status="APPROVED")
        report = audit(self.write_rows([row]))
        self.assertTrue(any("invalid review status" in error for error in report["errors"]))
        self.assertEqual(report["approved"], 0)

    def test_rejects_image_url_with_query_or_fragment(self):
        row = dict(BASE, image_url="https://static.inaturalist.org/photos/11/original.jpg?token=x")
        report = audit(self.write_rows([row]))
        self.assertTrue(any("unsafe image URL" in error for error in report["errors"]))

    def test_rejects_untrusted_image_host(self):
        row = dict(BASE, image_url="https://example.org/photos/11/original.jpg")
        report = audit(self.write_rows([row]))
        self.assertTrue(any("unsafe image URL" in error for error in report["errors"]))

    def test_rejects_photo_id_mismatch_in_original_url(self):
        row = dict(BASE, image_url="https://static.inaturalist.org/photos/12/original.jpg")
        report = audit(self.write_rows([row]))
        self.assertTrue(any("matching original photo" in error for error in report["errors"]))

    def test_rejects_duplicate_photo_and_observation(self):
        report = audit(self.write_rows([BASE, BASE]))
        self.assertTrue(any("duplicate photo" in error for error in report["errors"]))
        self.assertTrue(any("duplicate observation" in error for error in report["errors"]))

    def test_empty_queue_is_blocked(self):
        report = audit(self.write_rows([]))
        self.assertEqual(report["status"], "blocked")
        self.assertIn("No candidate records", report["errors"])


if __name__ == "__main__":
    unittest.main()
