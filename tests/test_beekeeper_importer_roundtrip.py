import importlib.util
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path


VALIDATOR_PATH = os.environ.get("BEEKEEPER_MULTILABEL_VALIDATOR")
if VALIDATOR_PATH:
    spec = importlib.util.spec_from_file_location("beekeeper_multilabel_dataset", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("BEEKEEPER_MULTILABEL_VALIDATOR is not importable")
    beekeeper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(beekeeper)
else:
    beekeeper = None


@unittest.skipUnless(beekeeper, "Set BEEKEEPER_MULTILABEL_VALIDATOR to the BeeKeeper branch validator path")
class BeeKeeperImporterRoundTripTests(unittest.TestCase):
    def test_multi_label_and_negative_export_fixture(self):
        rows = [
            {
                "image": "images/velutina-bee.jpg",
                "labels": ["vespa_velutina", "apis_mellifera"],
                "captured_at": "2026-11-23T08:00:00+01:00",
                "capture_session_id": "capture-session-pseudonym",
                "labeler_id": "reviewer:field-0001",
                "review_status": "approved",
                "reviewed_by": "reviewer:field-reviewer-0001",
                "reviewed_at": "2026-11-23T08:30:00+01:00",
                "rights": {
                    "source": "Eigene Feldaufnahme",
                    "basis": "LicenseRef-ExplicitPermission",
                    "permission_ref": "field-consent-fixture-001",
                    "status": "training_approved",
                },
            },
            {
                "image": "images/negative.jpg",
                "labels": [],
                "captured_at": "2026-11-23T08:05:00+01:00",
                "capture_session_id": "capture-session-pseudonym",
                "review_status": "approved",
                "reviewed_by": "reviewer:field-reviewer-0001",
                "reviewed_at": "2026-11-23T08:35:00+01:00",
                "rights": {
                    "source": "https://example.org/photos/negative",
                    "basis": "CC-BY-4.0",
                    "evidence_url": "https://creativecommons.org/licenses/by/4.0/",
                    "attribution": "Example photographer (CC BY 4.0)",
                    "status": "training_approved",
                },
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "field-dataset.zip"
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for row, image_bytes in zip(rows, (b"positive image bytes", b"negative image bytes")):
                    archive.writestr(row["image"], image_bytes)
                archive.writestr(
                    "annotations.jsonl",
                    "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                )
            accepted = beekeeper.validate_dataset_archive(archive_path)
        self.assertEqual(len(accepted), 2)
        self.assertEqual(accepted[0]["labels"], ["vespa_velutina", "apis_mellifera"])
        self.assertEqual(accepted[1]["labels"], [])


if __name__ == "__main__":
    unittest.main()
