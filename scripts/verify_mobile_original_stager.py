#!/usr/bin/env python3
"""Exercise the mobile expert-queue stager against every real local gallery original."""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from training.stage_mobile_reviews import stage
from scripts.prepare_cvat_review_pack import build_cvat_review_pack

ITEMS_RE = re.compile(r"\bconst\s+items\s*=\s*(\[.*?\])\s*;", re.DOTALL)


def verify_mobile_original_gallery(
    gallery_path: str | Path,
    asset_root: str | Path,
    *,
    expected_count: int = 94,
    prepare_cvat_pack: bool = False,
) -> tuple[int, int]:
    """Stage all Velutina gallery items using the extracted real original artifact.

    Returns (record_count, total_original_bytes). The output is deliberately
    checked in-memory only and is never written as a training dataset.
    """
    if type(expected_count) is not int or expected_count < 1:
        raise ValueError("expected_count must be a positive integer")

    path = Path(gallery_path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("gallery file is missing or unsafe")
    html = path.read_text(encoding="utf-8")
    match = ITEMS_RE.search(html)
    if not match:
        raise ValueError("gallery does not contain the expected JavaScript items array")

    try:
        items = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ValueError("gallery items array is not valid JSON") from exc

    if not isinstance(items, list) or len(items) != expected_count:
        raise ValueError(
            f"expected exactly {expected_count} gallery records, got "
            f"{len(items) if isinstance(items, list) else 'non-list'}"
        )

    records = []
    seen_ids = set()
    total_bytes = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"gallery record {index} is not an object")
        photo_id = str(item.get("photo_id", ""))
        if not photo_id.isdecimal() or photo_id in seen_ids:
            raise ValueError(f"gallery record {index} has an invalid or duplicate photo ID")
        seen_ids.add(photo_id)

        if item.get("species_candidate") != "Vespa velutina":
            raise ValueError(f"gallery record {photo_id} is not a Vespa velutina candidate")
        if item.get("image_delivery") != "LOCAL_UNMODIFIED_ORIGINAL":
            raise ValueError(f"gallery record {photo_id} is not a local unchanged original")
        if not isinstance(item.get("original_sha256"), str) or not item["original_sha256"]:
            raise ValueError(f"gallery record {photo_id} is missing original SHA-256")
        if type(item.get("original_file_bytes")) is not int or item["original_file_bytes"] <= 0:
            raise ValueError(f"gallery record {photo_id} is missing original byte count")
        if item.get("license") != "CC0-1.0" or not str(item.get("creator", "")).strip():
            raise ValueError(f"gallery record {photo_id} is missing the expected rights metadata")

        total_bytes += item["original_file_bytes"]
        records.append({
            "photo_id": photo_id,
            "observation_id": str(item.get("observation_id", "")),
            "species_candidate": item["species_candidate"],
            "source_url": item.get("source_url"),
            "image_url": item.get("image_url"),
            "license": item.get("license"),
            "creator": item.get("creator"),
            "creator_login": item.get("creator_login"),
            "attribution": item.get("attribution"),
            "license_notice": item.get("license_notice"),
            # The direct original URL is intentionally manifest-only; the gallery
            # exposes no such field, so the stager restores it from verified metadata.
            "training_eligible": False,
            "image_delivery": item.get("image_delivery"),
            "original_sha256": item.get("original_sha256"),
            "original_file_bytes": item.get("original_file_bytes"),
            "review": {"decision": "PENDING", "boxes": []},
        })

    payload = {
        "format": "vespaguard-unverified-mobile-review-v1",
        "species": "Vespa velutina",
        "records": records,
    }
    queued = stage(payload, asset_root=asset_root)
    if queued.get("training_eligible") is not False:
        raise ValueError("expert queue unexpectedly grants training eligibility")
    if len(queued.get("records", [])) != expected_count:
        raise ValueError("expert queue did not retain every original gallery record")

    for source, result in zip(records, queued["records"]):
        if (
            result.get("training_eligible") is not False
            or result.get("mobile_decision") != "PENDING"
            or result.get("original_sha256") != source["original_sha256"]
            or result.get("local_image_path") != source["image_url"]
            or result.get("creator_login") != source["creator_login"]
            or result.get("attribution") != source["attribution"]
            or result.get("license_notice") != source["license_notice"]
            or not result.get("source_image_url")
        ):
            raise ValueError(f"staged record {source['photo_id']} changed its non-approval or asset binding")

    if prepare_cvat_pack:
        with tempfile.TemporaryDirectory(prefix="cvat-real-original-smoke-") as temporary:
            result = build_cvat_review_pack(
                queued, asset_root, Path(temporary) / "review-pack"
            )
            if (
                result.get("images") != expected_count
                or result.get("annotations_generated") != 0
                or result.get("yolo_label_files_generated") != 0
                or result.get("training_approved") != 0
            ):
                raise ValueError("CVAT review-pack smoke test changed image count or created annotations/approval")
        print(
            f"PASS: CVAT image-only package verified for {expected_count} originals; "
            "0 annotations and 0 training approvals."
        )

    return expected_count, total_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gallery", type=Path, required=True)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, default=94)
    parser.add_argument("--prepare-cvat-pack", action="store_true", help="Build and discard a verified image-only CVAT pack as an end-to-end packaging smoke test")
    args = parser.parse_args()

    try:
        count, total_bytes = verify_mobile_original_gallery(
            args.gallery, args.asset_root, expected_count=args.expected_count,
            prepare_cvat_pack=args.prepare_cvat_pack,
        )
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        f"PASS: staged {count} real local originals through the mobile expert queue; "
        f"{total_bytes} source bytes re-verified; 0 records approved for training."
    )
    summary = __import__("os").environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(
                "\n## Real original → mobile expert queue\n"
                f"- Original files staged: {count}\n"
                f"- Source bytes re-verified: {total_bytes}\n"
                "- Training approvals created: 0\n"
                + ("- CVAT image-only pack smoke test: passed; 0 annotations\n" if args.prepare_cvat_pack else "")
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
