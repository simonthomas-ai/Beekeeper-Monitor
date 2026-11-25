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
pages=(root/".github/workflows/pages.yml").read_text()
private_build=(root/".github/workflows/private-pwa.yml").read_text()
assert "<html lang=\"de\">" in html
for path in ("backup-contract.js","app.js","integrations-ui.js","alert-rules.js","alert-ui.js","live-media.js","field-dataset.js","style.css","manifest.webmanifest","icon.svg","sw.js"):
    assert (root/path).is_file(),path
assert "capture=\"environment\"" in html
assert 'id="field-dataset"' in html
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
assert "RIGHTS_LICENSES" in field_dataset_source
assert (root/"tests/test_beekeeper_importer_roundtrip.py").is_file()
assert "BEEKEEPER_MULTILABEL_VALIDATOR" in (root/"tests/test_beekeeper_importer_roundtrip.py").read_text()
assert (root/"docs/FIELD-DATASET-CAPTURE.md").is_file()
assert (root/"scripts/validate_field_dataset_zip.py").is_file()
assert (root/"tests/test_field_dataset_zip.py").is_file()
assert "Bilder noch Labels" in (root/"datenschutz.html").read_text()
assert "./field-dataset.js" in sw
assert "beekeeper-shell-v20" in sw
assert "annotations.jsonl" in html
assert "field-dataset.js" in pages
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
assert "path: _site" in pages
assert r"grep -Eq '\[[^]]+\]'" in pages
assert re.search(r"\[[^]]+\]", "[MISSING OPERATOR DETAILS]")
assert "cp index.html datenschutz.html impressum.html style.css backup-contract.js app.js integrations-ui.js alert-rules.js alert-ui.js live-media.js field-dataset.js varroa-ui.js varroa.html sw.js manifest.webmanifest icon.svg _site/" in pages
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
assert 'id="ai-readiness-status"' in html and 'NICHT SCHARF' in html
assert 'id="camera-model"' not in html
assert 'src="./hornet-onnx-decoder.js"' not in html
assert './hornet-onnx-decoder.js' not in sw
assert 'src="./camera-onnx-runtime.js"' not in html
assert './camera-onnx-runtime.js' not in sw
assert 'camera-onnx-runtime.js' not in pages
private_copy_lines = [line for line in private_build.splitlines() if line.lstrip().startswith("cp ")]
assert private_copy_lines, "private PWA asset copy commands must remain explicit"
assert all("camera-onnx-runtime.js" not in line for line in private_copy_lines)
assert all("hornet-onnx-decoder.js" not in line for line in private_copy_lines)
