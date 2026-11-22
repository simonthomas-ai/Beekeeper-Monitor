#!/usr/bin/env python3
"""Transiently screen iNaturalist originals for basic image quality.

Images are fetched into memory only. No image bytes are written to disk or
committed. PASS means decodable and sufficiently large, not biologically
verified, sharp enough for training, or approved for any use.
"""
import argparse
import csv
import io
import json
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError

from PIL import Image, ImageFilter, ImageOps, ImageStat, UnidentifiedImageError

try:
    from training.inaturalist_media import original_image_url
except ModuleNotFoundError:
    from inaturalist_media import original_image_url

MAX_IMAGE_BYTES = 16 * 1024 * 1024
MAX_PIXELS = 40_000_000
MIN_LONG_EDGE = 960
MIN_SHORT_EDGE = 480
MIN_PIXELS = 450_000
HIGH_QUALITY_LONG_EDGE = 1600
HIGH_QUALITY_SHORT_EDGE = 900
HIGH_QUALITY_PIXELS = 1_500_000
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
LICENSE_URLS = {
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
}
EXTRA_FIELDS = [
    "original_review_url", "image_width", "image_height", "image_megapixels",
    "image_bytes", "sharpness_score", "image_quality_status",
    "quality_reason", "quality_rank", "resolution_tier",
]


def _inspect_image(body):
    if not body or len(body) > MAX_IMAGE_BYTES:
        raise ValueError("image payload empty or exceeds size limit")
    with Image.open(io.BytesIO(body)) as raw:
        if raw.format not in ALLOWED_FORMATS:
            raise ValueError("unsupported image format")
        raw.verify()
    with Image.open(io.BytesIO(body)) as raw:
        image = ImageOps.exif_transpose(raw).convert("RGB")
        width, height = image.size
        pixels = width * height
        if width <= 0 or height <= 0 or pixels > MAX_PIXELS:
            raise ValueError("invalid or excessive image dimensions")
        sample = image.copy()
        sample.thumbnail((512, 512))
        edges = sample.convert("L").filter(ImageFilter.FIND_EDGES)
        sharpness = float(ImageStat.Stat(edges).stddev[0])
    return width, height, sharpness


def _validate_candidate_provenance(row):
    """Fail closed before any image request unless media rights are explicit."""
    if not isinstance(row, dict):
        raise ValueError("candidate row must be an object")
    license_code = row.get("license")
    if license_code not in LICENSE_URLS:
        raise ValueError("media license is missing, non-commercial, or version-unverified")
    if row.get("license_url") != LICENSE_URLS[license_code]:
        raise ValueError("media license URL does not match the exact supported license")
    for field in ("creator", "creator_login", "license_notice", "attribution"):
        if not str(row.get(field, "")).strip():
            raise ValueError("required rights provenance missing: " + field)
    creator = str(row["creator"]).strip()
    login = str(row["creator_login"]).strip()
    if creator.casefold() in {"unknown", "no rights reserved", "attribution unavailable"}:
        raise ValueError("creator identity is missing or mislabelled")
    if license_code == "CC0-1.0":
        if row["attribution"] != f"{creator}, no rights reserved (CC0)":
            raise ValueError("CC0 attribution statement does not match the creator")
        if "no rights reserved" not in row["license_notice"].casefold():
            raise ValueError("CC0 source license notice missing")
    elif creator.casefold() not in row["attribution"].casefold() and login.casefold() not in row["attribution"].casefold():
        raise ValueError("CC-BY attribution does not identify the creator or observer login")

    if row.get("review_status") != "UNREVIEWED":
        raise ValueError("quality screening input must remain UNREVIEWED")
    observation_id = str(row.get("observation_id", "")).strip()
    if not observation_id.isdecimal():
        raise ValueError("invalid observation ID")
    source = urlsplit(str(row.get("source_url", "")))
    if (
        source.scheme != "https"
        or source.hostname != "www.inaturalist.org"
        or source.username or source.password
        or source.port not in (None, 443)
        or source.query or source.fragment
        or source.path != f"/observations/{observation_id}"
    ):
        raise ValueError("source URL does not bind to the observation ID")


