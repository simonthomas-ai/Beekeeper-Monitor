"""VespaGuard vendor-neutral event contracts. No external code or training data."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
import json
import math

Kind = Literal["camera_detection", "acoustic_event", "hive_telemetry", "varroa_count"]
ALLOWED = {"camera_detection", "acoustic_event", "hive_telemetry", "varroa_count"}

@dataclass(frozen=True)
class HiveEvent:
    kind: Kind
    device_id: str
    timestamp: str
    payload: dict
    source: str = "unverified"
    schema_version: int = 1

    def validate(self) -> None:
        if self.kind not in ALLOWED or self.schema_version != 1:
            raise ValueError("Unsupported event kind/version")
        if not isinstance(self.device_id, str) or not 1 <= len(self.device_id) <= 128:
            raise ValueError("Invalid device ID")
        if not isinstance(self.source, str) or not 1 <= len(self.source) <= 128:
            raise ValueError("Invalid source")
        if not isinstance(self.timestamp, str):
            raise ValueError("Timestamp required")
        try:
            dt = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Invalid timestamp") from exc
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("Timestamp must have timezone")
        if not isinstance(self.payload, dict):
            raise ValueError("Payload must be object")
        required = {
            "camera_detection": {"label": str, "confidence": float},
            "acoustic_event": {"label": str, "confidence": float},
            "hive_telemetry": {"temperature_c": float, "humidity_pct": float},
            "varroa_count": {"mites": int, "bees_examined": int},
        }[self.kind]
        for key, typ in required.items():
            value = self.payload.get(key)
            if typ is float:
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise ValueError(f"Invalid {key}")
            elif type(value) is not typ:
                raise ValueError(f"Invalid {key}")
        if self.kind in {"camera_detection", "acoustic_event"}:
            if not self.payload["label"] or not 0 <= self.payload["confidence"] <= 1:
                raise ValueError("Invalid detection label/confidence")
        elif self.kind == "hive_telemetry":
            if not -60 <= self.payload["temperature_c"] <= 100 or not 0 <= self.payload["humidity_pct"] <= 100:
                raise ValueError("Telemetry outside plausible range")
        else:
            if self.payload["mites"] < 0 or self.payload["bees_examined"] < 0:
                raise ValueError("Negative counts")
        # Explicitly disallow model assertions or human approval through untrusted events.
        for field in ("training_approved", "species_verified", "license_verified"):
            if field in self.payload:
                raise ValueError(f"Untrusted approval field: {field}")

    def to_json(self) -> str:
        self.validate()
        return json.dumps(self.__dict__, ensure_ascii=False, allow_nan=False, sort_keys=True)

    @classmethod
    def from_json(cls, raw: str) -> "HiveEvent":
        if len(raw) > 32768:
            raise ValueError("Event too large")
        data = json.loads(raw)
        if not isinstance(data, dict) or set(data) != {"kind", "device_id", "timestamp", "payload", "source", "schema_version"}:
            raise ValueError("Unexpected event structure")
        event = cls(**data)
        event.validate()
        return event
