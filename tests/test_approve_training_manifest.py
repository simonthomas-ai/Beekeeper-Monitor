import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "scripts/approve_training_manifest.py"
spec = importlib.util.spec_from_file_location("approve_training_manifest", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ApprovalTests(unittest.TestCase):
    def item(self):
        return {"suggested_class": "velutina", "species_verified": True,
                "human_approved_for_training": True, "reviewer": "Expert", "reviewed_at": "2026-11-21",
                "license": "CC BY 4.0", "source_page": "https://commons.wikimedia.org/wiki/File:Example.jpg",
                "sha256": "a" * 64, "local_file": "example.jpg"}
    def test_approved(self):
        a, r = mod.validate({"items": [self.item()]})
        self.assertEqual((len(a), len(r)), (1, 0))
    def test_no_auto_approval(self):
        x = self.item()
        x["human_approved_for_training"] = False
        a, r = mod.validate({"items": [x]})
        self.assertEqual((len(a), len(r)), (0, 1))
    def test_reject_unsafe_license(self):
        x = self.item()
        x["license"] = "CC BY-NC 4.0"
        self.assertEqual(len(mod.validate({"items": [x]})[0]), 0)
    def test_duplicate(self):
        x = self.item()
        a, r = mod.validate({"items": [x, x.copy()]})
        self.assertEqual((len(a), len(r)), (1, 1))
    def test_path_traversal(self):
        x = self.item()
        x["local_file"] = "../../secret.jpg"
        self.assertEqual(len(mod.validate({"items": [x]})[0]), 0)

if __name__ == "__main__":
    unittest.main()
