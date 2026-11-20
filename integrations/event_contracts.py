"""Strict, vendor-neutral metadata event contract. Media and precise location are excluded."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
import json
import math
import re

Kind = Literal["camera_detection", "acoustic_event", "hive_telemetry", "varroa_count"]
ALLOWED = {"camera_detection", "acoustic_event", "hive_telemetry", "varroa_count"}
REQUIRED_FIELDS = {
    "camera_detection": {"label", "confidence"},
    "acoustic_event": {"label", "confidence"},
    "hive_telemetry": {"temperature_c", "humidity_pct"},
    "varroa_count": {"mites", "bees_examined"},
}
IDENTIFIER = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._:-]{0,79}$")
SOURCE_EVENT_ID = re.compile(r"^[\x21-\x7E]{1,128}$")
OPTIONAL_FIELDS = {
    "camera_detection": {"origin_event_id", "verification_status", "prey_detected"},
    "acoustic_event": set(),
    "hive_telemetry": set(),
    "varroa_count": set(),
}


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
            raise ValueError("device_id must be a pseudonymous identifier")
        if not isinstance(self.source, str) or not IDENTIFIER.fullmatch(self.source):
            raise ValueError("source must be a short identifier")
        if not isinstance(self.timestamp, str) or not 1 <= len(self.timestamp) <= 40:
            raise ValueError("Timestamp required")
        try:
            dt = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Invalid timestamp") from exc
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("Timestamp must have timezone")
        if not isinstance(self.payload, dict):
            raise ValueError("Payload must be object")

        expected = REQUIRED_FIELDS[self.kind]
        allowed = expected | OPTIONAL_FIELDS[self.kind]
        # Allow only documented machine metadata. This prevents media,
        # coordinates, arbitrary personal data and spoofed approvals entering
        # the local metadata store.
        if not expected.issubset(self.payload) or not set(self.payload).issubset(allowed):
            raise ValueError("Payload fields do not match the strict event contract")

        if self.kind in {"camera_detection", "acoustic_event"}:
            label = self.payload["label"]
            confidence = self.payload["confidence"]
            if (
                not isinstance(label, str)
                or not 1 <= len(label) <= 64
                or any(ord(char) < 32 for char in label)
            ):
                raise ValueError("Invalid detection label")
            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
                or not math.isfinite(confidence)
                or not 0 <= confidence <= 1
            ):
                raise ValueError("Invalid confidence")
            if self.kind == "camera_detection":
                if "origin_event_id" in self.payload:
                    origin_id = self.payload["origin_event_id"]
                    if not isinstance(origin_id, str) or not SOURCE_EVENT_ID.fullmatch(origin_id):
                        raise ValueError("Invalid origin event ID")
                if "verification_status" in self.payload and self.payload["verification_status"] != "unverified":
                    raise ValueError("Only unverified candidate status is accepted")
                if "prey_detected" in self.payload and type(self.payload["prey_detected"]) is not bool:
                    raise ValueError("prey_detected must be boolean")
        elif self.kind == "hive_telemetry":
            temperature = self.payload["temperature_c"]
            humidity = self.payload["humidity_pct"]
            if (
                isinstance(temperature, bool)
                or not isinstance(temperature, (int, float))
                or not math.isfinite(temperature)
                or not -60 <= temperature <= 100
            ):
                raise ValueError("Telemetry temperature outside plausible range")
            if (
                isinstance(humidity, bool)
                or not isinstance(humidity, (int, float))
                or not math.isfinite(humidity)
                or not 0 <= humidity <= 100
            ):
                raise ValueError("Telemetry humidity outside plausible range")
        else:
            mites = self.payload["mites"]
            examined = self.payload["bees_examined"]
            if type(mites) is not int or type(examined) is not int:
                raise ValueError("Varroa counts must be integers")
            if not 0 <= mites <= 1_000_000 or not 0 <= examined <= 100_000_000:
                raise ValueError("Varroa counts outside plausible range")

    def to_json(self) -> str:
        self.validate()
        return json.dumps(self.__dict__, ensure_ascii=False, allow_nan=False, sort_keys=True)

    @classmethod
    def from_json(cls, raw: str) -> "HiveEvent":
        if not isinstance(raw, str) or len(raw.encode("utf-8")) > 32768:
            raise ValueError("Event too large")
        def reject_duplicate_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("Duplicate JSON object key")
                result[key] = value
            return result

        def reject_nonstandard_constant(value):
            raise ValueError("Non-standard JSON numeric constant")

        data = json.loads(
            raw,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonstandard_constant,
        )
        if not isinstance(data, dict) or set(data) != {
            "kind", "device_id", "timestamp", "payload", "source", "schema_version"
        }:
            raise ValueError("Unexpected event structure")
        event = cls(**data)
        event.validate()
        return event
