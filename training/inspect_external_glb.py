#!/usr/bin/env python3
"""Offline, read-only GLB + provenance inspector. Never grants training approval."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

MAX_BYTES = 100 * 1024 * 1024

def inspect(glb, license_file, manifest_file):
    report = {"model": glb.name, "training_approved": "NO", "species_verified": "NO",
              "geometry_verified": "NO", "license_verified": "NO", "issues": []}
    if not glb.is_file():
        report["issues"].append("GLB file missing")
        return report
    size = glb.stat().st_size
    if size > MAX_BYTES or size < 20:
        report["issues"].append("GLB size invalid or exceeds 100 MiB")
        return report
    data = glb.read_bytes()
    report["sha256"] = hashlib.sha256(data).hexdigest()
    magic, version, total = struct.unpack_from("<4sII", data)
    if magic != b"glTF" or version != 2 or total != len(data):
        report["issues"].append("Invalid GLB 2.0 header")
        return report
    offset, doc = 12, None
    while offset + 8 <= len(data):
        chunk_len, chunk_type = struct.unpack_from("<I4s", data, offset)
        offset += 8
        if chunk_len % 4 or offset + chunk_len > len(data):
            report["issues"].append("Invalid GLB chunk length")
            return report
        if chunk_type == b"JSON" and doc is None:
            try:
                doc = json.loads(data[offset:offset + chunk_len].decode("utf-8"))
            except (UnicodeError, ValueError):
                report["issues"].append("Invalid glTF JSON")
                return report
        offset += chunk_len
    if offset != len(data) or not isinstance(doc, dict):
        report["issues"].append("Missing/invalid glTF JSON chunk")
        return report
    report["mesh_count"] = len(doc.get("meshes", []))
    report["material_count"] = len(doc.get("materials", []))
    report["image_count"] = len(doc.get("images", []))
    if not report["mesh_count"]:
        report["issues"].append("No mesh objects")
    if any("uri" in x and str(x["uri"]).startswith(("http:", "https:")) for x in doc.get("buffers", []) + doc.get("images", [])):
        report["issues"].append("External network resource in glTF")
    if not license_file.is_file():
        report["issues"].append("LICENSE.txt missing")
    else:
        license_text = license_file.read_text(encoding="utf-8", errors="replace")
        report["license_mentions_cc0"] = "CC0" in license_text.upper()
        if not report["license_mentions_cc0"]:
            report["issues"].append("LICENSE.txt does not mention CC0")
    if not manifest_file.is_file():
        report["issues"].append("manifest.json missing")
    else:
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            report["manifest_present"] = isinstance(manifest, dict)
            if not isinstance(manifest, dict):
                report["issues"].append("manifest.json must contain an object")
        except ValueError:
            report["issues"].append("manifest.json invalid JSON")
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--glb", type=Path, required=True)
    p.add_argument("--license", dest="license_file", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("training/glb-provenance-review.json"))
    args = p.parse_args()
    result = inspect(args.glb, args.license_file, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result["issues"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
