#!/usr/bin/env python3
"""Select metadata candidates with exact CC0 rights for transient image screening.

This creates a review-only queue. It does not download images, approve records,
or treat a CC0 API label as independent proof of uploader authority.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

try:
    from training.dataset_groups import SPECIES_TO_GROUP
    from training.inaturalist_media import is_original_image_url
except ModuleNotFoundError:
    from dataset_groups import SPECIES_TO_GROUP
    from inaturalist_media import is_original_image_url

CC0_LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"
REQUIRED_FIELDS = {
    "source_id", "source_url", "image_url", "creator", "creator_login",
    "license", "license_url", "license_notice", "attribution",
    "observation_id", "photo_id", "species_candidate", "dataset_group",
    "review_status",
}
INVALID_IDENTITIES = {"", "unknown", "no rights reserved", "attribution unavailable"}


def select_cc0_candidates(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return only complete, exact-CC0, original-URL candidate rows."""
    selected = []
    seen_photos: set[str] = set()
    seen_observations: set[str] = set()
    seen_urls: set[str] = set()

    for index, row in enumerate(rows, start=2):
        if row.get("license") != "CC0-1.0":
            continue

        missing = sorted(field for field in REQUIRED_FIELDS if not str(row.get(field, "")).strip())
        if missing:
            raise ValueError(f"CC0 CSV row {index}: missing required fields: {', '.join(missing)}")
        if row["license_url"] != CC0_LICENSE_URL:
            raise ValueError(f"CC0 CSV row {index}: incorrect CC0 license URL")
        if row["review_status"] != "UNREVIEWED":
            raise ValueError(f"CC0 CSV row {index}: candidate must remain UNREVIEWED")

        creator = row["creator"].strip()
        login = row["creator_login"].strip()
        if creator.casefold() in INVALID_IDENTITIES or login.casefold() in INVALID_IDENTITIES:
            raise ValueError(f"CC0 CSV row {index}: creator identity is missing or mislabelled")
        if "no rights reserved" not in row["license_notice"].casefold():
            raise ValueError(f"CC0 CSV row {index}: source CC0 license notice is missing")
        if row["attribution"] != f"{creator}, no rights reserved (CC0)":
            raise ValueError(f"CC0 CSV row {index}: attribution does not match the creator")

        photo_id = row["photo_id"].strip()
        observation_id = row["observation_id"].strip()
        if not photo_id.isdecimal() or not observation_id.isdecimal():
            raise ValueError(f"CC0 CSV row {index}: photo/observation IDs must be numeric")
        if photo_id in seen_photos or observation_id in seen_observations:
            raise ValueError(f"CC0 CSV row {index}: duplicate photo or observation ID")

        source = urlsplit(row["source_url"])
        if (
            source.scheme != "https"
            or source.hostname != "www.inaturalist.org"
            or source.username or source.password
            or source.port not in (None, 443)
            or source.query or source.fragment
            or source.path != f"/observations/{observation_id}"
        ):
            raise ValueError(f"CC0 CSV row {index}: source URL does not bind to the observation ID")

        image = urlsplit(row["image_url"])
        if image.query or image.fragment or not is_original_image_url(row["image_url"], photo_id):
            raise ValueError(f"CC0 CSV row {index}: image URL is not the exact photo-bound original derivative")

        expected_group = SPECIES_TO_GROUP.get(row["species_candidate"])
        if expected_group is None or row["dataset_group"] != expected_group:
            raise ValueError(f"CC0 CSV row {index}: species and dataset group do not match")

        if row["image_url"] in seen_urls:
            raise ValueError(f"CC0 CSV row {index}: duplicate original image URL")
        if row["source_id"] != f"inaturalist-photo-{photo_id}":
            raise ValueError(f"CC0 CSV row {index}: source ID does not match photo ID")

        seen_photos.add(photo_id)
        seen_observations.add(observation_id)
        seen_urls.add(row["image_url"])
        selected.append(dict(row))

    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.input.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        missing = sorted(REQUIRED_FIELDS - set(fields))
        if missing:
            parser.error("Input CSV missing required columns: " + ", ".join(missing))
        rows = list(reader)

    selected = select_cc0_candidates(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(selected)

    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"candidate_count={len(selected)}\n")

    report = {
        "input_candidates": len(rows),
        "cc0_candidates_selected": len(selected),
        "non_cc0_candidates_excluded": len(rows) - len(selected),
        "images_downloaded": 0,
        "training_approvals": 0,
        "human_review_required": True,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
