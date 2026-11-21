"""Image-container and pixel-decoding checks for real training inputs.

Generated images in this module are disposable software fixtures only. They are
not insect photographs, species labels, or training samples.
"""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from training.train import validate, validate_image_file


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
            (training / "data.yaml").write_text(
                "path: datasets/beekeeper\\n"
                "train: images/train\\n"
                "val: images/val\\n"
                "test: images/test\\n"
                "names:\\n  0: vespa_velutina\\n  1: vespa_crabro\\n"
                "  2: other_vespidae\\n  3: apis_mellifera\\n"
                "  4: bombus_spp\\n  5: syrphidae\\n  6: other_insect\\n",
                encoding="utf-8",
            )
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


if __name__ == "__main__":
    unittest.main()
