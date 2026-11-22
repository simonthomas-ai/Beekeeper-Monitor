#!/usr/bin/env python3
"""Build a local CVAT image-only task pack from a verified, unapproved expert queue.

No labels, boxes, model weights, uploads or training approvals are created.
The source originals are re-hashed while copied byte-for-byte into the ZIP.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from training.class_schema import CLASS_NAMES
from training.stage_mobile_reviews import _asset_root, stage

METADATA_FIELDS = (
    "photo_id", "observation_id", "candidate_species", "source_url",
    "creator", "license", "mobile_decision", "proposed_box_count",
    "image_file", "original_path", "sha256", "file_bytes", "training_eligible",
)


def _payload_from_expert_queue(queue: dict) -> dict:
    if not isinstance(queue, dict) or queue.get("format") != "vespaguard-expert-queue-v1":
        raise ValueError("Unsupported expert queue format")
    if queue.get("training_eligible") is not False:
        raise ValueError("Expert queue must remain training_eligible=false")
    records = queue.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("Nonempty expert queue records are required")

    mobile_records = []
    for index, row in enumerate(records):
        if not isinstance(row, dict):
            raise ValueError(f"Expert queue record {index} must be an object")
        if row.get("training_eligible") is not False:
            raise ValueError(f"Expert queue record {index} is already marked training-eligible")
        mobile_records.append({
            "photo_id": row.get("photo_id"),
            "observation_id": row.get("observation_id"),
            "species_candidate": row.get("species_candidate"),
            "source_url": row.get("source_url"),
            "image_url": row.get("local_image_path"),
            "license": row.get("license_claim"),
            "creator": row.get("creator_claim"),
            "training_eligible": False,
            "image_delivery": "LOCAL_UNMODIFIED_ORIGINAL",
            "original_sha256": row.get("original_sha256"),
            "original_file_bytes": row.get("original_file_bytes"),
            "review": {
                "decision": row.get("mobile_decision"),
                "boxes": row.get("proposed_boxes"),
            },
        })
    return {
        "format": "vespaguard-unverified-mobile-review-v1",
        "species": queue.get("species"),
        "records": mobile_records,
    }


def _safe_source(root: Path, relative: str) -> Path:
    posix = PurePosixPath(relative)
    if posix.is_absolute() or len(posix.parts) != 3 or posix.parts[:2] != ("images", "velutina"):
        raise ValueError("Original image path is outside the verified Velutina asset tree")
    current = root
    for part in posix.parts:
        if part in ("", ".", ".."):
            raise ValueError("Unsafe original image path")
        current = current / part
        if current.is_symlink():
            raise ValueError("Original image path contains a symbolic link")
    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ValueError("Original image is missing or outside the asset root") from exc
    info = resolved.stat(follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("Original image must be a regular file")
    return resolved


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_original_to_zip(archive: zipfile.ZipFile, source: Path, archive_name: str,
                          expected_sha256: str, expected_bytes: int) -> None:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(source, flags)
    digest = hashlib.sha256()
    total = 0
    info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    try:
        with os.fdopen(descriptor, "rb") as source_stream, archive.open(info, "w") as target_stream:
            for chunk in iter(lambda: source_stream.read(1024 * 1024), b""):
                target_stream.write(chunk)
                digest.update(chunk)
                total += len(chunk)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise
    if total != expected_bytes:
        raise ValueError(f"Original byte count changed while packaging {source.name}")
    if digest.hexdigest() != expected_sha256:
        raise ValueError(f"Original SHA-256 changed while packaging {source.name}")


def build_cvat_review_pack(expert_queue: dict, asset_root: str | Path,
                           output_dir: str | Path) -> dict:
    """Create a local CVAT-ready images-only ZIP plus labels/provenance sidecars."""
    root = _asset_root(asset_root)
    raw_target = Path(output_dir).expanduser()
    if not raw_target.is_absolute():
        raw_target = Path.cwd() / raw_target
    raw_target = Path(os.path.abspath(raw_target))
    if raw_target.name in ("", ".", ".."):
        raise ValueError("Invalid CVAT review pack output directory")

    # Resolve the nearest existing ancestor before creating missing parents.
    # This prevents a target under the asset root (including through a symlink)
    # from creating even an empty directory inside the original artifact.
    probe = raw_target.parent
    missing_parts = []
    while not probe.exists() and not probe.is_symlink():
        missing_parts.insert(0, probe.name)
        probe = probe.parent
    resolved_ancestor = probe.resolve(strict=True)
    if resolved_ancestor == root or resolved_ancestor.is_relative_to(root):
        raise ValueError("CVAT review pack must be outside the original-image asset root")
    parent = resolved_ancestor.joinpath(*missing_parts)
    parent.mkdir(parents=True, exist_ok=True)
    parent = parent.resolve(strict=True)
    target = parent / raw_target.name
    if target.exists() or target.is_symlink():
        raise FileExistsError("Refusing to overwrite an existing CVAT review pack")
    if target == root or target.is_relative_to(root):
        raise ValueError("CVAT review pack must be outside the original-image asset root")

    mobile_payload = _payload_from_expert_queue(expert_queue)
    verified_queue = stage(mobile_payload, asset_root=root)
    records = verified_queue["records"]
    if not records:
        raise ValueError("No verified local originals are available for CVAT packaging")

    temp_path = Path(tempfile.mkdtemp(prefix=".cvat-review-pack-", dir=parent))
    total_bytes = 0
    metadata_rows = []
    archive_names = set()
    try:
        images_zip = temp_path / "cvat-images.zip"
        with zipfile.ZipFile(images_zip, mode="w", compression=zipfile.ZIP_STORED,
                             allowZip64=True) as archive:
            for row in records:
                photo_id = row["photo_id"]
                relative = row["local_image_path"]
                source = _safe_source(root, relative)
                suffix = source.suffix.lower()
                if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
                    raise ValueError(f"Unsupported original image extension: {suffix}")
                image_name = f"{photo_id}{suffix}"
                if image_name in archive_names:
                    raise ValueError("Duplicate image name in CVAT package")
                archive_names.add(image_name)
                byte_count = row["original_file_bytes"]
                _copy_original_to_zip(
                    archive, source, image_name,
                    row["original_sha256"], byte_count,
                )
                total_bytes += byte_count
                metadata_rows.append({
                    "photo_id": photo_id,
                    "observation_id": row["observation_id"],
                    "candidate_species": row["species_candidate"],
                    "source_url": row["source_url"],
                    "creator": row["creator_claim"],
                    "license": row["license_claim"],
                    "mobile_decision": row["mobile_decision"],
                    "proposed_box_count": len(row["proposed_boxes"]),
                    "image_file": image_name,
                    "original_path": relative,
                    "sha256": row["original_sha256"],
                    "file_bytes": byte_count,
                    "training_eligible": "false",
                })

        metadata_path = temp_path / "metadata.csv"
        with metadata_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=METADATA_FIELDS)
            writer.writeheader()
            writer.writerows(metadata_rows)

        labels = [{"name": name, "attributes": []} for name in CLASS_NAMES]
        labels_path = temp_path / "labels.json"
        labels_path.write_text(
            json.dumps(labels, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        readme = """# Beekeeper Monitor – CVAT review pack

