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

GBIF occurrence records can carry CC0, CC BY or CC BY-NC, but multimedia media objects have their own license field and can differ from the occurrence license. The discover_gbif_media_candidates.py script resolves an exact species key and additionally requires each returned occurrence's interpreted `speciesKey` and `species` name to match that exact requested species. This second per-record guard is necessary because taxon-key occurrence searches may include descendants. It filters each still-image media object's own license to CC0 or exact CC BY 4.0, requires HTTPS media URLs and attribution identity for CC BY, stores candidate metadata only, and marks every row UNREVIEWED_MEDIA_RIGHTS_AND_IMAGE. The metadata collector does not establish that the pictured insect is correctly identified. Existing candidate exports created before this guard must be regenerated and re-audited; they remain unapproved until manual visual and rights review.

The collector uses the documented canonical camelCase occurrence-search parameters `taxonKey` and `mediaType`, small bounded pages and retry limits on the public GBIF API. GBIF documents that occurrence-search parameter aliases such as `taxon_key` may also be tolerated; parameter spelling alone is therefore not used to explain an empty result. The status report includes per-species counts for returned occurrences, exact species keys/names, media objects/types, occurrence/media licence values and accepted candidates. A zero-result response is recorded as `empty`, not as a successful candidate discovery. It does not request bulk downloads, authenticate, or alter data on GBIF.

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


## Additional open research sources — review 2026-11-20

This section records newly identified sources. They remain research candidates unless the relevant record-level licence, rights holder, exact file version, attribution and biological labels are independently verified. No source in this section has been downloaded into the training corpus.

### InsectDCT — large multi-camera trap dataset and separate test split

- Dataset DOI: https://doi.org/10.5281/zenodo.21154490
- Research preprint: https://doi.org/10.64898/2026.07.07.736939
- Code: https://github.com/kimbjerge/insectDCT
- Published 3 July 2026; dataset version v1.

The Zenodo description lists RGB and motion-enhanced detector training archives (51 GB and 71 GB), a separate 35 GB detector test archive, a 4.5 GB hierarchical classification training archive, a 202 MB classification test archive and a 1.3 GB tracking test archive. The detection data spans multiple camera systems, plants and project sites. The classification description lists 80 taxonomic groups, while the separate test sets contain recordings from camera/site groups not all used for training. This could be valuable for testing generalisation across vegetation, illumination and different camera backgrounds.

**Rights hold:** the indexed Zenodo record exposed a License field but did not expose a usable licence value in the reviewed metadata. Do not infer CC BY from Zenodo's default settings or from the preprint's access status. The upstream insectDCT repository is GPL-3.0 and its README uses YOLO11; both code and its dependencies require separate review. No archive, weights or source code are approved for BeeKeeper3000 use until the precise dataset licence and all third-party image conditions are verified. The data are large and may contain no validated Vespa velutina class; inspect its taxonomy manifest before planning any target-class use. It is an ecological-camera benchmark candidate, not a ready-made Asian-hornet detector.

### VespApp / GBIF — expert-reviewed occurrence context, non-commercial licence

- GBIF dataset DOI: https://doi.org/10.15470/jl2i4v
- IPT resource: https://ipt.gbif.es/resource?r=uib-vespapp&request_locale=en
- GBIF dataset UUID: cd0ed6b1-e80b-475f-bda7-df2d534d7773

The dataset was published 6 July 2026 by Universitat de les Illes Balears. Its description states that VespApp collected suspicious individual and nest reports in the Balearic Islands from 2016 to 2024 and that observations were validated or discarded by taxonomic experts. The GBIF resource offers a 571-record Darwin Core Archive snapshot and declares CC BY-NC 4.0.

Potential use: regional occurrence trends and taxonomically reviewed non-target observations, subject to record-level review and a documented non-commercial-use decision. It is occurrence metadata, not camera imagery or a bounding-box dataset. The CC BY-NC licence is not included in the permissive CC0/CC BY training baseline; nonprofit status alone does not clear its conditions. Do not use its locations as current nest coordinates or publish sensitive locations without an independent privacy review.

