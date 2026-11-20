import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from training.provenance import DatasetProvenanceError, validate_provenance


class ProvenanceTests(unittest.TestCase):
    def _dataset(self, root):
        root = Path(root)
        rows = []
        for split in ("train", "val", "test"):
            target = root / "images" / split / (split + ".jpg")
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = ("synthetic test bytes " + split).encode()
            target.write_bytes(payload)
            row = {
                "image_path": "images/%s/%s.jpg" % (split, split),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "source_url": "https://example.org/source/" + split,
                "source_dataset": "test-dataset",
                "source_version": "1",
                "license_spdx": "CC0-1.0",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "creator": "",
                "attribution_text": "",
                "downloaded_at": "2026-11-20T00:00:00Z",
                "observation_group": "obs-" + split,
                "photographer_group": "photo-" + split,
                "site_group": "site-" + split,
                "species_review_status": "verified",
                "bbox_review_status": "verified",
                "reviewer_id": "reviewer-test",
                "reviewed_at": "2026-11-20T00:00:00Z",
            }
            rows.append(row)
        (root / "provenance.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
        )
        return root, rows

    def test_valid_cc0_records_across_all_splits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            report = validate_provenance(root)
            self.assertEqual(report["images"], 3)
            self.assertEqual(report["by_split"], {"test": 1, "train": 1, "val": 1})

    def test_cc_by_requires_creator_and_attribution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            rows[0]["license_spdx"] = "CC-BY-4.0"
            rows[0]["license_url"] = "https://creativecommons.org/licenses/by/4.0/"
            rows[0]["creator"] = ""
            rows[0]["attribution_text"] = ""
            (root / "provenance.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
            )
            with self.assertRaises(DatasetProvenanceError):
                validate_provenance(root)

    def test_rejects_noncommercial_and_unreviewed_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            rows[0]["license_spdx"] = "CC-BY-NC-4.0"
            (root / "provenance.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
            )
            with self.assertRaises(DatasetProvenanceError):
                validate_provenance(root)

    def test_rejects_hash_mismatch_and_duplicate_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            rows[0]["sha256"] = "0" * 64
            (root / "provenance.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
            )
            with self.assertRaises(DatasetProvenanceError):
                validate_provenance(root)
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            rows[1]["sha256"] = rows[0]["sha256"]
            (root / "provenance.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
            )
            with self.assertRaises(DatasetProvenanceError):
                validate_provenance(root)

    def test_rejects_group_leakage_across_splits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            rows[1]["photographer_group"] = rows[0]["photographer_group"]
            (root / "provenance.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
            )
            with self.assertRaises(DatasetProvenanceError):
                validate_provenance(root)

    def test_rejects_unverified_labels_and_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            rows[2]["bbox_review_status"] = "automatic"
            (root / "provenance.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
            )
            with self.assertRaises(DatasetProvenanceError):
                validate_provenance(root)
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            rows[0]["image_path"] = "../outside.jpg"
            (root / "provenance.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
            )
            with self.assertRaises(DatasetProvenanceError):
                validate_provenance(root)


if __name__ == "__main__":
    unittest.main()
