# Real data acquisition plan

The online source catalog is at [sources/catalog.json](../sources/catalog.json).

## No fabricated datasets
Training is blocked until each required class has authentic labeled data. Class definitions are not interchangeable:
- Varroa *on bee* labels may identify an infested bee rather than the mite.
- Drone bee images do not count as drone-brood cell annotations.
- Pollen-bearing bees do not provide pollen species labels.
- Swarm snapshots do not establish imminent swarming prediction.

## Candidate datasets
- Hornet: ISR Roboflow v1 and Vespa velutina Roboflow v1 (source pages list CC BY 4.0).
- Varroa: Zenodo 23276947 (v2), 4085044, and 13771384.
- Queen: Gratheon pipeline (weights not included in Git).
- Brood, pollen, swarm: still require correctly scoped real labeled datasets and/or task-specific models.

## Inventory public Zenodo records
```sh
python scripts/zenodo_inventory.py varroa-v2
python scripts/zenodo_inventory.py varroa-original
python scripts/zenodo_inventory.py varroa-ev2
```
Only after reviewing rights and file sizes, download a named file:
```sh
python scripts/zenodo_inventory.py varroa-v2 --download README.md
```

The script checks published MD5 where present. Large downloads are **not** scheduled in free GitHub Actions; downloading all training images and model weights could consume gigabytes and exhaust quotas. Roboflow exports may require user credentials, and no secrets should be committed.

## Training acceptance
Document authorship, license, checksums, source identifiers, class mapping, duplicate screening, train/validation/test isolation, independent evaluation and iPhone performance before any model is enabled in the PWA.