This pack contains byte-preserved source images for human annotation only.

- cvat-images.zip contains only the original image files. It contains no annotations or generated labels.
- labels.json is the exact seven-class task label schema. These names are available classes, not assignments to any image.
- metadata.csv preserves photo and observation IDs, source URL, creator attribution, license, original path, byte count and SHA-256.
- SHA256SUMS.txt binds the sidecar files and image archive.

## Create a CVAT Community task

1. Start a local or self-hosted CVAT Community instance.
2. Create a new image task and create the seven labels from labels.json.
3. Upload cvat-images.zip as the image archive. Keep metadata.csv alongside the task for source review.
4. Review every image from its original pixels. The mobile candidate and LIKELY decision are not verified species labels. Do not import the proposed mobile rectangles as ground truth.
5. Draw and classify each bounding box only after expert review. Leave uncertain objects unlabelled and record the review outcome separately.

This pack has zero annotations, zero YOLO label files and zero training approvals. Do not train from it until rights, species, image quality, annotations, per-file provenance and grouped train/val/test splits have all passed their separate validators.
"""
        readme_path = temp_path / "README.md"
        readme_path.write_text(readme, encoding="utf-8")

        summary = {
            "format": "beekeeper-cvat-image-only-pack-v1",
            "images": len(records),
            "source_bytes": total_bytes,
            "task_labels": list(CLASS_NAMES),
            "annotations_generated": 0,
            "yolo_label_files_generated": 0,
            "training_approved": 0,
            "rights_and_species_review_required": True,
        }
        summary_path = temp_path / "summary.json"
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        checksummed = [images_zip, metadata_path, labels_path, readme_path, summary_path]
        checksum_path = temp_path / "SHA256SUMS.txt"
        checksum_path.write_text(
            "".join(
                f"{_sha256_file(path)}  {path.name}\n"
                for path in checksummed
            ),
            encoding="utf-8",
        )

        with zipfile.ZipFile(images_zip, "r") as archive:
            names = archive.namelist()
            if len(names) != len(records):
                raise ValueError("CVAT image archive record count mismatch")
            if len(names) != len(set(names)):
                raise ValueError("CVAT image archive contains duplicate names")
            if any(Path(name).suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}
                   for name in names):
                raise ValueError("CVAT image archive unexpectedly contains non-image files")
        if summary["training_approved"] != 0 or summary["annotations_generated"] != 0:
            raise ValueError("CVAT pack must not generate annotations or training approval")

        os.rename(temp_path, target)
    except Exception:
        shutil.rmtree(temp_path, ignore_errors=True)
        raise

    return {
        **summary,
        "output_dir": str(target),
        "archive_sha256": _sha256_file(target / "cvat-images.zip"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expert_queue", type=Path)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        queue = json.loads(args.expert_queue.read_text(encoding="utf-8"))
        result = build_cvat_review_pack(queue, args.asset_root, args.output_dir)
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
