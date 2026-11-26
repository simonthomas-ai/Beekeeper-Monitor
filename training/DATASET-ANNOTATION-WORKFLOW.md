# Reproducible dataset intake and annotation workflow

Status: internal preparation only. This document does not approve any image or model, and no source contributor or institution has been contacted.

## Free, self-hosted annotation and review tools

### CVAT Community — primary bounding-box annotator

- Upstream: https://github.com/cvat-ai/cvat
- Documentation: https://docs.cvat.ai/docs/getting_started/overview/
- YOLO export: https://docs.cvat.ai/docs/manual/advanced/formats/format-yolo/
- CVAT Community is self-hosted and MIT licensed. CVAT's stack also uses FFmpeg components with LGPL/GPL licensing; review the exact container/dependency set and any redistribution obligations before bundling it. Online and Enterprise offerings are separate products and are not required for local annotation.
- Use it for bounding boxes, track review and independent human QA. Export annotations to YOLO format for the existing trainer.

### FiftyOne — local dataset review and quality analysis

- Upstream: https://github.com/voxel51/fiftyone
- Documentation: https://docs.voxel51.com/
- The open-source FiftyOne toolkit is Apache-2.0; the hosted/commercial Voxel51 platform is separate. Run the local toolkit against the dataset directory. Use it for duplicate/near-duplicate discovery, class balance, visual outlier inspection and model error analysis. It does not grant rights to the images it displays.

### Label Studio — alternative annotation tool

- Upstream: https://github.com/HumanSignal/label-studio
- Export guide: https://labelstud.io/guide/export.html
- The Community Edition can export YOLO annotations, but confirm the exact release and component license inventory before adopting it as a bundled dependency. Choose one primary annotator (CVAT recommended); do not maintain parallel, unsynchronised annotation sources.

These tools do not supply the dataset. The source image's own license, the uploader's rights, privacy restrictions and attribution requirements remain applicable regardless of the tool used.

## Mobile review export → local expert queue

The mobile gallery and the seven-class training intake are deliberately separate. A gallery export is an **unverified visual-review record**, not a YOLO annotation file: its rectangles have no per-object class IDs, and a `LIKELY` decision does not confirm species, image rights or bounding-box correctness.

The public candidate galleries and Actions image artifacts were discontinued on 2026-11-26. Do not download or use any legacy public Actions artifact as a training source. The CC0 discovery workflow now removes its temporary image files and generated candidate metadata from the runner and publishes no candidate artifacts.

For a private expert review, obtain each original image directly from its source only after an individual review of the media license, source identity and uploader's authority. Store approved files in a private, access-controlled directory and create the local manifest from the actual file bytes (byte count and SHA-256). Keep license evidence and any source-to-pseudonym mapping outside this public repository.

1. Keep review exports, source evidence and original images on a private local disk; do not commit them or upload them to public Actions artifacts.
2. Create `velutina-original-images-manifest.csv` for the privately approved files. Bind each photo ID to its observation URL, exact source image URL, concrete media license, attribution, local relative path, byte count and SHA-256. A metadata label of CC0 alone is not sufficient.
3. Export the local visual-review JSON only after the source image is available in the private review workspace.
4. Stage the JSON without granting training approval:

~~~sh
python training/stage_mobile_reviews.py /secure/review-export.json \
  --asset-root /secure/approved-originals \
  --output /secure/expert-queue.json
~~~

The stager checks each local path against the photo ID and manifest row, requires CC0-1.0 and the expected source metadata, rejects symlinks/path traversal, and recomputes the actual file byte count and SHA-256. It rejects missing artifacts, altered files and mismatched mobile-export hashes. The output remains `training_eligible: false`; it records no expert signoff and creates no training labels.

4. A qualified reviewer must inspect the actual original pixels and verify species, per-media rights, attribution, image suitability and every proposed box. Use CVAT Community for the actual class-labelled bounding boxes and independent annotation QA. The simple mobile rectangles are suggestions only; they must not be imported directly as class-labelled YOLO ground truth.
5. Only after review, export CVAT annotations to the expected YOLO structure, create the per-image image/label SHA-256 provenance records, assign observation/photographer/site groups to one split each, and run the provenance and training validators. Keep the source-rights evidence and reviewer signoff under controlled access.

### Prepare the seven-class CVAT task pack

After a mobile export has been staged into an expert queue, prepare a local image-only task pack:

