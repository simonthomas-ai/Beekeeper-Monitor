#!/usr/bin/env python3
"""Review-only public Sketchfab insect metadata discovery. No model downloads."""
import argparse
import csv
import json
from collections import Counter
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.sketchfab.com/v3/search"
TERMS = ("vespa velutina", "vespa crabro", "apis mellifera", "bombus", "hymenoptera")
FIELDS = ("source", "model_uid", "title", "model_url", "creator", "license_slug",
          "species_query", "downloadable", "species_verified", "rights_verified",
          "geometry_verified", "training_approved")
ALLOWED = {"cc0", "cc-by", "cc-by-4.0", "cc0-1.0"}
MAX_RESULTS_PER_TERM = 24


def normalize(item, term):
    if not isinstance(item, dict):
        return None
    uid = item.get("uid")
    if not isinstance(uid, str) or not (8 <= len(uid) <= 64 and uid.isalnum()):
        return None
    license_value = item.get("license")
    if isinstance(license_value, dict):
        license_value = license_value.get("slug", "")
    if not isinstance(license_value, str):
        license_value = ""
    slug = license_value.lower().strip()
    if slug not in ALLOWED or item.get("isDownloadable") is not True:
        return None
    user = item.get("user")
    creator = user.get("username", "") if isinstance(user, dict) else ""
    return dict(source="Sketchfab", model_uid=uid,
                title=str(item.get("name") or "")[:250],
                model_url="https://sketchfab.com/3d-models/" + uid,
                creator=str(creator)[:120], license_slug=slug,
                species_query=term, downloadable="YES",
                species_verified="NO", rights_verified="NO",
                geometry_verified="NO", training_approved="NO")


def discover(fetch=None, diagnostics=None):
    def public_fetch(url):
        request = urllib.request.Request(url, headers={"User-Agent": "VespaGuard-3D-metadata-review/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    fetch = fetch or public_fetch
    records, errors, seen = [], [], set()
    counters = {'raw_results': 0, 'accepted': 0, 'rejected': 0}
    per_query = []
    rejection_reasons = Counter()
    license_shapes = Counter()
    license_values = Counter()
    for term in TERMS:
        url = API + "?" + urllib.parse.urlencode({
            "type": "models", "q": term, "downloadable": "true", "count": MAX_RESULTS_PER_TERM})
        try:
            payload = fetch(url)
            if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
                raise ValueError("Invalid public search response")
            results = payload["results"][:MAX_RESULTS_PER_TERM]
            counters["raw_results"] += len(results)
            per_query.append({"query": term, "raw_results": len(results)})
            for item in results:
                if isinstance(item, dict):
                    raw_license = item.get("license")
                    if isinstance(raw_license, dict):
                        license_shapes["object"] += 1
                        license_values[str(raw_license.get("slug", ""))[:80]] += 1
                    elif isinstance(raw_license, str):
                        license_shapes["string"] += 1
                        license_values[raw_license[:80]] += 1
                    elif raw_license is None:
                        license_shapes["missing"] += 1
                    else:
                        license_shapes["other"] += 1
                if not isinstance(item, dict):
                    reason = "invalid_item"
                else:
                    uid = item.get("uid")
                    license_value = item.get("license")
                    if isinstance(license_value, dict):
                        license_value = license_value.get("slug", "")
                    slug = license_value.strip().lower() if isinstance(license_value, str) else ""
                    if not isinstance(uid, str) or not (8 <= len(uid) <= 64 and uid.isalnum()):
                        reason = "invalid_uid"
                    elif slug not in ALLOWED:
                        reason = "missing_or_disallowed_license"
                    elif item.get("isDownloadable") is not True:
                        reason = "missing_or_false_download_flag"
                    elif uid in seen:
                        reason = "duplicate"
                    else:
                        reason = "accepted"
                rejection_reasons[reason] += 1
                row = normalize(item, term)
                if row and row["model_uid"] not in seen:
                    seen.add(row["model_uid"])
                    records.append(row)
                    counters["accepted"] += 1
                else:
                    counters["rejected"] += 1
        except (ValueError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append({"query": term, "error_type": type(exc).__name__})
    if diagnostics is not None:
        diagnostics.update({"counts": counters, "reasons": dict(rejection_reasons), "license_shapes": dict(license_shapes), "license_values": dict(license_values), "per_query": per_query,
                            "note": "Only first page per query scanned; rejection reasons need further review."})
    return records, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="training/sketchfab-insect-review.csv")
    parser.add_argument("--status", default="training/sketchfab-insect-review.status.json")
    args = parser.parse_args()
    diagnostics = {}
    rows, errors = discover(diagnostics=diagnostics)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    status = {"status": "complete" if not errors else "partial_or_unavailable",
              "candidate_metadata_count": len(rows), "queries_attempted": len(TERMS),
              "query_errors": errors, "diagnostics": diagnostics, "training_approvals": 0,
              "warning": "Unverified search metadata only. No downloads or training approvals."}
    Path(args.status).write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status))
    if errors:
        raise SystemExit("Upstream metadata search incomplete; see status artifact")


if __name__ == "__main__":
    main()
