#!/usr/bin/env python3
"""Build an annotation task manifest for human review, never synthetic YOLO labels.

Input must be an unapproved species review queue. Output only specifies tasks.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

FIELDS = ["task_id", "photo_id", "observation_id", "species_candidate",
          "image_url", "source_url", "creator", "license", "license_url",
          "species_identity", "license_version", "image_quality",
          "bounding_boxes", "reviewer", "approval_status"]
REQUIRED = {"photo_id", "observation_id", "species_candidate", "image_url",
            "source_url", "creator", "license", "license_url",
            "license_review", "taxon_review", "image_quality_review",
            "bbox_annotation_review", "training_eligible"}

def prepare(input_path, output_path):
    with Path(input_path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError("Invalid species review queue schema")
        rows = list(reader)
    if not rows:
        raise ValueError("No annotation candidates available")
    seen = set()
    tasks = []
    for row in rows:
        photo = row["photo_id"].strip()
        if not photo or photo in seen:
            raise ValueError("Duplicate or missing photo_id")
        seen.add(photo)
        if row["training_eligible"] != "NO":
            raise ValueError("Refusing input that claims automatic training approval")
        if any(row[key] != "PENDING" for key in ("license_review", "taxon_review",
                                                  "image_quality_review", "bbox_annotation_review")):
            raise ValueError("Unexpected review state")
        if any(urlparse(row[key]).scheme != "https" for key in ("image_url", "source_url")):
            raise ValueError("HTTPS source URLs required")
        tasks.append({
            "task_id": "photo-" + photo,
            "photo_id": photo,
            "observation_id": row["observation_id"],
            "species_candidate": row["species_candidate"],
            "image_url": row["image_url"],
            "source_url": row["source_url"],
            "creator": row["creator"],
            "license": row["license"],
            "license_url": row["license_url"],
            "species_identity": "UNVERIFIED",
            "license_version": "UNVERIFIED",
            "image_quality": "UNREVIEWED",
            "bounding_boxes": "NOT_ANNOTATED",
            "reviewer": "",
            "approval_status": "NOT_APPROVED",
        })
    tasks.sort(key=lambda task: (task["species_candidate"], task["photo_id"]))
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(tasks)
    summary = {
        "annotation_tasks": len(tasks),
        "by_species_candidate": dict(sorted(Counter(t["species_candidate"] for t in tasks).items())),
        "training_approved": 0,
        "labels_generated": 0,
        "notes": "No automatic species confirmation, rights approval, or bounding boxes. All tasks need independent expert review."
    }
    path.with_suffix(".json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="training/inaturalist-species-review.csv")
    parser.add_argument("--output", default="training/inaturalist-annotation-tasks.csv")
    args = parser.parse_args()
    prepare(args.input, args.output)
