#!/usr/bin/env python3
"""Create a human visual-review queue from verified iNaturalist API metadata.

URLs are review candidates only; the generated larger variants are NOT checked
for availability, content, identity or copyright. No training approvals.
"""
import argparse
import csv
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

FIELDS = ["observation_id", "photo_id", "api_taxon", "api_quality_grade",
          "api_photo_license", "api_attribution", "source_url", "api_photo_url",
          "large_review_url", "license_metadata_match", "visual_species_verified",
          "image_quality_verified", "rights_verified", "reviewer", "review_notes",
          "training_approved"]

def large_url(url):
    p = urlsplit(url)
    if (p.scheme != "https" or p.username or p.password or p.port not in (None, 443)
            or not p.hostname or not p.hostname.endswith(".inaturalist.org")
            or not p.path.endswith("/square.jpg")):
        return ""
    return urlunsplit((p.scheme, p.netloc, p.path[:-len("square.jpg")] + "large.jpg", "", ""))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    with open(args.input, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            if (row.get("api_photo_found") != "YES" or
                    row.get("license_metadata_match") != "YES" or
                    row.get("api_photo_license", "").lower() != "cc0" or
                    row.get("api_taxon") != "Vespa velutina" or row.get("error")):
                continue
            record = {k: row.get(k, "") for k in FIELDS}
            record.update(large_review_url=large_url(row.get("api_photo_url", "")),
                          visual_species_verified="NO", image_quality_verified="NO",
                          rights_verified="NO", reviewer="", review_notes="",
                          training_approved="NO")
            writer.writerow(record)
    print("Human review queue written. No images downloaded or approved.")

if __name__ == "__main__":
    main()