~~~sh
python scripts/prepare_cvat_review_pack.py /secure/expert-queue.json \
  --asset-root /secure/approved-originals \
  --output-dir /secure/cvat-review-pack
~~~

The pack contains:
- `cvat-images.zip`: only the original image files, copied without image conversion or recompression; SHA-256 and byte counts are checked again while the ZIP is written.
- `labels.json`: the exact seven names from `training/class_schema.py`, offered as task labels only; no image receives a class assignment.
- `metadata.csv`: photo/observation IDs, source URL, creator, CC0 license, mobile decision, original file path, SHA-256 and bytes.
- `SHA256SUMS.txt` and `summary.json`: pack integrity and explicit zero-annotation/zero-approval status.

Create a CVAT Community image task, add the seven labels from `labels.json`, and upload only `cvat-images.zip` as the image archive. Keep `metadata.csv` with the task for provenance. The pack does not contain YOLO label files, imported boxes or approval flags. CVAT's current task guide describes creating labels and uploading local image files or an image archive: https://docs.cvat.ai/docs/workspace/tasks-page/. CVAT CLI also accepts a JSON label schema and local image inputs: https://docs.cvat.ai/docs/api_sdk/cli/.

The package generator refuses existing output directories, output paths inside the approved original asset root, altered files, missing manifest entries, symlinks and any queue that claims training approval. Its tests verify the seven-class schema and byte-preserving ZIP as well as the non-approval invariant:

~~~sh
python -m unittest scripts.test_prepare_cvat_review_pack -v
~~~

The stager's regression tests include valid local manifest-backed files, missing asset roots, changed bytes, a mobile SHA mismatch, path mismatch, symlink rejection and the non-approval invariant:

~~~sh
python -m unittest training.test_stage_mobile_reviews -v
~~~

## Scope and class policy

The camera-training baseline is a **seven-class insect detector** aimed at the Asian hornet field workflow:

0. `vespa_velutina` — Asian hornet
1. `vespa_crabro` — European hornet
2. `other_vespidae` — other wasps in the Vespidae family
3. `apis_mellifera` — honey bee
4. `bombus_spp` — bumblebees
5. `syrphidae` — hoverflies
6. `other_insect` — other insects and hard negatives

This is a provisional engineering taxonomy. Species identification must be reviewed by a qualified human expert; the model cannot infer a nest location or authorise destruction. `other_vespidae` and `other_insect` are important hard-negative groups, not catch-all classes for unidentified positives. When species cannot be reliably determined, keep the image in an unlabelled review queue rather than forcing a false positive label.

The previous mixed hive-inspection classes (Varroa mite counts, brood, pollen loads, swarms and queen identification) belong to separate imaging tasks and must not be mixed into this insect-camera detector. They can be supported later by their own datasets, task-specific models and acceptance protocols.

## Intake sequence

1. Discover source metadata only through approved APIs or manually documented source pages.
2. Check the **individual image/media license**, not just the dataset/observation license. Reject CC BY-NC, CC BY-ND, unknown, missing, conflicting or unversioned licenses from this initial trainer.
3. Confirm the source uploader was entitled to grant the license. Preserve source URL, dataset version, creator, rights-holder and original attribution. CC BY 4.0 requires attribution in the provenance record; CC0 remains traceable even when attribution is not a legal condition.
4. Download only manually approved source images into the private dataset directory. Never commit private image files, RTSP credentials, precise apiary GPS or reviewer personal details to this public repository.
5. Hash every exact image file and its corresponding YOLO label file with SHA-256. Store both paths and hashes in the same provenance record; the label path must mirror the image split and stem.
6. Assign an expert-checked species label and bounding boxes in CVAT. Record both review statuses as `verified` only after a human reviewer has checked them; automated labels are suggestions, not accepted ground truth.
7. Assign groups before splitting: observation, photographer and site must each belong to exactly one of train/val/test. Use stable pseudonymous IDs, not people's names or exact locations. This blocks near-duplicate leakage between splits.
8. Run the provenance gate (image and annotation file hashes), label geometry validator, duplicate checks and image review. Then run FiftyOne QA for duplicate, near-duplicate, lighting, scale, outlier and class imbalance inspection.
9. Only then train and evaluate. Select thresholds on validation data, never on the final test set. Preserve test metrics, confusion matrices, per-class precision/recall, false-positive events per station-day and confidence intervals.
10. A separate field capture set from unseen sites/cameras and a human entomology review is required before calling the detector operational.