### Ecdysis Foundation / BugBox — large entomologist-reviewed specimen image collection, CC BY-NC

- Collection and download description: https://bugbox.ecdysis.bio/samples/collection-download/1
- Training/inference code is linked from that page.

The publisher reports a reviewed collection of about 121,917 images representing 117,200 specimens identified by entomologists to 40 orders and 340 arthropod families; the all-specimen file contains more than 675,000 images, including records not reviewed for identification. The page declares the data and model available under CC BY-NC.

Potential use: taxonomy reference and research into visually similar arthropod groups. Prefer the reviewed-only file; never use the unreviewed set as authoritative labels. The images are specimen/collection imagery, not necessarily natural flying camera-trap images, and the licence is not part of the permissive training baseline. The publisher's model is a separate artifact and is not accepted for deployment. No images or weights have been downloaded.

### Urban insect detection dataset — useful methodology, NC restricted

- Dataset DOI: https://doi.org/10.6084/m9.figshare.28280792
- Data article: https://doi.org/10.1016/j.dib.2025.111673
- Article text and dataset description: https://pmc.ncbi.nlm.nih.gov/articles/PMC12159940/

The 2025 data article describes more than 25,000 annotations on scanned UV sticky-trap cards, with insect boxes labelled at order level by at least two entomologists. The article is CC BY-NC; the data record and any third-party image conditions must be checked separately. It is not equivalent to live insect footage and does not provide species-level labels for reliable Vespa velutina discrimination. Keep it outside the current permissive training route unless exact dataset rights and the intended use are cleared.

### Projekt VELUTINA media library — possible direct source for Asian-hornet reference media

- Media library: https://www.velutina.de/mediathek/
- The publisher states that its photos and videos are made available under Creative Commons licences and shows examples including nests, eggs, larvae, queens and flight/foraging behaviour.
- The page links separate Lizenz Vereinbarungen and asks users to follow the respective licence and attribution for each asset.

This is a potentially relevant source for Vespa velutina morphology and life-cycle reference images. It is not yet a cleared training dataset: the page's general statement does not identify one uniform licence for every file, and media made for public information may differ in camera angle, staging, nesting context and image distribution from a fixed camera station. Check the linked agreement and the per-asset attribution/licence before any reuse. No photos or videos have been downloaded, copied or annotated.

### EASIN — EU occurrence/taxonomy context, not an image dataset

- Official portal: https://easin.jrc.ec.europa.eu/easin/
- API documentation: https://easin.jrc.ec.europa.eu/apixg

EASIN is managed by the European Commission's Joint Research Centre and supports EU and Member State work under the Invasive Alien Species Regulation. Its catalogue, maps, open web services and citizen-science features can help with accepted names, aliases and European distribution context. It is not a per-image licence grant, a station camera feed or an independently verified nest-location source. Check source-provider conditions before redistributing records; keep it separate from the image-training corpus.

### Data-source separation rule

- Visual training/evaluation: only media with independently verified per-file rights, traceable source, expert-reviewed labels and group-safe split assignments.
- Taxonomy/distribution context: GBIF/EASIN and licensed observation archives, kept distinct from camera predictions.
- Reference material: specimen scans and educational media, not automatically representative of deployed camera footage.
- NC or unclear rights: quarantine pending a specific rights/use decision; never relabel as free because nonprofit.
- Sensitive geodata: restrict exact apiary/nest/station coordinates; do not publish imported observation coordinates as active targets without validation.


### VelutinaFinder — German occurrence aggregation, not an image-training licence

- Data sources and per-source licence notes: https://velutinafinder.aws-xdib.de/datenquellen.html
- Legal / operator information: https://velutinafinder.aws-xdib.de/impressum.html
- Privacy statement: https://velutinafinder.aws-xdib.de/datenschutz.html
- Review date: 20 November 2026; the provider's source page states a data snapshot dated 19 October 2026.

