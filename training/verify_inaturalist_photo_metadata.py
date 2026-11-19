#!/usr/bin/env python3
"""Recheck candidate photo licenses against iNaturalist observation API.

This produces evidence for human review, NOT training approvals.
Input: discovery CSV. Output: CSV with source metadata and API comparison.
"""
import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

FIELDS = ["observation_id", "photo_id", "species_candidate", "license", "source_url",
          "api_photo_found", "api_photo_license", "api_attribution",
          "api_taxon", "api_quality_grade", "api_photo_url",
          "license_metadata_match", "review_status", "error"]

def verify(row, timeout=15):
    out = {k: row.get(k, "") for k in FIELDS}
    out.update(api_photo_found="NO", api_photo_license="", api_attribution="",
               api_taxon="", api_quality_grade="", api_photo_url="",
               license_metadata_match="NO", review_status="UNREVIEWED", error="")
    obs = str(row.get("observation_id", ""))
    photo = str(row.get("photo_id", ""))
    if not obs.isdecimal() or not photo.isdecimal():
        out["error"] = "invalid observation/photo ID"
        return out
    url = "https://api.inaturalist.org/v1/observations/" + obs
    req = urllib.request.Request(url, headers={"User-Agent": "VespaGuard-PhotoLicenseAudit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.load(resp)
        results = payload.get("results", [])
        if len(results) != 1:
            out["error"] = "observation unavailable or ambiguous"
            return out
        observation = results[0]
        out["api_taxon"] = (observation.get("taxon") or {}).get("name", "")
        out["api_quality_grade"] = observation.get("quality_grade") or ""
        matches = [p for p in observation.get("photos", []) if str(p.get("id")) == photo]
        if len(matches) != 1:
            out["error"] = "photo not found in observation"
            return out
        p = matches[0]
        out["api_photo_found"] = "YES"
        out["api_photo_license"] = p.get("license_code") or ""
        out["api_attribution"] = p.get("attribution") or ""
        out["api_photo_url"] = p.get("url") or ""
        expected = {"CC0-1.0": "cc0", "CC-BY-VERSION-UNVERIFIED": "cc-by"}
        out["license_metadata_match"] = ("YES" if expected.get(row.get("license")) == str(p.get("license_code", "")).lower() else "NO")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        out["error"] = type(exc).__name__ + ": " + str(exc)[:160]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--species", default="Vespa velutina")
    ap.add_argument("--license", default="CC0-1.0")
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()
    if not 1 <= args.limit <= 1000:
        ap.error("limit must be 1..1000")
    with open(args.input, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r.get("species_candidate") == args.species and r.get("license") == args.license][:args.limit]
    if not rows:
        raise SystemExit("No matching candidate records")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for i, row in enumerate(rows):
            writer.writerow(verify(row))
            if i < len(rows)-1:
                time.sleep(1.1)  # under 60 requests/minute
    print(f"Audited {len(rows)} candidate metadata records; zero training approvals.")

if __name__ == "__main__":
    main()
