#!/usr/bin/env python3
"""Validate human-reviewed annotation metadata without creating labels or approvals.

This is a metadata/geometry gate only. It does not inspect image pixels, prove
licence evidence, authenticate reviewers, validate split independence, or
approve a dataset for training.
"""
import argparse
import json
import math
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

try:
    from .class_schema import CLASS_NAMES
except ImportError:  # Supports direct execution: python training/validate_reviewed_annotations.py
    from class_schema import CLASS_NAMES

MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_RECORDS = 100_000
MAX_BOXES_PER_RECORD = 1_000
MAX_SOURCE_URL_LENGTH = 2_048
MAX_PHOTO_ID_LENGTH = 128
SUPPORTED_LICENSES = {"CC0-1.0", "CC-BY-4.0"}
REQUIRED = frozenset({
    "photo_id", "species", "license", "license_verified",
    "species_verified", "image_quality_verified", "reviewer",
    "reviewed_at", "source_url", "boxes",
})
PHOTO_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
PSEUDONYMOUS_REVIEWER = re.compile(r"^reviewer:[A-Za-z0-9][A-Za-z0-9._:-]{7,79}$")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _read_payload(path):
    candidate = Path(path)
    if candidate.is_symlink():
        raise ValueError("annotation input must not be a symbolic link")
    try:
        with candidate.open("rb") as stream:
            raw = stream.read(MAX_FILE_BYTES + 1)
    except OSError as exc:
        raise ValueError("annotation input cannot be read") from exc
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError("annotation input exceeds the 16 MiB limit")
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise ValueError("annotation input must be bounded UTF-8 JSON with unique keys") from exc
    return payload


def _validate_source_url(value, index):
    if (
        not isinstance(value, str)
        or not value
        or len(value) > MAX_SOURCE_URL_LENGTH
        or "?" in value
        or "#" in value
        or any(ord(char) < 32 for char in value)
    ):
        raise ValueError(f"Record {index}: source_url must be a bounded credential-free HTTPS URL without query or fragment")
    try:
        parsed = urlparse(value)
        parsed.port  # Reject malformed ports.
    except ValueError as exc:
        raise ValueError(f"Record {index}: invalid source_url") from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(f"Record {index}: source_url must be credential-free HTTPS without query or fragment")


def _validate_reviewed_at(value, index):
    if not isinstance(value, str) or not value or len(value) > 40:
        raise ValueError(f"Record {index}: reviewed_at must be a timezone-aware ISO-8601 timestamp")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Record {index}: reviewed_at must be a timezone-aware ISO-8601 timestamp") from exc
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError(f"Record {index}: reviewed_at must include a timezone")


def check(path):
    payload = _read_payload(path)
    if not isinstance(payload, dict) or set(payload) != {"records"}:
        raise ValueError("Top-level annotation JSON must contain only a records array")
    records = payload["records"]
    if not isinstance(records, list) or not records or len(records) > MAX_RECORDS:
        raise ValueError(f"records must contain 1 to {MAX_RECORDS} entries")

    ids = set()
    box_count = 0
    for index, record in enumerate(records):
        if not isinstance(record, dict) or set(record) != REQUIRED:
            raise ValueError(f"Record {index}: unknown or missing fields")
        photo_id = record["photo_id"]
        if (
            not isinstance(photo_id, str)
            or len(photo_id) > MAX_PHOTO_ID_LENGTH
            or not PHOTO_ID.fullmatch(photo_id)
            or photo_id in ids
        ):
            raise ValueError(f"Record {index}: photo_id must be a unique opaque identifier")
        ids.add(photo_id)

        if not isinstance(record["species"], str) or record["species"] not in CLASS_NAMES:
            raise ValueError(f"Record {index}: species must be one of the seven project class IDs")
        license_id = record["license"]
        if not isinstance(license_id, str) or license_id not in SUPPORTED_LICENSES:
            raise ValueError(f"Record {index}: unsupported or unverified license version")
        for field in ("license_verified", "species_verified", "image_quality_verified"):
            if record[field] is not True:
                raise ValueError(f"Record {index}: {field} must be explicitly true")

        reviewer = record["reviewer"]
        if not isinstance(reviewer, str) or not PSEUDONYMOUS_REVIEWER.fullmatch(reviewer.strip()):
            raise ValueError(f"Record {index}: reviewer must use reviewer:<opaque-id>; names, emails and URLs are forbidden")
        _validate_reviewed_at(record["reviewed_at"], index)
        _validate_source_url(record["source_url"], index)

        boxes = record["boxes"]
        if not isinstance(boxes, list) or not boxes or len(boxes) > MAX_BOXES_PER_RECORD:
            raise ValueError(f"Record {index}: boxes must contain 1 to {MAX_BOXES_PER_RECORD} entries")
        box_count += len(boxes)
        for box in boxes:
            if not isinstance(box, dict) or set(box) != {"class_id", "x", "y", "width", "height"}:
                raise ValueError(f"Record {index}: invalid box schema")
            cls = box["class_id"]
            if type(cls) is not int or not 0 <= cls < len(CLASS_NAMES):
                raise ValueError(f"Record {index}: invalid class_id")
            values = [box[key] for key in ("x", "y", "width", "height")]
            if any(type(value) not in (int, float) or not math.isfinite(value) for value in values):
                raise ValueError(f"Record {index}: invalid box number")
            x, y, width, height = values
            if not (0 < width <= 1 and 0 < height <= 1 and 0 <= x <= 1 and 0 <= y <= 1):
                raise ValueError(f"Record {index}: invalid box bounds")
            if x - width / 2 < 0 or x + width / 2 > 1 or y - height / 2 < 0 or y + height / 2 > 1:
                raise ValueError(f"Record {index}: bounding box exceeds image")

    return {
        "reviewed_records": len(records),
        "validated_boxes": box_count,
        "limitations": (
            "Metadata/geometry only: image pixels, licence evidence, reviewer identity, "
            "split independence and training/field approval require separate verification"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Human-reviewed JSON; no generated approvals")
    args = parser.parse_args()
    print(json.dumps(check(args.input), indent=2))


if __name__ == "__main__":
    main()
