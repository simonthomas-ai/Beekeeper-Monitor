"""Regression tests for keeping unreviewed candidate metadata out of public Actions artifacts."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
CC0 = (WORKFLOWS / "ki-cc0-quellen.yml").read_text(encoding="utf-8")
PAGES = (WORKFLOWS / "pages.yml").read_text(encoding="utf-8")
AUDIT = (WORKFLOWS / "gallery-original-artifact-audit.yml").read_text(encoding="utf-8")
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
REVIEW_STATUS = (ROOT / "review" / "index.html").read_text(encoding="utf-8")

# These workflows create source-review queues or generated galleries. Their
# detailed candidate records are not suitable for public Actions artifacts.
CANDIDATE_REVIEW_WORKFLOWS = (
    "cc0-review-queue.yml",
    "inaturalist-balanced-discovery.yml",
    "hornet-photo-discovery.yml",
    "gbif-media-discovery.yml",
    "open-3d-metadata.yml",
    "commons-importer.yml",
    "cc0-insect-3d.yml",
)
FORBIDDEN_PUBLIC_ARTIFACT_NAMES = (
    "cc0-metadata-integrity-audit",
    "cc0-human-review-pending",
    "cc0-unreviewed-candidates",
    "inaturalist-balanced-review-queue",
    "insect-photo-review-queue",
    "gbif-media-review-queue",
    "unverified-sketchfab-3d-metadata",
    "commons-multiclass-metadata",
    "cc0-insect-3d-review",
)


class PublicReviewArtifactPolicyTests(unittest.TestCase):
    def test_cc0_discovery_uploads_no_candidate_artifacts(self):
        self.assertNotIn("actions/upload-artifact@", CC0)
        self.assertNotIn("name: original-velutina-images", CC0)
        self.assertNotIn("name: ki-cc0-quellen-prueflisten", CC0)
        self.assertIn("rm -rf public-review-assets", CC0)
        cleanup = "name: Generierte Review-Metadaten nach Ergebnisbericht entfernen"
        self.assertIn(cleanup, CC0)
        self.assertLess(CC0.index("name: Ergebnis"), CC0.index(cleanup))
        self.assertIn("rm -f training/inaturalist-review-queue.csv", CC0)

    def test_all_candidate_review_workflows_publish_no_actions_artifacts(self):
        for workflow_name in CANDIDATE_REVIEW_WORKFLOWS:
            with self.subTest(workflow=workflow_name):
                content = (WORKFLOWS / workflow_name).read_text(encoding="utf-8")
                self.assertNotIn("actions/upload-artifact@", content)

    def test_forbidden_candidate_artifact_names_are_absent_from_workflows(self):
        workflow_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(WORKFLOWS.glob("*.yml"))
        )
        for artifact_name in FORBIDDEN_PUBLIC_ARTIFACT_NAMES:
            with self.subTest(artifact=artifact_name):
                self.assertNotIn(artifact_name, workflow_text)

    def test_autonomous_control_artifact_excludes_candidate_queue(self):
        content = (WORKFLOWS / "autonomous-control.yml").read_text(encoding="utf-8")
        self.assertIn("name: Preserve test reports only", content)
        self.assertIn("name: autonomous-control-results", content)
        self.assertNotIn("training/inaturalist-review-queue.csv", content)
        self.assertIn("test-results/", content)

    def test_pages_remains_disabled_and_never_stages_candidate_media(self):
        pages = (WORKFLOWS / "pages.yml").read_text(encoding="utf-8")
        self.assertIn("if: ${{ false }}", pages)
        for forbidden in (
            "original-velutina-images",
            "ki-cc0-quellen-prueflisten",
            "public-review-assets",
            "actions/download-artifact",
            "review/all.html",
            "review/velutina.html",
            "audit_gallery_rights.py --root _site",
        ):
            self.assertNotIn(forbidden, pages)
        self.assertIn("cp review/index.html _site/review/index.html", pages)

    def test_artifact_audit_checks_exact_source_run_without_downloading_artifacts(self):
        self.assertIn("workflow_run:", AUDIT)
        self.assertIn("actions/runs/${SOURCE_RUN_ID}/artifacts", AUDIT)
        self.assertIn("contents/.github/workflows/ki-cc0-quellen.yml?ref=${SOURCE_SHA}", AUDIT)
        self.assertIn("predates the no-artifact policy", AUDIT)
        self.assertIn('if [[ -n "$artifact_names" ]]', AUDIT)
        self.assertNotIn("actions/download-artifact", AUDIT)
        self.assertNotIn("original-velutina-images", AUDIT)
        self.assertNotIn("ki-cc0-quellen-prueflisten", AUDIT)

    def test_public_pwa_links_only_to_the_safe_review_status_page(self):
        self.assertIn('href="./review/index.html"', INDEX)
        for gallery in ("all", "velutina", "crabro", "apis", "bombus", "vespula"):
            self.assertNotIn(f'href="./review/{gallery}.html"', INDEX)
        self.assertIn("Öffentliche Fotoprüfung derzeit nicht verfügbar", REVIEW_STATUS)
        self.assertNotIn("<img", REVIEW_STATUS.lower())
        self.assertNotIn("data:image", REVIEW_STATUS.lower())
        self.assertNotIn("images/velutina/", REVIEW_STATUS)
        for gallery in ("all", "velutina", "crabro", "apis", "bombus", "vespula"):
            self.assertFalse((ROOT / "review" / f"{gallery}.html").exists())

    def test_retired_public_gallery_license_audit_is_removed(self):
        self.assertFalse((WORKFLOWS / "photo-license-audit.yml").exists())
        self.assertFalse((ROOT / "scripts" / "check_live_photo_licenses.py").exists())


if __name__ == "__main__":
    unittest.main()
