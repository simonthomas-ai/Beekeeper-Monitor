#!/usr/bin/env python3
"""Prepare a per-species review manifest; no files are approved for training."""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

try:
    from training.dataset_groups import SPECIES_TO_GROUP
except ModuleNotFoundError:
    from dataset_groups import SPECIES_TO_GROUP

REQUIRED = {"source_id", "source_url", "image_url", "creator", "license", "license_url",
            "attribution", "observation_id", "photo_id", "species_candidate", "dataset_group", "review_status"}
PRIORITY = {"Vespa velutina": 1, "Bombus lapidarius": 2, "Vespa crabro": 3,
            "Vespula vulgaris": 4, "Vespula germanica": 4,
            "Apis mellifera": 5, "Bombus terrestris": 6}
FIELDS = ["review_priority", "species_candidate", "dataset_group", "review_group", "photo_id", "observation_id", "source_url",
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
        expected_group = SPECIES_TO_GROUP.get(row["species_candidate"])
        if not expected_group or row["dataset_group"] != expected_group:
            raise ValueError("Scientific species does not match the declared dataset group")
        item["review_group"] = expected_group
        item["review_priority"] = str(PRIORITY.get(row["species_candidate"], 9))
        item["license_review"] = "PENDING"
        item["taxon_review"] = "PENDING"
        item["image_quality_review"] = "PENDING"
        item["bbox_annotation_review"] = "PENDING"
        item["training_eligible"] = "NO"
        output.append(item)
    output.sort(key=lambda x: (int(x["review_priority"]),
                               0 if x["license"] == "CC0-1.0" else 1,
                               x["observation_id"], x["photo_id"]))
    dest = Path(target)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output)
    counts = dict(sorted(Counter(x["species_candidate"] for x in output).items()))
    group_counts = dict(sorted(Counter(x["review_group"] for x in output).items()))
    summary = {"candidates": len(output), "species_counts": counts,
               "dataset_group_counts": group_counts,
               "approved_for_training": 0, "requires_expert_review": True,
               "priority_order": ["Vespa velutina", "Bombus lapidarius",
                                  "Vespa crabro", "Vespula vulgaris",
                                  "Vespula germanica", "Apis mellifera",
                                  "Bombus terrestris"],
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
