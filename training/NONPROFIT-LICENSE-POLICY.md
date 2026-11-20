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
