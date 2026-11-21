"""Strict adapter for reviewed third-party camera detection metadata.

No external model or data is bundled. No networking, photos, GPS or audio.
"""
from __future__ import annotations

from datetime import datetime, timezone
from integrations.event_contracts import HiveEvent

TAXA = {
    "vespa_velutina": "vespa_velutina",
    "vespa_crabro": "vespa_crabro",
    "apis_mellifera": "apis_mellifera",
    "bombus_spp": "bombus_spp",
    "other_vespidae": "other_vespidae",
    "syrphidae": "syrphidae",
    "other_insect": "other_insect",
}


def adapt_detection(record: dict, *, device_id: str, source: str) -> HiveEvent:
    """Convert a single minimal detector record into an unverified station event.

    The caller must explicitly map each vendor's labels to TAXA. Unknown labels
    are rejected rather than guessed. Timestamp must be timezone-aware ISO-8601.
    """
    if not isinstance(record, dict) or set(record) != {"taxon", "confidence", "timestamp", "event_id"}:
        raise ValueError("Only taxon, confidence, timestamp and event_id are permitted")
    if not isinstance(record["taxon"], str) or record["taxon"] not in TAXA:
        raise ValueError("Unmapped detector taxon")
    if not isinstance(record["timestamp"], str):
        raise ValueError("Invalid timestamp")
    try:
        stamp = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid timestamp") from exc
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("Timestamp must have timezone")
    event = HiveEvent(
        kind="camera_detection",
        device_id=device_id,
        timestamp=record["timestamp"],
        source=source,
        schema_version=1,
        payload={
            "label": TAXA[record["taxon"]],
            "confidence": record["confidence"],
            "origin_event_id": record["event_id"],
            "verification_status": "unverified",
        },
    )
    event.validate()
    return event
