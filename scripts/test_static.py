#!/usr/bin/env python3
"""Static release checks. These do not establish real-device or AI accuracy."""
from pathlib import Path
import json
import re

root=Path(__file__).resolve().parents[1]
html=(root/"index.html").read_text()
app=(root/"app.js").read_text()
sw=(root/"sw.js").read_text()
manifest=json.loads((root/"manifest.webmanifest").read_text())
catalog=json.loads((root/"sources/catalog.json").read_text())
model_candidates=json.loads((root/"models/candidates.json").read_text())
pages=(root/".github/workflows/pages.yml").read_text()
review_status=(root/"review/index.html").read_text()
private_build=(root/".github/workflows/private-pwa.yml").read_text()
gesamttest=(root/".github/workflows/gesamttest.yml").read_text()
deployment=(root/"docs/DEPLOYMENT.md").read_text()
browser_workflow=(root/".github/workflows/browser.yml").read_text()
webkit_workflow=(root/".github/workflows/webkit.yml").read_text()
autonomous_workflow=(root/".github/workflows/autonomous-control.yml").read_text()
assert "<html lang=\"de\">" in html
for path in ("backup-contract.js","app.js","integrations-ui.js","alert-rules.js","alert-ui.js","live-media.js","field-image-privacy.js","field-dataset.js","camera-model-selector.js","style.css","manifest.webmanifest","icon.svg","sw.js"):
    assert (root/path).is_file(),path
assert "capture=\"environment\"" in html
assert 'id="field-dataset"' in html
assert 'src="./field-image-privacy.js" defer' in html
assert 'src="./field-dataset.js" defer' in html
assert 'accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"' in html
assert "nicht automatisch geprüft" in html
assert 'id="field-rights-basis"' in html and '<select id="field-rights-basis" required>' in html
for rights_basis in ("CC0-1.0", "CC-BY-4.0", "LicenseRef-ExplicitPermission"):
    assert f'value="{rights_basis}"' in html
assert 'id="field-rights-attribution"' in html
assert 'id="field-rights-permission-ref"' in html
field_dataset_source = (root/"field-dataset.js").read_text()
assert "rightsContractComplete" in field_dataset_source
assert "sanitizeImageForExport" in field_dataset_source
assert "RIGHTS_LICENSES" in field_dataset_source
assert (root/"tests/test_beekeeper_importer_roundtrip.py").is_file()
assert "BEEKEEPER_MULTILABEL_VALIDATOR" in (root/"tests/test_beekeeper_importer_roundtrip.py").read_text()
assert (root/"docs/FIELD-DATASET-CAPTURE.md").is_file()
assert (root/"scripts/validate_field_dataset_zip.py").is_file()
assert (root/"tests/test_field_dataset_zip.py").is_file()
assert "Bilder noch Labels" in (root/"datenschutz.html").read_text()
assert "./field-image-privacy.js" in sw
assert "./field-dataset.js" in sw
assert "beekeeper-shell-v23" in sw
assert "./camera-model-selector.js" in sw
assert "./models/candidates.json" in sw
assert "annotations.jsonl" in html
assert "field-image-privacy.js" in pages
assert "field-dataset.js" in pages
assert "camera-model-selector.js" in pages
assert "cp models/candidates.json _site/models/" in pages
for class_slug in ("vespa_velutina","vespa_crabro","other_vespidae","apis_mellifera","bombus_spp","syrphidae","other_insect"):
    assert class_slug in html and class_slug in (root/"field-dataset.js").read_text()
for legal in ("datenschutz.html", "impressum.html"):
    assert (root/legal).is_file(), legal
    assert f'href="./{legal}"' in html, legal
    assert f"./{legal}" in sw, legal
