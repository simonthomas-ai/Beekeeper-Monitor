# Manual VarroDetector ONNX export — blocked until review

Upstream: https://github.com/jodivaso/varrodetector (`model/weights/best.pt`, 9,596,067 bytes reported by GitHub on 2026-11-20). Repository metadata says AGPL-3.0; verify that the model weights, data and dependencies can be used under the intended deployment and redistribution terms.

**Security warning:** PyTorch `.pt` files may deserialize unsafe pickle content. Do not run this exporter in GitHub Actions, the production server, a beekeeper's phone, or on a trusted workstation. Only use a disposable, network-disabled sandbox after manual provenance and legal review. No automatic upstream downloads.

After recording the *actual downloaded file* SHA-256, invoke within that isolated environment:

```sh
python3 scripts/export_varroa_onnx.py --weights /reviewed/best.pt \
  --sha256 <64-character-verified-sha256> \
  --reviewed-source-and-license --imgsz 640 \
  --output-record /reviewed/export-record.json
```

The command requires separately installed, pinned Ultralytics/PyTorch dependencies and does **not** constitute approval. The resulting ONNX requires verified output semantics, preprocessing, postprocessing/NMS, independent mite counts and camera field trials. No actual ONNX or `.pt` weights are committed.
