# GBIF mobile media review

The GBIF workflow can generate `training/gbif-media-review-gallery.html` from the metadata-only candidate queue. The gallery is a local human-review aid, not an automated classifier or a training approval tool.

## What the gallery displays

- GBIF occurrence link and occurrence ID.
- Scientific name and GBIF species key.
- Media format, media creator/rights holder and publisher.
- Media licence and its official licence URL.
- Occurrence licence and its official licence URL, separately from the media licence.
- Media URL and hosting domain.

Every candidate must remain in `UNREVIEWED_MEDIA_RIGHTS_AND_IMAGE`. The browser stores visual review decisions locally in `localStorage`; use the JSON export to preserve them. Exported records remain `training_eligible=false`. `LIKELY` means only that the reviewer considers the candidate plausible and is not an expert-confirmed species label.

## Automatic image embedding policy

The gallery embeds an image only when all of the following hold:

1. The URL is credential-free HTTPS, with no query string or fragment.
2. The host is exactly `inaturalist-open-data.s3.amazonaws.com` or `static.inaturalist.org`.
3. The path is exactly the GBIF media's iNaturalist photo ID followed by `/original.jpg`, `/original.jpeg`, `/original.png` or `/original.webp`.
4. The path extension matches the declared media MIME type.

No URL on a different host or to a thumbnail derivative is assigned to the image element. It appears as an untrusted-host exception instead. The media URL is still visible as a manually actionable link, so a qualified reviewer can assess it separately. This does not imply that the external host or file is approved for bulk download or training use.

The HTML contains no image bytes. When a reviewer opens it, the browser requests only images that pass the allowlist. The generated Actions artifact contains CSV/JSON/HTML metadata only.

## Human review and licensing

A CC0 or CC BY label from GBIF is metadata, not independent proof that the uploader owns the media rights or that the pictured organism has been identified correctly. Confirm the actual source page, the relevant rights holder, exact licence version, attribution requirements, and any third-party restrictions before reuse. Media and occurrence licences are distinct: retain both.

For every candidate, a reviewer should determine:

- Is the target organism visible and identifiable?
- Is the scientific name correct based on the pixels, not merely the GBIF occurrence record?
- Is the image sufficiently sharp and the specimen sufficiently large?
- Does the image show an insect rather than only a nest, environment, drawing or unrelated subject?
- Are both media and occurrence rights documented, and is attribution complete?
- Is the source suitable for redistribution and the intended training use?

Uncertain records must be marked `REJECT` or left `PENDING`; never force an uncertain observation into a class. An independent expert must verify the species and bounding boxes before creating reviewed labels.

## Training-data boundary

The gallery does not create boxes, YOLO labels, dataset splits, annotations or model approvals. Human gallery decisions are still proposals. The downstream training gate requires a separate per-image provenance record, expert-confirmed class, independently quality-assured bounding boxes, duplicate checks, group-safe train/validation/test splits and a separate held-out evaluation set.

See also [the main training-data issue](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/191).


## Reconcile a local visual-review export

The gallery export is a proposal record, not a training dataset. Before archiving it, reconcile it against the exact original GBIF queue used to build the gallery:

```sh
python training/import_gbif_visual_reviews.py \
  --queue training/gbif-media-review-queue.csv \
  --review-export beekeeper-gbif-visual-review.json \
  --output training/gbif-visual-review-audit.json \
  --reviewer "Name of reviewer" \
  --recorded-at "2026-11-22T10:00:00+01:00"
```

The importer requires every original candidate exactly once. It rejects changed source IDs, occurrence URLs, species keys/names, media URLs, host allowlist decisions, licence URLs, creator/rights-holder fields, and any attempt to set `training_eligible=true` or add boxes/labels. The output records the decision counts, reviewer and timestamp, but explicitly keeps zero expert species confirmations, zero bounding boxes, zero training labels and zero training approvals.

The output path must be new; an existing audit file is never overwritten. Keep the original queue, review export and reconciled audit together so the review is reproducible.
