# Authorized image import (candidate staging only)

Use `python training/import_authorized_images.py --input approved_images.csv --limit 50`.

The input CSV must have columns:
`source_id,source_url,image_url,creator,license,license_url,attribution`

Include only **individually reviewed and explicitly downloadable** photos. The
script only accepts CC0-1.0 or CC-BY-4.0 metadata, HTTPS URLs and supported image
types; it limits file size and saves SHA256-named images under
`datasets/hornet/unreviewed/` with `licenses.csv`.

**No auto-discovery or scraping:** Roboflow dataset exports may require accounts,
API keys and separate rights checks. Never put API keys in public CSV or Git.

**Do not run this importer on arbitrary/untrusted CSV inputs.** Host resolution
checks and redirect blocking are defense in depth, not a complete SSRF security
boundary. Use a restricted runner with no internal network access.

Downloaded candidates are NOT YOLO-annotated training data. Before any training,
verify image ownership, photo license, author attribution, species identification,
annotation quality, near-duplicates, independent test isolation and negative
classes. Do not commit images until their redistribution rights are verified.
