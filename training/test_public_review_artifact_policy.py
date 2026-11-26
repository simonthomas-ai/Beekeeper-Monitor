"""Prevent public Actions artifacts from exposing unreviewed original media."""
from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ki-cc0-quellen.yml"


class PublicReviewArtifactPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_original_media_is_not_uploaded_as_an_actions_artifact(self):
        self.assertNotIn("name: original-velutina-images", self.workflow)
        self.assertNotIn("--images-manifest", self.workflow)

    def test_original_media_is_removed_from_the_runner_workspace(self):
        cleanup = "name: Originalbildbytes nach temporaerer Pruefung entfernen"
        upload = "name: Metadaten und Prueflisten bereitstellen"
        self.assertIn(cleanup, self.workflow)
        self.assertIn("if: always()", self.workflow)
        self.assertIn("run: rm -rf public-review-assets", self.workflow)
        self.assertLess(self.workflow.index(cleanup), self.workflow.index(upload))

    def test_remaining_artifact_contains_metadata_only_paths(self):
        marker = "name: ki-cc0-quellen-prueflisten"
        self.assertIn(marker, self.workflow)
        artifact_section = self.workflow.split(marker, 1)[1]
        self.assertNotIn("public-review-assets", artifact_section)
        self.assertNotRegex(artifact_section, r"(?i)\.(?:jpe?g|png|webp)\b")


if __name__ == "__main__":
    unittest.main()
