# iNaturalist candidate discovery (no automatic training)

Run from the repository root:

```sh
python training/discover_inaturalist_candidates.py --per-species 20
```

This uses the public iNaturalist observations API to find recent research-grade
observations of Vespa velutina, Vespa crabro and Vespula vulgaris, then filters
**each photo's** license code to CC0 or CC BY. It writes a CSV review queue,
not an approved training manifest. It does not download images.

## Image resolution

iNaturalist API photo URL fields and older candidate exports can point at the
square derivative (75 × 75 px). That is unsuitable for visual identification
or annotation. The discovery, verification and gallery pipeline now normalizes
known iNaturalist photo URLs to the original derivative before presenting them.
iNaturalist documents this as its largest hosted derivative, up to 2048 px on
the longest edge; it is not necessarily the camera-original file. The review
page reports the actual decoded pixel dimensions after the browser loads the image.

For observation **414481366**, photo **763034625**, the old gallery used the
square.jpg variant; it now uses the original.jpg variant. The candidate remains
unreviewed and is not automatically eligible for training.

**Required human review:** verify the license *version* and author on the
original photo page; iNaturalist API's `cc-by` code alone does not establish
CC BY **4.0**. Verify actual species, photo quality, use rights, observation
independence and any labeling requirements. The CSV's CC-BY-4.0 mapping is a
tentative importer-format placeholder, NOT a verified license grant; change or
exclude any row that cannot be verified. No YOLO bounding boxes are produced.

Only after review, copy the first seven fields of approved rows to a separate
`approved_images.csv` and use `training/import_authorized_images.py`.
Do not commit unreviewed photos, credentials or personal location data.
API calls should be infrequent and respect iNaturalist's service policies.
