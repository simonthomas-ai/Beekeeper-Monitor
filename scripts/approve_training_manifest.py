#!/usr/bin/env python3
"""Fail-closed curator gate for image training manifests."""
import argparse
import json
from pathlib import Path
import sys

CLASSES = {"velutina", "crabro", "apis", "bombus", "vespula"}
LICENSES = {"cc0", "cc by 4.0", "cc by 3.0", "cc by 2.0", "public domain"}

def validate(data):
    accepted, rejected = [], []
    seen = set()
    for index, item in enumerate(data.get("items", [])):
        errors = []
        category = item.get("suggested_class")
        if category not in CLASSES:
            errors.append("unknown class")
        if not item.get("species_verified") or not item.get("human_approved_for_training"):
            errors.append("manual species and training approval missing")
        if not str(item.get("reviewer", "")).strip() or not str(item.get("reviewed_at", "")).strip():
            errors.append("reviewer and review date required")
        if str(item.get("license", "")).lower().strip() not in LICENSES:
            errors.append("license not allowlisted")
        if not str(item.get("source_page", "")).startswith("https://"):
            errors.append("source page missing")
        digest = item.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            errors.append("valid SHA256 required")
        elif digest in seen:
            errors.append("duplicate SHA256")
        else:
            seen.add(digest)
        local = item.get("local_file")
        if not local or Path(local).name != local:
            errors.append("safe local filename required")
        if errors:
            rejected.append({"index": index, "source_page": item.get("source_page"), "reasons": errors})
        else:
            accepted.append(item)
    return accepted, rejected

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    approved, rejected = validate(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"items": approved, "approved_count": len(approved), "rejected": rejected}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Approved: {len(approved)}; rejected: {len(rejected)}")
    return 0 if approved and not rejected else 1

if __name__ == "__main__":
    sys.exit(main())
