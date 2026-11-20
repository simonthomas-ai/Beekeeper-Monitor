# Open biodiversity data sources and media-rights controls

Review date: 2026-11-20. This is an engineering register, not a legal opinion or blanket permission to train or redistribute models.

## Acceptance hierarchy

1. **CC0 media**: preferred for the training corpus. Preserve source URL and provenance anyway.
2. **CC BY 4.0 media**: usable only after a human checks the individual file's license URL, creator/rights-holder and attribution text. Persist the required attribution and version with the image. Do not infer the media license from the observation or dataset license.
3. **CC BY-SA**: defer until the consequences for annotations, derived datasets and model-weight distribution are reviewed. Share-alike conditions can affect downstream redistribution.
4. **CC BY-NC, CC BY-ND, unspecified, missing or conflicting rights**: excluded from automated training ingestion. Nonprofit status is not a substitute for satisfying license scope, restrictions and downstream conditions.
5. **Research papers and model repositories**: code, weights, training images and annotations each need their own rights/provenance review. A permissive code license does not clear model artifacts.

All automated discovery output is **UNREVIEWED**. Scripts retrieve metadata only; no images are downloaded, transformed, included in training or redistributed automatically.

## Sources

### iNaturalist

- Observation API: https://api.inaturalist.org/v1/observations
- Photo usage guidance: https://help.inaturalist.org/en/support/solutions/articles/151000169918
- License guidance: https://help.inaturalist.org/en/support/solutions/articles/151000173511

Each photo has its own creator/license information; observation metadata and image license must be kept separate. iNaturalist says the default media license is CC BY-NC, while some uploaders choose CC0 or other Creative Commons options. Therefore the candidate-discovery script requests CC0 and CC BY media metadata only, records the uploader attribution, and does not download the photo. The CC BY version is retained as unverified until an operator checks the specific photo.

### GBIF

- Occurrence API: https://techdocs.gbif.org/en/openapi/v1/occurrence
- Multimedia publishing and licensing: https://techdocs.gbif.org/en/data-publishing/multimedia-publishing
- Download format and multimedia terms: https://techdocs.gbif.org/en/data-use/download-formats
- Species name matching: https://techdocs.gbif.org/en/openapi/v1/species

GBIF occurrence records can carry CC0, CC BY or CC BY-NC, but multimedia media objects have their own license field and can differ from the occurrence license. The new discover_gbif_media_candidates.py queries exact taxon matches and filters each still-image media object's own license to CC0 or exact CC BY 4.0. It requires HTTPS media URLs and attribution identity for CC BY, stores candidate metadata only, and marks every row UNREVIEWED_MEDIA_RIGHTS_AND_IMAGE. The metadata collector does not establish that the pictured insect is correctly identified.

The collector uses small, bounded pages and retry limits on the public GBIF API. It does not request bulk downloads, authenticate, or alter data on GBIF.

### Smithsonian Open Access

- Reuse and CC0 guidance: https://www.si.edu/openaccess/faq
- Developer API: https://www.si.edu/openaccess/devtools
- Terms: https://www.si.edu/termsofuse

Only individual assets marked CC0 are candidates. The Smithsonian warns that some third-party or non-copyright rights can still apply and that the CC0 mark does not cover unrelated assets on the site. Smithsonian specimen scans and collection images may help taxonomy/reference review but are not automatically representative of flying insects in apiary camera footage. No bulk download or training ingestion is enabled.

### Wikimedia Commons

- License overview: https://commons.wikimedia.org/wiki/Commons:Licensing
- Machine-readable file metadata: https://commons.wikimedia.org/wiki/Commons:Machine-readable_data

Commons file pages expose creator and license metadata through the MediaWiki API, but metadata is not uniformly structured. CC0 and CC BY are preferred; CC BY-SA is deferred pending downstream review. A file must be checked individually. No automated Commons image download is enabled.

### Openverse

- Search API documentation: https://docs.openverse.org/api/

Openverse is a discovery index, not the rights holder and not the final license authority. Use it only to discover possible sources. Resolve every result to the original host, inspect the original file page, confirm the actual license, author, attribution and whether adaptations/training are allowed before accepting it. Do not rely only on an aggregated license label.

### Taxonomy and geographic context

GBIF Backbone and EASIN can help resolve accepted scientific names, synonyms and occurrence context. Occurrence metadata can inform regional sampling and distribution analyses; it is not an image training sample and is not ground truth for an individual detection. Preserve taxonomic authority/version and avoid using uncertain records as positive labels.

## Candidate queue and next manual steps

1. Review every source record against the original file page and capture exact license URL, creator, rights holder, publisher and source citation.
2. Confirm the source image actually depicts the candidate taxon and record identification confidence / reviewer.
3. Remove duplicate crops and near-duplicate observations; keep one observation/site/photographer group together for split assignment.
4. Record image SHA-256, downloaded bytes, acquisition date and source license evidence in a provenance manifest only after image use has been approved.
5. Assign separate train/validation/test partitions by observation, photographer, site, camera and capture period. No leakage across splits.
6. Keep a rights-revocation/deletion process. On removal from the approved dataset, identify affected splits, re-train/re-evaluate as required and preserve the deletion audit without retaining the removed image.

## Safety and privacy

- Never publish an apiary's exact location from a public image or observation by default.
- Strip EXIF GPS from any image later approved for training; do not publish a station's home location.
- Keep naturalist/source-user attribution only where needed for license compliance and restrict access to reviewer queues.
- Treat image/species identification as an uncertain scientific annotation, not an instruction to destroy a nest or harm an insect.
- No person, author, institution, dataset host or volunteer has been contacted. This register is internal preparation only.
