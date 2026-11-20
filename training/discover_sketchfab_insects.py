#!/usr/bin/env python3
"""Review-only public Sketchfab insect metadata discovery. No model downloads."""
import argparse
import csv
import json
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


def discover(fetch=None):
    def public_fetch(url):
        request = urllib.request.Request(url, headers={"User-Agent": "VespaGuard-3D-metadata-review/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    fetch = fetch or public_fetch
    records, errors, seen = [], [], set()
    for term in TERMS:
        url = API + "?" + urllib.parse.urlencode({
            "type": "models", "q": term, "downloadable": "true", "count": MAX_RESULTS_PER_TERM})
        try:
            payload = fetch(url)
            if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
                raise ValueError("Invalid public search response")
            for item in payload["results"][:MAX_RESULTS_PER_TERM]:
                row = normalize(item, term)
                if row and row["model_uid"] not in seen:
                    seen.add(row["model_uid"])
                    records.append(row)
        except (ValueError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append({"query": term, "error_type": type(exc).__name__})
    return records, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="training/sketchfab-insect-review.csv")
    parser.add_argument("--status", default="training/sketchfab-insect-review.status.json")
    args = parser.parse_args()
    rows, errors = discover()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    status = {"status": "complete" if not errors else "partial_or_unavailable",
              "candidate_metadata_count": len(rows), "queries_attempted": len(TERMS),
              "query_errors": errors, "training_approvals": 0,
              "warning": "Unverified search metadata only. No downloads or training approvals."}
    Path(args.status).write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status))
    if errors:
        raise SystemExit("Upstream metadata search incomplete; see status artifact")


if __name__ == "__main__":
    main()
