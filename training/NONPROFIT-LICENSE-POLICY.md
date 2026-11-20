# Free resources for the nonprofit bee-protection project

Updated 2026-11-19. This file documents candidate sources; it does not certify
their images, export access, or any resulting model for production.

## Open-source local annotation and QA tooling
- CVAT Community (MIT, self-hosted) for bounding-box annotation and YOLO export: https://github.com/cvat-ai/cvat. Review bundled FFmpeg LGPL/GPL components before redistribution.
- FiftyOne (Apache-2.0) for local duplicate discovery, dataset curation and model error analysis: https://github.com/voxel51/fiftyone.
- These tools do not license source images; per-image media rights remain mandatory. See [DATASET-ANNOTATION-WORKFLOW.md](DATASET-ANNOTATION-WORKFLOW.md).

## Source priority
1. **CC0**: preferred when authorship and image provenance can be verified.
2. **CC BY 4.0**: allowed with creator credit, license link, change notice and provenance.
3. **CC BY-SA**: review share-alike requirements for adaptations and redistribution.
4. **CC BY-NC / CC BY-NC-SA**: consider only after confirming the particular use is
   genuinely noncommercial and any share-alike conditions are met. Nonprofit or
   charitable purpose **alone does not automatically establish** noncommercial use.
5. **No license, all rights reserved, or ambiguous source rights**: exclude until
   written permission is obtained.
6. **CC BY-ND / CC BY-NC-ND**: do not redistribute modified images; seek
   permission before distributing transformations. Evaluate training use separately.

## Candidate datasets (license listed on source page, not yet export-verified)
- ISR Vespa velutina (CC BY 4.0):
  https://universe.roboflow.com/institute-of-systems-and-robotics-isr/vespa-velutina-hihv9-upzpe/dataset/1
- Vespa velutina v1 (CC BY 4.0):
  https://universe.roboflow.com/vespa-velutina-pobjr/vespa-velutina-nubcn/dataset/1
- AutoBee three classes, including European hornet and common wasp (CC BY 4.0):
  https://universe.roboflow.com/autobee/vespa-velutina
- One Two Vespa_velutina (CC BY 4.0, small candidate):
  https://universe.roboflow.com/one-two-s-workspace/vespa_velutina
- iNaturalist: photo-by-photo license, not one universal license:
  https://github.com/inaturalist/inaturalist-open-data

Roboflow project images may overlap or contain augmented duplicates.
Do not add reported image totals across projects as unique specimens.

## Required records for every imported image
source URL, creator, source dataset/version, exact photo license and URL,
attribution text, download date, SHA256, original observation/image ID,
species label review, box annotation review, train/val/test split.

Before training, verify source uploader rights, export availability, negative
classes, duplicates and near-duplicates, and independent test isolation.
Do not upload private API keys to GitHub. No downloads or training are claimed.

References:
- https://creativecommons.org/licenses/by/4.0/
- https://creativecommons.org/licenses/by-nc/4.0/
- https://creativecommons.org/licenses/by-nc-sa/4.0/


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
