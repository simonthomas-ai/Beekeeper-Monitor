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

def inspect(download=False, inspect_graph=False, run_inference=False, real_cc0=False, multispecies=False):
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
        graph = {}
        if inspect_graph:
            import onnx
            model = onnx.load(str(target), load_external_data=False)
            if any(t.data_location == onnx.TensorProto.EXTERNAL for t in model.graph.initializer):
                raise ValueError("External ONNX tensor data not permitted")
            def tensors(values):
                return [{"name": v.name, "type": onnx.helper.printable_type(v.type)} for v in values]
            graph = {"ir_version": model.ir_version, "opsets": [{"domain": x.domain, "version": x.version} for x in model.opset_import],
                     "inputs": tensors(model.graph.input), "outputs": tensors(model.graph.output),
                     "nodes": len(model.graph.node), "operators": sorted(set(n.op_type for n in model.graph.node)),
                     "metadata": {x.key: x.value[:2000] for x in model.metadata_props}}
        if run_inference:
            import numpy as np
            import onnxruntime as ort
            session = ort.InferenceSession(str(target), providers=["CPUExecutionProvider"])
            input_meta, output_meta = session.get_inputs(), session.get_outputs()
            if len(input_meta) != 1 or input_meta[0].name != "images" or input_meta[0].shape != [1, 3, 640, 640]:
                raise ValueError("Unexpected ONNX input contract")
            if len(output_meta) != 1 or output_meta[0].name != "output0" or output_meta[0].shape != [1, 9, 8400]:
                raise ValueError("Unexpected ONNX output contract")
            # Controlled synthetic frame; this is NOT a real hornet image or accuracy test.
            frame = np.zeros((1, 3, 640, 640), dtype=np.float32)
            output = session.run(["output0"], {"images": frame})[0]
            if output.shape != (1, 9, 8400) or not np.isfinite(output).all():
                raise ValueError("Unexpected or non-finite inference output")
            from scripts.hornet3000_decode import decode_raw
            decoded = decode_raw(output, confidence=0.5)
            graph["synthetic_decoder"] = {
                "status": "passed",
                "unverified_candidate_count": len(decoded),
                "unverified_velutina_candidates": sum(x["class_id"] == 3 for x in decoded),
                "real_image_tested": False,
                "validated_species_detection": False,
            }
            graph["synthetic_inference"] = {"status": "passed", "input": [1, 3, 640, 640],
                "output": list(output.shape), "finite": True, "real_image_tested": False,
                "accuracy_validated": False, "camera_connected": False}
        if real_cc0:
            from scripts.hornet3000_real_cc0_probe import run
            graph["real_cc0_probe"] = run(target)
        if multispecies:
            from scripts.hornet3000_cc0_multispecies import run as run_multispecies
            graph["cc0_multispecies_screen"] = run_multispecies(target)
        return {"status": "bytes_verified_not_executed", "source": URL,
                "bytes": total, "git_blob": git_blob.hexdigest(),
                "sha256": digest.hexdigest(), "graph": graph, "license_approved": False,
                "inference_validated": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--inspect-graph", action="store_true", help="Read ONNX graph metadata, never run inference")
    parser.add_argument("--synthetic-inference", action="store_true", help="CPU inference on a zero-valued synthetic frame")
    parser.add_argument("--real-cc0", action="store_true", help="Research-only inference on fresh verified CC0 iNaturalist image")
    parser.add_argument("--multispecies", action="store_true", help="Research-only CC0 photo comparison across four taxa")
    args = parser.parse_args()
    if (args.inspect_graph or args.synthetic_inference or args.real_cc0 or args.multispecies) and not args.download:
        parser.error("--inspect-graph requires --download")
    result = inspect(args.download, args.inspect_graph, args.synthetic_inference, args.real_cc0, args.multispecies)
    if args.synthetic_inference:
        result["status"] = "synthetic_inference_passed_not_validated"
    print(json.dumps(result, indent=2))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write("## hornet3000 ONNX-Pruefung\n\n")
            out.write("Status: " + result["status"] + ". Keine Inferenz oder Freigabe.\n\n")
            if result.get("sha256"):
                out.write("SHA-256: " + result["sha256"] + "\n")
            if result.get("graph"):
                out.write("ONNX-Graph (statisch, ohne Inferenz):\\n\\n```json\\n" + json.dumps(result["graph"], indent=2) + "\\n```\\n")

if __name__ == "__main__":
    main()
