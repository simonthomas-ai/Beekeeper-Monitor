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
for path in ("app.js","integrations-ui.js","alert-rules.js","alert-ui.js","live-media.js","style.css","manifest.webmanifest","icon.svg","sw.js"):
    assert (root/path).is_file(),path
assert "capture=\"environment\"" in html
for legal in ("datenschutz.html", "impressum.html"):
    assert (root/legal).is_file(), legal
    assert f'href="./{legal}"' in html, legal
    assert f"./{legal}" in sw, legal
assert "§ 5 DDG" in (root/"impressum.html").read_text()
assert "IndexedDB" in (root/"datenschutz.html").read_text()
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
assert re.search(r"beekeeper-shell-v\d+", sw)
assert "./wissen/wissenschaft-hornissen-bienen.html" in sw
assert (root/"wissen/wissenschaft-hornissen-bienen.html").is_file()
assert 'href="./wissen/wissenschaft-hornissen-bienen.html"' in html
assert "./integrations-ui.js" in sw
assert 'id="station-events-form"' in html
assert 'src="./integrations-ui.js"' in html
assert "./live-media.js" in sw
assert "SHELL.has(url.href)" in sw
pages=(root/".github/workflows/pages.yml").read_text()
assert "path: _site" in pages
assert "cp index.html datenschutz.html impressum.html style.css app.js integrations-ui.js alert-rules.js alert-ui.js live-media.js sw.js manifest.webmanifest icon.svg _site/" in pages
assert "cp wissen/wissenschaft-hornissen-bienen.html _site/wissen/" in pages
assert not re.search(r"99\s*%\s*(?:genau|erkennung)",html,re.I)
print("Static PWA and research catalog checks passed; real-device and AI tests remain outstanding.")
for asset in ("alert-rules.js","alert-ui.js"):
    assert f'./{asset}' in sw,asset
    assert f'./{asset}' in html,asset
assert "notificationclick" in sw
assert 'id="hornet-alert"' in html and "unbestätigt" in html
