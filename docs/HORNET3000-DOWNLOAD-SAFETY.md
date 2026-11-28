# Hornet3000 candidate download safety

**Status: blocked; no model or dataset rights approval.**

The candidate manifest pins an upstream ONNX file from
[vespCV/hornet3000](https://github.com/vespCV/hornet3000) for byte identity only.
The repository's GPL-3.0 source declaration does not establish the rights to
the exact weights, their training images, annotations, or intended downstream use.
The current audit did not establish a per-image provenance and attribution chain.

The verifier `scripts/verify_hornet3000_onnx.py` therefore has a code-level
`MODEL_DOWNLOADS_ENABLED = False` gate. Passing `--download` fails before
`urlopen` is called. The manual GitHub Actions workflow runs only local policy
tests and a Python syntax check. It does not fetch model bytes or iNaturalist
photos, install ONNX runtimes, run inference, or upload artifacts.

The CC0 photo probe scripts are research utilities, not a training dataset or
independent validation set. Their observation labels are not expert-confirmed
ground truth. They remain unreachable through the guarded workflow while model
downloads are disabled.

Re-enabling downloads requires a separate reviewed code change after:
1. independent evidence for the exact weight license and intended-use rights;
2. per-image training-data provenance, license, attribution and annotation review;
3. a security plan for parsing untrusted model files in an isolated environment;
4. a separate approval for any inference, training, redistribution or deployment.

A matching Git blob or SHA-256 proves byte identity only. It does not prove
ownership, license permission, model accuracy, or field readiness.

## Zenodo Varroa dataset files

The metadata inventory in `scripts/zenodo_inventory.py` may list public record
metadata. Actual file downloads are separately blocked by
`DOWNLOADS_ENABLED = False`; `--download` exits before even fetching record
metadata. A Zenodo checksum proves byte integrity, not the rights to images,
labels, annotations or downstream model use. Re-enabling requires a per-file
license/provenance/attribution review and a separate reviewed code change.
