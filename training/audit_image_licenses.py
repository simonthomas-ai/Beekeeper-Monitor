#!/usr/bin/env python3
"""Audit a real-image license manifest without downloading restricted content."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ALLOWED = {"CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0"}
REQUIRED = {"source_id", "source_url", "image_path", "creator", "license", "license_url", "sha256", "attribution"}
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="datasets/hornet/licenses.csv")
    args = parser.parse_args()
    path = Path(args.manifest)
    if not path.is_file():
        print("NO DATA: no authentic image license manifest present; import not approved")
        return
    errors = []
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not REQUIRED.issubset(reader.fieldnames or []):
            raise SystemExit("Missing required manifest columns: " + ", ".join(sorted(REQUIRED - set(reader.fieldnames or []))))
        rows = list(reader)
    seen = set()
    for i, row in enumerate(rows, 2):
        if row["license"] not in ALLOWED:
            errors.append(f"row {i}: license not in automatic allowlist")
        if not row["source_url"].startswith("https://") or not row["license_url"].startswith("https://"):
            errors.append(f"row {i}: HTTPS source and license URLs required")
        if not row["creator"].strip() or not row["attribution"].strip():
            errors.append(f"row {i}: missing author/attribution")
        image = Path(row["image_path"])
        if image.is_absolute() or ".." in image.parts or not image.parts or image.parts[0] != "datasets":
            errors.append(f"row {i}: image path must be relative under datasets/")
            continue
        if not image.is_file():
            errors.append(f"row {i}: missing image {image}")
            continue
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        if digest != row["sha256"].lower():
            errors.append(f"row {i}: image checksum mismatch")
        if digest in seen:
            errors.append(f"row {i}: duplicate image checksum")
        seen.add(digest)
    print(json.dumps({"images": len(rows), "approved_by_automated_metadata_checks": len(rows) if not errors else 0, "errors": errors}, indent=2))
    if not rows or errors:
        raise SystemExit(1)
    print("Metadata checks only; original copyright ownership, species and annotation accuracy require human review.")

if __name__ == "__main__":
    main()
