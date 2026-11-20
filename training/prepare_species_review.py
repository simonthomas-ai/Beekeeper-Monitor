#!/usr/bin/env python3
"""Prepare a per-species review manifest; no files are approved for training."""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

REQUIRED = {"source_id", "source_url", "image_url", "creator", "license", "license_url",
            "attribution", "observation_id", "photo_id", "species_candidate", "review_status"}
PRIORITY = {"Vespa velutina": 1, "Bombus lapidarius": 2, "Vespa crabro": 3,\n            "Vespula vulgaris": 4, "Vespula germanica": 4,\n            "Apis mellifera": 5, "Bombus terrestris": 6}\nFIELDS = ["review_priority", "species_candidate", "review_group", "photo_id", "observation_id", "source_url",
          "image_url", "creator", "attribution", "license", "license_url",
          "license_review", "taxon_review", "image_quality_review", "bbox_annotation_review",
          "training_eligible"]

def group(name):
    clean = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return clean or "unknown"

def prepare(source, target):
    with Path(source).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError("Missing source columns")
        rows = list(reader)
    if not rows:
        raise ValueError("No source candidates")
    output, seen = [], set()
    for row in rows:
        if row["review_status"] != "UNREVIEWED":
            raise ValueError("Unexpected review status; refusing automatic approval")
        photo_id = row["photo_id"]
        if not photo_id or photo_id in seen:
            raise ValueError("Missing or duplicate photo ID")
        seen.add(photo_id)
        item = {k: row.get(k, "") for k in FIELDS}
        item["review_group"] = group(row["species_candidate"])\n        item["review_priority"] = str(PRIORITY.get(row["species_candidate"], 9))
        item["license_review"] = "PENDING"
        item["taxon_review"] = "PENDING"
        item["image_quality_review"] = "PENDING"
        item["bbox_annotation_review"] = "PENDING"
        item["training_eligible"] = "NO"
        output.append(item)
    output.sort(key=lambda x: (int(x["review_priority"]),\n                               0 if x["license"] == "CC0-1.0" else 1,\n                               x["observation_id"], x["photo_id"]))
    dest = Path(target)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output)
    counts = dict(sorted(Counter(x["species_candidate"] for x in output).items()))
    summary = {"candidates": len(output), "species_groups": counts,
               "approved_for_training": 0, "requires_expert_review": True,\n               "priority_order": ["Vespa velutina", "Bombus lapidarius",\n                                  "Vespa crabro", "Vespula vulgaris",\n                                  "Vespula germanica", "Apis mellifera",\n                                  "Bombus terrestris"],
               "warning": "Species and licenses are unverified. No bounding boxes or trained models produced."}
    dest.with_suffix(".json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="training/inaturalist-review-queue.csv")
    parser.add_argument("--output", default="training/inaturalist-species-review.csv")
    args = parser.parse_args()
    prepare(args.input, args.output)

if __name__ == "__main__":
    main()
