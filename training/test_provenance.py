import hashlib
import json
import os
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
            label_target = root / "labels" / split / (split + ".txt")
            label_target.parent.mkdir(parents=True, exist_ok=True)
            label_payload = b"0 0.5 0.5 0.2 0.2\n"
            label_target.write_bytes(label_payload)
            row = {
                "image_path": "images/%s/%s.jpg" % (split, split),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "label_path": "labels/%s/%s.txt" % (split, split),
                "label_sha256": hashlib.sha256(label_payload).hexdigest(),
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

    def test_rejects_image_missing_from_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            extra = root / "images" / "train" / "not-in-manifest.jpg"
            extra.write_bytes(b"orphan image")
            with self.assertRaises(DatasetProvenanceError):
                validate_provenance(root)

    def test_rejects_label_file_changed_after_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            label = root / rows[0]["label_path"]
            label.write_text("0 0.25 0.25 0.1 0.1\n", encoding="utf-8")
            with self.assertRaisesRegex(DatasetProvenanceError, "label SHA-256 mismatch"):
                validate_provenance(root)

    def test_rejects_wrong_label_path_and_unmanifested_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            rows[0]["label_path"] = "labels/val/train.txt"
            (root / "provenance.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(DatasetProvenanceError, "label_path must match"):
                validate_provenance(root)
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            extra = root / "labels" / "train" / "orphan.txt"
            extra.write_text("0 0.5 0.5 0.1 0.1\n", encoding="utf-8")
            with self.assertRaisesRegex(DatasetProvenanceError, "bind every YOLO label"):
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


    def test_rejects_dataset_root_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            actual = parent / "actual-dataset"
            actual.mkdir()
            self._dataset(actual)
            alias = parent / "dataset-alias"
            try:
                alias.symlink_to(actual, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symbolic links are unavailable: {exc}")
            with self.assertRaisesRegex(DatasetProvenanceError, "dataset root path must not contain symbolic links"):
                validate_provenance(alias)

    def test_rejects_symlinked_parent_of_dataset_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            actual_parent = parent / "real-parent"
            actual_parent.mkdir()
            actual = actual_parent / "dataset"
            actual.mkdir()
            self._dataset(actual)
            alias_parent = parent / "alias-parent"
            try:
                alias_parent.symlink_to(actual_parent, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symbolic links are unavailable: {exc}")
            with self.assertRaisesRegex(DatasetProvenanceError, "dataset root path must not contain symbolic links"):
                validate_provenance(alias_parent / "dataset")

    def test_rejects_symlinked_image_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            image = root / rows[0]["image_path"]
            target = root / "external-image.jpg"
            target.write_bytes(image.read_bytes())
            image.unlink()
            try:
                image.symlink_to(target)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symbolic links are unavailable: {exc}")
            with self.assertRaisesRegex(DatasetProvenanceError, "symbolic links"):
                validate_provenance(root)

    def test_rejects_symlinked_label_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, rows = self._dataset(tmp)
            label = root / rows[0]["label_path"]
            target = root / "external-label.txt"
            target.write_bytes(label.read_bytes())
            label.unlink()
            try:
                label.symlink_to(target)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symbolic links are unavailable: {exc}")
            with self.assertRaisesRegex(DatasetProvenanceError, "symbolic links"):
                validate_provenance(root)

if __name__ == "__main__":
    unittest.main()
