"""Image-container and pixel-decoding checks for real training inputs.

Generated images in this module are disposable software fixtures only. They are
not insect photographs, species labels, or training samples.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from training.train import validate, validate_image_file, validate_checkpoint_rights_approval


class TrainingImageValidationTests(unittest.TestCase):
    def _save(self, root, name, image_format, size=(32, 24)):
        path = Path(root) / name
        Image.new("RGB", size, (120, 130, 140)).save(path, format=image_format)
        return path

    def test_valid_jpeg_and_png_are_fully_decoded(self):
        with tempfile.TemporaryDirectory() as tmp:
            jpeg = self._save(tmp, "frame.jpg", "JPEG")
            png = self._save(tmp, "frame.png", "PNG")
            self.assertEqual(validate_image_file(jpeg)["format"], "JPEG")
            self.assertEqual(validate_image_file(png)["format"], "PNG")

    def test_rejects_corrupt_image_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            corrupt = Path(tmp) / "broken.jpg"
            corrupt.write_bytes(b"not an image")
            with self.assertRaisesRegex(ValueError, "corrupt, unreadable or unsafe"):
                validate_image_file(corrupt)

    def test_rejects_extension_content_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            mislabeled = self._save(tmp, "actually-png.jpg", "PNG")
            with self.assertRaisesRegex(ValueError, "extension/content mismatch"):
                validate_image_file(mislabeled)

    def test_rejects_tiny_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            tiny = self._save(tmp, "tiny.png", "PNG", size=(8, 8))
            with self.assertRaisesRegex(ValueError, "dimensions are too small"):
                validate_image_file(tiny)


    def test_rejects_dataset_root_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            training = root / "training"
            training.mkdir()
            data_yaml = "\n".join([
                "path: datasets/beekeeper",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                "  0: vespa_velutina",
                "  1: vespa_crabro",
                "  2: other_vespidae",
                "  3: apis_mellifera",
                "  4: bombus_spp",
                "  5: syrphidae",
                "  6: other_insect",
            ]) + "\n"
            (training / "data.yaml").write_text(data_yaml, encoding="utf-8")
            actual = root / "actual-dataset"
            actual.mkdir()
            target = root / "datasets" / "beekeeper"
            target.parent.mkdir()
            try:
                target.symlink_to(actual, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symbolic links are unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "Dataset path must not contain symbolic links"):
                validate(root)

    def test_missing_real_dataset_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            training = root / "training"
            training.mkdir()
            (training / "data.yaml").write_text(
                "path: datasets/beekeeper\n"
                "train: images/train\n"
                "val: images/val\n"
                "test: images/test\n"
                "names:\n  0: vespa_velutina\n  1: vespa_crabro\n"
                "  2: other_vespidae\n  3: apis_mellifera\n"
                "  4: bombus_spp\n  5: syrphidae\n  6: other_insect\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(FileNotFoundError, "Real training dataset directory is missing"):
                validate(root)


class CheckpointRightsApprovalTests(unittest.TestCase):
    CHECKPOINT_SHA256 = "a" * 64
    SOURCE_URL = "https://example.invalid/checkpoint.pt"

    def _approval(self):
        return {
            "schema_version": 1,
            "status": "approved_for_training",
            "checkpoint_sha256": self.CHECKPOINT_SHA256,
            "source_url": self.SOURCE_URL,
            "spdx_license_expression": "AGPL-3.0-or-later",
            "license_evidence_sha256": "b" * 64,
            "training_use_permitted": True,
            "derivative_model_creation_permitted": True,
            "derivative_model_redistribution_permitted": False,
            "reviewer_id": "reviewer:test-reviewer-01",
            "reviewed_at": "2026-11-27",
            "evidence_reference": "https://example.invalid/licence-evidence-fixture-only",
        }

    def _write(self, root, approval=None):
        path = Path(root) / "training" / "checkpoint-rights-approvals" / "fixture.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(approval or self._approval()), encoding="utf-8")
        return "training/checkpoint-rights-approvals/fixture.json", path

    def test_accepts_only_matching_checkpoint_and_source_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            relative, path = self._write(tmp)
            result = validate_checkpoint_rights_approval(
                tmp, relative, self.CHECKPOINT_SHA256, self.SOURCE_URL
            )
            self.assertEqual(result["status"], "approved_for_training")
            self.assertEqual(result["approval_file_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_rejects_missing_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FileNotFoundError, "local checkpoint rights approval"):
                validate_checkpoint_rights_approval(
                    tmp, "training/checkpoint-rights-approvals/missing.json",
                    self.CHECKPOINT_SHA256, self.SOURCE_URL
                )

    def test_rejects_checkpoint_hash_or_source_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            relative, _ = self._write(tmp)
            with self.assertRaisesRegex(ValueError, "SHA-256 does not match"):
                validate_checkpoint_rights_approval(tmp, relative, "c" * 64, self.SOURCE_URL)
            with self.assertRaisesRegex(ValueError, "source URL does not match"):
                validate_checkpoint_rights_approval(
                    tmp, relative, self.CHECKPOINT_SHA256, "https://example.invalid/other.pt"
                )

    def test_rejects_unasserted_or_missing_license(self):
        for expression in ("NOASSERTION", "NONE", ""):
            with self.subTest(expression=expression), tempfile.TemporaryDirectory() as tmp:
                approval = self._approval()
                approval["spdx_license_expression"] = expression
                relative, _ = self._write(tmp, approval)
                with self.assertRaisesRegex(ValueError, "non-NOASSERTION licence expression"):
                    validate_checkpoint_rights_approval(
                        tmp, relative, self.CHECKPOINT_SHA256, self.SOURCE_URL
                    )

    def test_requires_training_and_derivative_creation_permission(self):
        for field in ("training_use_permitted", "derivative_model_creation_permitted"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                approval = self._approval()
                approval[field] = False
                relative, _ = self._write(tmp, approval)
                with self.assertRaisesRegex(ValueError, "explicitly permit"):
                    validate_checkpoint_rights_approval(
                        tmp, relative, self.CHECKPOINT_SHA256, self.SOURCE_URL
                    )

    def test_requires_explicit_redistribution_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            approval = self._approval()
            approval["derivative_model_redistribution_permitted"] = "unknown"
            relative, _ = self._write(tmp, approval)
            with self.assertRaisesRegex(ValueError, "redistribution permission"):
                validate_checkpoint_rights_approval(
                    tmp, relative, self.CHECKPOINT_SHA256, self.SOURCE_URL
                )

    def test_requires_pseudonymous_reviewer_date_and_evidence_hash(self):
        invalid_updates = (
            {"reviewer_id": "Simon"},
            {"reviewed_at": "27.11.2026"},
            {"reviewed_at": "2026-02-31"},
            {"license_evidence_sha256": "not-a-sha256"},
            {"evidence_reference": ""},
        )
        for update in invalid_updates:
            with self.subTest(update=update), tempfile.TemporaryDirectory() as tmp:
                approval = self._approval()
                approval.update(update)
                relative, _ = self._write(tmp, approval)
                with self.assertRaises(ValueError):
                    validate_checkpoint_rights_approval(
                        tmp, relative, self.CHECKPOINT_SHA256, self.SOURCE_URL
                    )

    def test_rejects_path_traversal_and_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "clean relative path"):
                validate_checkpoint_rights_approval(
                    tmp, "../approval.json", self.CHECKPOINT_SHA256, self.SOURCE_URL
                )
            relative, path = self._write(tmp)
            link = path.parent / "linked.json"
            try:
                link.symlink_to(path)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symbolic links are unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "symbolic links"):
                validate_checkpoint_rights_approval(
                    tmp, "training/checkpoint-rights-approvals/linked.json",
                    self.CHECKPOINT_SHA256, self.SOURCE_URL
                )

    def test_rejects_oversized_approval_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "training" / "checkpoint-rights-approvals" / "large.json"
            path.parent.mkdir(parents=True)
            path.write_text(" " * (64 * 1024 + 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "64 KiB"):
                validate_checkpoint_rights_approval(
                    tmp, "training/checkpoint-rights-approvals/large.json",
                    self.CHECKPOINT_SHA256, self.SOURCE_URL
                )


if __name__ == "__main__":
    unittest.main()
