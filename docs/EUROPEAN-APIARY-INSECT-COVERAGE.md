# European apiary insect coverage — taxonomy and safety requirements

Status: **scope specification only; no trained model or species-level accuracy is claimed**.

## Scope
Cover all insects *potentially encountered* around European hives as an open-set identification problem. An exhaustive fixed list of all European wild bees and insects is not feasible or stable; maintain a versioned taxonomic backbone and an explicit unknown outcome. Species names and synonyms must be checked against authoritative European taxonomic sources before publication.

## Hierarchical identification targets
- **Hymenoptera:** Apis mellifera (workers, drones, queens); European wild bees (Andrena, Lasioglossum, Halictus, Osmia, Megachile, Colletes, Anthophora, Xylocopa, Nomada, Hylaeus, etc.); Bombus spp.; Vespa velutina, Vespa crabro, other Vespa spp.; Vespula, Dolichovespula, Polistes; ants and parasitoid wasps.
- **Diptera:** hoverflies (Syrphidae), bee flies (Bombyliidae), robber flies (Asilidae), other fly mimics and scavengers.
- **Lepidoptera:** butterflies, moths, including Galleria mellonella and Achroia grisella.
- **Coleoptera:** native beetles; Aethina tumida (small hive beetle, where relevant), other hive-associated beetles.
- **Other insects:** earwigs, true bugs, lacewings, dragonflies, grasshoppers, and incidental visitors.
- **Non-insect lookalikes/pests:** spiders, mites (including Varroa destructor), and other arthropods must be kept taxonomically distinct from insects.

## Decision policy
1. Prioritize sensitive detection of **Vespa velutina**, with hard negatives from Vespa crabro, other wasps, wild bees, hoverflies and moths.
2. Do not label a harmless insect as a threat solely because the species is uncertain. Display **unknown / uncertain** and request additional evidence.
3. Do not treat native Vespa crabro, wild bees, or protected species as targets for removal.
4. Separate pest monitoring from identification; require evidence before a warning and never recommend indiscriminate trapping.
5. Use genus/family/order output when species confidence is insufficient. The threshold must be calibrated on held-out field data; do not invent confidence or a 99% accuracy claim.
6. Store raw observations only with appropriate privacy, location and retention controls.

## Data and validation
- Use GBIF/European taxonomic checklists and authoritative local bee lists to build a versioned name/synonym inventory; a name in a catalog is **not** a training sample.
- Use source photos only after checking photo-specific license, attribution, permitted redistribution and identification; nonprofit use does not override license conditions.
- Split train/validation/test by observation, photographer, site and capture period as feasible to prevent leakage.
- Collect representative real field imagery from European apiaries, seasons, devices and lighting, with bounding-box annotations for object detection.
- Measure per-group precision, recall, confusion (especially velutina vs crabro), false alarms per hive-day, open-set rejection, and mobile latency.
- Treat audio as a separate experimental modality until species-specific evidence and device testing establish validity.
- Maintain a model card and dataset provenance; no species-level deployment without independent evaluation.

## Implementation sequence
1. Version taxonomic reference and licensed source manifests.
2. Acquire and manually verify annotated data for the most critical groups and confusing lookalikes.
3. Train a broad insect/non-insect detector and a specialist hornet classifier/detector; keep the existing six-class tasks distinct.
4. Calibrate unknown handling and evaluate with independent field data.
5. Export browser-compatible models, test offline iPhone/Android, and only then enable notifications.
