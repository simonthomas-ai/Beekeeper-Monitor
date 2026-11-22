#!/usr/bin/env python3
"""Discover balanced iNaturalist insect photo candidates; metadata only.

Five operational dataset groups receive an equal share. Scientific taxon names
remain separate, and each observation contributes at most one photo.
"""
import argparse
import csv
import json
import time
import urllib.parse
import urllib.request

try:
    from training.dataset_groups import (
        GROUPS, GROUP_LABELS, SPECIES, SPECIES_TO_GROUP,
        balanced_quotas, balanced_taxon_quotas,
    )
    from training.inaturalist_media import original_image_url
except ModuleNotFoundError:
    from dataset_groups import (
        GROUPS, GROUP_LABELS, SPECIES, SPECIES_TO_GROUP,
        balanced_quotas, balanced_taxon_quotas,
    )
    from inaturalist_media import original_image_url

LICENSES = {
    "cc0": ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    "cc-by": ("CC-BY-VERSION-UNVERIFIED", ""),
}
FIELDS = [
    "source_id", "source_url", "image_url", "creator", "creator_login",
    "license", "license_url", "license_notice", "attribution",
    "observation_id", "photo_id", "species_candidate", "dataset_group",
    "review_status",
]


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


def _candidate_from_observation(obs, species, seen_photos, seen_observations):
    """Return one valid, original-resolution candidate from an observation."""
    if not isinstance(obs, dict) or obs.get("quality_grade") != "research":
        return None
    if (obs.get("taxon") or {}).get("name") != species:
        return None
    observation_id = obs.get("id")
    if not observation_id or str(observation_id) in seen_observations:
        return None
    for photo in obs.get("photos", []):
        photo_id = photo.get("id")
        if not photo_id or str(photo_id) in seen_photos:
            continue
        license_data = LICENSES.get(str(photo.get("license_code", "")).lower())
        license_notice = (photo.get("attribution") or "").strip()
        if not license_data or not license_notice:
            continue

        observer = obs.get("user")
        if not isinstance(observer, dict):
            observer = {}
        creator_login = str(observer.get("login") or obs.get("user_login") or "").strip()
        creator_name = str(observer.get("name") or "").strip()
        creator = creator_name or creator_login
        if not creator_login or not creator:
            continue

        # Keep creator identity, the source-provided media notice and the
        # formatted attribution as separate fields. iNaturalist documents this
        # CC0 attribution form; CC BY stays version-unverified until photo-page
        # review, so its source-provided attribution is preserved verbatim.
        if license_data[0] == "CC0-1.0":
            attribution = f"{creator}, no rights reserved (CC0)"
        else:
            attribution = license_notice
            identity = creator.casefold()
            login = creator_login.casefold()
            notice = attribution.casefold()
            if identity not in notice and login not in notice:
                continue

        try:
            image_url = original_image_url(photo.get("url") or "", photo_id)
        except ValueError:
            # Fail closed: never place an unknown or thumbnail URL in the queue.
            continue
        seen_photos.add(str(photo_id))
        seen_observations.add(str(observation_id))
        return {
            "source_id": "inaturalist-photo-" + str(photo_id),
            "source_url": "https://www.inaturalist.org/observations/" + str(observation_id),
            "image_url": image_url,
            "creator": creator,
            "creator_login": creator_login,
            "license": license_data[0],
            "license_url": license_data[1],
            "license_notice": license_notice,
            "attribution": attribution,
            "observation_id": str(observation_id),
            "photo_id": str(photo_id),
            "species_candidate": species,
            "dataset_group": SPECIES_TO_GROUP[species],
            "review_status": "UNREVIEWED",
        }
    return None


