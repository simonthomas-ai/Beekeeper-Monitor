"""The Varroa candidate workflow must never fetch or publish real model bytes."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "varroa-verified-download.yml"
PINNED_CHECKOUT = "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
EXPECTED_RUNS = [
    "python3 -m unittest discover -s tests -p test_download_verified_varroa.py -v",
    "python3 -m unittest discover -s tests -p test_varroa_download_workflow_policy.py -v",
]


class VarroaDownloadWorkflowPolicyTests(unittest.TestCase):
    def test_candidate_workflow_runs_synthetic_tests_only(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("test_download_verified_varroa.py", workflow)
        self.assertIn("test_varroa_download_workflow_policy.py", workflow)
        self.assertIn("synthetic bytes only", workflow)

        # Only one pinned checkout action and the two exact local test commands
        # are permitted. This rejects added download/upload actions and shell steps.
        uses = re.findall(r"^\s*-\s+uses:\s*(\S+)\s*$", workflow, flags=re.MULTILINE)
        runs = re.findall(r"^\s+run:\s*(.+?)\s*$", workflow, flags=re.MULTILINE)
        self.assertEqual(uses, [PINNED_CHECKOUT])
        self.assertEqual(runs, EXPECTED_RUNS)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertEqual(
            workflow.count("'scripts/verify_varroa_source_blob.py'"),
            2,
            "both push and pull_request must retest the imported verifier",
        )

        for forbidden in (
            "scripts.download_verified_varroa",
            "raw.githubusercontent.com",
            "varroa-source.pt",
            "actions/upload-artifact@",
            "curl ",
            "wget ",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, workflow)


if __name__ == "__main__":
    unittest.main()
