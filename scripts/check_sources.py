#!/usr/bin/env python3
"""Validate source catalog schema and report reachable URLs; no model validation implied."""
import json
import pathlib
import urllib.request
import urllib.error
import sys

catalog = json.loads(pathlib.Path("sources/catalog.json").read_text(encoding="utf-8"))
required = {"id", "modules", "url", "kind", "license", "status", "notes"}
allowed = {"hornet", "varroa", "brood", "pollen", "swarm", "queen"}
errors = []
ids = set()
for source in catalog["sources"]:
    if not isinstance(source, dict):
        errors.append("Source entry must be an object")
        continue
    missing = required.difference(source)
    if missing:
        errors.append(f"Missing fields for {source.get('id', '?')}: {', '.join(sorted(missing))}")
        continue
    source_id = source["id"]
    if not isinstance(source_id, str) or not source_id.strip():
        errors.append("Source ID must be a nonempty string")
        continue
    if source_id in ids:
        errors.append(f"Duplicate ID: {source_id}")
    ids.add(source_id)
    if not isinstance(source["modules"], list) or not source["modules"] or any(
        not isinstance(module, str) or module not in allowed for module in source["modules"]
    ):
        errors.append(f"Invalid modules: {source_id}")
    if not isinstance(source["url"], str) or not source["url"].startswith("https://"):
        errors.append(f"Non-HTTPS URL: {source_id}")
print(f"Catalog schema: {len(catalog['sources'])} documented sources")
for err in errors:
    print("ERROR:", err, file=sys.stderr)
if errors:
    sys.exit(1)
if "--online" in sys.argv:
    for source in catalog["sources"]:
        try:
            req = urllib.request.Request(source["url"], headers={"User-Agent": "BeekeeperMonitor-SourceAudit/1.0"})
            with urllib.request.urlopen(req, timeout=15) as response:
                print(source["id"], response.status, response.url)
        except (urllib.error.URLError, TimeoutError) as exc:
            print("UNVERIFIED:", source["id"], str(exc))
    print("Note: URL reachability does NOT verify license, weights, dataset or model accuracy.")
