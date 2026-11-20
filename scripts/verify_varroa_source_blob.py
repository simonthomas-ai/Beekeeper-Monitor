"""Offline exact-byte check against upstream Git tree metadata; never deserializes .pt."""
import argparse
import hashlib
import json
from pathlib import Path


def verify(path: Path, manifest: dict) -> dict:
    if not path.is_file() or path.is_symlink():
        raise ValueError("Expected a regular local file, not a symlink")
    expected_size = manifest["bytes"]
    expected_blob = manifest["git_blob_sha1"]
    if not isinstance(expected_size, int) or expected_size <= 0 or path.stat().st_size != expected_size:
        raise ValueError("File size differs from recorded upstream Git blob")
    if not isinstance(expected_blob, str) or len(expected_blob) != 40 or any(c not in "0123456789abcdef" for c in expected_blob):
        raise ValueError("Invalid upstream Git blob SHA-1")
    sha1 = hashlib.sha1()
    sha1.update(b"blob " + str(expected_size).encode() + bytes([0]))
    sha256 = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            sha1.update(chunk)
            sha256.update(chunk)
    if sha1.hexdigest() != expected_blob:
        raise ValueError("Local bytes do not match upstream Git blob")
    return {"source_blob_verified": True, "source_git_blob_sha1": expected_blob, "local_sha256": sha256.hexdigest(), "legal_review_complete": False, "model_validated": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path("data/model-sources/varrodetector-best.json"))
    args = parser.parse_args()
    print(json.dumps(verify(args.weights, json.loads(args.manifest.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
