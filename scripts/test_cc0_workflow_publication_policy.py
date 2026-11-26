"""Regression tests for the CC0 workflow's no-publication policy."""
from pathlib import Path
import unittest

import yaml

WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "ki-cc0-quellen.yml"
)


class CC0WorkflowPublicationPolicyTests(unittest.TestCase):
    def test_validation_workflows_are_valid_yaml(self):
        root = Path(__file__).resolve().parents[1]
        for workflow_name in (
            "ki-cc0-quellen.yml",
            "model-training-readiness.yml",
            "training-data.yml",
            "gesamttest.yml",
        ):
            with self.subTest(workflow=workflow_name):
                content = (root / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
                parsed = yaml.safe_load(content)
                self.assertIn("jobs", parsed)

    def test_validation_workflows_use_exact_audited_dependency_pins(self):
        root = Path(__file__).resolve().parents[1]
        lock = root / "training" / "requirements-ci-validation.txt"
        lock_text = lock.read_text(encoding="utf-8")
        self.assertIn("Pillow==13.0.0", lock_text)
        self.assertIn("PyYAML==6.0.3", lock_text)
        for workflow_name in (
            "ki-cc0-quellen.yml",
            "model-training-readiness.yml",
            "training-data.yml",
        ):
            with self.subTest(workflow=workflow_name):
                content = (root / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
                self.assertIn("-r training/requirements-ci-validation.txt", content)
                self.assertNotIn("Pillow>=10,<13", content)
        e2e = (root / ".github" / "workflows" / "gesamttest.yml").read_text(encoding="utf-8")
        self.assertIn("pip-audit==2.10.1", e2e)
        self.assertIn("--requirement training/requirements-ci-validation.txt --strict", e2e)

    @classmethod
    def setUpClass(cls):
        cls.content = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_uses_read_only_repository_permissions(self):
        self.assertIn("permissions:\n  contents: read", self.content)
        self.assertNotIn("contents: write", self.content)
        self.assertNotIn("pages: write", self.content)

    def test_checkout_does_not_persist_a_write_capable_token(self):
        self.assertIn("persist-credentials: false", self.content)

    def test_workflow_does_not_push_generated_galleries_to_a_branch(self):
        for forbidden in ("git push", "git commit", "git reset --hard", "git fetch origin"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.content)

    def test_pages_workflow_stays_disabled_without_deploy_permissions(self):
        pages_workflow = (
            Path(__file__).resolve().parents[1]
            / ".github"
            / "workflows"
            / "pages.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("if: " + "$" + "{{ false }}", pages_workflow)
        self.assertNotIn("pages: write", pages_workflow)
        self.assertNotIn("id-token: write", pages_workflow)
        self.assertNotIn("actions/download-artifact", pages_workflow)
        self.assertNotIn("public-review-assets", pages_workflow)
        self.assertIn("cp review/index.html _site/review/index.html", pages_workflow)

    def test_unreviewed_candidate_media_and_metadata_are_not_uploaded(self):
        self.assertNotIn("actions/upload-artifact", self.content)
        self.assertNotIn("name: original-velutina-images", self.content)
        self.assertNotIn("name: ki-cc0-quellen-prueflisten", self.content)
        self.assertIn('review_dir="${RUNNER_TEMP:?}/vespaguard-review-assets"', self.content)
        self.assertIn('--output-dir "${review_dir}/images/velutina"', self.content)
        self.assertIn('rm -rf -- "${RUNNER_TEMP:?}/vespaguard-review-assets"', self.content)
        self.assertIn("ephemeren GitHub-Runner", self.content)
        self.assertNotIn("keine Bildbytes gespeichert", self.content)
        self.assertIn("Generierte Review-Metadaten nach Ergebnisbericht entfernen", self.content)


if __name__ == "__main__":
    unittest.main()
