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
API = "https://api.inaturalist.org/v1/observations/"
def candidates():
    content = (ROOT / "review/all.html").read_text(encoding="utf-8")
    match = re.search(r"const items=(\[.*?\]);", content, re.S)
    if not match:
        raise ValueError("review/all.html: embedded items not found")
    items = json.loads(match.group(1))
    candidates_by_id = {}
    for item in items:
        pid = str(item["photo_id"])
        if pid in candidates_by_id and candidates_by_id[pid] != item:
            raise ValueError(f"Conflicting metadata for photo {pid}")
        candidates_by_id[pid] = item
    return candidates_by_id

def check_batch(batch):
    """Fetch observations in a single supported API call, then match exact photo IDs."""
    ids = sorted({str(item["observation_id"]) for _, item in batch})
    request = Request(API + ",".join(ids), headers={
        "User-Agent": "VespaGuardLicenseAudit/1.1 (github.com/simonthomas-ai/Beekeeper-Monitor)",
        "Accept": "application/json",
    })
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
        if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
            raise ValueError("Unexpected API response format")
        observations = {str(o["id"]): o for o in payload["results"]}
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError) as exc:
        reason = f"API {getattr(exc, 'code', type(exc).__name__)}"
        return [{"photo_id": pid, "status": "UNRESOLVED", "reason": reason} for pid, _ in batch]
    results = []
    for pid, item in batch:
        observation = observations.get(str(item["observation_id"]))
        if observation is None:
            results.append({"photo_id": pid, "status": "UNRESOLVED", "reason": "observation missing"})
            continue
        photos = [p for p in observation.get("photos", []) if str(p.get("id")) == pid]
        if len(photos) != 1:
            results.append({"photo_id": pid, "status": "UNRESOLVED", "reason": "photo missing or ambiguous"})
            continue
        remote_license = str(photos[0].get("license_code") or "").strip().lower()
        local_license = str(item.get("license") or "").strip().lower()
        aliases = {"cc0-1.0": "cc0"}
        if not remote_license:
            results.append({"photo_id": pid, "status": "UNRESOLVED", "reason": "no live photo license"})
        elif aliases.get(remote_license, remote_license) != aliases.get(local_license, local_license):
            results.append({"photo_id": pid, "status": "MISMATCH", "reason": "license changed or differs", "embedded_license": local_license, "live_license": remote_license})
        else:
            results.append({"photo_id": pid, "status": "MATCHED_METADATA", "license": remote_license})
    return results

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
    selected = sorted(items.items())[:args.limit]
    for offset in range(0, len(selected), 20):
        results.extend(check_batch(selected[offset:offset + 20]))
        if offset + 20 < len(selected):
            time.sleep(max(args.delay, 1.0))
    counts = dict(Counter(r["status"] for r in results))
    report = {"generated_utc": datetime.now(timezone.utc).isoformat(), "unique_gallery_candidates": len(items), "checked": len(results), "counts": counts, "results": results, "limitations": "API metadata comparison only; no proof of rights, author identity or training permission. Unchecked photos remain unresolved."}
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = Path(__import__("os").environ.get("GITHUB_STEP_SUMMARY", "/dev/null"))
    with summary.open("a", encoding="utf-8") as f:
        f.write(f"## iNaturalist-Fotolizenzen: täglicher Metadatenabgleich\n\nEinzelbilder: {len(items)}; geprüft: {len(results)}; Übereinstimmungen: {counts.get('MATCHED_METADATA',0)}; Abweichungen: {counts.get('MISMATCH',0)}; ungeklärt: {counts.get('UNRESOLVED',0)}.\n\n**Keine rechtliche Freigabe und keine Trainingsfreigabe.** JSON-Bericht im Workflow-Artefakt.\n")
    print(json.dumps({"checked": len(results), "counts": counts, "unresolved_reasons": dict(Counter(r.get("reason", "unknown") for r in results if r["status"] == "UNRESOLVED"))}, ensure_ascii=False))
    if counts.get("MISMATCH", 0):
        raise SystemExit("License metadata mismatches require manual review")
    if counts.get("UNRESOLVED", 0):
        raise SystemExit("Unresolved photo licenses require manual review; no automatic clearance")
    if len(results) < len(items):
        raise SystemExit("Not all gallery photos checked; no automatic clearance")

if __name__ == "__main__":
    main()
