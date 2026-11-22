"""Unit tests for the real-gallery-to-mobile-stager integration helper."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.verify_mobile_original_stager import verify_mobile_original_gallery


class MobileOriginalIntegrationTests(unittest.TestCase):
    def test_rejects_wrong_expected_record_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gallery = root / "velutina.html"
            gallery.write_text("const items=[];", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "expected exactly"):
                verify_mobile_original_gallery(gallery, root, expected_count=1)

    def test_rejects_gallery_with_non_json_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gallery = root / "velutina.html"
            gallery.write_text("const items=[not-json];", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not valid JSON"):
                verify_mobile_original_gallery(gallery, root, expected_count=1)


if __name__ == "__main__":
    unittest.main()
