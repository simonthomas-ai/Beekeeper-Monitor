#!/usr/bin/env python3
"""Validate an exported mobile review and create a NON-APPROVED expert queue.

This intentionally never generates reviewed-annotations.json or training labels.
"""
import argparse
import json
import math
from pathlib import Path
from urllib.parse import urlsplit

SPECIES = {"Vespa velutina", "Vespa crabro", "Apis mellifera",
           "Bombus terrestris", "Vespula vulgaris"}
DECISIONS = {"PENDING", "LIKELY", "REJECT"}

def stage(payload):
    if not isinstance(payload, dict) or payload.get("format") != "vespaguard-unverified-mobile-review-v1":
        raise ValueError("Unsupported mobile review format")
    species = payload.get("species")
    if species not in SPECIES:
        raise ValueError("Unknown species")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("Nonempty records required")
    seen = set()
    queue = []
    for i, row in enumerate(records):
        if not isinstance(row, dict) or row.get("species_candidate") != species:
            raise ValueError(f"Record {i}: species mismatch")
        photo_id = str(row.get("photo_id", "")).strip()
        if not photo_id or photo_id in seen:
            raise ValueError(f"Record {i}: duplicate or empty photo ID")
        seen.add(photo_id)
        if row.get("training_eligible") is not False:
            raise ValueError(f"Record {i}: mobile review cannot grant training eligibility")
        for field in ("source_url", "image_url"):
            url = urlsplit(str(row.get(field, "")))
            if url.scheme != "https" or not url.hostname or url.username or url.password:
                raise ValueError(f"Record {i}: invalid {field}")
        review = row.get("review")
        if not isinstance(review, dict) or review.get("decision") not in DECISIONS:
            raise ValueError(f"Record {i}: invalid decision")
        boxes = review.get("boxes")
        if not isinstance(boxes, list):
            raise ValueError(f"Record {i}: invalid boxes")
        for box in boxes:
            if not isinstance(box, dict) or set(box) != {"x", "y", "width", "height"}:
                raise ValueError(f"Record {i}: invalid box")
            if any(type(box[k]) not in (int, float) or not math.isfinite(box[k]) for k in box):
                raise ValueError(f"Record {i}: non-finite box coordinate")
            x, y, w, h = (box[k] for k in ("x", "y", "width", "height"))
            if w <= 0 or h <= 0 or x-w/2 < 0 or x+w/2 > 1 or y-h/2 < 0 or y+h/2 > 1:
                raise ValueError(f"Record {i}: box outside image")
        queue.append({
            "photo_id": photo_id, "observation_id": str(row.get("observation_id", "")),
            "species_candidate": species, "source_url": row["source_url"],
            "image_url": row["image_url"], "license_claim": str(row.get("license", "")),
            "creator_claim": str(row.get("creator", "")), "mobile_decision": review["decision"],
            "proposed_boxes": boxes, "training_eligible": False,
            "expert_checks_required": ["verify_species", "verify_license_and_attribution",
                                       "verify_image_pixels_and_quality", "verify_boxes_against_image",
                                       "record_named_reviewer"]
        })
    return {"format": "vespaguard-expert-queue-v1", "species": species,
            "records": queue, "training_eligible": False,
            "note": "Staging only. No expert signoff, downloads, training labels or approvals."}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    source, target = Path(args.input), Path(args.output)
    if source.resolve() == target.resolve():
        raise ValueError("Refusing to overwrite source")
    result = stage(json.loads(source.read_text(encoding="utf-8")))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Staged {len(result['records'])} unapproved records for expert review.")

if __name__ == "__main__":
    main()
