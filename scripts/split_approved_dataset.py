#!/usr/bin/env python3
"""Deterministic, group-aware dataset split from already curator-approved images."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import random
import sys

SPLITS = ("train", "val", "test")
CLASS_MAP = {"velutina": "vespa_velutina", "crabro": "vespa_crabro", "apis": "apis_mellifera", "bombus": "bombus_spp", "vespula": "other_vespidae"}
CANONICAL = {"vespa_velutina", "vespa_crabro", "other_vespidae", "apis_mellifera", "bombus_spp", "syrphidae", "other_insect"}

def split_manifest(data, seed=42):
    items = data.get("items", [])
    if not items:
        raise ValueError("No approved images supplied")
    groups = defaultdict(list)
    hashes = set()
    group_classes = defaultdict(set)
    for item in items:
        if item.get("human_approved_for_training") is not True or item.get("species_verified") is not True:
            raise ValueError("Unapproved image in input")
        digest = item.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError("Missing SHA256")
        if digest in hashes:
            raise ValueError("Duplicate image SHA256")
        hashes.add(digest)
        group = str(item.get("observation_group", "")).strip()
        label = str(item.get("suggested_class", "")).strip()
        if not group or not label:
            raise ValueError("Every image needs an observation_group and class")
        label = CLASS_MAP.get(label, label)
        if label not in CANONICAL:
            raise ValueError(f"Unknown model class: {label}")
        group_classes[group].add(label)
        groups[(label, group)].append({**item, "suggested_class": label})
    if any(len(classes) > 1 for classes in group_classes.values()):
        raise ValueError("Observation group spans multiple classes; reconcile groups before splitting")
    by_class = defaultdict(list)
    for (label, group), batch in groups.items():
        by_class[label].append((group, batch))
    result = {name: [] for name in SPLITS}
    for label in sorted(by_class):
        batches = sorted(by_class[label], key=lambda pair: pair[0])
        random.Random(f"{seed}:{label}").shuffle(batches)
        n = len(batches)
        if n < 3:
            raise ValueError(f"{label}: at least 3 independent observation groups required")
        n_test = max(1, round(n * 0.15))
        n_val = max(1, round(n * 0.15))
        if n_test + n_val >= n:
            raise ValueError(f"{label}: too few groups for independent split")
        for i, (_, batch) in enumerate(batches):
            part = "test" if i < n_test else "val" if i < n_test + n_val else "train"
            result[part].extend(batch)
    return {"seed": seed, "splits": result, "counts": {k: dict(Counter(x["suggested_class"] for x in v)) for k, v in result.items()},
            "method": "class-stratified observation_group split; no group shared across splits"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("approved_manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    data = json.loads(args.approved_manifest.read_text(encoding="utf-8"))
    result = split_manifest(data, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Split counts:", result["counts"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
