#!/usr/bin/env python3
"""Validate the offline shell against the exact GitHub Pages publication contract.

Static contract check only: does not replace browser or real-device testing.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SW = (ROOT / "sw.js").read_text(encoding="utf-8")
PAGES = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
errors = []
match = re.search(r"const FILES=\[(.*?)\];", SW, re.S)
if not match:
    errors.append("Service Worker: FILES array missing")
    files = []
else:
    files = re.findall(r"['\"](\.\/[^'\"]+)['\"]", match.group(1))
    if not files:
        errors.append("Service Worker: offline shell empty")
if len(files) != len(set(files)):
    errors.append("Service Worker: duplicate offline shell paths")
for path in files:
    relative = path[2:]
    if path == "./":
        continue
    if ".." in Path(relative).parts or not (ROOT / relative).is_file():
        errors.append(f"Missing or unsafe offline shell file: {path}")
    # Public root assets are published by the cp command; nested assets use their own cp.
    if "/" not in relative:
        published = any(
            line.strip().startswith("cp ") and "_site/" in line and
            relative in line.split("_site/")[0].split()
            for line in PAGES.splitlines()
        )
    else:
        published = any(
            line.strip().startswith("cp ") and
            relative in line.split("_site/")[0].split()
            for line in PAGES.splitlines()
        )
    if not published:
        errors.append(f"Offline shell asset not explicitly published: {path}")
if "cache.addAll(FILES)" not in SW:
    errors.append("Offline shell pre-cache not detected")
print(f"Offline-PWA-Vertrag: {len(files)} Einträge; {len(errors)} Probleme")
for error in errors:
    print("FEHLER:", error, file=sys.stderr)
if errors:
    raise SystemExit(1)