def _select_balanced(pools, target):
    """Meet group totals while balancing scientific taxa where data permit."""
    group_targets = balanced_quotas(target)
    selected = []
    by_group = {}
    by_species = {}
    for group, members in GROUPS.items():
        quota = group_targets[group]
        taxon_targets = balanced_taxon_quotas(group, quota)
        group_rows = []
        used = {species: 0 for species in members}

        # First pass: enforce an even per-taxon share when sufficient candidates exist.
        for species in members:
            wanted = taxon_targets[species]
            take = min(wanted, len(pools[species]))
            group_rows.extend(pools[species][:take])
            used[species] = take

        # Second pass: backfill any shortage from other taxa in this same group.
        remaining = quota - len(group_rows)
        offset = 0
        while remaining:
            added = False
            for species in members:
                index = used[species] + offset
                if index < len(pools[species]):
                    group_rows.append(pools[species][index])
                    remaining -= 1
                    added = True
                    if remaining == 0:
                        break
            if not added:
                break
            offset += 1

        selected.extend(group_rows)
        by_group[group] = len(group_rows)
        for species in members:
            by_species[species] = sum(
                row["species_candidate"] == species for row in group_rows
            )
    return selected, by_group, by_species, group_targets


def discover(target, max_pages, pause):
    """Fetch metadata pools, then select up to target with five equal group quotas."""
    if type(target) is not int or not 1 <= target <= 1000:
        raise ValueError("target must be 1..1000")
    if type(max_pages) is not int or not 1 <= max_pages <= 50:
        raise ValueError("max_pages must be 1..50")
    if not isinstance(pause, (int, float)) or pause < 0:
        raise ValueError("pause must be non-negative")

    group_targets = balanced_quotas(target)
    pools = {species: [] for species in SPECIES}
    seen_photos, seen_observations = set(), set()

    # Collect up to one group's quota from each underlying taxon. This permits
    # balanced subtype sampling (e.g. two bumblebee taxa) and within-group backfill.
    for page in range(1, max_pages + 1):
        found_any = False
        for species in SPECIES:
            group = SPECIES_TO_GROUP[species]
            if len(pools[species]) >= group_targets[group]:
                continue
            observations = fetch_observations(species, page)
            if observations:
                found_any = True
            for observation in observations:
                if len(pools[species]) >= group_targets[group]:
                    break
                candidate = _candidate_from_observation(
                    observation, species, seen_photos, seen_observations
                )
                if candidate:
                    pools[species].append(candidate)
            if pause:
                time.sleep(pause)
        if all(
            len(pools[species]) >= group_targets[SPECIES_TO_GROUP[species]]
            for species in SPECIES
        ):
            break
        if not found_any:
            break

    return _select_balanced(pools, target)[0]


def main():
    parser = argparse.ArgumentParser(
        description="Discover up to 1000 iNaturalist candidates balanced across five groups."
    )
    parser.add_argument("--output", default="training/inaturalist-review-queue.csv")
    parser.add_argument("--target", type=int, default=1000)
    parser.add_argument("--max-pages", type=int, default=12)
    parser.add_argument("--pause", type=float, default=1.1)
    args = parser.parse_args()
    if not 1 <= args.target <= 1000 or not 1 <= args.max_pages <= 50 or args.pause < 0:
        parser.error("Expected --target 1..1000, --max-pages 1..50 and --pause >= 0")

    rows = discover(args.target, args.max_pages, args.pause)
    with open(args.output, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    selected, by_group, by_species, targets = _select_balanced(
        {name: [row for row in rows if row["species_candidate"] == name] for name in SPECIES},
        args.target,
    )
    report = {
        "requested_total": args.target,
        "actual_total": len(rows),
        "group_targets": targets,
        "group_actual": by_group,
        "species_actual": by_species,
        "shortfalls": {group: targets[group] - by_group[group] for group in GROUPS},
        "training_approved": 0,
        "status": "BALANCED_CANDIDATE_QUEUE" if len(rows) == args.target else "SOURCE_SHORTFALL",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("One photo per observation; original-resolution URLs; no images downloaded or models trained.")


if __name__ == "__main__":
    main()
