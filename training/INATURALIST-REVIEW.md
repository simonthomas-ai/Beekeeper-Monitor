# iNaturalist candidate discovery (no automatic training)

Run from the repository root:

```sh
python training/discover_inaturalist_candidates.py --target 1000 --max-pages 12
python training/screen_inaturalist_image_quality.py --input training/inaturalist-review-queue.csv --output training/inaturalist-quality-screen.csv
```

This uses the public iNaturalist observations API to find recent research-grade
observations of Vespa velutina, Vespa crabro and Vespula vulgaris, then filters
**each photo's** license code to CC0 or CC BY. It writes a CSV review queue,
not an approved training manifest. It does not download images.

## Balanced 1,000-candidate target

The default research intake is balanced across five review groups, with a target
of **200 independent observations per group**:

| Dataset group | Scientific taxa retained in the CSV | Target |
|---|---|---:|
| Asian hornet | Vespa velutina | 200 |
| European hornet | Vespa crabro | 200 |
| Honey bee | Apis mellifera | 200 |
| Bumblebees | Bombus terrestris; Bombus lapidarius | 200 |
| Wasps | Vespula vulgaris; Vespula germanica | 200 |

For the two multi-taxon groups, the initial target is split 100/100 between the
scientific taxa. If one taxon has too few eligible observations, the remaining
quota is backfilled from the other taxon in the same group only. The exact
species name remains in `species_candidate`; `dataset_group` is a separate
sampling and review field and never replaces the taxonomic identification.

If sources do not provide enough suitable, independently observed, licensed
photos, the workflow reports a shortfall instead of duplicating images,
weakening license checks or inventing records. All records remain
`UNREVIEWED`; this is a candidate pool, not 1,000 approved training images.
The workflow also generates `training/inaturalist-review-gallery.html` with
a filter for the five groups.

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

The candidate queue keeps `creator`, `creator_login`, the source-provided
`license_notice` and the formatted `attribution` in separate columns. CC0
attribution follows iNaturalist's documented observer-name/login format.
**Required human review:** verify the license *version* and author on the
original photo page; iNaturalist API's `cc-by` code alone does not establish
CC BY **4.0**. Verify actual species, photo quality, use rights, observation
independence and any labeling requirements. `CC-BY-VERSION-UNVERIFIED` is
deliberately not accepted as CC-BY-4.0 and cannot pass training provenance.
No YOLO bounding boxes are produced.

A dedicated GitHub Actions workflow runs the balanced 1,000-candidate metadata
discovery weekly and stores the CSV plus its metadata-audit report as a
short-lived Actions artifact. It does not commit candidate metadata to `main`,
download image bytes, or approve training. The workflow can also be started
manually from the Actions tab. Local audit command:

```sh
python training/audit_inaturalist_candidates.py \
  --input training/inaturalist-review-queue.csv \
  --output training/inaturalist-metadata-audit.json
```

Only after review, copy the first seven fields of approved rows to a separate
`approved_images.csv` and use `training/import_authorized_images.py`.
Do not commit unreviewed photos, credentials or personal location data.
API calls should be infrequent and respect iNaturalist's service policies.


## Unveränderte Originaldateien in der öffentlichen Velutina-Prüfung

Die Datei-Prüfung ist nicht mit einer Bildbearbeitung gleichzusetzen. `training/download_original_inaturalist_images.py` lädt nur Kandidaten mit bestandener Dateiprüfung und exakter CC0-API-Nachprüfung herunter. Die Original-Response-Bytes werden unverändert gespeichert; SHA-256, Dateiformat, Pixelmaße und Dateigröße stehen im Manifest. GitHub Pages übernimmt die Originaldateien aus einem Actions-Artefakt. Vor Deployment werden die Hashes erneut verglichen. Es gibt keine Größenänderung, kein Zuschneiden, keine Drehung, keine EXIF-Umschreibung, keine Neukodierung, keine Kompression und keine Thumbnail-Erzeugung. Die Galerie verweist lokal auf genau diese Bytes.
