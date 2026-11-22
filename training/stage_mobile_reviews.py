#!/usr/bin/env python3
"""Validate mobile reviews and stage a NON-APPROVED expert queue.

Remote HTTPS candidates remain supported. Locally stored iNaturalist originals
are accepted only when the supplied artifact root contains the matching
manifest row and the actual file passes its recorded byte-count and SHA-256.
This tool never generates YOLO labels, reviewed-annotations.json or approvals.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

SPECIES = {
    "Vespa velutina", "Vespa crabro", "Apis mellifera",
    "Bombus terrestris", "Vespula vulgaris",
}
DECISIONS = {"PENDING", "LIKELY", "REJECT"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
LOCAL_IMAGE_RE = re.compile(r"^[0-9]+\.(?:jpg|jpeg|png|webp)$", re.IGNORECASE)
MANIFEST_NAME = "velutina-original-images-manifest.csv"
MANIFEST_FIELDS = {
    "photo_id", "observation_id", "species_candidate", "source_url", "license",
    "creator", "creator_login", "attribution", "license_notice", "source_image_url",
    "local_image_path", "image_format", "image_width", "image_height",
    "image_bytes", "sha256", "download_status",
}


def _https_url(value: object, field: str, index: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Record {index}: invalid {field}")
    url = urlsplit(value)
    if url.scheme != "https" or not url.hostname or url.username or url.password or url.fragment:
        raise ValueError(f"Record {index}: {field} must be a credential-free HTTPS URL")
    if url.port not in (None, 443):
        raise ValueError(f"Record {index}: unexpected port in {field}")
    return value


def _is_original_image_url(value: object, photo_id: str) -> bool:
    """Accept only the direct, photo-ID-bound iNaturalist original URL."""
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    allowed_hosts = {
        "static.inaturalist.org",
        "inaturalist-open-data.s3.amazonaws.com",
        "inaturalist-open-data.s3.us-west-2.amazonaws.com",
    }
    return (
        parsed.scheme == "https"
        and (parsed.hostname or "").lower() in allowed_hosts
        and parsed.username is None
        and parsed.password is None
        and parsed.port in (None, 443)
        and not parsed.query
        and not parsed.fragment
        and re.fullmatch(
            rf"/photos/{re.escape(photo_id)}/original\\.(?:jpe?g|png|webp)",
            parsed.path,
            re.IGNORECASE,
        ) is not None
    )


def _asset_root(path: str | Path) -> Path:
    requested = Path(path).expanduser()
    if not requested.is_absolute():
        requested = Path.cwd() / requested
    cursor = Path(requested.anchor)
    for part in requested.parts[1:]:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("Local original asset root must not contain symbolic links")
    root = requested.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Local original asset root must be a directory")
    return root


def _read_asset_manifest(root: Path) -> dict[str, dict[str, str]]:
    manifest = root / MANIFEST_NAME
    if manifest.is_symlink() or not manifest.is_file():
        raise ValueError(f"Local original-image manifest missing or unsafe: {MANIFEST_NAME}")
    assets: dict[str, dict[str, str]] = {}
    try:
        with manifest.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            fields = set(reader.fieldnames or ())
            missing = MANIFEST_FIELDS - fields
            if missing:
                raise ValueError(
                    "Local original-image manifest missing columns: " + ", ".join(sorted(missing))
                )
            for line, row in enumerate(reader, start=2):
                photo_id = str(row.get("photo_id", "")).strip()
                if not photo_id.isdecimal() or photo_id in assets:
                    raise ValueError(f"Local original-image manifest line {line}: invalid/duplicate photo_id")
                assets[photo_id] = dict(row)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ValueError("Unable to read local original-image manifest") from exc
    if not assets:
        raise ValueError("Local original-image manifest is empty")
    return assets


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_local_original(
    row: dict, photo_id: str, image_url: str, root: Path,
    assets: dict[str, dict[str, str]], index: int,
) -> dict:
    if row.get("image_delivery") != "LOCAL_UNMODIFIED_ORIGINAL":
        raise ValueError(f"Record {index}: local image path is not marked as an unchanged original")
    if not isinstance(image_url, str) or "\\" in image_url:
        raise ValueError(f"Record {index}: unsafe local image path")
    relative = PurePosixPath(image_url)
    if (
        relative.as_posix() != image_url
        or relative.is_absolute()
        or len(relative.parts) != 3
        or relative.parts[:2] != ("images", "velutina")
        or any(part in ("", ".", "..") for part in relative.parts)
        or not LOCAL_IMAGE_RE.fullmatch(relative.name)
        or Path(relative.name).stem != photo_id
    ):
        raise ValueError(f"Record {index}: local path is outside approved images/velutina layout")

    asset = assets.get(photo_id)
    if not asset:
        raise ValueError(f"Record {index}: photo ID is not present in the local original-image manifest")
    if asset.get("local_image_path") != image_url:
        raise ValueError(f"Record {index}: local path does not match its manifest entry")
    creator = str(asset.get("creator", "")).strip()
    creator_login = str(asset.get("creator_login", "")).strip()
    attribution = str(asset.get("attribution", "")).strip()
    license_notice = str(asset.get("license_notice", "")).strip()
    source_image_url = str(asset.get("source_image_url", "")).strip()
    if (
        asset.get("species_candidate") != "Vespa velutina"
        or asset.get("license") != "CC0-1.0"
        or asset.get("download_status") != "DOWNLOADED_UNMODIFIED"
        or not creator
        or not creator_login
        or attribution != f"{creator}, no rights reserved (CC0)"
        or "no rights reserved" not in license_notice.casefold()
        or not _is_original_image_url(source_image_url, photo_id)
        or asset.get("observation_id") != str(row.get("observation_id", ""))
        or asset.get("source_url") != str(row.get("source_url", ""))
    ):
        raise ValueError(f"Record {index}: local original provenance metadata is missing or differs from the manifest")

    # The manifest is authoritative. When an upstream queue includes copied
    # provenance fields, reject tampering rather than silently accepting it.
    for field, expected in (
        ("creator_login", creator_login),
        ("attribution", attribution),
        ("license_notice", license_notice),
        ("source_image_url", source_image_url),
    ):
        if field in row and row[field] != expected:
            raise ValueError(f"Record {index}: {field} differs from the verified manifest")

    digest = str(asset.get("sha256", ""))
    byte_count = str(asset.get("image_bytes", ""))
    if not SHA256_RE.fullmatch(digest) or not byte_count.isdecimal() or int(byte_count) <= 0:
        raise ValueError(f"Record {index}: local original manifest has invalid byte/hash metadata")
    if row.get("original_sha256") != digest:
        raise ValueError(f"Record {index}: mobile review SHA-256 differs from the manifest")
    if str(row.get("original_file_bytes", "")) != byte_count:
        raise ValueError(f"Record {index}: mobile review byte count differs from the manifest")
    if row.get("license") != asset.get("license") or row.get("creator") != asset.get("creator"):
        raise ValueError(f"Record {index}: mobile review rights metadata differs from the manifest")

    candidate = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Record {index}: local original file must not be a symbolic link")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ValueError(f"Record {index}: local original file is missing or outside the asset root") from exc
    if not resolved.is_file() or resolved.stat().st_size != int(byte_count):
        raise ValueError(f"Record {index}: local original file byte count differs from the manifest")
    if _sha256(resolved) != digest:
        raise ValueError(f"Record {index}: local original file SHA-256 differs from the manifest")

    return {
        "image_delivery": "LOCAL_UNMODIFIED_ORIGINAL",
        "local_image_path": image_url,
        "original_sha256": digest,
        "original_file_bytes": int(byte_count),
        "creator": asset["creator"],
        "license": asset["license"],
        "creator_login": creator_login,
        "attribution": attribution,
        "license_notice": license_notice,
        "source_image_url": source_image_url,
    }


def stage(payload, *, asset_root: str | Path | None = None):
    if not isinstance(payload, dict) or payload.get("format") != "vespaguard-unverified-mobile-review-v1":
        raise ValueError("Unsupported mobile review format")
    species = payload.get("species")
    if species not in SPECIES and species != "ALL":
        raise ValueError("Unknown species")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("Nonempty records required")

    root = _asset_root(asset_root) if asset_root is not None else None
    assets = _read_asset_manifest(root) if root is not None else {}
    seen = set()
    queue = []
    for i, row in enumerate(records):
        if not isinstance(row, dict) or row.get("species_candidate") not in SPECIES or (species != "ALL" and row.get("species_candidate") != species):
            raise ValueError(f"Record {i}: species mismatch")
        photo_id = str(row.get("photo_id", "")).strip()
        if not photo_id or photo_id in seen:
            raise ValueError(f"Record {i}: duplicate or empty photo ID")
        seen.add(photo_id)
        if row.get("training_eligible") is not False:
            raise ValueError(f"Record {i}: mobile review cannot grant training eligibility")

        source_url = _https_url(row.get("source_url"), "source_url", i)
        image_url = row.get("image_url")
        local_metadata = None
        parsed_image = urlsplit(str(image_url or ""))
        if parsed_image.scheme == "https":
            image_url = _https_url(image_url, "image_url", i)
            if row.get("image_delivery") == "LOCAL_UNMODIFIED_ORIGINAL":
                raise ValueError(f"Record {i}: locally marked original must use its relative manifest path")
        else:
            if root is None:
                raise ValueError(
                    f"Record {i}: local original requires --asset-root with the downloaded image manifest and bytes"
                )
            local_metadata = _verify_local_original(row, photo_id, image_url, root, assets, i)

        review = row.get("review")
        if not isinstance(review, dict) or review.get("decision") not in DECISIONS:
            raise ValueError(f"Record {i}: invalid decision")
        boxes = review.get("boxes")
        if not isinstance(boxes, list) or len(boxes) > 100:
            raise ValueError(f"Record {i}: invalid boxes")
        for box in boxes:
            if not isinstance(box, dict) or set(box) != {"x", "y", "width", "height"}:
                raise ValueError(f"Record {i}: invalid box")
            if any(type(box[k]) not in (int, float) or not math.isfinite(box[k]) for k in box):
                raise ValueError(f"Record {i}: non-finite box coordinate")
            x, y, w, h = (box[k] for k in ("x", "y", "width", "height"))
            if w <= 0 or h <= 0 or x-w/2 < 0 or x+w/2 > 1 or y-h/2 < 0 or y+h/2 > 1:
                raise ValueError(f"Record {i}: box outside image")

        staged = {
            "photo_id": photo_id,
            "observation_id": str(row.get("observation_id", "")),
            "species_candidate": row["species_candidate"],
            "source_url": source_url,
            "image_url": image_url,
            "license_claim": str(row.get("license", "")),
            "creator_claim": str(row.get("creator", "")),
            "mobile_decision": review["decision"],
            "proposed_boxes": boxes,
            "training_eligible": False,
            "expert_checks_required": [
                "verify_species", "verify_license_and_attribution",
                "verify_image_pixels_and_quality", "verify_boxes_against_image",
                "record_named_reviewer",
            ],
        }
        if local_metadata:
            staged.update({
                "image_delivery": local_metadata["image_delivery"],
                "local_image_path": local_metadata["local_image_path"],
                "original_sha256": local_metadata["original_sha256"],
                "original_file_bytes": local_metadata["original_file_bytes"],
                "creator_login": local_metadata["creator_login"],
                "attribution": local_metadata["attribution"],
                "license_notice": local_metadata["license_notice"],
                "source_image_url": local_metadata["source_image_url"],
            })
        queue.append(staged)

    return {
        "format": "vespaguard-expert-queue-v1",
        "species": species,
        "records": queue,
        "training_eligible": False,
        "note": "Staging only. No expert signoff, downloads, training labels or approvals.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--asset-root",
        help=f"Optional extracted original-image artifact root containing {MANIFEST_NAME} and images/velutina/",
    )
    args = parser.parse_args()
    source, target = Path(args.input), Path(args.output)
    if source.resolve() == target.resolve():
        raise ValueError("Refusing to overwrite source")
    payload = json.loads(source.read_text(encoding="utf-8"))
    result = stage(payload, asset_root=args.asset_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError("Refusing to overwrite existing expert queue")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Staged {len(result['records'])} unapproved records for expert review.")


if __name__ == "__main__":
    main()
