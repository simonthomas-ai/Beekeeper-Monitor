# GitHub-only source download, not conversion

Workflow: `.github/workflows/varroa-verified-download.yml` (manual `workflow_dispatch`).

This job downloads only the immutable upstream Git commit
`31c2cebd289ebfd558153d73ccc52c05f76067d8` model file
`model/weights/best.pt` from `jodivaso/varrodetector`.
It verifies its exact Git blob identity and byte length using the pinned manifest,
computes SHA-256 and uploads only the JSON provenance. The binary stays in the
ephemeral GitHub runner and is never committed, redistributed or uploaded as an artifact.

The workflow **does not** import PyTorch, deserialize the untrusted .pt,
export ONNX, claim model licensing, or approve detection accuracy.
Repository AGPL-3.0 is not sufficient to establish rights for all weights and datasets.

An actual ONNX conversion requires separately documented rights and an
isolated, restricted environment designed for untrusted pickle loading.
The existing exporter must not run on a normal CI runner with network access.
