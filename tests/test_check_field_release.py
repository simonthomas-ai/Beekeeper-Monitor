"""Fail-closed tests for the real field-release evidence gate."""
import contextlib
import io
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from scripts import check_field_release as gate


def valid_manifest():
    return {
        "gates": {
            key: {
                "evidence_url": f"https://example.org/evidence/{key}",
                "reviewer": "independent-reviewer",
                "approved": True,
                "approved_on": date.today().isoformat(),
            }
            for key in gate.REQUIRED
        }
    }


class FieldReleaseEvidenceTests(unittest.TestCase):
    def run_with_manifest(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "field-acceptance.json"
            evidence.write_text(json.dumps(payload), encoding="utf-8")
            output = io.StringIO()
            with patch.object(gate, "EVIDENCE", evidence), contextlib.redirect_stdout(output):
                result = gate.main()
            return result, output.getvalue()

    def test_missing_manifest_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "missing.json"
            output = io.StringIO()
            with patch.object(gate, "EVIDENCE", evidence), contextlib.redirect_stdout(output):
                result = gate.main()
        self.assertEqual(result, 1)
        self.assertIn("Software CI success is not field approval", output.getvalue())

    def test_malformed_json_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "field-acceptance.json"
            evidence.write_text("{broken", encoding="utf-8")
            output = io.StringIO()
            with patch.object(gate, "EVIDENCE", evidence), contextlib.redirect_stdout(output):
                result = gate.main()
        self.assertEqual(result, 1)
        self.assertIn("invalid evidence manifest", output.getvalue())

    def test_non_object_root_blocks_without_exception(self):
        result, output = self.run_with_manifest([])
        self.assertEqual(result, 1)
        self.assertIn("root must be a JSON object", output)

    def test_missing_gates_blocks(self):
        result, output = self.run_with_manifest({})
        self.assertEqual(result, 1)
        self.assertIn("gates must be an object", output)

    def test_complete_manifest_still_requires_human_verification(self):
        result, output = self.run_with_manifest(valid_manifest())
        self.assertEqual(result, 0)
        self.assertIn("human verification of linked evidence is still required", output)

    def test_non_public_or_secret_bearing_urls_block(self):
        invalid_urls = (
            "http://example.org/evidence",
            "https://user:password@example.org/evidence",
            "https://example.org/evidence?token=secret",
            "https://example.org/evidence#section",
            "https://localhost/evidence",
            "https://station.local/evidence",
            "https://127.0.0.1/evidence",
            "https://192.168.1.10/evidence",
            "https://[::1]/evidence",
            "https://[fe80::1%25eth0]/evidence",
            "https://bad host/evidence",
            "https://example.org:invalid/evidence",
        )
        for url in invalid_urls:
            with self.subTest(url=url):
                manifest = valid_manifest()
                manifest["gates"]["dataset_rights"]["evidence_url"] = url
                result, output = self.run_with_manifest(manifest)
                self.assertEqual(result, 1)
                self.assertIn("external HTTPS URL", output)

    def test_blank_reviewer_and_non_boolean_approval_block(self):
        manifest = valid_manifest()
        manifest["gates"]["model_validation"]["reviewer"] = "   "
        manifest["gates"]["model_validation"]["approved"] = "true"
        result, output = self.run_with_manifest(manifest)
        self.assertEqual(result, 1)
        self.assertIn("model_validation: explicit reviewer approval missing", output)

    def test_future_and_invalid_approval_dates_block(self):
        manifest = valid_manifest()
        manifest["gates"]["dataset_rights"]["approved_on"] = "9999-12-31"
        manifest["gates"]["model_validation"]["approved_on"] = "not-a-date"
        result, output = self.run_with_manifest(manifest)
        self.assertEqual(result, 1)
        self.assertIn("dataset_rights: approval date is in the future", output)
        self.assertIn("model_validation: valid ISO approval date missing", output)

    def test_local_and_secret_bearing_urls_are_rejected_directly(self):
        self.assertTrue(gate.valid_evidence_url("https://example.org/evidence"))
        self.assertFalse(gate.valid_evidence_url("https://example.org/evidence?access_token=x"))
        self.assertFalse(gate.valid_evidence_url("https://user@example.org/evidence"))
        self.assertFalse(gate.valid_evidence_url("https://10.0.0.1/evidence"))


if __name__ == "__main__":
    unittest.main()
