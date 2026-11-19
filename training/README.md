# Training with genuine data

This pipeline trains **one six-class object detector**, not six independently validated models. It does not pretend that an object detector can solve every task: swarm detection and brood classification may require separate architectures and temporal/context data.

## Requirements

- Real, legally usable images from each class, manually verified bounding-box labels in YOLO format.
- A documented dataset provenance and license for every source.
- Separate train/validation/test splits, preferably separated by apiary, date and camera to prevent leakage.
- Enough examples per class to assess performance; the script only checks minimal nonempty coverage, not scientific adequacy.
- Compute capacity. Free GitHub Actions runners are **not** a reliable place for GPU training.

## Usage

```sh
python -m pip install -r training/requirements.txt
python training/train.py --validate-only
python training/train.py --epochs 60 --device 0
```

Without actual labeled images the script fails deliberately. No fake images, placeholder weights, claimed 99% accuracy or fabricated test reports are generated.

For reproducible inference, model files must later be reviewed for licensing, converted to a mobile/browser-supported format, hashed, and independently evaluated. Never publish unreviewed dataset images.
