#!/usr/bin/env python3
"""Discover GBIF image-media candidates with explicit per-media license filtering.

Metadata only: no image URLs are fetched, no images are downloaded, and no
candidate is approved for training by this script.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.gbif.org/v1"
SPECIES = (
    "Vespa velutina", "Vespa crabro", "Vespula vulgaris", "Vespula germanica",
    "Apis mellifera", "Bombus terrestris", "Bombus lapidarius",
    "Polistes dominula", "Volucella zonaria", "Eristalis tenax",
)
FIELDS = [
    "source_id", "source_url", "image_url", "media_license", "media_license_url",
    "media_creator", "rights_holder", "publisher", "format", "occurrence_id",
    "occurrence_license", "dataset_key", "scientific_name", "review_status",
]
LICENSES = {
    "cc0": ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "cc0_1_0": ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "https://creativecommons.org/publicdomain/zero/1.0": ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "https://creativecommons.org/publicdomain/zero/1.0/": ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "cc by 4.0": ("CC-BY-4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "cc_by_4_0": ("CC-BY-4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "https://creativecommons.org/licenses/by/4.0": ("CC-BY-4.0", "https://creativecommons.org/licenses/by/4.0/"),
    "https://creativecommons.org/licenses/by/4.0/": ("CC-BY-4.0", "https://creativecommons.org/licenses/by/4.0/"),
}


class DiscoveryError(RuntimeError):
    pass


def normalize_license(value):
    if not isinstance(value, str):
        return None
    return LICENSES.get(value.strip().lower())


def fetch_json(url, *, timeout=30, retries=3, pause=1.0):
    if not url.startswith(BASE + "/"):
        raise DiscoveryError("Only the official GBIF API host is allowed")
    last_error = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "BeekeeperMonitor-GBIF-Metadata-Review/1.0"},
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise DiscoveryError("GBIF API returned HTTP %s" % response.status)
                return json.load(response)
        except Exception as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(pause * (attempt + 1))
    raise DiscoveryError("GBIF API unavailable after bounded retries") from last_error


def match_species(name, fetch=fetch_json):
    query = urllib.parse.urlencode({"name": name, "strict": "true"})
    result = fetch(BASE + "/species/match?" + query)
    if not isinstance(result, dict):
        raise DiscoveryError("GBIF species match response is malformed")
    if result.get("matchType") != "EXACT" or result.get("rank") != "SPECIES":
        return None
    if result.get("canonicalName") != name or type(result.get("usageKey")) is not int:
        return None
    return result["usageKey"]


def media_candidate(media, occurrence, species):
    if not isinstance(media, dict):
        return None
    if str(media.get("type", "")).lower() not in {"stillimage", "image"}:
        return None
    license_data = normalize_license(media.get("license"))
    if not license_data:
        return None
    image_url = media.get("identifier")
    if not isinstance(image_url, str) or not image_url.startswith("https://"):
        return None
    media_creator = (media.get("creator") or "").strip()
    rights_holder = (media.get("rightsHolder") or "").strip()
    publisher = (media.get("publisher") or "").strip()
    if license_data[0] == "CC-BY-4.0" and not (media_creator or rights_holder):
        return None
    occurrence_id = occurrence.get("key")
    if type(occurrence_id) is not int:
        return None
    media_id = image_url.strip()
    dataset_key = occurrence.get("datasetKey") or ""
    return {
        "source_id": "gbif-media-" + str(occurrence_id) + "-" + hashlib.sha256(media_id.encode("utf-8")).hexdigest()[:16],
        "source_url": "https://www.gbif.org/occurrence/" + str(occurrence_id),
        "image_url": image_url,
        "media_license": license_data[0],
        "media_license_url": license_data[1],
        "media_creator": media_creator,
        "rights_holder": rights_holder,
        "publisher": publisher,
        "format": (media.get("format") or "").strip(),
        "occurrence_id": occurrence_id,
        "occurrence_license": occurrence.get("license") or "",
        "dataset_key": dataset_key,
        "scientific_name": species,
        "review_status": "UNREVIEWED_MEDIA_RIGHTS_AND_IMAGE",
    }


def discover(target=1000, max_pages=3, limit=100, pause=1.0, fetch=fetch_json):
    if not 1 <= target <= 5000 or not 1 <= max_pages <= 50 or not 1 <= limit <= 300 or pause < 0.5:
        raise ValueError("Invalid discovery limits")
    rows, seen_media = [], set()
    quotas = {name: target // len(SPECIES) + (i < target % len(SPECIES)) for i, name in enumerate(SPECIES)}
    counts = {name: 0 for name in SPECIES}
    errors = []
    for species in SPECIES:
        if len(rows) >= target:
            break
        quota = quotas[species]
        if quota == 0:
            continue
        try:
            taxon_key = match_species(species, fetch=fetch)
            if taxon_key is None:
                errors.append("No exact GBIF species match: " + species)
                continue
            for page in range(max_pages):
                if counts[species] >= quota or len(rows) >= target:
                    break
                query = urllib.parse.urlencode({
                    "taxon_key": taxon_key, "media_type": "StillImage",
                    "limit": limit, "offset": page * limit,
                })
                payload = fetch(BASE + "/occurrence/search?" + query)
                records = payload.get("results", []) if isinstance(payload, dict) else []
                if not records:
                    break
                for occurrence in records:
                    for media in occurrence.get("media", []) if isinstance(occurrence, dict) else []:
                        candidate = media_candidate(media, occurrence, species)
                        if not candidate:
                            continue
                        identity = candidate["image_url"]
                        if identity in seen_media:
                            continue
                        seen_media.add(identity)
                        rows.append(candidate)
                        counts[species] += 1
                        break
                    if counts[species] >= quota or len(rows) >= target:
                        break
                if len(records) < limit:
                    break
                if pause:
                    time.sleep(pause)
        except Exception as exc:
            errors.append("%s: %s" % (species, type(exc).__name__))
    status = "complete" if not errors else ("partial" if rows else "unavailable")
    return rows, {"status": status, "requested": target, "found": len(rows),
                  "counts_by_species": counts, "errors": errors,
                  "media_downloaded": False, "training_performed": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="training/gbif-media-review-queue.csv")
    parser.add_argument("--status", default="training/gbif-media-discovery-status.json")
    parser.add_argument("--target", type=int, default=1000)
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--pause", type=float, default=1.0)
    parser.add_argument("--allow-unavailable", action="store_true")
    args = parser.parse_args()
    if args.pause < 0.5:
        parser.error("--pause must be at least 0.5 seconds")
    try:
        rows, status = discover(args.target, args.max_pages, args.limit, args.pause)
    except Exception as exc:
        rows = []
        status = {"status": "unavailable", "requested": args.target, "found": 0,
                  "errors": [type(exc).__name__], "media_downloaded": False,
                  "training_performed": False}
    output = Path(args.output)
    status_path = Path(args.status)
    output.parent.mkdir(parents=True, exist_ok=True)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("GBIF media candidates: %d; status=%s; no images downloaded." % (len(rows), status["status"]))
    if status["status"] == "unavailable" and not args.allow_unavailable:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
