#!/usr/bin/env python3
"""Find iNaturalist hornet photos with per-photo open license metadata.

Produces a REVIEW QUEUE, never training labels or automatically approved images.
"""
import argparse
import csv
import json
import urllib.parse
import urllib.request

LICENSES = {
    "cc0": ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "cc-by": ("CC-BY-4.0", "https://creativecommons.org/licenses/by/4.0/"),
}
FIELDS = ["source_id", "source_url", "image_url", "creator", "license", "license_url", "attribution", "observation_id", "photo_id", "species_candidate", "review_status"]
SPECIES = ("Vespa velutina", "Vespa crabro", "Vespula vulgaris")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="training/inaturalist-review-queue.csv")
    ap.add_argument("--per-species", type=int, default=20)
    args = ap.parse_args()
    if not 1 <= args.per_species <= 50:
        raise SystemExit("--per-species must be 1..50")
    rows = []
    seen = set()
    for species in SPECIES:
        params = urllib.parse.urlencode({"taxon_name": species, "quality_grade": "research", "photos": "true", "per_page": args.per_species, "order_by": "observed_on", "order": "desc"})
        url = "https://api.inaturalist.org/v1/observations?" + params
        req = urllib.request.Request(url, headers={"User-Agent": "BeekeeperMonitor-Research/1.0 (source review only)"})
        with urllib.request.urlopen(req, timeout=25) as response:
            data = json.load(response)
        for obs in data.get("results", []):
            if (obs.get("taxon") or {}).get("name") != species:
                continue
            for photo in obs.get("photos", []):
                license_data = LICENSES.get(str(photo.get("license_code", "")).lower())
                photo_id = photo.get("id")
                image_url = photo.get("url") or ""
                if not license_data or not photo_id or not image_url.startswith("https://") or photo_id in seen:
                    continue
                # The API returns a thumbnail; preserve it as supplied. The importer
                # will verify HTTPS, MIME, size and SHA256 at download time.
                seen.add(photo_id)
                attribution = photo.get("attribution") or ""
                if not attribution.strip():
                    continue
                rows.append({
                    "source_id": "inaturalist-photo-" + str(photo_id),
                    "source_url": "https://www.inaturalist.org/photos/" + str(photo_id),
                    "image_url": image_url,
                    "creator": attribution,
                    "license": license_data[0],
                    "license_url": license_data[1],
                    "attribution": attribution,
                    "observation_id": obs.get("id"),
                    "photo_id": photo_id,
                    "species_candidate": species,
                    "review_status": "UNREVIEWED",
                })
    with open(args.output, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {len(rows)} candidate photo records. All UNREVIEWED.")
    print("CC BY version must be confirmed on each original photo page before import.")
    print("No images downloaded, no training labels produced, no accuracy claimed.")

if __name__ == "__main__":
    main()
