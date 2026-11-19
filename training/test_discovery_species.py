import unittest
from discover_inaturalist_candidates import SPECIES, LICENSES

class SpeciesTest(unittest.TestCase):
    def test_target_groups(self):
        for name in ("Vespa velutina", "Vespa crabro", "Vespula vulgaris", "Vespula germanica", "Apis mellifera", "Bombus terrestris", "Bombus lapidarius"):
            self.assertIn(name, SPECIES)
        self.assertEqual(len(SPECIES), len(set(SPECIES)))

    def test_unverified_license(self):
        self.assertEqual(LICENSES["cc-by"][0], "CC-BY-VERSION-UNVERIFIED")

if __name__ == "__main__":
    unittest.main()
