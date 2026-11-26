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
The discovery workflow creates candidate CSV/JSON/HTML files only in its temporary Actions runner workspace. It removes those files after writing an aggregate status summary; it does not publish or commit the candidate queue or galleries.

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

A dedicated GitHub Actions workflow runs metadata discovery on a schedule and on manual request. Because this repository is public, it no longer uploads candidate metadata or original-image files as Actions artifacts. It writes only aggregate counts/status to the run summary and removes generated CSV, JSON and HTML review files from the runner workspace.

For quality screening, a separate fail-closed selector passes only rows marked
exactly `CC0-1.0`, with the official CC0 licence URL, observer identity,
attribution, observation binding and photo-bound iNaturalist `original.jpg`
URL. CC-BY rows whose licence version is unverified are excluded before any
image request. The image-quality tool independently checks the exact licence
and provenance again before requesting a file. Original derivatives are read
into memory only; no image bytes are written to the repository or artifact.
The output contains pixel dimensions, decode status and a ranking-only
edge-contrast score. PASS is not a species determination, biological visibility
assessment, rights decision or training approval. The workflow can be started
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


## Öffentliche Kandidatengalerien pausiert

Die früher eingecheckten Kandidatengalerien wurden aus dem aktuellen Quellbaum entfernt. Die öffentliche PWA zeigt nur noch eine Statusseite; sie veröffentlicht keine Kandidatenlisten, Originalbilder oder Beobachter-Identitäten. Die generische lokale Review-Oberfläche `review/photos.html` bleibt ein Werkzeug für eine vom Prüfer bereitgestellte lokale CSV und lädt nur die darin angegebenen iNaturalist-Bildquellen. Sie ist nicht mit einem freigegebenen Datensatz verbunden.

Der CC0-Workflow kann Originalbildbytes auf dem kurzlebigen Runner temporär zur technischen Prüfung speichern. Der Arbeitsordner wird anschließend mit einem Always-Cleanup entfernt; erzeugte Kandidatenlisten werden nach der aggregierten Zusammenfassung ebenfalls gelöscht. Diese technische Prüfung bestätigt keine Bildrechte, keine Artbestimmung und keine Trainingsfreigabe. Es werden keine Kandidaten-Artefakte mehr hochgeladen.

Legacy-Artefakte aus früheren Läufen bleiben bis zur manuellen Löschung oder zum Ablauf der Aufbewahrung in der GitHub-Actions-Verwaltung sichtbar. Ihre Löschung ist in [Issue #308](https://github.com/simonthomas-ai/Beekeeper-Monitor/issues/308) nachzuweisen. Die früheren Galerieinhalte bleiben außerdem in der öffentlichen Git-Historie älterer Commits erreichbar; eine History-Umschreibung wurde nicht vorgenommen und benötigt eine gesonderte Eigentümerentscheidung (Issue #310).

