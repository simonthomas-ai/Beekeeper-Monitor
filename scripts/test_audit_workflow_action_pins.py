"""Regression tests for immutable GitHub Actions pin enforcement."""
import unittest

from scripts.audit_workflow_action_pins import find_unpinned_actions


class ActionPinTests(unittest.TestCase):
    def test_accepts_full_commit_sha_with_version_comment(self):
        text = "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1"
        self.assertEqual(find_unpinned_actions(text), [])

    def test_rejects_major_tag(self):
        text = "      - uses: actions/checkout@v7"
        self.assertEqual(len(find_unpinned_actions(text)), 1)

    def test_rejects_short_commit_reference(self):
        text = "      - uses: owner/action@abcdef123456"
        self.assertEqual(len(find_unpinned_actions(text)), 1)

    def test_accepts_local_action_path(self):
        text = "      - uses: ./.github/actions/my-action"
        self.assertEqual(find_unpinned_actions(text), [])

    def test_requires_docker_digest(self):
        mutable = "      - uses: docker://ghcr.io/example/action:latest"
        immutable = "      - uses: docker://ghcr.io/example/action@sha256:" + "a" * 64
        self.assertEqual(len(find_unpinned_actions(mutable)), 1)
        self.assertEqual(find_unpinned_actions(immutable), [])

    def test_ignores_comments_and_run_lines(self):
        text = "# uses: actions/checkout@v4\n      - run: echo done"
        self.assertEqual(find_unpinned_actions(text), [])


if __name__ == "__main__":
    unittest.main()
