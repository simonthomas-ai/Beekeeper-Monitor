"""Strict, vendor-neutral BeeKeeper event contracts.

Only small, validated metadata is accepted. Images, audio, precise GPS,
credentials and free-form extension objects are deliberately outside v1.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
import json
import math
import re

Kind = Literal["camera_detection", "acoustic_event", "hive_telemetry", "varroa_count"]
ALLOWED = {"camera_detection", "acoustic_event", "hive_telemetry", "varroa_count"}
IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
LABEL = re.compile(r"^[^\x00-\x1f\x7f]{1,120}$")
SOURCE_EVENT_ID = re.compile(r"^[\x21-\x7e]{1,128}$")
REQUIRED_FIELDS = {
    "camera_detection": {"label", "confidence"},
    "acoustic_event": {"label", "confidence"},
    "hive_telemetry": {"temperature_c", "humidity_pct"},
    "varroa_count": {"mites", "bees_examined"},
}
OPTIONAL_FIELDS = {
    # Explicit, bounded bridge metadata only. No media, GPS or arbitrary text.
    "camera_detection": {"origin_event_id", "verification_status", "prey_detected"},
    "acoustic_event": set(),
    "hive_telemetry": set(),
    "varroa_count": set(),
}


def _finite_number(value, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Invalid {field}")
    try:
        number = float(value)
    except (OverflowError, TypeError, ValueError):
        raise ValueError(f"Invalid {field}") from None
    if not math.isfinite(number):
        raise ValueError(f"Invalid {field}")
    return number


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def _reject_nonstandard_constant(value):
    raise ValueError("Non-standard JSON numeric constant")


@dataclass(frozen=True)
class HiveEvent:
    kind: Kind
    device_id: str
    timestamp: str
    payload: dict
    source: str = "unverified"
    schema_version: int = 1

    def validate(self) -> None:
        if not isinstance(self.kind, str) or self.kind not in ALLOWED:
            raise ValueError("Unsupported event kind")
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("Unsupported event schema version")
        if not isinstance(self.device_id, str) or not IDENTIFIER.fullmatch(self.device_id):
            raise ValueError("Invalid device ID")
        if not isinstance(self.source, str) or not IDENTIFIER.fullmatch(self.source):
            raise ValueError("Invalid source ID")
        if not isinstance(self.timestamp, str) or not 1 <= len(self.timestamp) <= 40:
            raise ValueError("Timestamp required")
        try:
            dt = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Invalid ISO-8601 timestamp") from exc
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("Timestamp must have timezone")

        if not isinstance(self.payload, dict):
            raise ValueError("Payload must be an object")
        required = REQUIRED_FIELDS[self.kind]
        allowed = required | OPTIONAL_FIELDS[self.kind]
        if not required.issubset(self.payload) or not set(self.payload).issubset(allowed):
            raise ValueError("Payload fields do not match the strict event contract")

        if self.kind in {"camera_detection", "acoustic_event"}:
            label = self.payload["label"]
            confidence = self.payload["confidence"]
            if not isinstance(label, str) or not LABEL.fullmatch(label.strip()):
                raise ValueError("Invalid detection label")
            confidence_number = _finite_number(confidence, "confidence")
            if not 0 <= confidence_number <= 1:
                raise ValueError("Confidence outside 0..1")
            if self.kind == "camera_detection":
                if "origin_event_id" in self.payload:
                    origin_id = self.payload["origin_event_id"]
                    if not isinstance(origin_id, str) or not SOURCE_EVENT_ID.fullmatch(origin_id):
                        raise ValueError("Invalid source event ID")
                if "verification_status" in self.payload and self.payload["verification_status"] != "unverified":
                    raise ValueError("Untrusted events may only remain unverified")
                if "prey_detected" in self.payload and type(self.payload["prey_detected"]) is not bool:
                    raise ValueError("prey_detected must be boolean")
        elif self.kind == "hive_telemetry":
            temperature = _finite_number(self.payload["temperature_c"], "temperature_c")
            humidity = _finite_number(self.payload["humidity_pct"], "humidity_pct")
            if not -60 <= temperature <= 100 or not 0 <= humidity <= 100:
                raise ValueError("Telemetry outside plausible range")
        else:
            mites = self.payload["mites"]
            examined = self.payload["bees_examined"]
            if type(mites) is not int or type(examined) is not int:
                raise ValueError("Counts must be integers")
            if not 0 <= mites <= 1_000_000 or not 1 <= examined <= 100_000_000:
                raise ValueError("Counts outside plausible range")

    def to_json(self) -> str:
        self.validate()
        return json.dumps(self.__dict__, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_json(cls, raw: str) -> "HiveEvent":
        if not isinstance(raw, str) or len(raw.encode("utf-8")) > 32768:
            raise ValueError("Event too large")
        data = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_constant,
        )
        expected = {"kind", "device_id", "timestamp", "payload", "source", "schema_version"}
        if not isinstance(data, dict) or set(data) != expected:
            raise ValueError("Unexpected event structure")
        event = cls(**data)
        event.validate()
        return event
