"""Regression tests for apiary module activation guard."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from scripts.apiary_module_registry import ModuleNotReady, validate_manifest

class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.weights = Path(self.tmp.name) / "weights.onnx"
        self.weights.write_bytes(b"synthetic test bytes, not a model")
        self.manifest = {
            "schema": "vespaguard.apiary-module.v1",
            "id": "queen_on_comb", "enabled": False,
            "release_status": "research_only",
            "human_confirmation_required": True,
            "weights_sha256": hashlib.sha256(self.weights.read_bytes()).hexdigest(),
            "weights_license": "example license; not a grant",
            "training_data_evidence": "test-only",
            "independent_validation_evidence": "test-only",
            "hardware_acceptance_evidence": "test-only",
        }
    def test_disabled_by_default(self):
        with self.assertRaises(ModuleNotReady):
            validate_manifest(self.manifest, weights_path=self.weights)
    def test_missing_evidence_rejected(self):
        self.manifest.update(enabled=True, release_status="field_approved")
        self.manifest["independent_validation_evidence"] = ""
        with self.assertRaises(ModuleNotReady):
            validate_manifest(self.manifest, weights_path=self.weights)
    def test_missing_weights_rejected(self):
        self.manifest.update(enabled=True, release_status="field_approved")
        with self.assertRaises(ModuleNotReady):
            validate_manifest(self.manifest)
    def test_tampered_weights_rejected(self):
        self.manifest.update(enabled=True, release_status="field_approved")
        self.weights.write_bytes(b"tampered")
        with self.assertRaises(ModuleNotReady):
            validate_manifest(self.manifest, weights_path=self.weights)
    def test_unknown_module_rejected(self):
        self.manifest.update(enabled=True, release_status="field_approved", id="unknown")
        with self.assertRaises(ModuleNotReady):
            validate_manifest(self.manifest, weights_path=self.weights)
    def test_structural_evidence_not_approval(self):
        self.manifest.update(enabled=True, release_status="field_approved")
        result = validate_manifest(self.manifest, weights_path=self.weights)
        self.assertEqual(result["status"], "evidence_present_not_independently_verified")

if __name__ == "__main__":
    unittest.main()
