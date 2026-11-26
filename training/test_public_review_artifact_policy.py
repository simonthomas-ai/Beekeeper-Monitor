"""Regression tests for keeping unreviewed candidate metadata out of public Actions artifacts."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
CC0 = (WORKFLOWS / "ki-cc0-quellen.yml").read_text(encoding="utf-8")
PAGES = (WORKFLOWS / "pages.yml").read_text(encoding="utf-8")
AUDIT = (WORKFLOWS / "gallery-original-artifact-audit.yml").read_text(encoding="utf-8")
PWA_BUILD = (WORKFLOWS / "private-pwa.yml").read_text(encoding="utf-8")
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
    "verify-grab3d-bee.yml",
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
    "grab3d-bee-provenance-review",
)


class PublicReviewArtifactPolicyTests(unittest.TestCase):
    def test_pwa_build_artifact_is_explicitly_public_and_short_lived(self):
        self.assertIn("öffentliches Actions-Artefakt, kein Deployment", PWA_BUILD)
        self.assertIn("name: vespaguard-pwa-preview", PWA_BUILD)
        self.assertIn("retention-days: 7", PWA_BUILD)
        self.assertIn("Jeder Repository-Leser kann dieses Artefakt herunterladen; es ist nicht privat.", PWA_BUILD)
        self.assertIn("Keine gehostete Website.", PWA_BUILD)
        self.assertNotIn("vespaguard-private-pwa", PWA_BUILD)

    def test_image_review_workflows_pin_pillow_exactly(self):
        image_review_workflows = (
            "training-data.yml",
            "ki-cc0-quellen.yml",
            "model-training-readiness.yml",
            "hornet-photo-discovery.yml",
            "inaturalist-balanced-discovery.yml",
        )
        for workflow_name in image_review_workflows:
            with self.subTest(workflow=workflow_name):
                content = (WORKFLOWS / workflow_name).read_text(encoding="utf-8")
                self.assertIn("Pillow==12.3.0", content)
                self.assertNotRegex(content, r"Pillow\\s*(?:>=|<=|>|<|~=)")

    def test_cc0_discovery_uploads_no_candidate_artifacts(self):
        self.assertNotIn("actions/upload-artifact@", CC0)
        self.assertNotIn("name: original-velutina-images", CC0)
        self.assertNotIn("name: ki-cc0-quellen-prueflisten", CC0)
        self.assertIn('review_dir="${RUNNER_TEMP:?}/vespaguard-review-assets"', CC0)
        self.assertIn('--output-dir "${review_dir}/images/velutina"', CC0)
        self.assertIn('rm -rf -- "${RUNNER_TEMP:?}/vespaguard-review-assets"', CC0)
        self.assertIn("ephemeren GitHub-Runner", CC0)
        self.assertNotIn("keine Bildbytes gespeichert", CC0)
        download = "name: Unveraenderte CC0-Originaldateien fuer Vespa velutina herunterladen"
        image_cleanup = "name: Originalbildbytes nach temporaerer Pruefung entfernen"
        cleanup = "name: Generierte Review-Metadaten nach Ergebnisbericht entfernen"
        self.assertLess(CC0.index(download), CC0.index(image_cleanup))
        self.assertLess(CC0.index(image_cleanup), CC0.index("name: Ergebnis"))
        self.assertIn(cleanup, CC0)
        self.assertLess(CC0.index("name: Ergebnis"), CC0.index(cleanup))
        self.assertIn("rm -f training/inaturalist-review-queue.csv", CC0)

    def test_all_candidate_review_workflows_publish_no_actions_artifacts(self):
        for workflow_name in CANDIDATE_REVIEW_WORKFLOWS:
            with self.subTest(workflow=workflow_name):
                content = (WORKFLOWS / workflow_name).read_text(encoding="utf-8")
                self.assertNotIn("actions/upload-artifact@", content)

    def test_every_workflow_checkout_disables_credential_persistence(self):
        workflow_paths = sorted(
            [*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")]
        )
        self.assertTrue(workflow_paths, "workflow directory must not be empty")
        for path in workflow_paths:
            lines = path.read_text(encoding="utf-8").splitlines()
            checkout_indices = [
                index for index, line in enumerate(lines)
                if "uses: actions/checkout@" in line
            ]
            for index in checkout_indices:
                use_indent = len(lines[index]) - len(lines[index].lstrip())
                start = index
                if not lines[index].lstrip().startswith("- uses:"):
                    for candidate in range(index - 1, -1, -1):
                        match = re.match(r"^(\s*)-\s+", lines[candidate])
                        if match and len(match.group(1)) < use_indent:
                            start = candidate
                            break
                start_indent = len(lines[start]) - len(lines[start].lstrip())
                end = next(
                    (
                        candidate for candidate in range(index + 1, len(lines))
                        if (match := re.match(r"^(\s*)-\s+", lines[candidate]))
                        and len(match.group(1)) <= start_indent
                    ),
                    len(lines),
                )
                step = "\n".join(lines[start:end])
                with self.subTest(workflow=path.name, checkout_line=index + 1):
                    self.assertIn("persist-credentials: false", step)

    def test_forbidden_candidate_artifact_names_are_absent_from_upload_steps(self):
        # A candidate filename may still be used locally to build a review page.
        # Only the name assigned to an actions/upload-artifact step makes it a
        # public Actions artifact. Inspect those step inputs, not every workflow
        # reference to a local CSV/HTML filename.
        import re

        uploaded_names = set()
        for path in sorted(WORKFLOWS.glob("*.yml")):
            lines = path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines):
                if "uses: actions/upload-artifact@" not in line:
                    continue
                uses_indent = len(line) - len(line.lstrip())
                step_indent = max(0, uses_indent - 2)
                step_lines = []
                for following in lines[index + 1:]:
                    stripped = following.lstrip()
                    indent = len(following) - len(stripped)
                    if stripped.startswith("- ") and indent <= step_indent:
                        break
                    step_lines.append(following)

                with_index = next(
                    (i for i, item in enumerate(step_lines)
                     if item.strip() == "with:"),
                    None,
                )
                if with_index is None:
                    continue
                with_indent = len(step_lines[with_index]) - len(step_lines[with_index].lstrip())
                for item in step_lines[with_index + 1:]:
                    if item.strip():
                        indent = len(item) - len(item.lstrip())
                        if indent <= with_indent:
                            break
                    match = re.match(r"^\s+name:\s*([^\s#]+)", item)
                    if match:
                        uploaded_names.add(match.group(1))

        for artifact_name in FORBIDDEN_PUBLIC_ARTIFACT_NAMES:
            with self.subTest(artifact=artifact_name):
                self.assertNotIn(artifact_name, uploaded_names)

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