assert "§ 5 DDG" in (root/"impressum.html").read_text()
assert "IndexedDB" in (root/"datenschutz.html").read_text()
assert "indexedDB.open" in app
backup_contract=(root/"backup-contract.js").read_text()
assert "parseBackupText" in backup_contract
assert "buildPrivacySummaryCsv" in backup_contract
assert "buildPrivacySummaryCsv" in app
assert 'id="privacy-summary-export"' in html
assert "Monatsmuster können trotzdem Rückschlüsse zulassen" in html
assert "Monatliche Muster können dennoch Rückschlüsse ermöglichen" in (root/"datenschutz.html").read_text()
assert "restoreMissing" in app
assert "tx.onabort" in app
assert "navigator.geolocation.getCurrentPosition" in app
assert "crypto.randomUUID()" in app
assert "addEventListener('fetch'" in sw
assert manifest["display"]=="standalone"
assert manifest["start_url"]=="./"
assert set(["hornet","varroa","brood","pollen","swarm","queen"]) <= set(sum((s["modules"] for s in catalog["sources"]),[]))
assert "noch nicht validiert" in html
assert 'id="import"' in html
assert "validObservation" in backup_contract
assert "./backup-contract.js" in sw
assert 'src="./backup-contract.js" defer' in html
assert "async function remove(id)" in app
assert re.search(r"beekeeper-shell-v\d+", sw)
assert "./wissen/wissenschaft-hornissen-bienen.html" in sw
assert (root/"wissen/wissenschaft-hornissen-bienen.html").is_file()
assert 'href="./wissen/wissenschaft-hornissen-bienen.html"' in html
assert "./wissen/weltlage-vespa-velutina.html" in sw
assert (root/"wissen/weltlage-vespa-velutina.html").is_file()
assert 'href="./wissen/weltlage-vespa-velutina.html"' in html
global_page=(root/"wissen/weltlage-vespa-velutina.html").read_text()
for marker in ("id=\"weltweite-verbreitung\"", "id=\"nestlokalisierung\"", "id=\"quellen\"", "10.14411/eje.2026.022", "10.1038/s42003-024-05979-z"):
    assert marker in global_page, marker
assert "./integrations-ui.js" in sw
assert 'id="station-events-form"' in html
assert 'src="./integrations-ui.js"' in html
assert "./live-media.js" in sw
assert "SHELL.has(url.href)" in sw

# Safety regression: the manual Pages workflow may stage files but must never publish.
pages_triggers = pages.split("permissions:", 1)[0]
pages_events = re.findall(r"(?m)^  ([A-Za-z0-9_-]+):", pages_triggers)
assert pages_events == ["workflow_dispatch"], f"Pages workflow must remain manual-only: {pages_events}"
assert re.search(r"(?m)^jobs:\s*\n  verify-only:\s*$", pages), "Pages workflow must be validation-only"
workflow_files = [*(root / ".github" / "workflows").glob("*.yml"), *(root / ".github" / "workflows").glob("*.yaml")]
for workflow_path in workflow_files:
    workflow_text = workflow_path.read_text(encoding="utf-8")
    assert not re.search(
        r"(?m)^\s*uses:\s*actions/(?:configure-pages|upload-pages-artifact|deploy-pages)@",
        workflow_text,
    ), f"Pages publishing action is forbidden: {workflow_path.name}"
assert 'href="./review/index.html"' in html
assert "Öffentliche Fotoprüfung derzeit nicht verfügbar" in review_status
assert "<img" not in review_status.lower()
assert "original-velutina-images" not in pages
assert "ki-cc0-quellen-prueflisten" not in pages
assert "public-review-assets" not in pages
assert "actions/download-artifact" not in pages
assert "cp review/index.html _site/review/index.html" in pages
for gallery in ("all", "velutina", "crabro", "apis", "bombus", "vespula"):
    assert not (root/"review"/f"{gallery}.html").exists(), gallery
assert r"grep -Eq '\[[^]]+\]'" in pages
assert re.search(r"\[[^]]+\]", "[MISSING OPERATOR DETAILS]")
assert "cp index.html datenschutz.html impressum.html style.css backup-contract.js app.js integrations-ui.js alert-rules.js alert-ui.js live-media.js field-image-privacy.js field-dataset.js camera-model-selector.js varroa-ui.js varroa.html sw.js manifest.webmanifest icon.svg _site/" in pages
assert "cp wissen/wissenschaft-hornissen-bienen.html _site/wissen/" in pages
assert not re.search(r"99\s*%\s*(?:genau|erkennung)",html,re.I)
# Local original-image byte verification runs only after Pages stages the
# artifact into _site/review; this source-only static test has no binary assets.
print("Static PWA and research catalog checks passed; real-device and AI tests remain outstanding.")
for asset in ("alert-rules.js","alert-ui.js"):
    assert f'./{asset}' in sw,asset
    assert f'./{asset}' in html,asset
assert "notificationclick" in sw
assert 'id="hornet-alert"' in html and "unbestätigt" in html

assert (root/'varroa.html').is_file()
assert (root/'varroa-ui.js').is_file()
assert 'href="./varroa.html"' in html
assert 'id="varroa-mode"' in (root/'varroa.html').read_text()
assert './varroa.html' in sw and './varroa-ui.js' in sw

