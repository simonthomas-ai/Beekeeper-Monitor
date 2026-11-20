"""Fail-closed per-image license, provenance, split and annotation review gate.

Manifest: datasets/beekeeper/provenance.jsonl (one JSON object per image).
Only CC0-1.0 and CC-BY-4.0 are enabled in the initial policy.
No images are downloaded or uploaded by this module.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_LICENSES = {
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
}
SPLITS = {"train", "val", "test"}
SHA256 = re.compile(r"^[a-f0-9]{64}$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$")


class DatasetProvenanceError(ValueError):
    pass


def _https_url(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise DatasetProvenanceError(f"{field} must be an HTTPS URL")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise DatasetProvenanceError(f"{field} must be an HTTPS URL without embedded credentials")
    return value


def _required_text(row: dict, key: str, max_length: int = 2048) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise DatasetProvenanceError(f"{key} is required and must be at most {max_length} characters")
    if any(ord(char) < 32 and char not in "\t" for char in value):
        raise DatasetProvenanceError(f"{key} contains control characters")
    return value.strip()


def _valid_group(row: dict, key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise DatasetProvenanceError(f"{key} must be a stable pseudonymous grouping identifier")
    return value


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise DatasetProvenanceError("cannot read dataset image for SHA-256 verification") from exc
    return digest.hexdigest()


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DatasetProvenanceError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_provenance(dataset_root: str | Path, *, expected_splits=SPLITS) -> dict:
    root = Path(dataset_root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise DatasetProvenanceError("dataset root must be a directory")
    manifest = root / "provenance.jsonl"
    if not manifest.is_file():
        raise DatasetProvenanceError("required per-image provenance.jsonl is missing")

    rows = []
    paths, digests = set(), set()
    group_splits = defaultdict(set)
    observation_splits = defaultdict(set)
    photographer_splits = defaultdict(set)
    site_splits = defaultdict(set)
    counts = Counter()
    try:
        lines = manifest.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise DatasetProvenanceError("provenance manifest must be readable UTF-8 JSONL") from exc
    if not lines:
        raise DatasetProvenanceError("provenance manifest is empty")

    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line, object_pairs_hook=_reject_duplicate_keys)
        except (json.JSONDecodeError, DatasetProvenanceError) as exc:
            raise DatasetProvenanceError(f"invalid JSON in provenance line {line_number}") from exc
        if not isinstance(row, dict):
            raise DatasetProvenanceError(f"provenance line {line_number} must contain an object")

        image = _required_text(row, "image_path", 1024).replace("\\", "/")
        path = Path(image)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            raise DatasetProvenanceError(f"image_path on line {line_number} must be a clean relative path")
        if len(path.parts) < 3 or path.parts[0] != "images" or path.parts[1] not in expected_splits:
            raise DatasetProvenanceError(f"image_path on line {line_number} must be under images/train|val|test")
        split = path.parts[1]
        full_path = (root / path).resolve()
        try:
            full_path.relative_to(root)
        except ValueError as exc:
            raise DatasetProvenanceError("image path resolves outside the dataset directory") from exc
        if not full_path.is_file():
            raise DatasetProvenanceError(f"dataset image does not exist: {image}")
        if image in paths:
            raise DatasetProvenanceError(f"duplicate image_path in manifest: {image}")
        paths.add(image)

        digest = _required_text(row, "sha256", 64)
        if not SHA256.fullmatch(digest):
            raise DatasetProvenanceError(f"invalid sha256 on line {line_number}")
        if digest in digests:
            raise DatasetProvenanceError("duplicate image SHA-256 found; remove exact duplicate images")
        digests.add(digest)
        if _digest_file(full_path) != digest:
            raise DatasetProvenanceError(f"image SHA-256 mismatch: {image}")

        license_id = _required_text(row, "license_spdx", 80)
        if license_id not in ALLOWED_LICENSES:
            raise DatasetProvenanceError(f"license {license_id} is not allowed by current training policy")
        license_url = _https_url(row.get("license_url"), "license_url")
        if license_url.rstrip("/") != ALLOWED_LICENSES[license_id].rstrip("/"):
            raise DatasetProvenanceError(f"license_url does not match the exact {license_id} license")
        source_url = _https_url(row.get("source_url"), "source_url")
        _required_text(row, "source_dataset", 200)
        _required_text(row, "source_version", 120)
        downloaded_at = _required_text(row, "downloaded_at", 40)
        reviewed_at = _required_text(row, "reviewed_at", 40)
        for stamp in (downloaded_at, reviewed_at):
            try:
                parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError as exc:
                raise DatasetProvenanceError("downloaded_at and reviewed_at must be ISO-8601 timestamps") from exc
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise DatasetProvenanceError("downloaded_at and reviewed_at must include a timezone")
        image_creator = row.get("creator", "")
        attribution = row.get("attribution_text", "")
        if image_creator is not None and not isinstance(image_creator, str):
            raise DatasetProvenanceError("creator must be text")
        if image_creator and len(image_creator) > 300:
            raise DatasetProvenanceError("creator is too long")
        if license_id == "CC-BY-4.0":
            _required_text(row, "creator", 300)
            _required_text(row, "attribution_text", 1000)

        observation = _valid_group(row, "observation_group")
        photographer = _valid_group(row, "photographer_group")
        site = _valid_group(row, "site_group")
        group_splits["observation:" + observation].add(split)
        group_splits["photographer:" + photographer].add(split)
        group_splits["site:" + site].add(split)
        observation_splits[observation].add(split)
        photographer_splits[photographer].add(split)
        site_splits[site].add(split)

        if row.get("species_review_status") != "verified":
            raise DatasetProvenanceError(f"species_review_status must be verified: {image}")
        if row.get("bbox_review_status") != "verified":
            raise DatasetProvenanceError(f"bbox_review_status must be verified: {image}")
        _required_text(row, "reviewer_id", 160)
        rows.append({
            "image_path": image,
            "split": split,
            "sha256": digest,
            "license_spdx": license_id,
            "source_url": source_url,
            "creator": image_creator or "",
            "attribution_text": attribution or "",
        })
        counts[split] += 1

    if not rows:
        raise DatasetProvenanceError("no usable provenance records found")
    actual_images = {
        path.relative_to(root).as_posix()
        for path in root.joinpath("images").rglob("*")
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    }
    if actual_images != paths:
        missing = sorted(actual_images - paths)
        stale = sorted(paths - actual_images)
        raise DatasetProvenanceError(
            "provenance must cover every image exactly once; missing=%d stale=%d"
            % (len(missing), len(stale))
        )
    for key, values in group_splits.items():
        if len(values) > 1:
            raise DatasetProvenanceError(f"data leakage: {key.split(':', 1)[0]} group appears across splits")
    missing = set(expected_splits) - {row["split"] for row in rows}
    if missing:
        raise DatasetProvenanceError("provenance manifest missing splits: " + ", ".join(sorted(missing)))
    return {
        "images": len(rows),
        "by_split": {split: counts[split] for split in sorted(expected_splits)},
        "licenses": dict(Counter(row["license_spdx"] for row in rows)),
        "groups_checked": {
            "observations": len(observation_splits),
            "photographers": len(photographer_splits),
            "sites": len(site_splits),
        },
        "status": "provenance_verified_not_species_accuracy",
    }
