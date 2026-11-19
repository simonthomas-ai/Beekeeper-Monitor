# External 3D insect model candidates — manual license review

This list is **discovery only**. No source listed here has been approved for model training, download, redistribution, or synthetic image generation. Verify each model's individual license, provenance, taxonomy, mesh quality, and permitted uses before use.

| Candidate | Source URL | Claimed/possible license | Species verified | License verified | Geometry verified | Training approved | Notes |
|---|---|---|---|---|---|---|---|
| Grab3D Honey Bee (bee.glb) | https://grab3d.com/models/animals/bee/ | Publisher explicitly labels CC0 1.0; 36 MB GLB (800k triangles), 17 MB light GLB (400k triangles), no login; provenance LICENSE.txt/manifest.json offered | NO | PUBLISHER CLAIM CHECKED; FILE PROVENANCE NOT CHECKED | NO | NO | Static honey bee with pollen; publisher says high-detail base meshes are AI-generated and reworked. Do not treat as taxonomically verified. |
| Sketchfab insect collection | https://sketchfab.com/shotworld0720/collections/bug-28275def471e4acda224fee9f354f361 | Per-model licenses vary | NO | NO | NO | NO | Collection is not a license; check each model separately |
| Asian hornet (Vespa velutina) | https://sketchfab.com/3d-models/asian-hornet-vespa-velutina-9855d99180034cf79b0d3e961b6a4db6 | CC BY-NC-SA reported; independently verify on model page | NO | NO | NO | NO | Noncommercial and share-alike restrictions; do not ingest automatically |

## Approval gate

1. Open original model page and capture creator, exact license, model ID, download permission and attribution requirements.
2. Verify species using trustworthy taxonomic evidence and inspect geometry and textures.
3. Check whether the license allows the *specific* intended operations: downloading, rendering, synthetic-data generation, redistribution and training. If uncertain, seek permission or exclude.
4. Preserve evidence and provenance; only a human reviewer can change approval status. Never automatically mark training_approved=YES.
5. Keep synthetic images separate from real-world evaluation images; measure model accuracy on held-out, independently reviewed real photographs.

Last reviewed: 2026-11-19. All rows remain unverified candidates.

## Source inspection (2026-11-19)

- Grab3D original product page inspected directly. Explicit CC0 1.0 claim, download formats and model specifications visible. Downloaded model bytes, LICENSE.txt and manifest.json have **not** been inspected, so this is **not** a completed asset-license/provenance review. Do not mark training approved.
- Sketchfab model and collection pages returned HTTP 403 on direct retrieval. Current individual licenses, downloadable files and provenance could **not** be independently verified. Keep both blocked.
- No 3D meshes were downloaded, rendered or added to training data in this review.
