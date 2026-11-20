"""Audit a local third-party ONNX artifact without executing untrusted model code.

This is a provenance intake, not license approval or model validation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

def inspect_artifact(path: str | Path, *, source_url: str, license_spdx: str,
                     attribution: str, module: str) -> dict:
    from scripts.apiary_module_registry import MODULES
    p = Path(path)
    if not p.is_file() or p.suffix.lower() != ".onnx":
        raise ValueError("Provide a local .onnx model file")
    if p.stat().st_size == 0 or p.stat().st_size > 250 * 1024 * 1024:
        raise ValueError("Model must be nonempty and at most 250 MiB")
    u = urlsplit(source_url)
    if u.scheme != "https" or not u.hostname or u.username or u.password:
        raise ValueError("Model source must be a public HTTPS URL")
    if module not in MODULES:
        raise ValueError("Unknown module")
    if not license_spdx.strip() or not attribution.strip():
        raise ValueError("License claim and attribution required")
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return {
        "schema": "vespaguard.apiary-artifact-intake.v1",
        "module": module, "source_url": source_url,
        "license_claim_unverified": license_spdx,
        "attribution": attribution, "sha256": h.hexdigest(),
        "bytes": p.stat().st_size, "review_status": "pending_human_license_and_model_validation",
        "approved_for_inference": False,
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--attribution", required=True)
    parser.add_argument("--module", required=True)
    args = parser.parse_args()
    print(json.dumps(inspect_artifact(args.model, source_url=args.source_url,
        license_spdx=args.license, attribution=args.attribution,
        module=args.module), indent=2))

if __name__ == "__main__":
    main()
