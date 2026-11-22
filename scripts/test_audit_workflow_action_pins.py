"""Regression tests for immutable GitHub Actions and container image pins."""
import unittest

from scripts.audit_workflow_action_pins import find_unpinned_actions, find_unpinned_images


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

    def test_requires_docker_action_digest(self):
        mutable = "      - uses: docker://ghcr.io/example/action:latest"
        immutable = "      - uses: docker://ghcr.io/example/action@sha256:" + "a" * 64
        self.assertEqual(len(find_unpinned_actions(mutable)), 1)
        self.assertEqual(find_unpinned_actions(immutable), [])

    def test_ignores_action_comments_and_run_lines(self):
        text = "# uses: actions/checkout@v4\n      - run: echo done"
        self.assertEqual(find_unpinned_actions(text), [])

    def test_accepts_container_image_with_oci_digest(self):
        text = "      image: mcr.microsoft.com/playwright:v1.65.1-noble@sha256:" + "b" * 64
        self.assertEqual(find_unpinned_images(text), [])

    def test_rejects_container_image_tag_without_digest(self):
        text = "      image: mcr.microsoft.com/playwright:v1.65.1-noble"
        self.assertEqual(len(find_unpinned_images(text)), 1)

    def test_accepts_quoted_container_image_digest(self):
        text = "      image: 'ghcr.io/example/test:2.0@sha256:" + "c" * 64 + "'"
        self.assertEqual(find_unpinned_images(text), [])

    def test_ignores_image_comments_and_run_lines(self):
        text = "# image: ubuntu:latest\n      - run: echo done"
        self.assertEqual(find_unpinned_images(text), [])


if __name__ == "__main__":
    unittest.main()