# No model weights are released in this repository; inference stays out of the PWA.
# The dormant research runtime must not execute remote CDN code or claim activation.
runtime_source = (root / "camera-onnx-runtime.js").read_text(encoding="utf-8")
assert "cdn.jsdelivr.net" not in runtime_source
assert "document.createElement('script')" not in runtime_source
assert "KI-Laufzeit nicht freigegeben" in runtime_source
assert "EXPERIMENTELLE KI AKTIV" not in runtime_source
assert 'id="ai-readiness-status"' in html and 'NICHT SCHARF' in html
assert 'id="camera-model"' in html
assert 'id="camera-model-status"' in html
assert 'id="camera-model-active"' in html
assert 'src="./camera-model-selector.js" defer' in html
assert model_candidates["schema_version"] == 1
assert model_candidates["status"] == "candidates_only_no_execution"
assert len(model_candidates["models"]) == 6
assert all(row.get("review_status") == "rights_and_runtime_pending" for row in model_candidates["models"])
assert all(not any(key in row for key in ("enabled","active","inference_enabled","deployable","sha256","license_approved")) for row in model_candidates["models"])
selector_source=(root/"camera-model-selector.js").read_text()
assert "models/candidates.json" in selector_source
assert "same-origin" in selector_source
assert "redirect: 'error'" in selector_source
assert "Kein Modell aktiv" in selector_source
assert "Aktives Modell: keines" in selector_source
assert 'src="./hornet-onnx-decoder.js"' not in html
assert './hornet-onnx-decoder.js' not in sw
assert 'src="./camera-onnx-runtime.js"' not in html
assert './camera-onnx-runtime.js' not in sw
assert 'camera-onnx-runtime.js' not in pages
# Public Actions artifacts are visible to readers of this public repository.
# The manual preview must stay on the ephemeral runner and must not be uploaded.
preview_triggers = private_build.split("permissions:", 1)[0]
preview_events = re.findall(r"(?m)^  ([A-Za-z0-9_-]+):", preview_triggers)
assert preview_events == ["workflow_dispatch"], (
    f"PWA staging must be manual-only, got triggers: {preview_events}"
)
assert "actions/upload-artifact@" not in private_build, (
    "PWA staging must not publish a public Actions artifact"
)
assert "vespaguard-pwa-preview" not in private_build
assert "retention-days:" not in private_build
assert "ephemeral GitHub-hosted runner" in private_build
assert "no artifact upload and no deployment" in private_build
for action in ("actions/configure-pages@", "actions/upload-pages-artifact@", "actions/deploy-pages@"):
    assert action not in private_build, f"PWA staging must not publish through {action}"
private_copy_lines = [line for line in private_build.splitlines() if line.lstrip().startswith("cp ")]
assert private_copy_lines, "private PWA asset copy commands must remain explicit"
assert any("field-image-privacy.js" in line for line in private_copy_lines), "private PWA must include the image privacy module"
assert any("field-dataset.js" in line for line in private_copy_lines), "private PWA must include the field dataset module"
assert any("camera-model-selector.js" in line for line in private_copy_lines), "private PWA must include the camera model selector"
assert any("cp models/candidates.json pwa-preview/models/" in line for line in private_copy_lines), "private PWA must include the local candidate catalog"
offline_assets = sw.split("const FILES=[", 1)[1].split("];", 1)[0]
for asset in re.findall(r"'(\./[^']+)'", offline_assets):
    relative = asset.removeprefix("./")
    if relative:
        assert any(relative in line for line in private_copy_lines), f"private PWA copy misses offline asset: {relative}"
assert all("camera-onnx-runtime.js" not in line for line in private_copy_lines)
assert all("hornet-onnx-decoder.js" not in line for line in private_copy_lines)

# Browser reports can contain traces/screenshots. The overall test must not
# publish any artifact from this public repository; retain only the step summary.
assert "actions/upload-artifact@" not in gesamttest, (
    "the one-click overall test must not publish public Actions artifacts"
)
assert "Browser-Testartefakte" not in gesamttest
assert "gesamttest-berichte" not in gesamttest
assert "GITHUB_STEP_SUMMARY" in gesamttest, (
    "the sanitized diagnostic summary must remain available"
)
assert "Pushes auf `main` starten Softwaretests, aber keine PWA-Buildvorschau." in deployment
assert "workflow_dispatch" in deployment
assert "weder ein herunterladbares PWA-Actions-Artefakt" in deployment

# Manual browser diagnostics publish failure traces only, for one day.
for workflow in (browser_workflow, webkit_workflow):
    triggers = workflow.split("permissions:", 1)[0]
    assert "  workflow_dispatch:" in triggers
    assert not re.search(r"(?m)^  (?:push|pull_request|schedule):", triggers)
    assert "        if: failure()" in workflow
    assert "          retention-days: 1" in workflow

# The scheduled autonomous run keeps its logs/summary, but only a manual
# dispatch may publish its browser trace artifact.
autonomous_artifact = autonomous_workflow.split("      - name: Preserve test reports only (manual, public, one day)", 1)[1]
assert "        if: ${{ always() && github.event_name == 'workflow_dispatch' }}" in autonomous_artifact
assert "          retention-days: 1" in autonomous_artifact
