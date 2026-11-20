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
FIELDS = {
    "camera_detection": {"label", "confidence"},
    "acoustic_event": {"label", "confidence"},
    "hive_telemetry": {"temperature_c", "humidity_pct"},
    "varroa_count": {"mites", "bees_examined"},
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
            raise ValueError("Invalid device ID")
        if not isinstance(self.source, str) or not IDENTIFIER.fullmatch(self.source):
            raise ValueError("Invalid source ID")
        if not isinstance(self.timestamp, str) or not 1 <= len(self.timestamp) <= 40:
            raise ValueError("Timestamp required")
        try:
            dt = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Invalid timestamp") from exc
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("Timestamp must have timezone")
        if not isinstance(self.payload, dict) or set(self.payload) != FIELDS[self.kind]:
            raise ValueError("Payload fields do not match the strict event contract")

        if self.kind in {"camera_detection", "acoustic_event"}:
            label = self.payload["label"]
            confidence = self.payload["confidence"]
            if not isinstance(label, str) or not LABEL.fullmatch(label.strip()):
                raise ValueError("Invalid detection label")
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not math.isfinite(confidence):
                raise ValueError("Invalid confidence")
            if not 0 <= confidence <= 1:
                raise ValueError("Confidence outside 0..1")
        elif self.kind == "hive_telemetry":
            temperature = self.payload["temperature_c"]
            humidity = self.payload["humidity_pct"]
            for value in (temperature, humidity):
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise ValueError("Invalid telemetry value")
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
        data = json.loads(raw)
        expected = {"kind", "device_id", "timestamp", "payload", "source", "schema_version"}
        if not isinstance(data, dict) or set(data) != expected:
            raise ValueError("Unexpected event structure")
        event = cls(**data)
        event.validate()
        return event
