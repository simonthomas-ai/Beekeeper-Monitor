# Hornet-only dataset gate

Use real, licensed, manually checked Vespa velutina images with YOLO annotations.

Expected layout:

```text
datasets/hornet/
  images/train/  images/val/  images/test/
  labels/train/  labels/val/  labels/test/
```

Each image requires a matching text label with class **0** for Vespa velutina.
Run `python training/validate_hornet.py --dataset datasets/hornet`.

The gate rejects missing data, invalid boxes, and exact duplicate images across splits.
It does **not** verify species identity, near-duplicates, license permissions,
or independent model accuracy. Those still require review before deployment.
No data is downloaded automatically, and no model is trained by this gate.
