#!/usr/bin/env python3
"""Validate review-gallery provenance and byte integrity before publication.

This checks that local gallery references resolve to manifest-listed files whose
bytes match the recorded SHA-256. It does NOT independently establish copyright,
license validity, or permission to use images for model training.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

GALLERY_NAMES = ("all", "velutina", "crabro", "apis", "bombus", "vespula")
MANIFEST_RELATIVE_PATH = Path("review") / "velutina-original-images-manifest.csv"
MANIFEST_FIELDS = {
    "photo_id", "observation_id", "species_candidate", "source_url", "license",
    "creator", "source_image_url", "local_image_path", "image_format",
    "image_width", "image_height", "image_bytes", "sha256", "download_status",
}
IMAGE_HOSTS = {
    "static.inaturalist.org",
    "inaturalist-open-data.s3.amazonaws.com",
    "inaturalist-open-data.s3.us-west-2.amazonaws.com",
}
FORMAT_EXTENSIONS = {"JPEG": {".jpg", ".jpeg"}, "PNG": {".png"}, "WEBP": {".webp"}}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
OBSERVATION_PATH_RE = re.compile(r"^/observations/([0-9]+)/?$")
PHOTO_PATH_RE = re.compile(r"^/photos/([0-9]+)/original\.(jpe?g|png|webp)$", re.IGNORECASE)
ITEMS_RE = re.compile(r"\bconst\s+items\s*=\s*(\[.*?\])\s*;", re.DOTALL)


class AuditError(ValueError):
    """Raised when a gallery or local asset fails the publication contract."""


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_observation_url(value: object, observation_id: str) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    match = OBSERVATION_PATH_RE.fullmatch(parsed.path)
    return (
        parsed.scheme == "https"
        and parsed.hostname == "www.inaturalist.org"
        and parsed.username is None
        and parsed.password is None
        and parsed.port in (None, 443)
        and not parsed.query
        and not parsed.fragment
        and match is not None
        and match.group(1) == observation_id
    )


def _is_original_image_url(value: object, photo_id: str) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    match = PHOTO_PATH_RE.fullmatch(parsed.path)
    return (
        parsed.scheme == "https"
        and (parsed.hostname or "").lower() in IMAGE_HOSTS
        and parsed.username is None
        and parsed.password is None
        and parsed.port in (None, 443)
        and not parsed.fragment
        and match is not None
        and match.group(1) == photo_id
    )


def _safe_local_path(value: object, photo_id: str, image_format: str) -> PurePosixPath:
    if not isinstance(value, str) or "\\" in value:
        raise AuditError("local_image_path is not a safe POSIX-relative path")
    relative = PurePosixPath(value)
    if (
        relative.as_posix() != value
        or relative.is_absolute()
        or len(relative.parts) != 3
        or relative.parts[0:2] != ("images", "velutina")
        or any(part in ("", ".", "..") for part in relative.parts)
        or ":" in value
        or not re.fullmatch(rf"{re.escape(photo_id)}\.(?:jpg|jpeg|png|webp)", relative.name, re.IGNORECASE)
        or Path(relative.name).suffix.lower() not in FORMAT_EXTENSIONS.get(image_format, set())
    ):
        raise AuditError("local_image_path is outside the approved images/velutina layout")
    return relative


def _read_manifest(review_root: Path) -> dict[str, dict[str, str]]:
    manifest_path = review_root / MANIFEST_RELATIVE_PATH.name
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise AuditError(f"local original-image manifest missing or unsafe: {manifest_path}")

    with manifest_path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = set(reader.fieldnames or ())
        missing = MANIFEST_FIELDS - fields
        if missing:
            raise AuditError("manifest columns missing: " + ", ".join(sorted(missing)))

        assets: dict[str, dict[str, str]] = {}
        paths: set[str] = set()
        for line_number, row in enumerate(reader, start=2):
            photo_id = str(row.get("photo_id", "")).strip()
            if not photo_id.isdecimal():
                raise AuditError(f"manifest line {line_number}: invalid photo_id")
            if photo_id in assets:
                raise AuditError(f"manifest line {line_number}: duplicate photo_id {photo_id}")
            if row.get("species_candidate") != "Vespa velutina":
                raise AuditError(f"manifest line {line_number}: unexpected species")
            if row.get("license") != "CC0-1.0":
                raise AuditError(f"manifest line {line_number}: image is not marked CC0-1.0")
            if row.get("download_status") != "DOWNLOADED_UNMODIFIED":
                raise AuditError(f"manifest line {line_number}: original download status is invalid")
            if not _nonempty(row.get("creator")):
                raise AuditError(f"manifest line {line_number}: creator/attribution is missing")
            observation_id = str(row.get("observation_id", "")).strip()
            if not observation_id.isdecimal() or not _is_observation_url(row.get("source_url"), observation_id):
                raise AuditError(f"manifest line {line_number}: invalid observation/source URL binding")
            if not _is_original_image_url(row.get("source_image_url"), photo_id):
                raise AuditError(f"manifest line {line_number}: invalid iNaturalist original-image URL")

            image_format = str(row.get("image_format", "")).upper()
            relative = _safe_local_path(row.get("local_image_path"), photo_id, image_format)
            relative_text = relative.as_posix()
            if relative_text in paths:
                raise AuditError(f"manifest line {line_number}: duplicate local image path")
            paths.add(relative_text)
            digest = str(row.get("sha256", ""))
            if not SHA256_RE.fullmatch(digest):
                raise AuditError(f"manifest line {line_number}: invalid SHA-256")

            for field in ("image_width", "image_height", "image_bytes"):
                raw = str(row.get(field, ""))
                if not raw.isdecimal() or int(raw) <= 0:
                    raise AuditError(f"manifest line {line_number}: invalid {field}")
            assets[photo_id] = dict(row)

    if not assets:
        raise AuditError("local original-image manifest is empty")
    return assets


def _resolve_verified_asset(review_root: Path, row: dict[str, str]) -> Path:
    photo_id = str(row["photo_id"])
    relative = _safe_local_path(row.get("local_image_path"), photo_id, row.get("image_format", "").upper())
    candidate = review_root.joinpath(*relative.parts)

    # Reject symlinks in every component; resolve() alone would allow an
    # in-tree symlink to point elsewhere within the same directory.
    current = review_root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise AuditError(f"symbolic link is not allowed for original image: {relative.as_posix()}")

    try:
        resolved_root = review_root.resolve(strict=True)
        resolved_file = candidate.resolve(strict=True)
        resolved_file.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise AuditError(f"original image missing or outside review root: {relative.as_posix()}") from exc
    if not resolved_file.is_file():
        raise AuditError(f"original image is not a regular file: {relative.as_posix()}")

    expected_size = int(row["image_bytes"])
    if resolved_file.stat().st_size != expected_size:
        raise AuditError(f"original image byte count differs from manifest: {relative.as_posix()}")
    digest = hashlib.sha256()
    with resolved_file.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != row["sha256"]:
        raise AuditError(f"original image SHA-256 differs from manifest: {relative.as_posix()}")
    return resolved_file


def _extract_items(page_path: Path) -> list[dict[str, object]]:
    try:
        content = page_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AuditError(f"cannot read gallery: {page_path}: {exc}") from exc
    match = ITEMS_RE.search(content)
    if not match:
        raise AuditError(f"{page_path}: embedded gallery items array not found")
    try:
        items = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise AuditError(f"{page_path}: embedded gallery JSON is invalid: {exc}") from exc
    if not isinstance(items, list):
        raise AuditError(f"{page_path}: gallery items must be a JSON array")
    if any(not isinstance(item, dict) for item in items):
        raise AuditError(f"{page_path}: each gallery item must be an object")
    return items


def audit(root: Path) -> tuple[int, int]:
    """Audit the six staged galleries; root contains the review/ directory."""
    root = Path(root).resolve()
    review_root = root / "review"
    if not review_root.is_dir() or review_root.is_symlink():
        raise AuditError(f"review directory missing or unsafe: {review_root}")

    galleries: dict[str, list[dict[str, object]]] = {}
    for name in GALLERY_NAMES:
        page_path = review_root / f"{name}.html"
        if page_path.is_symlink():
            raise AuditError(f"gallery page must not be a symlink: {page_path}")
        galleries[name] = _extract_items(page_path)

    local_references: dict[str, dict[str, object]] = {}
    total = 0
    for gallery_name, items in galleries.items():
        seen_in_gallery: set[str] = set()
        for index, item in enumerate(items, start=1):
            total += 1
            prefix = f"{gallery_name} candidate {index}"
            photo_id = str(item.get("photo_id", "")).strip()
            observation_id = str(item.get("observation_id", "")).strip()
            if not photo_id.isdecimal() or not observation_id.isdecimal():
                raise AuditError(f"{prefix}: invalid photo or observation ID")
            if not _is_observation_url(item.get("source_url"), observation_id):
                raise AuditError(f"{prefix}: invalid observation source URL")
            if not _nonempty(item.get("license")):
                raise AuditError(f"{prefix}: license metadata missing")
            if not _nonempty(item.get("creator")):
                raise AuditError(f"{prefix}: creator/attribution metadata missing")

            image_url = item.get("image_url")
            delivery = item.get("image_delivery")
            if delivery == "LOCAL_UNMODIFIED_ORIGINAL" or (isinstance(image_url, str) and not urlsplit(image_url).scheme):
                if gallery_name not in ("velutina", "all"):
                    raise AuditError(f"{prefix}: local Velutina originals are not allowed in this gallery")
                if delivery != "LOCAL_UNMODIFIED_ORIGINAL":
                    raise AuditError(f"{prefix}: local image path lacks explicit local-original delivery marker")
                if not isinstance(image_url, str):
                    raise AuditError(f"{prefix}: local image path missing")
                if photo_id in seen_in_gallery:
                    raise AuditError(f"{prefix}: duplicate photo ID in gallery")
                seen_in_gallery.add(photo_id)
                local_references.setdefault(gallery_name, {})[photo_id] = item
            else:
                if delivery not in (None, "REMOTE_INATURALIST_ORIGINAL"):
                    raise AuditError(f"{prefix}: unknown image-delivery mode")
                if not isinstance(image_url, str):
                    raise AuditError(f"{prefix}: image URL missing")
                parsed = urlsplit(image_url)
                if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                    raise AuditError(f"{prefix}: remote image URL must use HTTPS")
                if (parsed.hostname or "").lower() in IMAGE_HOSTS and not _is_original_image_url(image_url, photo_id):
                    raise AuditError(f"{prefix}: iNaturalist image URL must reference the original derivative")

    all_local_ids = set().union(*(set(items) for items in local_references.values())) if local_references else set()
    manifest_path = review_root / MANIFEST_RELATIVE_PATH.name
    if all_local_ids or manifest_path.exists():
        manifest = _read_manifest(review_root)
        manifest_ids = set(manifest)
        velutina_ids = set(local_references.get("velutina", {}))
        all_page_ids = set(local_references.get("all", {}))
        if velutina_ids != manifest_ids:
            missing = sorted(manifest_ids - velutina_ids)
            extra = sorted(velutina_ids - manifest_ids)
            raise AuditError(f"velutina gallery and manifest differ (missing={missing}, extra={extra})")
        if all_page_ids != manifest_ids:
            missing = sorted(manifest_ids - all_page_ids)
            extra = sorted(all_page_ids - manifest_ids)
            raise AuditError(f"all gallery and manifest differ (missing={missing}, extra={extra})")

        for photo_id, asset in manifest.items():
            _resolve_verified_asset(review_root, asset)
            expected = {
                "observation_id": asset["observation_id"],
                "species_candidate": asset["species_candidate"],
                "source_url": asset["source_url"],
                "license": asset["license"],
                "creator": asset["creator"],
                "image_url": asset["local_image_path"],
                "image_width": int(asset["image_width"]),
                "image_height": int(asset["image_height"]),
                "image_bytes": int(asset["image_bytes"]),
                "original_sha256": asset["sha256"],
                "original_file_bytes": int(asset["image_bytes"]),
                "original_file_format": asset["image_format"].upper(),
            }
            for gallery_name in ("velutina", "all"):
                item = local_references[gallery_name][photo_id]
                for field, expected_value in expected.items():
                    if item.get(field) != expected_value:
                        raise AuditError(f"{gallery_name} gallery photo {photo_id}: {field} differs from manifest")

        image_dir = review_root / "images" / "velutina"
        if image_dir.exists():
            if image_dir.is_symlink() or not image_dir.is_dir():
                raise AuditError("review/images/velutina must be a regular directory")
            entries = list(image_dir.iterdir())
            if any(entry.is_symlink() or not entry.is_file() for entry in entries):
                raise AuditError("review/images/velutina may contain only regular image files")
            actual_files = {p.name for p in entries}
            expected_files = {PurePosixPath(row["local_image_path"]).name for row in manifest.values()}
            if actual_files != expected_files:
                raise AuditError(
                    "unmanifested or missing files in review/images/velutina "
                    f"(unmanifested={sorted(actual_files - expected_files)}, missing={sorted(expected_files - actual_files)})"
                )
        else:
            raise AuditError("review/images/velutina directory missing")

        print(f"Local originals verified: {len(manifest)} files; byte counts and SHA-256 match.")
    else:
        image_dir = review_root / "images" / "velutina"
        if image_dir.exists():
            raise AuditError("local image files exist without a manifest and local gallery references")
        print("Local originals: none referenced by the galleries.")

    placeholders = 0
    for items in galleries.values():
        placeholders += sum(
            str(item.get("creator", "")).strip().lower()
            in ("", "unknown", "no rights reserved", "attribution unavailable")
            for item in items
        )
    print(f"Galleries audited: {len(galleries)}; records checked (gallery overlaps included): {total}.")
    print(f"Records with generic or unavailable creator attribution: {placeholders}.")
    print("Rights limitation: source metadata and CC0 labels are not independent legal proof or model-training approval.")
    return len(galleries), total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1],
        help="repository or staged Pages root containing review/ (default: repository root)",
    )
    args = parser.parse_args(argv)
    try:
        audit(args.root)
    except (ValueError, OSError, csv.Error) as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
