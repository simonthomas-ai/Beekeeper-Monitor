"""Strict per-class test evidence validation for the pinned Ultralytics result API."""
from __future__ import annotations

import math
from numbers import Real

try:
    from .class_schema import CLASS_NAMES
except ImportError:  # Supports direct execution from training/
    from class_schema import CLASS_NAMES


METRIC_KEYS = {
    "Box-P": "precision",
    "Box-R": "recall",
    "Box-F1": "f1",
    "mAP50": "map50",
    "mAP75": "map75",
    "mAP50-95": "map50_95",
}


def _positive_count(value, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{field} must be a positive integer")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 1 or not numeric.is_integer():
        raise ValueError(f"{field} must be a positive integer")
    return int(numeric)


def _unit_metric(value, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{field} must be finite and within 0..1")
    numeric = float(value)
    if not math.isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{field} must be finite and within 0..1")
    return numeric


def validate_per_class_summary(rows, class_names=CLASS_NAMES) -> dict:
    """Validate Ultralytics DetMetrics.summary() output for every required class.

    Ultralytics 8.4.215 reports only classes represented in the test targets.
    The training pipeline separately requires nonzero objects for all classes
    in train/val/test; this second guard ensures every class's metrics are
    present, numeric and bounded before an ONNX artifact is exported.
    """
    names = tuple(class_names)
    if not names or len(set(names)) != len(names):
        raise ValueError("required class schema must be non-empty and unique")
    if not isinstance(rows, list):
        raise ValueError("per-class test summary must be a list")

    indexed = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("per-class test summary rows must be objects")
        name = row.get("Class")
        if not isinstance(name, str) or name not in names:
            raise ValueError("test summary contains an unknown or invalid class")
        if name in indexed:
            raise ValueError(f"duplicate per-class test metrics for {name}")

        images = _positive_count(row.get("Images"), f"{name}.Images")
        instances = _positive_count(row.get("Instances"), f"{name}.Instances")
        metrics = {
            key: _unit_metric(row.get(source_key), f"{name}.{source_key}")
            for source_key, key in METRIC_KEYS.items()
        }
        indexed[name] = {
            "images": images,
            "instances": instances,
            **metrics,
        }

    missing = [name for name in names if name not in indexed]
    if missing:
        raise ValueError("test summary is missing required classes: " + ", ".join(missing))
    return {name: indexed[name] for name in names}
