"""Security and integrity tests for local CVAT review-pack preparation."""
import csv
import hashlib
import json
import tempfile
import unittest
import zipfile
from unittest.mock import patch
from pathlib import Path

from training.class_schema import CLASS_NAMES
from training.stage_mobile_reviews import MANIFEST_NAME, stage
from scripts.prepare_cvat_review_pack import build_cvat_review_pack


def make_verified_queue(root: Path):
    image_dir = root / "images" / "velutina"
    image_dir.mkdir(parents=True)
    data = b"unchanged-original-cvat-review-fixture"
    image = image_dir / "101.jpg"
    image.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    source_url = "https://www.inaturalist.org/observations/202"
    manifest = {
        "photo_id": "101", "observation_id": "202",
        "species_candidate": "Vespa velutina", "source_url": source_url,
        "license": "CC0-1.0", "creator": "public-creator",
        "source_image_url": "https://static.inaturalist.org/photos/101/original.jpg",
        "local_image_path": "images/velutina/101.jpg",
        "image_format": "JPEG", "image_width": "1200", "image_height": "800",
        "image_bytes": str(len(data)), "sha256": digest,
        "download_status": "DOWNLOADED_UNMODIFIED",
    }
    with (root / MANIFEST_NAME).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(manifest))
        writer.writeheader()
        writer.writerow(manifest)
    mobile_payload = {
        "format": "vespaguard-unverified-mobile-review-v1",
        "species": "Vespa velutina",
        "records": [{
            "photo_id": "101", "observation_id": "202",
            "species_candidate": "Vespa velutina", "source_url": source_url,
            "image_url": "images/velutina/101.jpg",
            "license": "CC0-1.0", "creator": "public-creator",
            "training_eligible": False,
            "image_delivery": "LOCAL_UNMODIFIED_ORIGINAL",
            "original_sha256": digest, "original_file_bytes": len(data),
            "review": {"decision": "LIKELY", "boxes": [
                {"x": 0.5, "y": 0.5, "width": 0.2, "height": 0.3}
            ]},
        }],
    }
    return stage(mobile_payload, asset_root=root), image, digest, data


class CvatReviewPackTests(unittest.TestCase):
    def test_builds_image_only_pack_with_seven_unassigned_task_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "artifact"
            root.mkdir()
            queue, _, digest, original = make_verified_queue(root)
            output = Path(tmp) / "cvat-pack"
            result = build_cvat_review_pack(queue, root, output)

            self.assertEqual(result["images"], 1)
            self.assertEqual(result["source_bytes"], len(original))
            self.assertEqual(result["annotations_generated"], 0)
            self.assertEqual(result["yolo_label_files_generated"], 0)
            self.assertEqual(result["training_approved"], 0)

            with zipfile.ZipFile(output / "cvat-images.zip") as archive:
                self.assertEqual(archive.namelist(), ["101.jpg"])
                self.assertEqual(archive.read("101.jpg"), original)
            labels = json.loads((output / "labels.json").read_text(encoding="utf-8"))
            self.assertEqual([row["name"] for row in labels], list(CLASS_NAMES))
            with (output / "metadata.csv").open(newline="", encoding="utf-8") as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row["sha256"], digest)
            self.assertEqual(row["training_eligible"], "false")
            self.assertEqual(row["mobile_decision"], "LIKELY")

    def test_rejects_queue_that_grants_training_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "artifact"
            root.mkdir()
            queue, _, _, _ = make_verified_queue(root)
            queue["training_eligible"] = True
            with self.assertRaisesRegex(ValueError, "training_eligible=false"):
                build_cvat_review_pack(queue, root, Path(tmp) / "pack")

    def test_rejects_record_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "artifact"
            root.mkdir()
            queue, _, _, _ = make_verified_queue(root)
            queue["records"][0]["training_eligible"] = True
            with self.assertRaisesRegex(ValueError, "already marked training-eligible"):
                build_cvat_review_pack(queue, root, Path(tmp) / "pack")

    def test_rehashes_original_while_packaging(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "artifact"
            root.mkdir()
            queue, image, _, _ = make_verified_queue(root)
            import scripts.prepare_cvat_review_pack as module
            real_stage = module.stage

            def stage_then_tamper(payload, *, asset_root):
                verified = real_stage(payload, asset_root=asset_root)
                image.write_bytes(b"tampered-after-queue-staging")
                return verified

            with patch("scripts.prepare_cvat_review_pack.stage", side_effect=stage_then_tamper):
                with self.assertRaisesRegex(ValueError, "byte count changed|SHA-256 changed"):
                    build_cvat_review_pack(queue, root, Path(tmp) / "pack")
            self.assertFalse((Path(tmp) / "pack").exists())

    def test_resolves_symlinked_output_parent_before_containment_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "artifact"
            root.mkdir()
            queue, _, _, _ = make_verified_queue(root)
            link = Path(tmp) / "artifact-link"
            try:
                link.symlink_to(root, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"directory symlinks unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "outside the original-image"):
                build_cvat_review_pack(queue, root, link / "pack")

    def test_refuses_output_inside_source_asset_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "artifact"
            root.mkdir()
            queue, _, _, _ = make_verified_queue(root)
            with self.assertRaisesRegex(ValueError, "outside the original-image"):
                build_cvat_review_pack(queue, root, root / "cvat-pack")

    def test_refuses_to_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "artifact"
            root.mkdir()
            queue, _, _, _ = make_verified_queue(root)
            output = Path(tmp) / "pack"
            output.mkdir()
            with self.assertRaises(FileExistsError):
                build_cvat_review_pack(queue, root, output)


if __name__ == "__main__":
    unittest.main()
