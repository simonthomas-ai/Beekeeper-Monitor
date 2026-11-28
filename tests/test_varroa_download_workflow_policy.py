"""The Varroa candidate workflow must never fetch or publish real model bytes."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "varroa-verified-download.yml"


class VarroaDownloadWorkflowPolicyTests(unittest.TestCase):
    def test_candidate_workflow_runs_synthetic_tests_only(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("test_download_verified_varroa.py", workflow)
        self.assertIn("test_varroa_download_workflow_policy.py", workflow)
        self.assertIn("synthetic bytes only", workflow)
        for forbidden in (
            "scripts.download_verified_varroa",
            "raw.githubusercontent.com",
            "varroa-source.pt",
            "actions/upload-artifact@",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, workflow)


if __name__ == "__main__":
    unittest.main()
