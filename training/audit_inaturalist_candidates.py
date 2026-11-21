#!/usr/bin/env python3
"""Fail-closed metadata quality audit for iNaturalist candidate CSV. No training approval."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

REQUIRED = ("source_id", "source_url", "image_url", "creator", "license",
            "license_url", "attribution", "observation_id", "photo_id",
            "species_candidate", "review_status")
ALLOWED = {"CC0-1.0", "CC-BY-VERSION-UNVERIFIED"}

def audit(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or any(k not in reader.fieldnames for k in REQUIRED):
            raise ValueError("Required metadata columns missing")
        rows = list(reader)
    seen_photos, seen_observations, seen_image_urls, problems = set(), set(), set(), []
    by_species = Counter()
    for i, row in enumerate(rows, start=2):
        errors = []
        if any(not (row.get(k) or "").strip() for k in ("source_id", "source_url",
                "image_url", "creator", "attribution", "observation_id", "photo_id", "species_candidate")):
            errors.append("missing_required_value")
        if row.get("license") not in ALLOWED:
            errors.append("unapproved_license_code")
        if row.get("license") == "CC0-1.0" and row.get("license_url") != "https://creativecommons.org/publicdomain/zero/1.0/":
            errors.append("incorrect_cc0_reference")
        if row.get("review_status") != "UNREVIEWED":
            errors.append("unverified_approval_status")
        for key in ("source_url", "image_url"):
            u = urlparse(row.get(key) or "")
            if u.scheme != "https" or not u.netloc or u.username or u.password:
                errors.append("invalid_" + key)
        if (row.get("image_url") or "").strip() in seen_image_urls:\n            errors.append("duplicate_image_url")\n        seen_image_urls.add((row.get("image_url") or "").strip())\n        if row.get("photo_id") in seen_photos or row.get("observation_id") in seen_observations:
            errors.append("duplicate_photo_or_observation")
        seen_photos.add(row.get("photo_id"))
        seen_observations.add(row.get("observation_id"))
        by_species[row.get("species_candidate") or "UNKNOWN"] += 1
        if errors:
            problems.append({"csv_line": i, "errors": sorted(set(errors))})
    return {"candidates": len(rows), "by_species": dict(sorted(by_species.items())),
            "metadata_errors": problems, "requires_human_review": True,
            "approved_training_images": 0,
            "note": "Metadata validation cannot establish species identity, actual license version, image quality, bounding boxes, or model accuracy."}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="training/inaturalist-review-queue.csv")
    p.add_argument("--output", default="training/inaturalist-metadata-audit.json")
    args = p.parse_args()
    result = audit(args.input)
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["candidates"] or result["metadata_errors"]:
        raise SystemExit("Missing candidates or invalid metadata; see audit report")

if __name__ == "__main__":
    main()