## Required provenance manifest

Every dataset root must contain `provenance.jsonl`. Each line binds exactly one image file to exactly one YOLO label file, including their individual SHA-256 values. The label file path must be the same relative stem under `labels/<same split>/`. The validator rejects unlisted images or labels, duplicate image bytes, bad image or label hashes, unsupported rights, missing attribution, unverified labels, path traversal and split leakage. Changing a reviewed label after approval invalidates the provenance record.

Example (replace every value; never use these example IDs as evidence):

~~~json
{
  "image_path": "images/train/observation-001-frame-01.jpg",
  "sha256": "REPLACE_WITH_REAL_64_CHARACTER_IMAGE_SHA256",
  "label_path": "labels/train/observation-001-frame-01.txt",
  "label_sha256": "REPLACE_WITH_REAL_64_CHARACTER_LABEL_SHA256",
  "source_url": "https://example.org/original-image-page",
  "source_dataset": "dataset-name",
  "source_version": "immutable-version-or-release",
  "license_spdx": "CC0-1.0",
  "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
  "creator": "creator-attribution-as-published",
  "attribution_text": "Attribution text; required for CC-BY-4.0",
  "downloaded_at": "2026-11-20T10:00:00Z",
  "observation_group": "obs-pseudonym-001",
  "photographer_group": "photographer-pseudonym-001",
  "site_group": "apiary-pseudonym-001",
  "species_review_status": "verified",
  "bbox_review_status": "verified",
  "reviewer_id": "reviewer-pseudonym-001",
  "reviewed_at": "2026-11-20T12:00:00Z"
}
~~~

For every image, `label_path` and `label_sha256` are mandatory and bind the exact YOLO annotation bytes to the review record. For CC-BY-4.0, `creator` and `attribution_text` must be populated. `source_url` and `license_url` must be HTTPS. The accepted initial SPDX values are deliberately restricted to `CC0-1.0` and `CC-BY-4.0`. CC-BY-SA and public-domain-mark records may be considered only after a separate downstream dataset/model redistribution review.

## Validation

From the Monitor repository root:

~~~sh
python -m unittest training.test_provenance -v
python scripts/model_readiness.py
python -m pip install -r training/requirements-training.txt
python training/train.py --validate-only
~~~

The last command succeeds only when actual images, labels, class coverage and the complete provenance manifest exist. It does not train a model.

After a manual review of the AGPL terms, install the pinned training environment, acquire a pretrained checkpoint from a documented source, and verify its exact SHA-256 before starting training:

~~~powershell
Get-FileHash .\models\yolo11n.pt -Algorithm SHA256
python training/train.py --pretrained-model .\models\yolo11n.pt --pretrained-model-sha256 <64-character-lowercase-sha256> --pretrained-model-source-url https://github.com/ultralytics/assets/releases --accept-agpl --device cpu
~~~

Automatic checkpoint downloads are intentionally disabled. The script checks the local checkpoint hash and exact Ultralytics package version, trains a single seven-class baseline, evaluates the held-out test split, exports an ONNX model with an explicit post-NMS matrix6 output, and writes a model manifest plus training evidence. The confidence threshold in that initial manifest is a configurable starting value only; it is not calibrated.

Actual Ultralytics training is additionally gated behind explicit `--accept-agpl` because the configured Ultralytics path has AGPL-3.0 obligations. This flag is an operator acknowledgement, not legal advice. The generated ONNX export uses the post-NMS six-column format consumed by BeeKeeper3000's camera inference adapter. The exported model and manifest remain marked **experimental**; the configured confidence threshold is not a calibrated operating threshold.

## Data protection and deletion

- Strip EXIF/GPS metadata from approved images before annotation and keep a controlled source-to-pseudonym lookup outside the public repository.
- Do not upload private apiary imagery to hosted annotation SaaS, shared demos or public issue trackers.
- Keep exact site coordinates out of provenance records; use stable pseudonyms only.
- Keep creator/attribution strings only as necessary for license compliance, with access restricted to dataset maintainers.
- Implement source-rights revocation: identify affected image hashes, remove them from train/val/test and future exports, record the deletion event, then retrain/evaluate any model whose training corpus changed.
- Retain model hashes, training configuration, code revision and evidence files, not deleted media bytes.
