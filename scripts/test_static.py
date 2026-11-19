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
assert "<html lang=\"de\">" in html
for path in ("app.js","style.css","manifest.webmanifest","icon.svg","sw.js"):
    assert (root/path).is_file(),path
assert "capture=\"environment\"" in html
assert "indexedDB.open" in app
assert "navigator.geolocation.getCurrentPosition" in app
assert "crypto.randomUUID()" in app
assert "addEventListener('fetch'" in sw
assert manifest["display"]=="standalone"
assert manifest["start_url"]=="./"
assert set(["hornet","varroa","brood","pollen","swarm","queen"]) <= set(sum((s["modules"] for s in catalog["sources"]),[]))
assert "noch nicht validiert" in html
assert 'id="import"' in html
assert "validObservation" in app
assert "async function remove(id)" in app
assert "beekeeper-shell-v5" in sw
assert "SHELL.has(url.href)" in sw
pages=(root/".github/workflows/pages.yml").read_text()
assert "path: _site" in pages
assert "cp index.html style.css app.js sw.js manifest.webmanifest icon.svg _site/" in pages
assert not re.search(r"99\s*%\s*(?:genau|erkennung)",html,re.I)
print("Static PWA and research catalog checks passed; real-device and AI tests remain outstanding.")
