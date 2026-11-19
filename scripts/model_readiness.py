#!/usr/bin/env python3
"""Truthful model readiness snapshot for GitHub Actions (no mock data)."""
from pathlib import Path
import json
import os

root = Path(__file__).resolve().parents[1]
classes = ["vespa_velutina", "varroa_destructor", "drone_brood",
           "pollen_bearing_bee", "bee_swarm", "queen_bee"]
base = root / "training" / "datasets"
splits = ("train", "val", "test")
rows = []
for split in splits:
    image_dir = base / "images" / split
    label_dir = base / "labels" / split
    images = [p for p in image_dir.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}] if image_dir.is_dir() else []
    labels = list(label_dir.rglob("*.txt")) if label_dir.is_dir() else []
    rows.append((split, len(images), len(labels)))
ready = all(images > 0 and labels > 0 for _, images, labels in rows)
report = [
    "## KI-Trainingsdaten: " + ("vorhanden (noch nicht validiert)" if ready else "nicht vollständig vorhanden"),
    "",
    "| Datensatz | Bilder | Labeldateien |",
    "|---|---:|---:|",
]
report += [f"| {split} | {images} | {labels} |" for split, images, labels in rows]
report += ["", "Diese Inventur belegt weder korrekte Annotationen noch Modellgewichte,",
           "Erkennungsgenauigkeit, SMS-Zustellung oder reale Hardwaretests.",
           "Die Modellfreigabe bleibt bis zu unabhängiger Validierung offen."]
output = "\n".join(report) + "\n"
print(output)
if os.environ.get("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
        f.write(output)
