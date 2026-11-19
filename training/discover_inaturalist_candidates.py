#!/usr/bin/env python3
"""Discover up to 1000 independently observed insect photo CANDIDATES.

Metadata only. No image downloads, training, license approval, or inferred accuracy.
"""
import argparse
import csv
import json
import time
import urllib.parse
import urllib.request

LICENSES = {
    "cc0": ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "cc-by": ("CC-BY-VERSION-UNVERIFIED", ""),
}
FIELDS = ["source_id", "source_url", "image_url", "creator", "license", "license_url", "attribution", "observation_id", "photo_id", "species_candidate", "review_status"]
SPECIES = ("Vespa velutina", "Bombus lapidarius", "Vespa crabro", "Vespula vulgaris", "Vespula germanica", "Apis mellifera", "Bombus terrestris")


def fetch_observations(species, page):
    params = urllib.parse.urlencode({
        "taxon_name": species, "quality_grade": "research", "photos": "true",
        "photo_license": "cc0,cc-by", "per_page": 200, "page": page,
        "order_by": "observed_on", "order": "desc",
    })
    request = urllib.request.Request(
        "https://api.inaturalist.org/v1/observations?" + params,
        headers={"User-Agent": "BeekeeperMonitor-Research/1.0 (metadata review only)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response).get("results", [])


def discover(target, max_pages, pause):
    rows, seen_photos, seen_observations = [], set(), set()
    # Round-robin across species prevents abundant species consuming the full quota.\n    # Prioritize scarce target species first, but retain one record per observation.
    for page in range(1, max_pages + 1):
        found_any = False
        for species in SPECIES:
            if len(rows) >= target:
                return rows
            observations = fetch_observations(species, page)
            if observations:
                found_any = True
            for obs in observations:
                if len(rows) >= target:
                    break
                if (obs.get("taxon") or {}).get("name") != species:
                    continue
                obs_id = obs.get("id")
                if not obs_id or obs_id in seen_observations:
                    continue
                for photo in obs.get("photos", []):
                    license_data = LICENSES.get(str(photo.get("license_code", "")).lower())
                    photo_id = photo.get("id")
                    image_url = photo.get("url") or ""
                    attribution = (photo.get("attribution") or "").strip()
                    if not license_data or not photo_id or photo_id in seen_photos or not image_url.startswith("https://") or not attribution:
                        continue
                    rows.append({
                        "source_id": "inaturalist-photo-" + str(photo_id),
                        "source_url": "https://www.inaturalist.org/photos/" + str(photo_id),
                        "image_url": image_url, "creator": attribution,
                        "license": license_data[0], "license_url": license_data[1],
                        "attribution": attribution, "observation_id": obs_id,
                        "photo_id": photo_id, "species_candidate": species,
                        "review_status": "UNREVIEWED",
                    })
                    seen_photos.add(photo_id)
                    seen_observations.add(obs_id)
                    break  # At most one photo per independent observation
            if pause:
                time.sleep(pause)
        if not found_any:
            break
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="training/inaturalist-review-queue.csv")
    parser.add_argument("--target", type=int, default=1000)
    parser.add_argument("--max-pages", type=int, default=12)
    parser.add_argument("--pause", type=float, default=1.1)
    parser.add_argument("--per-species", type=int, default=None, help="Legacy option; use --target instead")
    args = parser.parse_args()
    if not 1 <= args.target <= 1000 or not 1 <= args.max_pages <= 50 or args.pause < 1:
        raise SystemExit("Expected --target 1..1000, --max-pages 1..50 and --pause >= 1")
    rows = discover(args.target, args.max_pages, args.pause)
    with open(args.output, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {len(rows)} of {args.target} requested UNREVIEWED candidate records.")
    print("One photo per observation; CC BY version unverified; no photos downloaded or models trained.")


if __name__ == "__main__":
    main()
