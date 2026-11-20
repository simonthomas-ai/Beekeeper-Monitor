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

## Scope and class policy

The current dataset schema expects six object-detection classes:

0. `vespa_velutina`
1. `varroa_destructor`
2. `drone_brood`
3. `pollen_bearing_bee`
4. `bee_swarm`
5. `queen_bee`

This is a provisional engineering taxonomy, not a biological standard. In particular, Varroa mite inspection, brood-cell inspection and flying insect detection have very different image scales and acquisition setups. Do not mix them into one camera detector merely because they fit a single class index. Keep them as separately evaluated tasks and models when their camera modalities differ. The six-class trainer exists as a gated baseline only; a domain review should decide whether this should become several task-specific models before collecting production labels.

For the Vespa task, include difficult negative examples and confusion species (especially Vespa crabro, Vespula, Dolichovespula, bees, hoverflies and unknown insects) in a broader taxonomy plan. The existing six-class YAML does not yet represent those negatives; do not map them falsely to another positive class. Until the taxonomy is expanded and validated, preserve unknown/other records outside the six-class training set.

## Intake sequence

1. Discover source metadata only through approved APIs or manually documented source pages.
2. Check the **individual image/media license**, not just the dataset/observation license. Reject CC BY-NC, CC BY-ND, unknown, missing, conflicting or unversioned licenses from this initial trainer.
3. Confirm the source uploader was entitled to grant the license. Preserve source URL, dataset version, creator, rights-holder and original attribution. CC BY 4.0 requires attribution in the provenance record; CC0 remains traceable even when attribution is not a legal condition.
4. Download only manually approved source images into the private dataset directory. Never commit private image files, RTSP credentials, precise apiary GPS or reviewer personal details to this public repository.
5. Hash every exact image file with SHA-256 and create one provenance record for each image.
6. Assign an expert-checked species label and bounding boxes in CVAT. Record both review statuses as `verified` only after a human reviewer has checked them; automated labels are suggestions, not accepted ground truth.
7. Assign groups before splitting: observation, photographer and site must each belong to exactly one of train/val/test. Use stable pseudonymous IDs, not people's names or exact locations. This blocks near-duplicate leakage between splits.
8. Run the provenance gate, label geometry validator, duplicate checks and image review. Then run FiftyOne QA for duplicate, near-duplicate, lighting, scale, outlier and class imbalance inspection.
9. Only then train and evaluate. Select thresholds on validation data, never on the final test set. Preserve test metrics, confusion matrices, per-class precision/recall, false-positive events per station-day and confidence intervals.
10. A separate field capture set from unseen sites/cameras and a human entomology review is required before calling the detector operational.

## Required provenance manifest

Every dataset root must contain `provenance.jsonl`. Each line corresponds to exactly one image file; the validator rejects unlisted images, duplicate image bytes, bad hashes, unsupported rights, missing attribution, unverified labels, path traversal and split leakage.

Example (replace every value; never use these example IDs as evidence):

~~~json
{
  "image_path": "images/train/observation-001-frame-01.jpg",
  "sha256": "REPLACE_WITH_REAL_64_CHARACTER_SHA256",
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

For CC-BY-4.0, `creator` and `attribution_text` must be populated. `source_url` and `license_url` must be HTTPS. The accepted initial SPDX values are deliberately restricted to `CC0-1.0` and `CC-BY-4.0`. CC-BY-SA and public-domain-mark records may be considered only after a separate downstream dataset/model redistribution review.

## Validation

From the Monitor repository root:

~~~sh
python -m unittest training.test_provenance -v
python scripts/model_readiness.py
python -m pip install PyYAML==6.0.3
python training/train.py --validate-only
~~~

The last command succeeds only when actual images, labels, class coverage and the complete provenance manifest exist. It does not train a model.

Actual Ultralytics training is additionally gated behind explicit `--accept-agpl` because the configured Ultralytics path has AGPL-3.0 obligations. This flag is an operator acknowledgement, not legal advice. The generated ONNX export uses the post-NMS six-column format consumed by BeeKeeper3000's camera inference adapter. The exported model and manifest remain marked **experimental**; the configured confidence threshold is not a calibrated operating threshold.

## Data protection and deletion

- Strip EXIF/GPS metadata from approved images before annotation and keep a controlled source-to-pseudonym lookup outside the public repository.
- Do not upload private apiary imagery to hosted annotation SaaS, shared demos or public issue trackers.
- Keep exact site coordinates out of provenance records; use stable pseudonyms only.
- Keep creator/attribution strings only as necessary for license compliance, with access restricted to dataset maintainers.
- Implement source-rights revocation: identify affected image hashes, remove them from train/val/test and future exports, record the deletion event, then retrain/evaluate any model whose training corpus changed.
- Retain model hashes, training configuration, code revision and evidence files, not deleted media bytes.
