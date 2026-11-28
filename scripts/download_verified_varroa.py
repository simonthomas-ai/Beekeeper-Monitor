"""Download a pinned upstream model only after explicit rights authorization.

Never import torch, ultralytics or pickle here. Never deserialize or run the weights.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from scripts.verify_varroa_source_blob import verify

UPSTREAM_COMMIT = "31c2cebd289ebfd558153d73ccc52c05f76067d8"
SOURCE_URL = (
    "https://raw.githubusercontent.com/jodivaso/varrodetector/"
    + UPSTREAM_COMMIT + "/model/weights/best.pt"
)


def _require_download_authorization(manifest: dict) -> None:
    if not isinstance(manifest, dict):
        raise ValueError("Invalid Varroa source manifest")
    if manifest.get("weights_license_independently_confirmed") is not True:
        raise ValueError("Blocked: independent model-weight license review is not confirmed")
    if manifest.get("download_authorized") is not True:
        raise ValueError("Blocked: explicit model-weight download authorization is missing")
    reference = manifest.get("download_authorization_ref")
    if not isinstance(reference, str) or not reference.strip():
        raise ValueError("Blocked: download authorization review reference is required")


def download_verified(destination: Path, manifest: dict, opener=urlopen) -> dict:
    _require_download_authorization(manifest)
    if destination.exists() or destination.is_symlink():
        raise ValueError("Refusing to overwrite an existing path")
    if not isinstance(manifest.get("bytes"), int) or not 0 < manifest["bytes"] <= 25_000_000:
        raise ValueError("Invalid pinned file size")
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_name(destination.name + ".partial")
    if tmp.exists() or tmp.is_symlink():
        raise ValueError("Refusing to overwrite an existing partial file")
    try:
        request = Request(SOURCE_URL, headers={"User-Agent": "VespaGuard-source-verifier/1"})
        with opener(request, timeout=60) as response, tmp.open("xb") as output:
            if response.geturl() != SOURCE_URL:
                raise ValueError("Unexpected upstream redirect")
            remaining = manifest["bytes"]
            while True:
                chunk = response.read(min(1024 * 1024, remaining + 1))
                if not chunk:
                    break
                remaining -= len(chunk)
                if remaining < 0:
                    raise ValueError("Upstream download exceeded pinned byte count")
                output.write(chunk)
            if remaining:
                raise ValueError("Truncated upstream download")
        result = verify(tmp, manifest)
        os.replace(tmp, destination)
        return {**result, "source_url": SOURCE_URL, "downloaded_bytes": manifest["bytes"],
                "approval": "blocked_pending_license_and_independent_validation",
                "converted_to_onnx": False}
    finally:
        tmp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/model-sources/varrodetector-best.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--record", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = download_verified(args.output, manifest)
    args.record.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
