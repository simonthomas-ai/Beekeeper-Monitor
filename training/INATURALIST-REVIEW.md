# iNaturalist candidate discovery (no automatic training)

Run from the repository root:

```sh
python training/discover_inaturalist_candidates.py --per-species 20
```

This uses the public iNaturalist observations API to find recent research-grade
observations of Vespa velutina, Vespa crabro and Vespula vulgaris, then filters
**each photo's** license code to CC0 or CC BY. It writes a CSV review queue,
not an approved training manifest. It does not download images.

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
