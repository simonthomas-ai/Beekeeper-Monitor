"""Controlled *manual* export of an independently reviewed VarroDetector .pt model.

Run only in an isolated disposable environment after verifying provenance and licenses.
This tool deliberately does not download or execute anything by default.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def validate_export_request(weights: Path, expected_sha256: str, *, reviewed: bool) -> None:
    if not reviewed:
        raise ValueError("Explicit review acknowledgement required")
    if not weights.is_file() or weights.suffix.lower() != ".pt":
        raise ValueError("Expected a local PyTorch .pt file")
    if weights.stat().st_size < 1024 or weights.stat().st_size > 250 * 1024 * 1024:
        raise ValueError("Unexpected weights file size")
    if len(expected_sha256) != 64 or any(x not in "0123456789abcdef" for x in expected_sha256):
        raise ValueError("Expected lowercase SHA-256")
    if sha256(weights) != expected_sha256:
        raise ValueError("Upstream model digest mismatch")

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--reviewed-source-and-license", action="store_true")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--output-record", type=Path, required=True)
    args = parser.parse_args()
    validate_export_request(args.weights, args.sha256, reviewed=args.reviewed_source_and_license)
    if not 64 <= args.imgsz <= 2048:
        parser.error("imgsz out of range")
    # WARNING: .pt deserialization may execute code. Only run inside an isolated,
    # disposable, network-disabled environment with an explicitly reviewed source.
    from ultralytics import YOLO
    model = YOLO(str(args.weights))
    exported = Path(model.export(format="onnx", imgsz=args.imgsz, simplify=False, dynamic=False))
    if exported.suffix.lower() != ".onnx" or not exported.is_file():
        raise RuntimeError("ONNX export did not produce a file")
    record = {
        "schema": "vespaguard.apiary-export.v1",
        "module": "varroa_board",
        "source_pt_sha256": args.sha256,
        "exported_onnx_sha256": sha256(exported),
        "exported_onnx_bytes": exported.stat().st_size,
        "imgsz": args.imgsz,
        "status": "conversion_only_not_validated_not_approved",
        "manual_legal_review_required": True,
        "independent_detection_validation_required": True,
    }
    args.output_record.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))

if __name__ == "__main__":
    main()
