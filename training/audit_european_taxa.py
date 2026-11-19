#!/usr/bin/env python3
"""Resolve a curated priority taxon list against the Catalogue of Life XR via GBIF.
Results are taxonomy candidates, not proof of European presence or model training.
"""
import argparse
import csv
import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CHECKLIST = "7ddf754f-d193-4cc9-b351-99906754a03b"
API = "https://api.gbif.org/v2/species/match"

def match(name):
    url = API + "?" + urlencode({"scientificName": name, "checklistKey": CHECKLIST})
    req = Request(url, headers={"User-Agent": "VespaGuard-taxonomy-audit/1.0"})
    with urlopen(req, timeout=30) as response:
        result = json.load(response)
    usage = result.get("usage") or {}
    return {"matched_name": usage.get("canonicalName", ""), "taxon_key": str(usage.get("key", "")),
            "taxon_status": usage.get("status", ""), "match_type": result.get("matchType", ""),
            "issues": ";".join(map(str, result.get("issues") or []))}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="training/european-apiary-priority-taxa.csv")
    p.add_argument("--output", default="training/european-apiary-taxonomy-audit.csv")
    p.add_argument("--pause", type=float, default=0.3)
    args = p.parse_args()
    if args.pause < 0:
        p.error("--pause must be nonnegative")
    with open(args.input, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit("Empty taxonomy seed")
    output = []
    for row in rows:
        try:
            resolved = match(row["scientific_name"])
            row.update(resolved)
            row["review_status"] = "NEEDS_REVIEW" if not resolved["taxon_key"] or resolved["issues"] else "MATCHED_NOT_VERIFIED"
        except Exception as exc:
            row.update({"matched_name": "", "taxon_key": "", "taxon_status": "", "match_type": "",
                        "issues": str(exc), "review_status": "API_ERROR"})
        output.append(row)
        time.sleep(args.pause)
    fields = list(output[0])
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)
    print(f"Audited {len(output)} priority taxa. All entries require expert review for European distribution and image rights.")
    if any(r["review_status"] == "API_ERROR" for r in output):
        raise SystemExit("Taxonomy API errors occurred; review output")

if __name__ == "__main__":
    main()
