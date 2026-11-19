#!/usr/bin/env python3
"""Collect *unreviewed* iNaturalist photo metadata, never training labels.

Uses only CC0 photo licenses; research grade is a discovery filter, not proof
of identification. No images downloaded, annotations generated or approvals.
"""
import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

SPECIES = ("Vespa velutina", "Vespa crabro", "Apis mellifera",
           "Bombus terrestris", "Vespula vulgaris")
FIELDS = ("source_id", "source_url", "image_url", "creator", "license",
          "license_url", "attribution", "observation_id", "photo_id",
          "species_candidate", "review_status")
API = "https://api.inaturalist.org/v1/observations"

def get_json(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": "VespaGuard-Research-Review/1.0 (noncommercial metadata audit)",
        "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=35) as response:
        return json.load(response)

def discover(per_species, max_pages=10):
    rows = []
    seen_photos = set()
    for species in SPECIES:
        # Exact scientific name from authoritative iNaturalist taxa search.
        query = urllib.parse.urlencode({"q": species, "rank": "species", "per_page": 30})
        taxa = get_json("https://api.inaturalist.org/v1/taxa/autocomplete?" + query)
        matches = [t for t in taxa.get("results", []) if t.get("name") == species]
        if len(matches) != 1:
            print("TAXON_UNRESOLVED:", species, flush=True)
            continue
        taxon_id = matches[0]["id"]
        time.sleep(1.1)
        # Scan multiple bounded pages, rather than only the newest observations.
        # Keep one independent observation per photo to limit duplicate leakage.
        count = 0
        for page in range(1, (max_pages if species != "Vespa velutina" else max(max_pages, 25)) + 1):
            params = urllib.parse.urlencode({
                "taxon_id": taxon_id, "quality_grade": "research", "photos": "true",
                "photo_license": "cc0",
                "per_page": 200, "page": page, "order_by": "observed_on",
                "order": "desc"})
            data = get_json(API + "?" + params)
            observations = data.get("results", [])
            for obs in observations:
                if count >= per_species:
                    break
                if obs.get("quality_grade") != "research":
                    continue
                if (obs.get("taxon") or {}).get("name") != species:
                    continue
                for photo in obs.get("photos", []):
                    if str(photo.get("license_code", "")).lower() != "cc0":
                        continue
                    pid = str(photo.get("id", ""))
                    url = photo.get("url") or ""
                    if not pid.isdecimal() or pid in seen_photos or not url.startswith("https://"):
                        continue
                    oid = str(obs.get("id", ""))
                    if not oid.isdecimal():
                        continue
                    seen_photos.add(pid)
                    rows.append({
                        "source_id": "inat-photo-" + pid,
                        "source_url": "https://www.inaturalist.org/observations/" + oid,
                        "image_url": url,
                        "creator": photo.get("attribution") or "Attribution unavailable",
                        "license": "CC0-1.0",
                        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                        "attribution": photo.get("attribution") or "CC0; verify creator",
                        "observation_id": oid, "photo_id": pid,
                        "species_candidate": species, "review_status": "UNREVIEWED"})
                    count += 1
                    break
            print(species, "page", page, "candidates", count, flush=True)
            if count >= per_species or len(observations) < 200:
                break
            time.sleep(1.1)
        print(species, "candidate records:", len([r for r in rows if r["species_candidate"] == species]), flush=True)
        time.sleep(1.1)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="training/inaturalist-review-queue.csv")
    ap.add_argument("--per-species", type=int, default=50)
    ap.add_argument("--max-pages", type=int, default=10)
    args = ap.parse_args()
    if not 1 <= args.max_pages <= 25:
        ap.error("--max-pages must be 1..25")
    if not 1 <= args.per_species <= 100:
        ap.error("--per-species must be 1..100")
    rows = discover(args.per_species, args.max_pages)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print("UNREVIEWED candidate metadata:", len(rows))
    print("Training approvals: 0. Model accuracy: NOT MEASURED.")
    if not rows:
        raise SystemExit("No eligible CC0 metadata retrieved; fail closed")

if __name__ == "__main__":
    main()
