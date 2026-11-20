# Apiary AI modules — experimental, not approved for diagnosis

This catalog is an integration **contract**, not a model, weight file, or working inference implementation. Every module starts disabled; never present a result as confirmed without independent evidence and human review.

| Module ID | Task | Input | Candidate / status | Output | Field limitation |
|---|---|---|---|---|---|
| `varroa_board` | Count mites on removable bottom-board insert | Sharp overhead macro image + scale | VarroDetector candidate; rights and weight checks pending | Unconfirmed count + boxes | Cannot equate counts to infestation without sampling protocol |
| `varroa_on_bee` | Detect visible mites on bees | Macro image of bee body | Gratheon models-varroa-on-bee, YOLO11n; rights and weights pending | Unconfirmed boxes | Reported varroa recall 0.651; negative result does not exclude infestation |
| `queen_on_comb` | Locate queen on comb | Focused comb photo/video | Gratheon models-queen-bee-detector, YOLOv8n; rights and weights pending | Unconfirmed box | Reported recall 0.859; no detection does not mean queenless |
| `swarm_activity` | Detect abnormal flight-entrance activity | Time-stamped counts, video + optionally hive weight | No validated swarm prediction model selected | Activity anomaly, never definitive swarm prediction | Orientation flights and weather can confound |
| `pollen_flow` | Count pollen-bearing arrivals | Entrance video | New labeled data and model required | Pollen-carrying counts | Does not directly measure pollen stores |
| `brood_pattern` | Describe visible brood pattern | Well-lit comb images | Separate segmentation dataset required | Review-only overlays | No disease diagnosis |

## Proposed standard module manifest

```json
{
  "schema": "vespaguard.apiary-module.v1",
  "id": "queen_on_comb",
  "enabled": false,
  "release_status": "research_only",
  "task": "object_detection",
  "runtime": "onnxruntime-web-or-local-edge",
  "weights_sha256": null,
  "weights_license": null,
  "training_data_evidence": null,
  "independent_validation_evidence": null,
  "hardware_acceptance_evidence": null,
  "human_confirmation_required": true
}
```

## Requirements before activating any module

1. Verify original repository, exact version/commit, code and weights licenses, dependencies (including Ultralytics terms), training images and per-image attribution; record SHA-256 of the precise model artifact.
2. Evaluate independent test images from new hives, devices, seasons and lighting. Publish per-class precision, recall, confidence intervals and false positives/negatives per operating hour; do not claim 99% without evidence.
3. Run inference locally by default. Do not send images, audio or GPS to third-party APIs without a separate privacy review and user consent or other documented legal basis.
4. Return `unconfirmed` candidate events only. Never auto-trigger treatment, queen replacement or swarm intervention.
5. Test real iPhone, Android and Raspberry Pi hardware for latency, battery, offline recovery and thermal behavior.
6. Keep existing hornet detector and PWA unaffected. Only integrate code and weights after explicit field release evidence is approved.

## Candidate references (not incorporated)

- https://github.com/Gratheon/models-varroa-on-bee
- https://github.com/Gratheon/models-queen-bee-detector
- https://github.com/jodivaso/varrodetector
- https://gratheon.com/research/models/

Research metrics belong to the respective authors and are **not VespaGuard performance measurements**.
