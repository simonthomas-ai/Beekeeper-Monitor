"""Regression tests for local-original gallery and Pages publication checks."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_gallery_rights import AuditError, audit


class GalleryRightsAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.review = self.root / "review"
        self.review.mkdir()
        self.image_dir = self.review / "images" / "velutina"
        self.image_dir.mkdir(parents=True)
        self.body = b"unchanged original image bytes for regression test"
        self.image = self.image_dir / "42.jpg"
        self.image.write_bytes(self.body)
        self.sha = hashlib.sha256(self.body).hexdigest()
        self.asset = {
            "photo_id": "42",
            "observation_id": "99",
            "species_candidate": "Vespa velutina",
            "source_url": "https://www.inaturalist.org/observations/99",
            "license": "CC0-1.0",
            "creator": "Example photographer",
            "creator_login": "example-photographer",
            "attribution": "Example photographer, no rights reserved (CC0)",
            "license_notice": "no rights reserved",
            "source_image_url": "https://static.inaturalist.org/photos/42/original.jpg",
            "local_image_path": "images/velutina/42.jpg",
            "image_format": "JPEG",
            "image_width": "1920",
            "image_height": "1080",
            "image_bytes": str(len(self.body)),
            "sha256": self.sha,
            "download_status": "DOWNLOADED_UNMODIFIED",
        }
        self.local_item = {
            "photo_id": "42",
            "observation_id": "99",
            "species_candidate": "Vespa velutina",
            "dataset_group": "asian_hornet",
            "image_url": "images/velutina/42.jpg",
            "source_url": self.asset["source_url"],
            "license": "CC0-1.0",
            "creator": "Example photographer",
            "creator_login": "example-photographer",
            "attribution": "Example photographer, no rights reserved (CC0)",
            "license_notice": "no rights reserved",
            "image_width": 1920,
            "image_height": 1080,
            "image_bytes": len(self.body),
            "original_sha256": self.sha,
            "original_file_bytes": len(self.body),
            "original_file_format": "JPEG",
            "image_delivery": "LOCAL_UNMODIFIED_ORIGINAL",
        }
        self._write_manifest([self.asset])
        self._write_galleries()

    def _write_manifest(self, rows):
        path = self.review / "velutina-original-images-manifest.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(self.asset))
            writer.writeheader()
            writer.writerows(rows)

    def _write_galleries(self, velutina_items=None, all_items=None):
        pages = {
            "all": self.local_items() if all_items is None else all_items,
            "velutina": self.local_items() if velutina_items is None else velutina_items,
            "crabro": [],
            "apis": [],
            "bombus": [],
            "vespula": [],
        }
        for name, items in pages.items():
            (self.review / f"{name}.html").write_text(
                "<!doctype html><script>const items=" + json.dumps(items) + ";</script>",
                encoding="utf-8",
            )

    def local_items(self):
        return [dict(self.local_item)]

    def test_accepts_local_original_when_manifest_and_bytes_match(self):
        self.assertEqual(audit(self.root), (6, 2))

    def test_rejects_symlinked_original_file(self):
        self.image.unlink()
        real_file = self.image_dir / "42.real.jpg"
        real_file.write_bytes(self.body)
        self.image.symlink_to(real_file.name)
        with self.assertRaisesRegex(AuditError, "symbolic link is not allowed"):
            audit(self.root)

    def test_rejects_modified_original_bytes(self):
        self.image.write_bytes(self.body + b"tampered")
        with self.assertRaisesRegex(AuditError, "byte count differs"):
            audit(self.root)

    def test_rejects_same_size_hash_mismatch(self):
        self.image.write_bytes(b"x" * len(self.body))
        with self.assertRaisesRegex(AuditError, "SHA-256 differs"):
            audit(self.root)

    def test_rejects_path_traversal(self):
        self.asset["local_image_path"] = "images/velutina/../../secret.jpg"
        self._write_manifest([self.asset])
        self.local_item["image_url"] = self.asset["local_image_path"]
        self._write_galleries()
        with self.assertRaisesRegex(AuditError, "approved images/velutina layout"):
            audit(self.root)

    def test_rejects_gallery_manifest_metadata_mismatch(self):
        item = self.local_items()[0]
        item["creator"] = "Different author"
        self._write_galleries([item], [item])
        with self.assertRaisesRegex(AuditError, "creator differs from manifest"):
            audit(self.root)

    def test_rejects_missing_local_asset(self):
        self.image.unlink()
        with self.assertRaisesRegex(AuditError, "original image missing"):
            audit(self.root)

    def test_rejects_gallery_missing_local_delivery_marker(self):
        item = self.local_items()[0]
        item.pop("image_delivery")
        self._write_galleries([item], [item])
        with self.assertRaisesRegex(AuditError, "lacks explicit local-original"):
            audit(self.root)

    def test_rejects_missing_all_gallery_reference(self):
        self._write_galleries(all_items=[])
        with self.assertRaisesRegex(AuditError, "all gallery and manifest differ"):
            audit(self.root)

    def test_accepts_remote_species_original_with_local_velutina_manifest(self):
        remote_item = {
            "photo_id": "51", "observation_id": "101",
            "species_candidate": "Vespa crabro", "dataset_group": "european_hornet",
            "image_url": "https://static.inaturalist.org/photos/51/original.jpg",
            "source_url": "https://www.inaturalist.org/observations/101",
            "license": "CC0-1.0", "creator": "Author",
            "creator_login": "author-login",
            "attribution": "Author, no rights reserved (CC0)",
            "license_notice": "no rights reserved",
            "image_delivery": "REMOTE_INATURALIST_ORIGINAL",
        }
        self._write_galleries(
            all_items=self.local_items() + [remote_item],
        )
        crabro = self.review / "crabro.html"
        crabro.write_text(
            "<script>const items=" + json.dumps([remote_item]) + ";</script>",
            encoding="utf-8",
        )
        self.assertEqual(audit(self.root), (6, 4))


    def test_rejects_remote_inaturalist_thumbnail(self):
        remote_item = {
            "photo_id": "51", "observation_id": "101",
            "image_url": "https://static.inaturalist.org/photos/51/square.jpg",
            "source_url": "https://www.inaturalist.org/observations/101",
            "license": "CC-BY-4.0", "creator": "Author",
            "image_delivery": "REMOTE_INATURALIST_ORIGINAL",
        }
        self._write_galleries(all_items=self.local_items() + [remote_item])
        (self.review / "crabro.html").write_text(
            "<script>const items=" + json.dumps([remote_item]) + ";</script>", encoding="utf-8")
        with self.assertRaisesRegex(AuditError, "original derivative"):
            audit(self.root)

    def test_rejects_velutina_remote_fallback(self):
        remote_item = {
            "photo_id": "51", "observation_id": "101",
            "species_candidate": "Vespa velutina", "dataset_group": "asian_hornet",
            "image_url": "https://static.inaturalist.org/photos/51/original.jpg",
            "source_url": "https://www.inaturalist.org/observations/101",
            "license": "CC0-1.0", "creator": "Author",
            "creator_login": "author-login",
            "attribution": "Author, no rights reserved (CC0)",
            "license_notice": "no rights reserved",
            "image_delivery": "REMOTE_INATURALIST_ORIGINAL",
        }
        self._write_galleries([remote_item], [remote_item])
        with self.assertRaisesRegex(AuditError, "remote fallback is forbidden"):
            audit(self.root)

    def test_rejects_manifest_with_wrong_photo_url_host(self):
        self.asset["source_image_url"] = "https://evil.example/photos/42/original.jpg"
        self._write_manifest([self.asset])
        with self.assertRaisesRegex(AuditError, "invalid iNaturalist original-image URL"):
            audit(self.root)


    def test_rejects_unmanifested_extra_image(self):
        (self.image_dir / "999.jpg").write_bytes(b"unlisted")
        with self.assertRaisesRegex(AuditError, "unmanifested or missing files"):
            audit(self.root)

    def test_rejects_creator_field_that_contains_only_licence_notice(self):
        self.asset["creator"] = "no rights reserved"
        self._write_manifest([self.asset])
        with self.assertRaisesRegex(AuditError, "photographer/observer identity"):
            audit(self.root)

    def test_rejects_gallery_resolution_metadata_mismatch(self):
        item = self.local_items()[0]
        item["image_width"] = 640
        self._write_galleries([item], [item])
        with self.assertRaisesRegex(AuditError, "image_width differs from manifest"):
            audit(self.root)

if __name__ == "__main__":
    unittest.main()