def inspect_candidate(row, timeout=25):
    photo_id = str(row.get("photo_id", "")).strip()
    raw_url = row.get("image_url", "")
    result = dict(row)
    result.update({
        "original_review_url": "",
        "image_width": "",
        "image_height": "",
        "image_megapixels": "",
        "image_bytes": "",
        "sharpness_score": "",
        "image_quality_status": "UNAVAILABLE",
        "quality_reason": "",
        "quality_rank": "",
        "resolution_tier": "UNVERIFIED",
    })
    try:
        _validate_candidate_provenance(row)
        if not photo_id.isdecimal():
            raise ValueError("invalid photo ID")
        original_url = original_image_url(raw_url, photo_id)
        result["original_review_url"] = original_url
        request = urllib.request.Request(
            original_url,
            headers={
                "User-Agent": "BeekeeperMonitor-ImageQualityReview/1.0 (noncommercial; transient in-memory screening)",
                "Accept": "image/jpeg,image/png,image/webp",
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            final_url = response.geturl()
            # Redirects must remain on a recognized iNaturalist image host and
            # resolve to this exact photo's original derivative.
            final_original = original_image_url(final_url, photo_id)
            if final_original != final_url:
                raise ValueError("image redirect did not resolve to the original derivative")
            content_type = (response.headers.get("Content-Type") or "").split(";")[0].lower()
            if content_type and not content_type.startswith("image/"):
                raise ValueError("response is not an image")
            body = response.read(MAX_IMAGE_BYTES + 1)
        width, height, sharpness = _inspect_image(body)
        pixels = width * height
        result["resolution_tier"] = ("HIGH_RESOLUTION" if max(width, height) >= HIGH_QUALITY_LONG_EDGE
            and min(width, height) >= HIGH_QUALITY_SHORT_EDGE
            and pixels >= HIGH_QUALITY_PIXELS else "STANDARD")
        result.update({
            "image_width": width,
            "image_height": height,
            "image_megapixels": round(pixels / 1_000_000, 3),
            "image_bytes": len(body),
            "sharpness_score": round(sharpness, 2),
        })
        if max(width, height) < MIN_LONG_EDGE or min(width, height) < MIN_SHORT_EDGE or pixels < MIN_PIXELS:
            result["resolution_tier"] = "REJECTED"
            reasons = []
            if max(width, height) < MIN_LONG_EDGE:
                reasons.append("long edge below " + str(MIN_LONG_EDGE) + " px")
            if min(width, height) < MIN_SHORT_EDGE:
                reasons.append("short edge below " + str(MIN_SHORT_EDGE) + " px")
            if pixels < MIN_PIXELS:
                reasons.append("below " + str(MIN_PIXELS) + " total pixels")
            result["image_quality_status"] = "REJECT_LOW_RESOLUTION"
            result["quality_reason"] = "; ".join(reasons)
        else:
            result["image_quality_status"] = "PASS"
            result["quality_reason"] = "dimensions and image decoding passed; sharpness score is ranking-only"
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, UnidentifiedImageError) as exc:
        result["quality_reason"] = type(exc).__name__ + ": " + str(exc)[:240]
    return result


def screen_rows(rows, pause=0.15, timeout=25):
    if pause < 0 or timeout <= 0:
        raise ValueError("pause must be non-negative and timeout must be positive")
    output = []
    for index, row in enumerate(rows, 1):
        output.append(inspect_candidate(row, timeout=timeout))
        if pause and index < len(rows):
            time.sleep(pause)

    # A simple edge-contrast statistic is only a ranking aid. It is not a
    # calibrated blur detector and must never make a training decision.
    groups = defaultdict(list)
    for row in output:
        if row["image_quality_status"] == "PASS":
            groups[row.get("species_candidate", "UNKNOWN")].append(row)
    for species_rows in groups.values():
        species_rows.sort(
            key=lambda r: (float(r["sharpness_score"]), int(r["image_width"]) * int(r["image_height"])),
            reverse=True,
        )
        for rank, row in enumerate(species_rows, 1):
            row["quality_rank"] = rank

    output.sort(key=lambda r: (
        r.get("species_candidate", ""),
        0 if r["image_quality_status"] == "PASS" else 1,
        int(r["quality_rank"] or 10**9),
        r.get("observation_id", ""),
    ))
    return output


def main():
    parser = argparse.ArgumentParser(description="Screen original iNaturalist image files in memory; save metadata only.")
    parser.add_argument("--input", default="training/inaturalist-review-queue.csv")
    parser.add_argument("--output", default="training/inaturalist-quality-screen.csv")
    parser.add_argument("--pause", type=float, default=0.15)
    parser.add_argument("--timeout", type=int, default=25)
    args = parser.parse_args()
    if args.pause < 0 or args.timeout <= 0:
        parser.error("--pause must be non-negative and --timeout must be positive")

    source = Path(args.input)
    with source.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not {"photo_id", "image_url", "species_candidate"}.issubset(reader.fieldnames):
            raise SystemExit("Input CSV is missing required columns")
        rows = list(reader)
    if not rows:
        raise SystemExit("No candidate rows to screen")

    screened = screen_rows(rows, pause=args.pause, timeout=args.timeout)
    fields = list(dict.fromkeys(list(reader.fieldnames) + EXTRA_FIELDS))
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(screened)

    status_counts = Counter(row["image_quality_status"] for row in screened)
    species_counts = {}
    for species in sorted({row.get("species_candidate", "") for row in screened}):
        subset = [row for row in screened if row.get("species_candidate") == species]
        species_counts[species] = {
            "candidates": len(subset),
            "passed": sum(row["image_quality_status"] == "PASS" for row in subset),
            "high_resolution": sum(row["image_quality_status"] == "PASS" and row["resolution_tier"] == "HIGH_RESOLUTION" for row in subset),
            "standard_resolution": sum(row["image_quality_status"] == "PASS" and row["resolution_tier"] == "STANDARD" for row in subset),
            "rejected_or_unavailable": sum(row["image_quality_status"] != "PASS" for row in subset),
        }
    report = {
        "input_candidates": len(screened),
        "status_counts": dict(status_counts),
        "by_species": species_counts,
        "image_bytes_persisted": False,
        "high_resolution_candidates": sum(r["image_quality_status"] == "PASS" and r["resolution_tier"] == "HIGH_RESOLUTION" for r in screened),
        "training_approvals": 0,
        "warning": "PASS checks file decoding and pixel dimensions only. Sharpness is ranking-only; insect visibility, focus on the insect, taxonomy, rights and annotations require human review.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
