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
    if not required.issubset(source):
        errors.append(f"Missing fields: {source.get('id', '?')}")
    if source["id"] in ids:
        errors.append(f"Duplicate ID: {source['id']}")
    ids.add(source["id"])
    if not set(source["modules"]).issubset(allowed):
        errors.append(f"Invalid modules: {source['id']}")
    if not source["url"].startswith("https://"):
        errors.append(f"Non-HTTPS URL: {source['id']}")
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
