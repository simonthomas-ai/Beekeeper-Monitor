"""Regression tests for the CC0 workflow's no-publication policy."""
from pathlib import Path
import unittest

WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "ki-cc0-quellen.yml"
)


class CC0WorkflowPublicationPolicyTests(unittest.TestCase):
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

    def test_review_galleries_remain_limited_to_actions_artifacts(self):
        self.assertIn("name: ki-cc0-quellen-prueflisten", self.content)
        self.assertIn("training/*-visual-review.html", self.content)
        self.assertIn("retention-days: 14", self.content)


if __name__ == "__main__":
    unittest.main()
