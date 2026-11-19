# Online hornet data sources and license review (2026-11-19)

This is a source review, **not** proof of downloaded or verified training images.
Do not copy third-party photographs into this repository until their exact license
and attribution requirements have been recorded. Never assume that public access
means permission to redistribute or train on images.

| Source | URL | License shown at source | Required review |
|---|---|---|---|
| ISR Vespa velutina v1 | https://universe.roboflow.com/institute-of-systems-and-robotics-isr/vespa-velutina-hihv9-upzpe/dataset/1 | CC BY 4.0; 1,508 images listed | Verify downloaded export license, author attribution, original provenance, annotations, split leakage |
| One Two Vespa_velutina | https://universe.roboflow.com/one-two-s-workspace/vespa_velutina | CC BY 4.0 shown on project page | Verify version, export, original images and duplicates |
| Other Vespa velutina Roboflow | https://universe.roboflow.com/vespa-velutina/vespa-velutina-a9tnw | CC BY 4.0 shown on project page | Verify source and overlap with other Roboflow projects |
| iNaturalist Open Data | https://github.com/inaturalist/inaturalist-open-data | Per-photo license; CC0, CC BY and CC BY-NC among possibilities | Record each photo's actual license, author, photo ID, observation ID, URL |
| iNaturalist observations | https://www.inaturalist.org/ | Default photo license CC BY-NC; individual creators may choose other terms or all rights reserved | Filter by photo license, not observation license; no blanket reuse |
| GBIF occurrence data | https://www.gbif.org/ | Dataset/occurrence and media rights may differ | Record dataset citation DOI, image rights, publisher, attribution |

License reminders:
- **CC0:** attribution encouraged but generally not required.
- **CC BY 4.0:** credit creator, link license, indicate changes, retain provenance.
- **CC BY-SA:** attribution and share-alike conditions for adapted material.
- **CC BY-NC:** non-commercial use only; do not assume a public PWA or donations make every use non-commercial.
- **All rights reserved / unclear:** exclude pending permission.
- Model weights, code and source images may have **different licenses**.
- Roboflow-hosted exports may require account/API credentials. Never commit API keys.
- Source licenses do not guarantee the source uploader owned the original images.

For every admitted image maintain a manifest with:
`source_id, source_url, original_image_url, creator, license, license_url, attribution, sha256, species_review, annotation_review, split`.

Recommended pipeline: review license -> download authorized export -> preserve provenance ->
review species and boxes -> de-duplicate and isolate train/val/test ->
run `python training/validate_hornet.py --dataset datasets/hornet` ->
train only after independent holdout review.

Do not label the detector accurate or production-ready until independent evaluation
(including bees, European hornets and wasps as negative examples) passes.
