#!/usr/bin/env python3
"""Inventory candidate CC0 insect 3D scans; never approve species or training rights automatically."""
import argparse
import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://datasets-server.huggingface.co/rows"
DATASET = "hugging-3d/smithsonian-open-access-3d"
TERMS = ("vespa", "hornet", "wasp", "apis", "honeybee", "bumblebee", "bombus", "bee", "insect", "hymenoptera")
RETRYABLE_HTTP = {408, 425, 429, 500, 502, 503, 504}
FIELDS = [
    "package_id", "title", "scientific_name", "record_link", "mesh_url",
    "preview_url", "voyager_url", "vertices", "faces", "license",
    "media_usage_access", "species_verified", "geometry_verified",
    "training_approved", "review_notes",
]


def candidates(rows):
    found = []
    for item in rows:
        r = item.get("row", {})
        if r.get("license") != "CC0-1.0" or r.get("media_usage_access") != "CC0":
            continue
        fields = ("title", "package_title", "scientific_name", "tax_order", "object_type")
        description = " ".join(str(r.get(k, "")) for k in fields).lower()
        if not any(re.search(r"\b" + re.escape(term) + r"\b", description) for term in TERMS):
            continue
        found.append({
            "package_id": str(r.get("package_id", "")),
            "title": str(r.get("title", "")),
            "scientific_name": json.dumps(r.get("scientific_name", []), ensure_ascii=False),
            "record_link": str(r.get("record_link", "")),
            "mesh_url": str(r.get("mesh_url", "")),
            "preview_url": str(r.get("preview_url", "")),
            "voyager_url": str(r.get("voyager_url", "")),
            "vertices": str(r.get("vertices", "")),
            "faces": str(r.get("faces", "")),
            "license": "CC0-1.0",
            "media_usage_access": "CC0",
            "species_verified": "NO",
            "geometry_verified": "NO",
            "training_approved": "NO",
            "review_notes": "",
        })
    return found


def _retry_delay(error, attempt):
    """Return a bounded retry delay; never wait indefinitely on an upstream."""
    headers = getattr(error, "headers", None)
    retry_after = headers.get("Retry-After") if headers is not None else None
    if retry_after:
        try:
            return min(30.0, max(0.0, float(retry_after)))
        except (TypeError, ValueError):
            pass
    return min(8.0, 0.5 * (2 ** (attempt - 1)))


def fetch_all(urlopen=None, sleep_fn=time.sleep, max_attempts=5):
    """Fetch all pages, retrying only transient transport/upstream failures.

    Injection points keep tests deterministic and avoid calling external APIs.
    """
    if type(max_attempts) is not int or not 1 <= max_attempts <= 8:
        raise ValueError("max_attempts must be between 1 and 8")
    open_url = urlopen or urllib.request.urlopen
    offset, rows = 0, []
    page_count = 0
    while True:
        query = urllib.parse.urlencode({
            "dataset": DATASET, "config": "metadata", "split": "train",
            "offset": offset, "length": 100,
        })
        req = urllib.request.Request(
            API + "?" + query,
            headers={"User-Agent": "VespaGuard-CC0-3D-inventory/1.0"},
        )
        payload = None
        for attempt in range(1, max_attempts + 1):
            try:
                with open_url(req, timeout=45) as response:
                    payload = json.load(response)
                break
            except urllib.error.HTTPError as exc:
                if exc.code not in RETRYABLE_HTTP or attempt == max_attempts:
                    raise
                delay = _retry_delay(exc, attempt)
                sleep_fn(delay)
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
                if attempt == max_attempts:
                    raise
                sleep_fn(_retry_delay(exc, attempt))
        if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
            raise ValueError("Upstream response does not contain a valid rows array")
        if type(payload.get("num_rows_total")) is not int or payload["num_rows_total"] < 0:
            raise ValueError("Upstream response has an invalid num_rows_total")
        chunk = payload["rows"]
        if len(chunk) > 100:
            raise ValueError("Upstream page exceeds the requested 100-row limit")
        rows.extend(chunk)
        page_count += 1
        if page_count > 10000:
            raise RuntimeError("Upstream pagination exceeded the safety page limit")
        if not chunk:
            break
        offset += len(chunk)
        if offset >= payload["num_rows_total"]:
            break
    return rows


def _write_csv(path, records):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
        handle.flush()
    temporary.replace(output)


def _write_status(path, status):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(
        json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True) + "\\n",
        encoding="utf-8",
    )
    temporary.replace(target)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="training/cc0-3d-insect-candidates.csv")
    parser.add_argument("--status-output", default="training/cc0-3d-insect-candidates.status.json")
    parser.add_argument(
        "--allow-unavailable", action="store_true",
        help="Write an explicit unavailable status and an empty-header CSV instead of failing CI.",
    )
    args = parser.parse_args(argv)
    generated_at = datetime.now(timezone.utc).isoformat()
    try:
        rows = fetch_all()
        records = candidates(rows)
        _write_csv(args.output, records)
        status = {
            "status": "complete",
            "generated_at": generated_at,
            "source": API,
            "dataset": DATASET,
            "rows_scanned": len(rows),
            "candidates_found": len(records),
            "training_approvals": 0,
            "note": "Metadata candidates only; no species, geometry or training approval is implied.",
        }
    except Exception as exc:
        _write_csv(args.output, [])
        status = {
            "status": "upstream_unavailable",
            "generated_at": generated_at,
            "source": API,
            "dataset": DATASET,
            "rows_scanned": None,
            "candidates_found": None,
            "training_approvals": 0,
            "error_type": type(exc).__name__,
            "error": str(exc)[:300],
            "note": "No inventory result was obtained. The header-only CSV is not evidence that the dataset contains zero models.",
        }
        _write_status(args.status_output, status)
        print("::warning::Smithsonian/Hugging Face metadata endpoint unavailable after bounded retries; artifact status records the failed discovery.")
        if not args.allow_unavailable:
            raise
        return 0

    _write_status(args.status_output, status)
    print(
        f"Found {len(records)} CC0 metadata-matched 3D candidates from "
        f"{len(rows)} rows; zero training approvals. No meshes downloaded or rendered."
    )
    for item in records:
        print("3D candidate:", json.dumps({
            key: item[key] for key in (
                "package_id", "title", "scientific_name", "record_link",
                "voyager_url", "preview_url", "vertices", "faces",
            )
        }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
