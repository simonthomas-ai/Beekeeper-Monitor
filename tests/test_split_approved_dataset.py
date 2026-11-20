import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).resolve().parents[1] / "scripts/split_approved_dataset.py"
s = importlib.util.spec_from_file_location("split_approved_dataset", p)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)

def item(label, group, n):
    return {"suggested_class": label, "observation_group": group, "sha256": f"{n:064x}",
            "species_verified": True, "human_approved_for_training": True}

class SplitTests(unittest.TestCase):
    def dataset(self):
        return {"items": [item(label, f"{label}-site-{i}", k + 1)
                for k, (label, i) in enumerate((label, i) for label in ("velutina", "crabro") for i in range(10))]}
    def test_reproducible_and_disjoint(self):
        a = m.split_manifest(self.dataset(), 42)
        self.assertEqual(a, m.split_manifest(self.dataset(), 42))
        seen = set()
        for part in ("train", "val", "test"):
            groups = {x["observation_group"] for x in a["splits"][part]}
            self.assertFalse(seen & groups)
            seen |= groups
            self.assertTrue(a["splits"][part])
    def test_unapproved_rejected(self):
        data = self.dataset()
        data["items"][0]["human_approved_for_training"] = False
        with self.assertRaises(ValueError):
            m.split_manifest(data)
    def test_duplicate_rejected(self):
        data = self.dataset()
        data["items"][1]["sha256"] = data["items"][0]["sha256"]
        with self.assertRaises(ValueError):
            m.split_manifest(data)
    def test_canonical_class_mapping(self):
        result = m.split_manifest(self.dataset())
        self.assertEqual(set(result["counts"]["train"]), {"vespa_velutina", "vespa_crabro"})
    def test_cross_class_group_collision_rejected(self):
        data = self.dataset()
        data["items"][10]["observation_group"] = data["items"][0]["observation_group"]
        with self.assertRaises(ValueError):
            m.split_manifest(data)
    def test_unknown_class_rejected(self):
        data = self.dataset()
        data["items"][0]["suggested_class"] = "unrecognized"
        with self.assertRaises(ValueError):
            m.split_manifest(data)
    def test_insufficient_groups_rejected(self):
        with self.assertRaises(ValueError):
            m.split_manifest({"items": [item("velutina", "one", 1)]})

if __name__ == "__main__":
    unittest.main()
