"""Model inventory must fail visibly when the real dataset is absent."""
import contextlib
import io
import os
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


if __name__ == "__main__":
    unittest.main()
