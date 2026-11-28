# Verified availability of external Varroa weights (20 Nov 2026)

Repository API tree inspection confirmed **real weight files**, not merely descriptions:

| Use case | Upstream | Weight path | GitHub reported size | Repository license |
|---|---|---|---:|---|
| Mite fall on sticky board | https://github.com/jodivaso/varrodetector | \`model/weights/best.pt\` | 9,596,067 bytes | AGPL-3.0 |
| Visible mites on bee | https://github.com/Gratheon/models-varroa-on-bee | \`yolo11n.pt\` | 5,613,764 bytes | AGPL-3.0 |

**Critical distinctions**
- Both are **PyTorch \`.pt\` files**, not ONNX. The existing \`scripts/apiary_onnx_adapter.py\` cannot execute them. A separate, sandboxed conversion/evaluation process with trusted Ultralytics/PyTorch dependencies is required.
- GitHub's AGPL-3.0 repository license is not sufficient by itself to establish complete rights to training images, all model components, dependencies, and deployment. Verify the license scope for each weight, dataset provenance and network-service obligations.
- Never load untrusted \`.pt\` with unrestricted Python pickle in the website or CI. Do not automatically download or execute external weights.
- VarroDetector analyzes **sticky-board mite fall**, not mites directly on bees. Gratheon analyzes **mites on bees** and reports varroa recall 0.651 on its own evaluation, not on VespaGuard images.
- No weights were copied into VespaGuard. No runtime integration or detection accuracy is claimed.

## Download safety gate – 28 November 2026

The upstream VarroDetector weight is not approved for use. Its manifest records \`weights_license_independently_confirmed=false\`, \`download_authorized=false\`, and no authorization reference.

The downloader now has a separate code-level default-off switch (\`MODEL_WEIGHT_DOWNLOADS_ENABLED = False\`). Manifest booleans and a text reference alone cannot enable external network access. The switch must not be changed until an independent review has documented the exact weight license, training-data rights, attribution, intended use and a separately reviewed authorization. The GitHub Actions workflow for this candidate runs only local synthetic-byte tests with read-only repository permission; it does not fetch external model bytes or publish an artifact. Its policy test restricts the workflow to one pinned checkout action and two exact local test commands.

A later download approval would still not authorize deserialization, conversion, inference, training, redistribution or deployment. Each requires its own security, rights and validation review.

## Practical next actions
1. Record exact upstream commit, Git blob ID, download SHA-256, model card, license evidence and attribution for each candidate.
2. Review conversion risks and third-party license requirements before isolated export to ONNX.
3. Independently evaluate images from distinct hives/cameras, report false negatives and false positives, and require human verification.
4. Only then add a local image workflow to the PWA behind a disabled-by-default feature gate.

Sources: https://github.com/jodivaso/varrodetector and https://github.com/Gratheon/models-varroa-on-bee
