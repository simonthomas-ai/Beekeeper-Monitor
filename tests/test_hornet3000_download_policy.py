"""Policy tests: unapproved Hornet3000 bytes and CC0 photos are never fetched."""
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from scripts import verify_hornet3000_onnx as verifier


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "hornet3000-integrity.yml"
PINNED_CHECKOUT = "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
EXPECTED_RUNS = [
    "python3 -m unittest discover -s tests -p test_hornet3000_download_policy.py -v",
    "python3 -m py_compile scripts/verify_hornet3000_onnx.py",
]


class Hornet3000DownloadPolicyTests(unittest.TestCase):
    def test_explicit_download_is_blocked_before_network_access(self):
        with patch.object(verifier.urllib.request, "urlopen") as opener:
            with self.assertRaisesRegex(PermissionError, "downloads are disabled in code"):
                verifier.inspect(download=True)
            opener.assert_not_called()

    def test_default_inspection_is_metadata_only(self):
        with patch.object(verifier.urllib.request, "urlopen") as opener:
            result = verifier.inspect()
            self.assertEqual(result["status"], "not_downloaded")
            self.assertEqual(result["expected_bytes"], verifier.SIZE)
            opener.assert_not_called()

    def test_candidate_workflow_runs_only_local_policy_checks(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        uses = re.findall(
            r"^\s*-\s+uses:\s*(\S+)(?:\s+#.*)?\s*$",
            workflow,
            flags=re.MULTILINE,
        )
        runs = re.findall(r"^\s+run:\s*(.+?)\s*$", workflow, flags=re.MULTILINE)
        self.assertEqual(uses, [PINNED_CHECKOUT])
        self.assertEqual(runs, EXPECTED_RUNS)
        self.assertIn("permissions:\n  contents: read", workflow)
        for forbidden in (
            "--download",
            "--real-cc0",
            "--multispecies",
            "raw.githubusercontent.com",
            "api.inaturalist.org",
            "pip install onnx",
            "onnxruntime",
            "actions/upload-artifact@",
            "curl ",
            "wget ",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, workflow)


if __name__ == "__main__":
    unittest.main()
