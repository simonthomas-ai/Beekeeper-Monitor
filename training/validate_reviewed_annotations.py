#!/usr/bin/env python3
"""Validate human-reviewed annotation records without creating fictitious labels.

Input JSON: {"records":[{"photo_id":"...","species":"Vespa velutina",
"license":"CC0-1.0","license_verified":true,"species_verified":true,
"image_quality_verified":true,"reviewer":"name","source_url":"https://...",
"boxes":[{"class_id":0,"x":0.5,"y":0.5,"width":0.2,"height":0.3}]}]}
This validates metadata and boxes, not image pixels, split integrity, or legal rights.
"""
import argparse
import json
import math
from pathlib import Path
from urllib.parse import urlparse

REQUIRED = ("photo_id", "species", "license", "license_verified",
            "species_verified", "image_quality_verified", "reviewer", "source_url", "boxes")
SUPPORTED_LICENSES = {"CC0-1.0", "CC-BY-4.0"}
try:
    from .class_schema import CLASS_NAMES
except ImportError:  # Supports direct execution: python training/validate_reviewed_annotations.py
    from class_schema import CLASS_NAMES

def check(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("Nonempty records array required")
    ids = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict) or any(key not in record for key in REQUIRED):
            raise ValueError(f"Record {index}: missing required fields")
        photo_id = str(record["photo_id"]).strip()
        if not photo_id or photo_id in ids:
            raise ValueError(f"Record {index}: missing/duplicate photo_id")
        ids.add(photo_id)
        for field in ("species", "reviewer"):
            if not isinstance(record[field], str) or not record[field].strip():
                raise ValueError(f"Record {index}: missing {field}")
        if record["license"] not in SUPPORTED_LICENSES:
            raise ValueError(f"Record {index}: unsupported or unverified license version")
        for field in ("license_verified", "species_verified", "image_quality_verified"):
            if record[field] is not True:
                raise ValueError(f"Record {index}: {field} must be explicitly true")
        url = urlparse(record["source_url"])
        if url.scheme != "https" or not url.netloc:
            raise ValueError(f"Record {index}: invalid source_url")
        boxes = record["boxes"]
        if not isinstance(boxes, list) or not boxes:
            raise ValueError(f"Record {index}: no bounding boxes")
        for box in boxes:
            if not isinstance(box, dict) or set(box) != {"class_id", "x", "y", "width", "height"}:
                raise ValueError(f"Record {index}: invalid box schema")
            cls = box["class_id"]
            if type(cls) is not int or not 0 <= cls < len(CLASS_NAMES):
                raise ValueError(f"Record {index}: invalid class_id")
            values = [box[k] for k in ("x", "y", "width", "height")]
            if any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
                raise ValueError(f"Record {index}: invalid box number")
            x, y, w, h = values
            if not (0 < w <= 1 and 0 < h <= 1 and 0 <= x <= 1 and 0 <= y <= 1):
                raise ValueError(f"Record {index}: invalid box bounds")
            if x-w/2 < 0 or x+w/2 > 1 or y-h/2 < 0 or y+h/2 > 1:
                raise ValueError(f"Record {index}: bounding box exceeds image")
    return {"reviewed_records": len(records), "validated_boxes": sum(len(r["boxes"]) for r in records),
            "limitations": "Metadata-only: image files, identity, license evidence, and split leakage require separate verification"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Human-reviewed JSON; no generated approvals")
    args = parser.parse_args()
    print(json.dumps(check(args.input), indent=2))

if __name__ == "__main__":
    main()
