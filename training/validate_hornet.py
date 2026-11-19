#!/usr/bin/env python3
"""Validate authentic YOLO hornet annotations before model training."""
import argparse
import hashlib
import json
from pathlib import Path

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
SPLITS = ("train", "val", "test")

def validate(root: Path):
    seen = {}
    results = {}
    errors = []
    for split in SPLITS:
        images = root / "images" / split
        labels = root / "labels" / split
        count = 0
        objects = 0
        if not images.is_dir() or not labels.is_dir():
            errors.append(f"{split}: missing images/labels directory")
            continue
        for image in sorted(images.rglob("*")):
            if image.suffix.lower() not in EXTENSIONS:
                continue
            count += 1
            relative = image.relative_to(images)
            annotation = labels / relative.with_suffix(".txt")
            if not annotation.is_file():
                errors.append(f"{split}: missing annotation for {relative}")
                continue
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            if digest in seen:
                errors.append(f"duplicate image across splits: {seen[digest]} and {split}/{relative}")
            seen[digest] = f"{split}/{relative}"
            for line_number, line in enumerate(annotation.read_text(encoding="utf-8").splitlines(), 1):
                values = line.split()
                try:
                    if len(values) != 5 or int(values[0]) != 0:
                        raise ValueError("expected class 0 and four coordinates")
                    x, y, w, h = map(float, values[1:])
                    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1 and x-w/2 >= 0 and x+w/2 <= 1 and y-h/2 >= 0 and y+h/2 <= 1):
                        raise ValueError("box outside image")
                    objects += 1
                except ValueError as exc:
                    errors.append(f"{split}/{relative}:{line_number}: {exc}")
        results[split] = {"images": count, "hornet_boxes": objects}
        if count == 0 or objects == 0:
            errors.append(f"{split}: no annotated hornet examples")
    return {"splits": results, "errors": errors, "passed": not errors}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="datasets/hornet")
    args = parser.parse_args()
    report = validate(Path(args.dataset))
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
