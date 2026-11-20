#!/usr/bin/env python3
"""Prepare a human review sheet; never auto-approve iNaturalist photos."""
import argparse
import csv
from pathlib import Path

REVIEW_FIELDS = ("photo_id","observation_id","species_candidate","source_url","image_url","claimed_license","license_rechecked","species_verified","image_quality_checked","bounding_box_checked","reviewer","review_date","review_notes","decision")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    with Path(args.input).open(encoding="utf-8-sig",newline="") as source:
        reader=csv.DictReader(source)
        required={"photo_id","observation_id","species_candidate","source_url","image_url","license","review_status"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise SystemExit("Missing required discovery metadata columns")
        rows=list(reader)
    seen=set()
    output=[]
    for row in rows:
        photo=row["photo_id"]
        if not photo.isdecimal() or photo in seen or row["review_status"]!="UNREVIEWED":
            raise SystemExit("Invalid, duplicate or pre-approved input; refusing review manifest")
        seen.add(photo)
        output.append({
            "photo_id":photo,"observation_id":row["observation_id"],
            "species_candidate":row["species_candidate"],
            "source_url":row["source_url"],"image_url":row["image_url"],
            "claimed_license":row["license"],"license_rechecked":"PENDING",
            "species_verified":"PENDING","image_quality_checked":"PENDING",
            "bounding_box_checked":"PENDING","reviewer":"","review_date":"",
            "review_notes":"","decision":"PENDING"
        })
    if not output: raise SystemExit("No candidates to review")
    dest=Path(args.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("w",encoding="utf-8",newline="") as target:
        writer=csv.DictWriter(target,fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        writer.writerows(output)
    print(f"Human review rows: {len(output)}; approvals: 0; all decisions PENDING")
if __name__=="__main__":
    main()
