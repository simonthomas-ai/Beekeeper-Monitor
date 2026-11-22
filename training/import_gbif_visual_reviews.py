#!/usr/bin/env python3
"""Validate GBIF mobile-gallery exports against the original metadata queue.

This imports only human review decisions. It never confirms a species, creates
training labels, adds bounding boxes, or grants training eligibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from training.prepare_gbif_review_gallery import prepare_items

FORMAT_IN = "beekeeper-gbif-unverified-review-v2"
FORMAT_OUT = "beekeeper-gbif-visual-review-audit-v2"
DECISIONS = {"PENDING", "LIKELY", "REJECT"}
RECORD_KEYS = {
    "source_id", "occurrence_id", "source_url", "image_url",
    "inline_image_url", "image_host", "inline_allowed",
    "scientific_name", "species_key", "format",
    "media_license", "media_license_url", "media_creator",
    "media_rights_holder", "publisher",
    "occurrence_license", "occurrence_license_url",
    "occurrence_rights_holder", "dataset_key", "review_status",
    "review", "training_eligible",
}


def _recorded_at(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("recorded_at must be a timezone-aware ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("recorded_at must be a timezone-aware ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("recorded_at must include an explicit timezone")
    return parsed.isoformat()


def validate_review_export(queue_path: str | Path, export: object, *,
                           reviewer: str, recorded_at: str) -> dict:
    """Reconcile all exported records and decisions with the immutable GBIF CSV."""
    reviewer = reviewer.strip() if isinstance(reviewer, str) else ""
    if not reviewer:
        raise ValueError("reviewer identity is required")
    timestamp = _recorded_at(recorded_at)

    queue_path = Path(queue_path)
    expected = prepare_items(queue_path)
    queue_sha256 = hashlib.sha256(queue_path.read_bytes()).hexdigest()
    if not isinstance(export, dict) or set(export) != {"format", "source_queue_sha256", "records", "training_eligible"}:
        raise ValueError("review export must contain exactly format, source_queue_sha256, records and training_eligible")
    if export.get("format") != FORMAT_IN:
        raise ValueError("unsupported GBIF visual review export format")
    if export.get("source_queue_sha256") != queue_sha256:
        raise ValueError("source queue SHA-256 does not match the gallery export")
    if export.get("training_eligible") is not False:
        raise ValueError("review export must keep training_eligible=false")

    records = export.get("records")
    if not isinstance(records, list) or len(records) != len(expected):
        raise ValueError("review export must contain every original GBIF queue record exactly once")

    expected_by_id = {row["source_id"]: row for row in expected}
    seen = set()
    reviewed = []
    for index, row in enumerate(records, start=1):
        if not isinstance(row, dict) or set(row) != RECORD_KEYS:
            raise ValueError(f"review record {index}: unexpected or missing metadata fields")
        source_id = row.get("source_id")
        if not isinstance(source_id, str) or source_id not in expected_by_id or source_id in seen:
            raise ValueError(f"review record {index}: unknown or duplicate source_id")
        seen.add(source_id)
        source = expected_by_id[source_id]

        # Every immutable field must remain byte-for-byte/value-for-value identical
        # to the original metadata queue and its validated, derived gallery fields.
        for field in RECORD_KEYS - {"review", "training_eligible"}:
            if row.get(field) != source.get(field):
                raise ValueError(f"review record {index}: immutable field {field} differs from source queue")

        if row.get("training_eligible") is not False:
            raise ValueError(f"review record {index}: training approval is forbidden")
        review = row.get("review")
        if not isinstance(review, dict) or set(review) != {"decision"}:
            raise ValueError(f"review record {index}: only a visual decision is allowed; boxes/labels are forbidden")
        decision = review.get("decision")
        if not isinstance(decision, str) or decision not in DECISIONS:
            raise ValueError(f"review record {index}: unsupported decision")

        reviewed.append({
            **source,
            "visual_decision": decision,
            "decision_recorded_by": reviewer,
            "decision_recorded_at": timestamp,
            "expert_species_confirmation": False,
            "bounding_boxes": [],
            "training_eligible": False,
        })

    if seen != set(expected_by_id):
        raise ValueError("review export is missing one or more source queue records")

    counts = {decision: sum(row["visual_decision"] == decision for row in reviewed)
              for decision in sorted(DECISIONS)}
    return {
        "format": FORMAT_OUT,
        "source_queue_records": len(expected),
        "source_queue_sha256": queue_sha256,
        "review_records_reconciled": len(reviewed),
        "reviewer": reviewer,
        "recorded_at": timestamp,
        "decision_counts": counts,
        "expert_species_confirmations": 0,
        "bounding_boxes_created": 0,
        "training_labels_created": 0,
        "training_approvals": 0,
        "training_eligible": False,
        "human_expert_review_still_required": True,
        "records": reviewed,
    }


def write_new_file(path: str | Path, payload: dict) -> None:
    """Create a new result file without overwriting an existing review record."""
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            target.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True,
                        help="Original GBIF metadata CSV used to create the gallery")
    parser.add_argument("--review-export", type=Path, required=True,
                        help="JSON downloaded from the mobile review gallery")
    parser.add_argument("--output", type=Path, required=True,
                        help="New audit JSON path; existing files are never overwritten")
    parser.add_argument("--reviewer", required=True,
                        help="Human reviewer identity recorded with the decisions")
    parser.add_argument("--recorded-at", required=True,
                        help="Timezone-aware ISO 8601 timestamp, e.g. 2026-11-22T10:00:00+01:00")
    args = parser.parse_args()

    try:
        export = json.loads(args.review_export.read_text(encoding="utf-8"))
        result = validate_review_export(
            args.queue, export, reviewer=args.reviewer, recorded_at=args.recorded_at
        )
        write_new_file(args.output, result)
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")

    print(json.dumps({
        "review_records_reconciled": result["review_records_reconciled"],
        "decision_counts": result["decision_counts"],
        "training_approvals": 0,
        "training_eligible": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
