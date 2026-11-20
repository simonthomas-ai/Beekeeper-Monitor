# Verified availability of external Varroa weights (20 Nov 2026)

Repository API tree inspection confirmed **real weight files**, not merely descriptions:

| Use case | Upstream | Weight path | GitHub reported size | Repository license |
|---|---|---|---:|---|
| Mite fall on sticky board | https://github.com/jodivaso/varrodetector | `model/weights/best.pt` | 9,596,067 bytes | AGPL-3.0 |
| Visible mites on bee | https://github.com/Gratheon/models-varroa-on-bee | `yolo11n.pt` | 5,613,764 bytes | AGPL-3.0 |

**Critical distinctions**
- Both are **PyTorch `.pt` files**, not ONNX. The existing `scripts/apiary_onnx_adapter.py` cannot execute them. A separate, sandboxed conversion/evaluation process with trusted Ultralytics/PyTorch dependencies is required.
- GitHub's AGPL-3.0 repository license is not sufficient by itself to establish complete rights to training images, all model components, dependencies, and deployment. Verify the license scope for each weight, dataset provenance and network-service obligations.
- Never load untrusted `.pt` with unrestricted Python pickle in the website or CI. Do not automatically download or execute external weights.
- VarroDetector analyzes **sticky-board mite fall**, not mites directly on bees. Gratheon analyzes **mites on bees** and reports varroa recall 0.651 on its own evaluation, not on VespaGuard images.
- No weights were copied into VespaGuard. No runtime integration or detection accuracy is claimed.

## Practical next actions
1. Record exact upstream commit, Git blob ID, download SHA-256, model card, license evidence and attribution for each candidate.
2. Review conversion risks and third-party license requirements before isolated export to ONNX.
3. Independently evaluate images from distinct hives/cameras, report false negatives and false positives, and require human verification.
4. Only then add a local image workflow to the PWA behind a disabled-by-default feature gate.

Sources: https://github.com/jodivaso/varrodetector and https://github.com/Gratheon/models-varroa-on-bee
