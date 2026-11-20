import unittest
from scripts.varroa_export_readiness import assess


class ExportReadinessTests(unittest.TestCase):
    def test_verified_source_alone_does_not_authorize_export(self):
        result = assess({"source_blob_verified": True, "local_sha256": "a" * 64})
        self.assertTrue(result["checks"]["source_integrity_verified"])
        self.assertFalse(result["ready_for_manual_security_and_legal_review"])
        self.assertFalse(result["automatic_export_authorized"])
        self.assertFalse(result["field_approved"])

    def test_fake_boolean_values_fail_closed(self):
        result = assess({"source_blob_verified": "true", "local_sha256": "a" * 64},
                        rights_evidence="document", isolated_environment_evidence="document")
        self.assertFalse(result["checks"]["source_integrity_verified"])
        self.assertFalse(result["ready_for_manual_security_and_legal_review"])

    def test_review_material_is_not_approval(self):
        result = assess({"source_blob_verified": True, "local_sha256": "a" * 64},
                        rights_evidence="pending counsel review", isolated_environment_evidence="sandbox design")
        self.assertTrue(result["ready_for_manual_security_and_legal_review"])
        self.assertFalse(result["automatic_export_authorized"])
        self.assertFalse(result["field_approved"])
        self.assertFalse(result["independent_model_validation_complete"])


if __name__ == "__main__":
    unittest.main()
