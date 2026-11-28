# Varroa source-byte verification – offline only

Workflow: `.github/workflows/varroa-source-integrity.yml` and the synthetic-only guard `.github/workflows/varroa-verified-download.yml`.

The pinned manifest records upstream Git metadata for
`31c2cebd289ebfd558153d73ccc52c05f76067d8` and
`model/weights/best.pt` from `jodivaso/varrodetector`. This is a source reference,
not permission to obtain or use the model.

The byte verifier (`scripts/verify_varroa_source_blob.py`) operates only on a
file already supplied locally by an operator. It checks the recorded Git blob
identity and byte length and computes a local SHA-256. It does not fetch files,
deserialize PyTorch, convert ONNX, or validate model quality or licensing.

The Varroa Actions workflows run synthetic-byte tests only. They do not download
external model bytes, do not publish a provenance artifact, and have read-only
repository permissions. The downloader also has a code-level default-off switch
(`MODEL_WEIGHT_DOWNLOADS_ENABLED = False`); manifest fields alone cannot enable
network access.

The repository's AGPL-3.0 statement is not sufficient to establish rights for
the exact weights, training images, annotations, dependencies or intended use.
A future download would require an independently documented rights review and
a separate reviewed code change. Download permission would still not authorize
deserialization, conversion, inference, training, redistribution or deployment.

An actual ONNX conversion is not part of CI. Any future conversion requires
separately documented rights and a restricted, isolated environment designed
for untrusted pickle inputs. Never run the exporter on a normal CI runner or
production station.
