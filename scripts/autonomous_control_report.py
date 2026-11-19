#!/usr/bin/env python3
"""Write one truthful GitHub Actions report for the autonomous controller."""
import csv
import os
from collections import Counter
from pathlib import Path

results = {
    "Static app": os.getenv("STATIC_RESULT", "unknown"),
    "Browser tests": os.getenv("BROWSER_RESULT", "unknown"),
    "Readiness script": os.getenv("READINESS_RESULT", "unknown"),
    "Photo discovery": os.getenv("DISCOVERY_RESULT", "unknown"),
}
lines = ["# Beekeeper-Monitor: autonome Projektkontrolle", "",
         "Weekly scheduled check or manual run; no claim of production readiness.", ""]
for name, result in results.items():
    lines.append(f"- {name}: **{result}**")
path = Path("training/inaturalist-review-queue.csv")
if path.exists():
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    counts = Counter(row["species_candidate"] for row in rows)
    licenses = Counter(row["license"] for row in rows)
    lines.extend(["", f"## Source candidates: {len(rows)} / 1000 (UNREVIEWED)", ""])
    for name in ("Vespa velutina", "Vespa crabro", "Vespula vulgaris",
                 "Vespula germanica", "Apis mellifera", "Bombus terrestris", "Bombus lapidarius"):
        lines.append(f"- {name}: {counts[name]}")
    lines.extend(["", "License metadata:"])
    for name, count in sorted(licenses.items()):
        lines.append(f"- {name}: {count}")
else:
    lines.extend(["", "**No photo CSV available.**"])
lines.extend(["", "No images downloaded or approved, no AI model trained, and no accuracy certified.",
              "A successful readiness script means the script ran, not that a model is ready.",
              "This controller does not automatically merge code or send messages."])
report = "\n".join(lines) + "\n"
print(report)
summary = os.getenv("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a", encoding="utf-8") as output:
        output.write(report)
