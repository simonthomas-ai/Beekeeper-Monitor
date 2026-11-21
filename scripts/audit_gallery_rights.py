#!/usr/bin/env python3
"""Audit embedded candidate metadata; does not verify third-party licenses."""
from pathlib import Path
import json
import re
import sys

root = Path(__file__).resolve().parents[1]
names = ("all", "velutina", "crabro", "apis", "bombus", "vespula")
issues = []
total = 0
for name in names:
    path = root / "review" / (name + ".html")
    if not path.is_file():
        issues.append(f"{path}: Datei fehlt")
        continue
    content = path.read_text(encoding="utf-8")
    match = re.search(r"const items=(\[.*?\]);", content, re.S)
    if not match:
        issues.append(f"{path}: Bildkandidaten nicht auffindbar")
        continue
    try:
        items = json.loads(match.group(1))
    except ValueError:
        issues.append(f"{path}: Kandidaten-JSON unlesbar")
        continue
    total += len(items)
    for index, item in enumerate(items, 1):
        prefix = f"{name} Kandidat {index}"
        if not str(item.get("source_url", "")).startswith("https://www.inaturalist.org/observations/"):
            issues.append(f"{prefix}: kein gültiger Beobachtungsquellenlink")
        if not str(item.get("image_url", "")).startswith("https://"):
            issues.append(f"{prefix}: keine HTTPS-Bildquelle")
        if not item.get("license"):
            issues.append(f"{prefix}: Lizenzangabe fehlt")
        if not item.get("creator"):
            issues.append(f"{prefix}: Urheberfeld fehlt")
    placeholder = sum(str(i.get("creator", "")).strip().lower() in ("no rights reserved", "unknown", "") for i in items)
    print(f"{name}: {len(items)} Kandidaten; {placeholder} ohne individuelle Urheberbenennung")
print(f"Geprüfte Galeriedatensätze (einschließlich Überschneidungen): {total}")
print("Hinweis: API-Metadaten sind KEIN unabhängiger Lizenznachweis; keine Trainingsfreigabe.")
for issue in issues:
    print("FEHLER:", issue, file=sys.stderr)
if issues:
    raise SystemExit(1)
