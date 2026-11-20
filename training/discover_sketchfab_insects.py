#!/usr/bin/env python3
"""Review-only public Sketchfab insect metadata discovery. No model downloads."""
import argparse
import csv
import json
import re
from collections import Counter
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.sketchfab.com/v3/search"
TERMS = ("vespa velutina", "vespa crabro", "apis mellifera", "bombus", "hymenoptera")
FIELDS = ("source", "model_uid", "title", "model_url", "creator", "license_slug",
          "species_query", "downloadable", "species_verified", "rights_verified",
          "geometry_verified", "training_approved")
ALLOWED = {"cc0", "cc-by", "cc-by-4.0", "cc0-1.0"}
MAX_RESULTS_PER_TERM = 24
LICENSE_API = "https://api.sketchfab.com/v3/licences/"
LICENSE_UID_RE = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


def verified_license_slug(item, fetch=None, cache=None, outcomes=None):
    """Fail closed: never infer a license from a human-readable label."""
    if not isinstance(item, dict):
        return ""
    value = item.get("license")
    if isinstance(value, str):
        return value.strip().lower() if value.strip().lower() in ALLOWED else ""
    if not isinstance(value, dict):
        return ""
    slug = value.get("slug")
    if isinstance(slug, str) and slug.strip().lower() in ALLOWED:
        return slug.strip().lower()
    uid = value.get("uid")
    if not fetch or not isinstance(uid, str) or not LICENSE_UID_RE.fullmatch(uid):
        return ""
    cache = cache if cache is not None else {}
    if uid not in cache:
        try:
            detail = fetch(LICENSE_API + urllib.parse.quote(uid, safe=""))
            if not isinstance(detail, dict):
                if outcomes is not None:
                    outcomes["non_object_response"] += 1
                detail = {}
            else:
                if outcomes is not None:
                    for key in ("slug", "uid", "label", "name", "url"):
                        if key in detail:
                            outcomes["field_" + key + "_" + type(detail[key]).__name__] += 1
            detail_slug = detail.get("slug", detail.get("uid", ""))
            cache[uid] = detail_slug.strip().lower() if isinstance(detail_slug, str) and detail_slug.strip().lower() in ALLOWED else ""
            if outcomes is not None:
                outcomes["verified_allowed" if cache[uid] else "unverified_detail"] += 1
        except urllib.error.HTTPError as exc:
            if outcomes is not None:
                outcomes["http_" + str(exc.code) if exc.code in (400, 401, 403, 404, 429, 500, 502, 503) else "http_other"] += 1
            cache[uid] = ""
        except (ValueError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            if outcomes is not None:
                outcomes["error_" + type(exc).__name__] += 1
            cache[uid] = ""
    return cache[uid]


def normalize(item, term, license_slug=None):
    if not isinstance(item, dict):
        return None
    uid = item.get("uid")
    if not isinstance(uid, str) or not (8 <= len(uid) <= 64 and uid.isalnum()):
        return None
    slug = license_slug if license_slug is not None else verified_license_slug(item)
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
    license_object_keys = Counter()
    license_field_types = Counter()
    license_cache = {}
    resolved_license_counts = Counter()
    license_lookup_outcomes = Counter()
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
                        for key, value in raw_license.items():
                            if isinstance(key, str) and key in ("slug", "uid", "label", "url", "name", "id"):
                                license_object_keys[key] += 1
                                license_field_types[key + ":" + type(value).__name__] += 1
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
                    slug = verified_license_slug(item, fetch, license_cache, license_lookup_outcomes)
                    resolved_license_counts[slug or "unverified"] += 1
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
                row = normalize(item, term, license_slug=slug if isinstance(item, dict) else "")
                if row and row["model_uid"] not in seen:
                    seen.add(row["model_uid"])
                    records.append(row)
                    counters["accepted"] += 1
                else:
                    counters["rejected"] += 1
        except (ValueError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append({"query": term, "error_type": type(exc).__name__})
    if diagnostics is not None:
        diagnostics.update({"counts": counters, "reasons": dict(rejection_reasons), "license_shapes": dict(license_shapes), "license_values": dict(license_values), "license_object_keys": dict(license_object_keys), "license_field_types": dict(license_field_types), "resolved_licenses": dict(resolved_license_counts), "license_detail_requests": len(license_cache), "license_lookup_outcomes": dict(license_lookup_outcomes), "per_query": per_query,
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
