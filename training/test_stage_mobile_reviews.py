import copy
import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from training.stage_mobile_reviews import MANIFEST_NAME, stage

SAMPLE = {
    "format": "vespaguard-unverified-mobile-review-v1",
    "species": "Vespa velutina",
    "records": [{
        "photo_id": "101", "observation_id": "202",
        "species_candidate": "Vespa velutina",
        "source_url": "https://www.inaturalist.org/observations/202",
        "image_url": "https://static.inaturalist.org/photos/101/medium.jpg",
        "license": "CC0-1.0", "creator": "observer",
        "training_eligible": False,
        "review": {"decision": "LIKELY", "boxes": [{"x": 0.5, "y": 0.5, "width": 0.2, "height": 0.3}]}
    }]
}


class MobileStageTests(unittest.TestCase):
    def test_likely_stays_unapproved(self):
        result = stage(copy.deepcopy(SAMPLE))
        self.assertFalse(result["training_eligible"])
        self.assertFalse(result["records"][0]["training_eligible"])
        self.assertEqual(result["records"][0]["mobile_decision"], "LIKELY")
        self.assertIn("verify_license_and_attribution", result["records"][0]["expert_checks_required"])

    def test_forged_training_approval_rejected(self):
        data = copy.deepcopy(SAMPLE)
        data["records"][0]["training_eligible"] = True
        with self.assertRaises(ValueError):
            stage(data)

    def test_out_of_bounds_box_rejected(self):
        data = copy.deepcopy(SAMPLE)
        data["records"][0]["review"]["boxes"][0]["x"] = 0.99
        with self.assertRaises(ValueError):
            stage(data)

    def test_duplicate_id_rejected(self):
        data = copy.deepcopy(SAMPLE)
        data["records"].append(copy.deepcopy(data["records"][0]))
        with self.assertRaises(ValueError):
            stage(data)

    def test_unknown_species_rejected(self):
        data = copy.deepcopy(SAMPLE)
        data["species"] = "Unverified species"
        with self.assertRaises(ValueError):
            stage(data)

    def test_pending_is_not_approved(self):
        data = copy.deepcopy(SAMPLE)
        data["records"][0]["review"] = {"decision": "PENDING", "boxes": []}
        self.assertFalse(stage(data)["records"][0]["training_eligible"])

    def _make_local_artifact(self, directory):
        root = Path(directory)
        image_dir = root / "images" / "velutina"
        image_dir.mkdir(parents=True)
        body = b"byte-preserved-original-image-for-test"
        image_path = image_dir / "101.jpg"
        image_path.write_bytes(body)
        digest = hashlib.sha256(body).hexdigest()
        row = {
            "photo_id": "101",
            "observation_id": "202",
            "species_candidate": "Vespa velutina",
            "source_url": SAMPLE["records"][0]["source_url"],
            "license": "CC0-1.0",
            "creator": "observer",
            "source_image_url": "https://static.inaturalist.org/photos/101/original.jpg",
            "local_image_path": "images/velutina/101.jpg",
            "image_format": "JPEG",
            "image_width": "1200",
            "image_height": "800",
            "image_bytes": str(len(body)),
            "sha256": digest,
            "download_status": "DOWNLOADED_UNMODIFIED",
        }
        with (root / MANIFEST_NAME).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)
        data = copy.deepcopy(SAMPLE)
        item = data["records"][0]
        item.update({
            "image_url": "images/velutina/101.jpg",
            "image_delivery": "LOCAL_UNMODIFIED_ORIGINAL",
            "original_sha256": digest,
            "original_file_bytes": len(body),
        })
        return data, root, image_path, digest

    def test_local_original_requires_artifact_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, _, _, _ = self._make_local_artifact(tmp)
            with self.assertRaisesRegex(ValueError, "--asset-root"):
                stage(data)

    def test_accepts_manifest_verified_local_original_without_approving_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, root, _, digest = self._make_local_artifact(tmp)
            result = stage(data, asset_root=root)
            record = result["records"][0]
            self.assertFalse(result["training_eligible"])
            self.assertFalse(record["training_eligible"])
            self.assertEqual(record["image_delivery"], "LOCAL_UNMODIFIED_ORIGINAL")
            self.assertEqual(record["original_sha256"], digest)
            self.assertIn("verify_boxes_against_image", record["expert_checks_required"])

    def test_rejects_tampered_local_original_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, root, image_path, _ = self._make_local_artifact(tmp)
            image_path.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "byte count differs|SHA-256 differs"):
                stage(data, asset_root=root)

    def test_rejects_mobile_sha_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, root, _, _ = self._make_local_artifact(tmp)
            data["records"][0]["original_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "SHA-256 differs from the manifest"):
                stage(data, asset_root=root)

    def test_rejects_manifest_path_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, root, _, _ = self._make_local_artifact(tmp)
            data["records"][0]["image_url"] = "images/velutina/102.jpg"
            with self.assertRaises(ValueError):
                stage(data, asset_root=root)

    def test_rejects_symlinked_local_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            data, root, image_path, _ = self._make_local_artifact(tmp)
            target = image_path.with_name("real-original.jpg")
            image_path.rename(target)
            try:
                image_path.symlink_to(target.name)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "symbolic link"):
                stage(data, asset_root=root)