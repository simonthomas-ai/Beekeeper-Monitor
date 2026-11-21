# iNaturalist image quality screening (21 November 2026)

## Why the URL change was not enough

Changing an iNaturalist URL from `square.jpg` to `original.jpg` only selects the largest derivative hosted by iNaturalist (up to 2048 px on the longest edge). It does not establish that the decoded image is large enough, readable, in focus, or framed so that the insect is visible. The older CC0 workflow generated the public `review/velutina.html` page without inspecting the image bytes, so poor candidates could still appear.

## New publication gate

The CC0 discovery workflow now collects up to 100 metadata candidates per configured taxon and screens each trusted iNaturalist original derivative before building the public gallery.

The screening script is `training/screen_inaturalist_image_quality.py`:

- The URL must resolve to the matching photo ID on a recognized iNaturalist image host and the original derivative.
- The response must decode as JPEG, PNG or WebP and remain within the 16 MiB in-memory download limit.
- Minimum dimensions: long edge at least 960 px, short edge at least 480 px and at least 450,000 total pixels.
- Pixel dimensions, byte size and a simple edge-detail statistic are written to the CSV.
- Failed, corrupt, inaccessible and too-small files are not placed in the public review gallery.
- Passing images are sorted per taxon by edge-detail statistic and pixel count.

Image bytes are processed in memory only. The workflow does not save or commit the downloaded images. The persisted CSV contains metadata and measurements only.

## Interpreting the screening result

`PASS` means only that the file decoded and met the pixel-size thresholds. The edge-detail statistic is a relative sorting aid, not a calibrated blur detector. It cannot determine whether the insect itself is sharp, large in frame, unobstructed, correctly identified, or biologically suitable. A human reviewer must still inspect the actual picture and the original observation.

The gallery offers a direct link to the original image file, uses a larger viewing area, and reports the measured dimensions. If no candidate for a taxon passes, the gallery displays an explicit empty-state message instead of silently showing low-resolution images.

No candidate is automatically approved for training. License version, attribution, taxonomic identity, insect visibility, focus, image quality and annotations remain separate human-review steps. No bounding boxes, training labels or model weights are created by this workflow.


## Byte-preserving original-file delivery

For the public `review/velutina.html` page, qualified CC0 originals are now downloaded as the exact response body from the iNaturalist `original` derivative. The download step requires an exact photo-ID match, a successful per-photo CC0 API recheck, research-grade taxon metadata and a passing file decode/dimension screen. The byte stream is hashed with SHA-256, stored without Pillow re-saving it, and deployed as a separate Pages build artifact. A deployment-time check recomputes every hash before publication. No resize, crop, rotation, EXIF rewrite, recompression, thumbnail generation or image-format conversion is performed. The gallery points to these same-origin local files and provides a direct link to each one. The browser may scale the display to fit the available viewport, but the downloaded file itself remains unchanged and opens directly at its native dimensions.
