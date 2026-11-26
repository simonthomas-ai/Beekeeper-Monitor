#!/usr/bin/env python3
"""Fail-closed structural audit of unreviewed iNaturalist CC0 candidate metadata."""
import argparse
import collections
import csv
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

try:
    from training.discover_cc0_candidates import FIELDS as DISCOVERY_FIELDS
    from training.dataset_groups import SPECIES_TO_GROUP
    from training.inaturalist_media import ALLOWED_HOSTS
except ModuleNotFoundError:
    from discover_cc0_candidates import FIELDS as DISCOVERY_FIELDS
    from dataset_groups import SPECIES_TO_GROUP
    from inaturalist_media import ALLOWED_HOSTS

# Reuse the producer's exact schema so the audit cannot silently drift.
FIELDS = tuple(DISCOVERY_FIELDS)
LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"
OBSERVATION_BASE = "https://www.inaturalist.org/observations/"
ORIGINAL_IMAGE_PATH = re.compile(r"^/photos/([0-9]+)/original\.(?:jpe?g|png|webp)$", re.IGNORECASE)
SPECIES = set(SPECIES_TO_GROUP)


def _safe_text(value, *, required=False, maximum=1000):
    if not isinstance(value, str) or len(value) > maximum:
        return False
    if required and not value.strip():
        return False
    if value != value.strip():
        return False
    return not any(ord(char) < 32 or ord(char) == 127 for char in value)


def _safe_https_url(value, *, hosts):
    if not _safe_text(value, required=True, maximum=2048):
        return None
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme != "https"
        or (parsed.hostname or "").lower() not in hosts
        or parsed.username
        or parsed.password
        or port not in (None, 443)
        or parsed.query
        or parsed.fragment
    ):
        return None
    return parsed


def audit(path):
    errors = []
    counts = collections.Counter()
    seen_photos, seen_observations, seen_urls = set(), set(), set()

    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or tuple(reader.fieldnames) != FIELDS:
            return {
                "status": "blocked",
                "errors": ["Unexpected CSV columns"],
                "counts": {},
                "total": 0,
                "approved": 0,
            }

        for line, row in enumerate(reader, 2):
            species = row.get("species_candidate", "")
            photo_id = row.get("photo_id", "")
            observation_id = row.get("observation_id", "")
            creator = row.get("creator", "")
            creator_login = row.get("creator_login", "")
            counts[species] += 1

            if species not in SPECIES:
                errors.append(f"line {line}: unknown species")
            elif row.get("dataset_group") != SPECIES_TO_GROUP[species]:
                errors.append(f"line {line}: dataset group/species mismatch")

            if row.get("license") != "CC0-1.0" or row.get("license_url") != LICENSE_URL:
                errors.append(f"line {line}: license metadata mismatch")
            if row.get("review_status") != "UNREVIEWED":
                errors.append(f"line {line}: invalid review status")

            if not isinstance(photo_id, str) or not photo_id.isdecimal() or row.get("source_id") != "inat-photo-" + photo_id:
                errors.append(f"line {line}: invalid photo ID")
            if (
                not isinstance(observation_id, str) or not observation_id.isdecimal()
                or row.get("source_url") != OBSERVATION_BASE + observation_id
            ):
                errors.append(f"line {line}: invalid observation URL")

            if not _safe_text(creator, required=True, maximum=200):
                errors.append(f"line {line}: missing or unsafe creator name")
            if not _safe_text(creator_login, required=True, maximum=100):
                errors.append(f"line {line}: missing or unsafe creator login")
            if not _safe_text(row.get("license_notice", ""), maximum=1000):
                errors.append(f"line {line}: unsafe license notice")
            expected_attribution = f"{creator}, no rights reserved (CC0)"
            if row.get("attribution") != expected_attribution:
                errors.append(f"line {line}: attribution does not match creator metadata")

            image = _safe_https_url(row.get("image_url", ""), hosts=ALLOWED_HOSTS)
            if image is None:
                errors.append(f"line {line}: unexpected or unsafe image URL")
            else:
                match = ORIGINAL_IMAGE_PATH.fullmatch(image.path)
                if not match or match.group(1) != photo_id:
                    errors.append(f"line {line}: image URL is not the matching original photo")

            for label, value, seen in (
                ("photo", photo_id, seen_photos),
                ("observation", observation_id, seen_observations),
                ("image URL", row.get("image_url", ""), seen_urls),
            ):
                if value in seen:
                    errors.append(f"line {line}: duplicate {label}")
                seen.add(value)

    if not seen_photos:
        errors.append("No candidate records")

    return {
        "status": "metadata_passed_human_review_required" if not errors else "blocked",
        "errors": errors[:100],
        "counts": dict(sorted(counts.items())),
        "total": len(seen_photos),
        "approved": 0,
        "note": (
            "Structural metadata audit only. Does not verify live licenses, image contents, "
            "species labels or image quality. Human review remains mandatory."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = audit(args.input)
    Path(args.output).write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
