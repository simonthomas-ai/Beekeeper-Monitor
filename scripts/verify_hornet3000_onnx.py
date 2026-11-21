#!/usr/bin/env python3
"""Download and verify pinned ONNX bytes without executing the model."""
import argparse
import hashlib
import json
import os
import tempfile
import urllib.request
from pathlib import Path

COMMIT = "78f51980ee99e45748e78e54dd1312cff846a5ac"
PATH = "yolov8sModel/best.onnx"
BLOB = "97fb748affc642238c1135768a53098f594de0d1"
SIZE = 44737849
URL = "https://raw.githubusercontent.com/vespCV/hornet3000/" + COMMIT + "/" + PATH

def inspect(download=False):
    if not download:
        return {"status": "not_downloaded", "source": URL, "expected_bytes": SIZE}
    req = urllib.request.Request(URL, headers={"User-Agent": "VespaGuard-research-integrity/1"})
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "candidate.onnx"
        digest = hashlib.sha256()
        git_blob = hashlib.sha1()
        git_blob.update(("blob " + str(SIZE) + "\\0").encode("ascii"))
        total = 0
        with urllib.request.urlopen(req, timeout=60) as response, target.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > SIZE:
                    raise ValueError("Size exceeds pinned Git tree")
                digest.update(chunk)
                git_blob.update(chunk)
                out.write(chunk)
        if total != SIZE or git_blob.hexdigest() != BLOB:
            raise ValueError("Git blob identity or size mismatch")
        return {"status": "bytes_verified_not_executed", "source": URL,
                "bytes": total, "git_blob": git_blob.hexdigest(),
                "sha256": digest.hexdigest(), "license_approved": False,
                "inference_validated": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    result = inspect(args.download)
    print(json.dumps(result, indent=2))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write("## hornet3000 ONNX-Pruefung\\n\\n")
            out.write("Status: " + result["status"] + ". Keine Inferenz oder Freigabe.\\n\\n")
            if result.get("sha256"):
                out.write("SHA-256: " + result["sha256"] + "\\n")

if __name__ == "__main__":
    main()
