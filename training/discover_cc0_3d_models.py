#!/usr/bin/env python3
"""Inventory candidate CC0 insect 3D scans; never approve species or training rights automatically."""
import argparse
import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://datasets-server.huggingface.co/rows"
DATASET = "hugging-3d/smithsonian-open-access-3d"
TERMS = ("vespa", "hornet", "wasp", "apis", "honeybee", "bumblebee", "bombus", "bee", "insect", "hymenoptera")

def candidates(rows):
    found = []
    for item in rows:
        r = item.get("row", {})
        if r.get("license") != "CC0-1.0" or r.get("media_usage_access") != "CC0":
            continue
        fields = ("title", "package_title", "scientific_name", "tax_order", "object_type")
        description = " ".join(str(r.get(k, "")) for k in fields).lower()
        if not any(term in description for term in TERMS):
            continue
        found.append({
            "package_id": str(r.get("package_id", "")),
            "title": str(r.get("title", "")),
            "scientific_name": json.dumps(r.get("scientific_name", []), ensure_ascii=False),
            "record_link": str(r.get("record_link", "")),
            "mesh_url": str(r.get("mesh_url", "")),
            "preview_url": str(r.get("preview_url", "")),
            "voyager_url": str(r.get("voyager_url", "")),
            "vertices": str(r.get("vertices", "")),
            "faces": str(r.get("faces", "")),
            "license": "CC0-1.0",
            "media_usage_access": "CC0",
            "species_verified": "NO",
            "geometry_verified": "NO",
            "training_approved": "NO",
            "review_notes": "",
        })
    return found

def fetch_all():
    offset, rows = 0, []
    while True:
        query = urllib.parse.urlencode({"dataset": DATASET, "config": "metadata", "split": "train", "offset": offset, "length": 100})
        req = urllib.request.Request(API + "?" + query, headers={"User-Agent": "VespaGuard-CC0-3D-inventory/1.0"})
        with urllib.request.urlopen(req, timeout=45) as response:
            payload = json.load(response)
        chunk = payload["rows"]
        rows.extend(chunk)
        offset += len(chunk)
        if not chunk or offset >= payload["num_rows_total"]:
            break
    return rows

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="training/cc0-3d-insect-candidates.csv")
    args = p.parse_args()
    records = candidates(fetch_all())
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["package_id", "title", "scientific_name", "record_link", "mesh_url", "preview_url", "voyager_url", "vertices", "faces", "license", "media_usage_access", "species_verified", "geometry_verified", "training_approved", "review_notes"])
        writer.writeheader()
        writer.writerows(records)
    print(f"Found {len(records)} CC0 metadata-matched 3D candidates; zero training approvals. No meshes downloaded or rendered.")
    for item in records:
        print("3D candidate:", json.dumps({key: item[key] for key in ("package_id", "title", "scientific_name", "record_link", "voyager_url", "preview_url", "vertices", "faces")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
