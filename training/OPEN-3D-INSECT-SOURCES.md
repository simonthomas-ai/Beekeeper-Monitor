# Open 3D insect sources — review-only research (2026-11-20)

This is a **source registry, not a model inventory or training approval**. No files have been downloaded, verified, or added to training. All candidate licenses and species must be checked per individual model and retained with provenance.

| Source | Evidence / entry point | Candidate scope | License policy | Status |
|---|---|---|---|---|
| Smithsonian Open Access 3D (via hugging-3d metadata) | https://huggingface.co/datasets/hugging-3d/smithsonian-open-access-3d | Museum 3D objects; current filtered 3,451-row scan found 0 target-insect candidates | Per-object `license=CC0-1.0` and `media_usage_access=CC0`; verify record and geometry | SCANNED_NO_MATCH |
| Digital Archive of Natural History (DiNArDa / DISC3D) | https://sketchfab.com/disc3d/collections/digital-archive-of-natural-history-cc0-bd284e3d31d447b3964c218f46491deb | Natural-history models, including `Musca domestica`, `Chorthippus biguttulus` and `Tytthaspis sedecimpunctata` (not Vespa velutina) | Collection described as CC0; check **individual model** license and download rights | SOURCE_IDENTIFIED_UNVERIFIED |
| Europeana 3D | https://www.europeana.eu/en/stories/explore-and-reuse-1000s-of-openly-licensed-3d-items-on-europeana-eu | European cultural heritage, mixed 3D objects; species relevance unconfirmed | Mixed rights statements: allow only independently verified compatible rights; reject NC/ND for unrestricted training | SOURCE_IDENTIFIED_UNVERIFIED |
| Smithsonian institution Sketchfab account | https://sketchfab.com/Smithsonian | Official institutional uploads; possible duplication of Smithsonian scans | Per-model CC0 and provenance must be verified; deduplicate by source object | SOURCE_IDENTIFIED_UNVERIFIED |

## Review gate for any future automated discovery

1. Search **metadata only** using official permitted APIs or clearly authorized exports. Do not scrape pages or download geometry by default.
2. Store source URL, creator/rightsholder, model ID, scientific taxon, original license URL and retrieval date. Avoid private locations and personal data.
3. Treat search matches as `training_approved=NO`, `species_verified=NO`, `geometry_verified=NO`. No 3D models are approved at this stage.
4. Verify taxonomic identity, model provenance, per-model rights, attribution obligations, geometry integrity and duplicate status before import. Keep CC0 and CC BY 4.0 distinct; evaluate share-alike obligations separately and do not silently assume compatibility.
5. Never convert a model of a different insect into a labeled Vespa velutina training example. 3D renderings are not a substitute for independently validated real camera images.

The original Smithsonian dataset's CC0 designation does not guarantee third-party rights clearance. These sources are **leads**, not verified training assets.
