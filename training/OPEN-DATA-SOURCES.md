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


### EASIN — European Alien Species Information Network (European Commission JRC)

- Official API documentation: https://easin.jrc.ec.europa.eu/apixg
- Catalogue API: https://easin.jrc.ec.europa.eu/apixg/catxg
- Geospatial API: https://easin.jrc.ec.europa.eu/apixg/geoxg
- EASIN portal: https://easin.jrc.ec.europa.eu/

EASIN is useful for accepted names, invasive-alien-species catalogue information and European occurrence context. Its catalogue endpoint can be queried by taxon term; its geospatial service exposes occurrence context through the documented API. Use the official API documentation to select currently supported query and pagination parameters.

**Data boundary:** EASIN catalogue/occurrence records are not camera photographs, not per-image licenses, not verified nest locations and not ground truth for an individual camera event. They can support taxonomy, synonym handling and regional sampling plans, but do not grant rights to train on third-party media. Preserve source, taxonomic authority and retrieval date; do not convert occurrence points into precise public nest alerts.

EASIN data originates from partner datasets and may have separate source-specific terms. Before redistributing records or combining them with a derived dataset, check record-level/source-provider terms and applicable API conditions. This project currently documents EASIN as a candidate metadata source; no EASIN bulk download or automatic model-training ingestion is enabled.


## Recently verified candidate datasets and upstream implementations (reviewed 2026-11-20)

These are source leads for a controlled manual review queue. A public dataset listing or a platform-level licence label is not an approval to download, train, redistribute or bundle the content. The per-file provenance gate remains mandatory.

### Insect Detect — useful generic insect hard negatives, not a Vespa velutina model

- Research paper (PLOS ONE, CC BY 4.0): https://doi.org/10.1371/journal.pone.0295474
- Detection data record: https://doi.org/10.5281/zenodo.7725941
- Classification data record: https://doi.org/10.5281/zenodo.8325384
- Creator's object-detection dataset listing: https://universe.roboflow.com/maximilian-sittinger/insect_detect_detection
- Software: https://github.com/maxsitt/insect-detect
- ML project: https://github.com/maxsitt/insect-detect-ml
- Documentation and component licences: https://maxsitt.github.io/insect-detect-docs/

The creator's Roboflow dataset page lists CC BY 4.0 and 1,335 images in six classes: fly, honey bee, hoverfly, other, shadow and wasp. The wasp category is described mainly as Vespula spp.; it is not a Vespa velutina-specific positive class. The imagery is from a standardized artificial flower platform and is useful as a candidate for generic insect/background/hard-negative research, not as proof of performance on Asian hornets around real apiaries.

The separate Zenodo classification dataset (DOI 10.5281/zenodo.8325384) is explicitly CC BY-NC-SA 4.0. It is therefore **excluded from the current permissive production-training route**. Its terms are not interchangeable with the PLOS article's CC BY 4.0 licence. The detection dataset DOI 10.5281/zenodo.7725941 must have its own record-level rights metadata independently verified before use; the listing metadata available in this review did not establish an explicit dataset licence.

The upstream software tree is GPL-3.0 and its ML project is AGPL-3.0. Do not copy or bundle these codebases, model files or derived code in BeeKeeper3000 without a separate component-by-component compatibility decision. The paper itself is CC BY 4.0 and can be cited/adapted with attribution under that licence. Its camera design is an architectural reference only; it uses a flower platform and Luxonis OAK hardware, so it is not a drop-in implementation for a Reolink or USB camera.

### Roboflow Asian hornet datasets — manual source audit only

- Dataset listing, Asian-hornet detection: https://universe.roboflow.com/asianhornet-detection/detection-asian-hornet
- Dataset listing, Vespa velutina: https://universe.roboflow.com/vespa-velutina/vespa-velutina-a9tnw

The public listings advertise CC BY 4.0; one lists approximately 3,300 images and the other is a small 35-image candidate. These are potentially useful targeted positives, but their public listings do not establish that every source image was uploaded by the rights holder, that labels are taxonomically correct, that train/test splits are independent or that versions remain immutable. They remain **UNREVIEWED**. Do not fetch images into the training set until the exact version, source chain, creator/rights-holder, attribution, per-image terms, duplicate overlap and expert labels have been checked and recorded in provenance.jsonl.

### iNaturalist and GBIF — important licence distinction

iNaturalist documents that observations, images and sounds have separate licences and that the default licence for user content is CC BY-NC unless changed by the contributor. Check the licence of each individual photo; an observation being exported to GBIF does not change that photo's own rights.

GBIF explicitly states that multimedia licences can differ from the associated occurrence-record licence. The GBIF discovery script therefore filters the individual still-image media licence field, not just the occurrence licence. Keep CC BY-NC and unknown/unversioned media out of the current permissive baseline.

### Practical data-use decision

1. Prioritize the Insect Detect CC BY 4.0 object-detection listing for a small manually audited hard-negative pilot, subject to original-image rights confirmation and no code/model reuse from its GPL/AGPL software components.
2. Audit the two Asian-hornet Roboflow candidate versions at the individual image and annotation level; use neither until that audit is completed.
3. Continue the existing iNaturalist CC0 and GBIF CC0/CC BY metadata discovery queues, but do not interpret their records as human-verified images.
4. Exclude the CC BY-NC-SA Insect Detect classification dataset from the current permissive baseline.
5. Keep source records, image files, model weights and software dependencies under separate licence inventories. No candidate is approved for model training by this document.
