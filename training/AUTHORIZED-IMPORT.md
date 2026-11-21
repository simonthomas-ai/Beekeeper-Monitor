# Authorized image import (sanitized candidate staging only)

Run:

~~~sh
python training/import_authorized_images.py --input individually-reviewed-images.csv --limit 50
~~~

The CSV columns are:
\`source_id,source_url,image_url,creator,license,license_url,attribution\`.

Only individually reviewed and explicitly downloadable CC0-1.0 or CC-BY-4.0 source records are accepted. Verify the actual rights holder and the individual media licence before use. The importer cannot establish that an uploader owned the image or had authority to license it.

The importer:
- accepts public HTTPS URLs only, rejects embedded credentials, private/reserved DNS resolutions and redirects;
- reads at most 10 MiB per image, checks the declared MIME type against decoded contents and rejects corrupt or oversized images;
- applies EXIF orientation, re-encodes pixels, strips EXIF and other copied metadata, and verifies the staged file has no EXIF block;
- records separate SHA-256 hashes for the downloaded original and the sanitized output;
- upgrades recognized iNaturalist square, small, medium and large image URLs to the original derivative before download; records both the requested URL and the actual downloaded URL;
- records the sanitized raster width and height in pixels in the per-image manifest so image dimensions can be audited;
- writes to local \`unreviewed/\` and \`licenses.csv\`; attempts owner-only POSIX permissions where supported;
- refuses to overwrite an existing manifest or candidate file and removes newly-created candidates if a later step fails before manifest publication.

Pillow is required and is listed in \`training/requirements.txt\`.

**Output remains UNREVIEWED.** The importer creates no species labels, bounding boxes, rights approval, split assignment or training permission. Human review must confirm the actual image, species, creator, per-file rights, attribution and quality. Then use the separate provenance and annotation gate.

**No scraping or automatic image discovery:** GBIF/iNaturalist/Smithsonian discovery tools create metadata queues only. Candidate URLs are never automatically fed into this importer.

**Network-isolation warning:** DNS checks and redirect blocking are defense in depth, not a complete SSRF boundary. Never run the importer with untrusted CSV input. Use a restricted outbound-only runner with no access to internal networks or credentials.

Do not commit private images, exact apiary coordinates, RTSP credentials or reviewer personal details to this public repository.
