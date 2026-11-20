# Detector training framework and model licence options

Review date: 2026-11-20. This register is a technical screening, not legal advice or a model acceptance.

## Current repository licensing blocker

Both project repository roots currently have no standard `LICENSE` file. The component inventory (`LICENSES.md`) is not a licence grant for the whole BeeKeeper3000 or Beekeeper-Monitor source tree. Before distributing a station image, executable or complete project, the owner must select and publish an explicit project licence for each repository and check that their relationship is compatible.

Do not infer that a public GitHub repository, a nonprofit purpose or a free-to-use dependency grants a general licence to the project source.

## Candidate training frameworks

| Candidate | Upstream code/model scope | Initial assessment | Required checks |
|---|---|---|---|
| RF-DETR Nano / Small / Medium / Large | Official package and these core model families are described as Apache-2.0 | **Preferred candidate for a permissive benchmark** | Pin exact version; verify the exact checkpoint, included backbone/pretraining assets and downstream dependencies; preserve notices; export and validate an ONNX contract |
| YOLOX | Official repository is Apache-2.0 and documents ONNX/OpenVINO deployment | **Secondary benchmark candidate** | Verify the exact pretrained checkpoint separately; confirm currently supported dependencies and reproducible export |
| PaddleDetection | Official repository is Apache-2.0; supports multiple detection families and edge deployment | **Possible alternative, heavier integration** | Review the exact selected config/checkpoint, Paddle runtime, dependency licences and CPU/Raspberry Pi resource footprint |
| Ultralytics YOLO | AGPL-3.0 by default; Enterprise licence is a separate paid route | **Not the default for a permissively licensed station release** | Use only after the full-project AGPL decision and compatibility review, or a valid applicable licence |

### RF-DETR scope boundary

The current RF-DETR official documentation identifies Nano, Small, Medium and Large detection models as Apache-2.0. The optional Atto, Femto, Pico, XLarge and 2XLarge detection models are listed under Roboflow Platform Model License (PML 1.0); they are excluded from this free self-hosted candidate set unless their terms are independently confirmed for the intended deployment.

- Package and component licence overview: https://github.com/roboflow/rf-detr
- Official installation/licence documentation: https://rfdetr.roboflow.com/latest/getting-started/install/
- Official pretrained-model matrix: https://rfdetr.roboflow.com/latest/learn/pretrained/

### YOLOX scope boundary

The official YOLOX source repository declares Apache-2.0 and documents ONNX, TensorRT, ncnn and OpenVINO paths. That does not automatically establish the licence of every checkpoint, third-party weight or dataset used with YOLOX. Each actual file must have its own immutable source URL, licence record and SHA-256 before use.

- Official source: https://github.com/Megvii-BaseDetection/YOLOX
- Official licence file: https://github.com/Megvii-BaseDetection/YOLOX/blob/main/LICENSE

### Ultralytics restriction

The current training script uses `ultralytics[export]==8.4.215` and a YOLO11 checkpoint path. Ultralytics' official licensing guidance says the AGPL route requires release of the entire corresponding project under AGPL-3.0, or an Enterprise licence where the user does not want to release that source. It also describes trained Ultralytics models as AGPL by default. A non-profit label alone is not an exemption.

The script's `--accept-agpl` switch is only an operator acknowledgement; it is not legal clearance and does not make the current repository's missing root-level project licence disappear. No Ultralytics checkpoint or derivative is approved for distribution or station deployment by this document.

Official licensing:
- https://www.ultralytics.com/license
- https://github.com/ultralytics/ultralytics

## Benchmark plan before choosing a production trainer

The model architecture is not selected on COCO leaderboard scores. Once a legally approved, human-reviewed seven-class insect dataset exists:

1. Train RF-DETR Nano and one independently licence-cleared YOLOX candidate with identical train/validation/test manifests and the same site/photographer/observation group boundaries.
2. Evaluate on a locked test set from unseen cameras and apiaries; do not use the test set for hyperparameter tuning or confidence calibration.
3. Report per-class precision, recall, AP50 and AP50:95, confusion matrix, false positives per camera-hour, missed detections and confidence intervals.
4. Measure cold-start time, sustained CPU latency/FPS, RAM, thermal throttling, energy use and ONNX Runtime compatibility on the actual Windows Ryzen station and the intended Raspberry Pi class device.
5. Keep a separate unknown/uncertain category in operator workflow; never turn weak detections into confirmed nest locations.
6. Record exact code revision, package lock, model checkpoint SHA-256, model and dataset licences, export command, ONNX graph I/O contract and reproducibility evidence.

## Decision now

- Keep the existing generic ONNX runtime as the camera inference boundary.
- Keep the current Ultralytics path explicitly experimental and licence-gated.
- Add RF-DETR Nano and YOLOX only as **candidate benchmarks**; do not silently replace the trainer or download weights.
- Do not choose a project-wide licence without explicit owner approval.
- No camera model accuracy, legal clearance, hardware compatibility or production readiness is claimed.
