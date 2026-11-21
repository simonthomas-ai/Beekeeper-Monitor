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

def inspect(download=False, inspect_graph=False):
    if not download:
        return {"status": "not_downloaded", "source": URL, "expected_bytes": SIZE}
    req = urllib.request.Request(URL, headers={"User-Agent": "VespaGuard-research-integrity/1"})
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "candidate.onnx"
        digest = hashlib.sha256()
        git_blob = hashlib.sha1()
        git_blob.update(("blob " + str(SIZE) + "\0").encode("ascii"))
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
        graph = {}\n        if inspect_graph:\n            import onnx\n            model = onnx.load(str(target), load_external_data=False)\n            if any(t.data_location == onnx.TensorProto.EXTERNAL for t in model.graph.initializer):\n                raise ValueError("External ONNX tensor data not permitted")\n            def tensors(values):\n                return [{"name": v.name, "type": onnx.helper.printable_type(v.type)} for v in values]\n            graph = {"ir_version": model.ir_version, "opsets": [{"domain": x.domain, "version": x.version} for x in model.opset_import],\n                     "inputs": tensors(model.graph.input), "outputs": tensors(model.graph.output),\n                     "nodes": len(model.graph.node), "operators": sorted(set(n.op_type for n in model.graph.node)),\n                     "metadata": {x.key: x.value[:2000] for x in model.metadata_props}}\n        return {"status": "bytes_verified_not_executed", "source": URL,
                "bytes": total, "git_blob": git_blob.hexdigest(),
                "sha256": digest.hexdigest(), "graph": graph, "license_approved": False,
                "inference_validated": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--inspect-graph", action="store_true", help="Read ONNX graph metadata, never run inference")\n    args = parser.parse_args()\n    if args.inspect_graph and not args.download:\n        parser.error("--inspect-graph requires --download")
    result = inspect(args.download, args.inspect_graph)
    print(json.dumps(result, indent=2))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write("## hornet3000 ONNX-Pruefung\n\n")
            out.write("Status: " + result["status"] + ". Keine Inferenz oder Freigabe.\n\n")
            if result.get("sha256"):
                out.write("SHA-256: " + result["sha256"] + "\n")\n            if result.get("graph"):\n                out.write("ONNX-Graph (statisch, ohne Inferenz):\\n\\n```json\\n" + json.dumps(result["graph"], indent=2) + "\\n```\\n")

if __name__ == "__main__":
    main()
