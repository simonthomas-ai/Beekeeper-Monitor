"""Regression tests for keeping unreviewed candidate media and metadata private."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CC0 = (ROOT / ".github" / "workflows" / "ki-cc0-quellen.yml").read_text(encoding="utf-8")
PAGES = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
AUDIT = (ROOT / ".github" / "workflows" / "gallery-original-artifact-audit.yml").read_text(encoding="utf-8")
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
REVIEW_STATUS = (ROOT / "review" / "index.html").read_text(encoding="utf-8")


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

    def test_pages_remains_disabled_and_never_stages_candidate_media(self):
        self.assertIn("if: ${{ false }}", PAGES)
        for forbidden in (
            "original-velutina-images",
            "ki-cc0-quellen-prueflisten",
            "public-review-assets",
            "actions/download-artifact",
            "review/all.html",
            "review/velutina.html",
            "audit_gallery_rights.py --root _site",
        ):
            self.assertNotIn(forbidden, PAGES)
        self.assertIn("cp review/index.html _site/review/index.html", PAGES)

    def test_artifact_audit_checks_exact_source_run_without_downloading_artifacts(self):
        self.assertIn("workflow_run:", AUDIT)
        self.assertIn("actions/runs/${SOURCE_RUN_ID}/artifacts", AUDIT)
        self.assertIn("contents/.github/workflows/ki-cc0-quellen.yml?ref=${SOURCE_SHA}", AUDIT)
        self.assertIn("predates the no-artifact policy", AUDIT)
        self.assertIn("if [[ -n \"$artifact_names\" ]]", AUDIT)
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

if __name__ == "__main__":
    unittest.main()
