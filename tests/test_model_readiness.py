"""Model inventory must fail visibly without blocking software CI.""" 
import contextlib
import io
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import model_readiness


class ModelReadinessTests(unittest.TestCase):
    def test_missing_dataset_returns_failure_and_explicit_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": ""}):
                with contextlib.redirect_stdout(output):
                    result = model_readiness.main(Path(directory))

        self.assertEqual(result, 1)
        self.assertIn("unvollständig oder inkonsistent", output.getvalue())
        self.assertIn("Provenienzmanifest", output.getvalue())
        self.assertIn("Die Modellfreigabe bleibt bis zu unabhängiger Validierung offen.", output.getvalue())

    def test_incomplete_ai_inventory_is_reported_but_not_a_software_ci_gate(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github" / "workflows" / "gesamttest.yml").read_text(encoding="utf-8")
        overall = workflow.split("      - name: Gesamtergebnis", 1)[1].split(
            "\n  beekeeper3000-bridge:", 1
        )[0]

        required_software_gates = re.findall(
            r'(?m)^\s*test "\$([A-Z_]+)" = success\s*$', overall
        )
        self.assertEqual(
            required_software_gates,
            ["STATIC", "ALERTTESTS", "BROWSER", "WEBKIT", "IPHONE", "IMPORTTESTS", "SITE"],
        )
        self.assertIn("MODEL_STATUS: ${{ steps.model.outcome }}", workflow)
        self.assertIn("KI-Dateninventur (nur Zählung, nicht validiert)", workflow)
        self.assertIn('id: model\n        continue-on-error: true', workflow)
        self.assertIn("TRAINING_STATUS: ${{ steps.training.outcome }}", workflow)
        self.assertIn("ANNOTATIONS_STATUS: ${{ steps.annotations.outcome }}", workflow)


if __name__ == "__main__":
    unittest.main()
