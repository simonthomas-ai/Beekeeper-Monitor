#!/usr/bin/env python3
"""Compare unique public photo candidates with live iNaturalist photo metadata.

A matching API license is evidence of consistency, not proof of ownership.
Unreachable/missing metadata is unresolved, never automatically approved.
"""
import argparse
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.inaturalist.org/v1/photos/"
def candidates():
    content = (ROOT / "review/all.html").read_text(encoding="utf-8")
    match = re.search(r"const items=(\[.*?\]);", content, re.S)
    if not match:
        raise ValueError("review/all.html: embedded items not found")
    items = json.loads(match.group(1))
    return {str(i["photo_id"]): i for i in items}

def check(photo_id, item):
    request = Request(API + photo_id, headers={"User-Agent": "VespaGuardLicenseAudit/1.0 (github.com/simonthomas-ai/Beekeeper-Monitor)", "Accept": "application/json"})
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        return {"photo_id": photo_id, "status": "UNRESOLVED", "reason": type(exc).__name__}
    photos = payload.get("results", [])
    if not isinstance(photos, list) or len(photos) != 1:
        return {"photo_id": photo_id, "status": "UNRESOLVED", "reason": "photo not uniquely returned"}
    remote = photos[0]
    remote_license = str(remote.get("license_code") or "").strip().lower()
    local_license = str(item.get("license") or "").strip().lower()
    # iNaturalist uses cc0 while embedded gallery uses CC0-1.0.
    aliases = {"cc0-1.0": "cc0", "cc0": "cc0"}
    if not remote_license:
        return {"photo_id": photo_id, "status": "UNRESOLVED", "reason": "no live license metadata"}
    if aliases.get(remote_license, remote_license) != aliases.get(local_license, local_license):
        return {"photo_id": photo_id, "status": "MISMATCH", "reason": "license changed or differs", "embedded_license": local_license, "live_license": remote_license}
    return {"photo_id": photo_id, "status": "MATCHED_METADATA", "license": remote_license}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=250)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument("--output", default="photo-license-audit.json")
    args = parser.parse_args()
    if not 1 <= args.limit <= 500 or not 0 <= args.delay <= 5:
        parser.error("invalid limit/delay")
    items = candidates()
    results = []
    for n, (photo_id, item) in enumerate(sorted(items.items())[:args.limit], 1):
        results.append(check(photo_id, item))
        if n < min(len(items), args.limit):
            time.sleep(args.delay)
    counts = dict(Counter(r["status"] for r in results))
    report = {"generated_utc": datetime.now(timezone.utc).isoformat(), "unique_gallery_candidates": len(items), "checked": len(results), "counts": counts, "results": results, "limitations": "API metadata comparison only; no proof of rights, author identity or training permission. Unchecked photos remain unresolved."}
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = Path(__import__("os").environ.get("GITHUB_STEP_SUMMARY", "/dev/null"))
    with summary.open("a", encoding="utf-8") as f:
        f.write(f"## iNaturalist-Fotolizenzen: täglicher Metadatenabgleich\n\nEinzelbilder: {len(items)}; geprüft: {len(results)}; Übereinstimmungen: {counts.get('MATCHED_METADATA',0)}; Abweichungen: {counts.get('MISMATCH',0)}; ungeklärt: {counts.get('UNRESOLVED',0)}.\n\n**Keine rechtliche Freigabe und keine Trainingsfreigabe.** JSON-Bericht im Workflow-Artefakt.\n")
    print(json.dumps({"checked": len(results), "counts": counts}, ensure_ascii=False))
    if counts.get("MISMATCH", 0):
        raise SystemExit("License metadata mismatches require manual review")
    if counts.get("UNRESOLVED", 0) == len(results):
        raise SystemExit("No license metadata could be checked; review connectivity/API")

if __name__ == "__main__":
    main()