The provider reports 67,709 sightings across four categories: 52 own reports, 26,150 GBIF occurrences (described as mostly CC0/CC BY), 6,684 iNaturalist occurrences (mostly CC BY-NC), and 34,823 Observation.org records (CC BY-NC 4.0). The portal is free to access. Its own legal page says the analyses are freely usable with attribution, while the portal-created content remains protected by copyright. The provider also says the map's imported external records are displayed with their source/original record and source licence.

Potential use for BeeKeeper: compare broad regional occurrence trends and source coverage; use it as a discovery index to find underlying GBIF occurrence records that can be checked and cited individually. It is not an authorised bulk export of the portal database, an image dataset, or permission to reuse the portal's own user-submitted reports, photos, user tracks or reviewer decisions. Do not scrape the portal or treat its aggregation as a separate licence grant.

**Privacy boundary:** the provider's privacy notice describes optional GPS reports, uploaded photos, route recordings and reviewer accounts. These are personal or sensitive operational records under the provider's own system. Do not copy them into BeeKeeper. For any eventual occurrence-only use, fetch and retain only the underlying public records allowed by their individual source terms, preserve attribution and original record links, and avoid redistributing precise private apiary/nest coordinates.

This source is also an example of a useful community-facing detection workflow, but its model, verification policy, storage and infrastructure are separate works and are not imported or adopted here.


## Additional reference services — review 2026-11-20

### EASIN (European Commission Joint Research Centre)

- Web Services: https://easin.jrc.ec.europa.eu/apixg
- Catalogue service: https://easin.jrc.ec.europa.eu/apixg/catxg
- Catalogue species search and paged results are documented by EASIN; the geospatial service returns occurrence context separately.
- EASIN makes EU invasive-alien-species taxonomy and broad distribution context discoverable to the public. Source records may originate from partner datasets and do not carry one blanket licence for every underlying record.

**Permitted project role:** reference accepted scientific names, synonyms, Union-concern catalogue metadata and broad European occurrence context after preserving the source/provider and retrieval date. A record is not a camera image, an independently verified current nest, or a licence to train on a photograph. Do not turn coarse distribution records into nest alerts or publish private apiary coordinates.

Official service documentation: https://easin.jrc.ec.europa.eu/apixg

### Open-Meteo — optional weather context only

- API / project: https://open-meteo.com/
- Terms: https://open-meteo.com/en/terms
- Source code: https://github.com/open-meteo/open-meteo
- The hosted API is free for non-commercial use within its published fair-use limits. Its weather data is CC BY 4.0 and requires attribution. The hosted API's source code is AGPL-3.0; data rights and software rights must remain separate.
- The provider states a limit below 10,000 API calls/day, 5,000/hour and 600/minute for the non-commercial free API; verify current terms before a deployment or scale-up.

**Potential project role:** optional, explanatory covariates such as temperature, wind, precipitation and humidity for reviewing station performance or correlating activity. Weather cannot confirm Vespa velutina identity, diagnose a nest, or override human review.

**Privacy and deployment boundary:** no automatic API calls are enabled by this catalogue entry. Any future integration must be an explicit local opt-in, cache results, respect rate limits and attribution, and avoid sending exact private apiary coordinates. Prefer a user-selected coarse location or a coarse grid computed locally. Do not call the hosted free API for a commercial deployment or a subscription/ad-supported app without checking the current terms and selecting an appropriate plan.

### Separation rule

- Taxonomy and occurrences: EASIN / GBIF, retained as source-linked reference metadata.
- Training imagery: per-file rights and human-reviewed biology only; each image must pass the provenance gate.
- Weather: optional contextual metadata, kept separate from detections, labels and model scores.
- None of these sources authorises an automated nest intervention or an unverified public alert.
