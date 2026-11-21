#!/usr/bin/env python3
"""Download exact iNaturalist original-file bytes for a CC0 visual-review page.

No resizing, EXIF rewriting, re-encoding, recompression, thumbnail generation or
content transformation occurs. The bytes are written exactly as received.
Only candidates with an exact, successful CC0 API recheck are accepted.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError

from PIL import Image, UnidentifiedImageError

try:
    from training.inaturalist_media import original_image_url, ALLOWED_HOSTS
except ModuleNotFoundError:
    from inaturalist_media import original_image_url, ALLOWED_HOSTS

MAX_IMAGE_BYTES = 30 * 1024 * 1024
MAX_PIXELS = 40_000_000
ALLOWED_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
MANIFEST_FIELDS = [
    "photo_id", "observation_id", "species_candidate", "source_url",
    "license", "creator", "source_image_url", "local_image_path",
    "image_format", "image_width", "image_height", "image_bytes",
    "sha256", "download_status",
]


def _load_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def _verified_cc0(verification, species):
    result = {}
    for row in verification:
        pid = str(row.get("photo_id", ""))
        if not pid.isdecimal():
            continue
        if (row.get("api_photo_found") == "YES"
                and row.get("license_metadata_match") == "YES"
                and row.get("api_photo_license", "").lower() == "cc0"
                and row.get("api_taxon") == species
                and row.get("api_quality_grade") == "research"
                and not row.get("error")):
            result[pid] = row
    return result


def _download_exact_original(url, photo_id, timeout=25):
    requested = original_image_url(url, photo_id)
    request = urllib.request.Request(
        requested,
        headers={
            "User-Agent": "BeekeeperMonitor-OriginalCC0Image/1.0 (attribution retained; byte-preserving review copy)",
            "Accept": "image/jpeg,image/png,image/webp",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        parsed = urlsplit(final_url)
        if parsed.scheme != "https" or (parsed.hostname or "").lower() not in ALLOWED_HOSTS:
            raise ValueError("redirect left the trusted iNaturalist image hosts")
        if original_image_url(final_url, photo_id) != final_url:
            raise ValueError("redirect did not resolve to the matching original image derivative")
        content_type = (response.headers.get("Content-Type") or "").split(";")[0].lower()
        if content_type and not content_type.startswith("image/"):
            raise ValueError("server response is not an image")
        body = response.read(MAX_IMAGE_BYTES + 1)
    if not body or len(body) > MAX_IMAGE_BYTES:
        raise ValueError("original image is empty or larger than 30 MiB")

    with Image.open(io.BytesIO(body)) as image:
        image_format = image.format
        width, height = image.size
        if image_format not in ALLOWED_FORMATS:
            raise ValueError("unsupported source image format")
        if width <= 0 or height <= 0 or width * height > MAX_PIXELS:
            raise ValueError("invalid or excessive image dimensions")
        image.verify()

    # Hash and persist the exact response body: Pillow is used only to inspect
    # the container and dimensions; it never saves or modifies image bytes.
    digest = hashlib.sha256(body).hexdigest()
    return body, image_format, width, height, digest, requested


def download_originals(input_csv, verification_csv, species, output_dir, manifest,
                       pause=0.15, timeout=25):
    if pause < 0 or timeout <= 0:
        raise ValueError("pause must be non-negative and timeout must be positive")
    rows = _load_csv(input_csv)
    verification = _verified_cc0(_load_csv(verification_csv), species)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates = [
        row for row in rows
        if row.get("species_candidate") == species
        and row.get("license") == "CC0-1.0"
        and row.get("image_quality_status") == "PASS"
        and str(row.get("photo_id", "")).isdecimal()
        and str(row.get("photo_id")) in verification
    ]
    if not candidates:
        raise ValueError("No image passed both the image screen and the exact CC0 API recheck")

    seen = set()
    manifest_rows = []
    errors = []
    for index, row in enumerate(candidates, 1):
        pid = str(row["photo_id"])
        if pid in seen:
            raise ValueError("Duplicate photo ID in original-image download queue")
        seen.add(pid)
        checked = verification[pid]
        if str(row.get("observation_id", "")) != str(checked.get("observation_id", "")):
            errors.append({"photo_id": pid, "error": "observation ID differs from CC0 recheck"})
            continue
        if str(row.get("source_url", "")) != str(checked.get("source_url", "")):
            errors.append({"photo_id": pid, "error": "source URL differs from CC0 recheck"})
            continue
        try:
            body, image_format, width, height, digest, requested = _download_exact_original(
                row.get("image_url", ""), pid, timeout
            )
            suffix = ALLOWED_FORMATS[image_format]
            filename = pid + suffix
            destination = output_dir / filename
            temporary = destination.with_suffix(destination.suffix + ".part")
            temporary.write_bytes(body)
            os.replace(temporary, destination)
            manifest_rows.append({
                "photo_id": pid,
                "observation_id": str(row.get("observation_id", "")),
                "species_candidate": species,
                "source_url": row.get("source_url", ""),
                "license": "CC0-1.0",
                "creator": row.get("creator") or row.get("attribution") or "Attribution unavailable",
                "source_image_url": requested,
                "local_image_path": "images/velutina/" + filename,
                "image_format": image_format,
                "image_width": width,
                "image_height": height,
                "image_bytes": len(body),
                "sha256": digest,
                "download_status": "DOWNLOADED_UNMODIFIED",
            })
        except (HTTPError, URLError, TimeoutError, OSError, ValueError,
                UnidentifiedImageError) as exc:
            errors.append({"photo_id": pid, "error": type(exc).__name__ + ": " + str(exc)[:240]})
        if pause and index < len(candidates):
            time.sleep(pause)

    if not manifest_rows:
        raise RuntimeError("No original files could be downloaded; refusing to publish an empty gallery")
    manifest = Path(manifest)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(manifest_rows)

    report = {
        "species": species,
        "metadata_verified_and_quality_screen_passed": len(candidates),
        "exact_original_files_downloaded": len(manifest_rows),
        "download_failures": len(errors),
        "bytes_persisted_without_modification": sum(int(row["image_bytes"]) for row in manifest_rows),
        "all_source_licenses": "CC0-1.0",
        "training_approvals": 0,
        "manifest": str(manifest),
        "failures": errors,
        "note": "Image bytes are stored as received. No resize, crop, rotation, re-encoding or compression was performed.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if errors:
        # Keep successful assets and record failures, but the manifest exposes
        # exactly which photos were retrieved successfully.
        Path(str(manifest) + ".errors.json").write_text(
            json.dumps(errors, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return manifest_rows


def main():
    parser = argparse.ArgumentParser(description="Save unchanged CC0 iNaturalist original-image bytes for the public review page.")
    parser.add_argument("--input", required=True, help="Quality-screen CSV")
    parser.add_argument("--verification", required=True, help="Per-photo iNaturalist CC0 API verification CSV")
    parser.add_argument("--species", default="Vespa velutina")
    parser.add_argument("--output-dir", default="public-review-assets/images/velutina")
    parser.add_argument("--manifest", default="public-review-assets/velutina-original-images-manifest.csv")
    parser.add_argument("--pause", type=float, default=0.15)
    parser.add_argument("--timeout", type=int, default=25)
    args = parser.parse_args()
    download_originals(args.input, args.verification, args.species,
                       args.output_dir, args.manifest, args.pause, args.timeout)


if __name__ == "__main__":
    main()
