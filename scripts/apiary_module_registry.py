"""Fail-closed registry for optional apiary AI modules. No inference or weights bundled."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

MODULES = frozenset({"varroa_board", "varroa_on_bee", "queen_on_comb", "swarm_activity", "pollen_flow", "brood_pattern"})
REQUIRED = ("weights_sha256", "weights_license", "training_data_evidence",
            "independent_validation_evidence", "hardware_acceptance_evidence")

class ModuleNotReady(ValueError):
    """Model cannot be used without documented evidence."""

def validate_manifest(manifest: dict, *, weights_path: str | Path | None = None) -> dict:
    if not isinstance(manifest, dict) or manifest.get("schema") != "vespaguard.apiary-module.v1":
        raise ModuleNotReady("Invalid apiary module schema")
    if manifest.get("id") not in MODULES:
        raise ModuleNotReady("Unknown apiary module")
    if manifest.get("human_confirmation_required") is not True:
        raise ModuleNotReady("Human confirmation must remain mandatory")
    if manifest.get("enabled") is not True or manifest.get("release_status") != "field_approved":
        raise ModuleNotReady("Module is disabled or research-only")
    for key in REQUIRED:
        value = manifest.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ModuleNotReady(f"Missing evidence: {key}")
    expected = manifest["weights_sha256"]
    if len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected):
        raise ModuleNotReady("Invalid SHA-256 digest")
    if weights_path is None:
        raise ModuleNotReady("No local model weights supplied")
    p = Path(weights_path)
    if not p.is_file():
        raise ModuleNotReady("Model weights missing")
    digest = hashlib.file_digest(p.open("rb"), "sha256").hexdigest()
    if digest != expected:
        raise ModuleNotReady("Model weight digest mismatch")
    return {"id": manifest["id"], "status": "evidence_present_not_independently_verified"}

def load_manifest(path: str | Path, *, weights_path: str | Path | None = None) -> dict:
    with Path(path).open("r", encoding="utf-8") as stream:
        manifest = json.load(stream)
    return validate_manifest(manifest, weights_path=weights_path)
