#!/usr/bin/env python3
"""Validate iPhone CSV review exports and produce a NON-APPROVED expert queue."""
import argparse
import csv
import json
from pathlib import Path
from urllib.parse import urlsplit

FIELDS = ("photo_id","observation_id","species_candidate","source_url","image_url","claimed_license","license_rechecked","species_verified","image_quality_checked","bounding_box_checked","reviewer","review_date","review_notes","decision")
SPECIES = {"Vespa velutina","Vespa crabro","Apis mellifera","Bombus terrestris","Vespula vulgaris"}
DECISIONS = {"PENDING","REJECTED","NEEDS_EXPERT","REVIEWED"}
HOSTS = {"static.inaturalist.org","inaturalist-open-data.s3.amazonaws.com","inaturalist-open-data.s3.us-west-2.amazonaws.com","www.inaturalist.org","inaturalist.org"}

def safe_url(raw, source=False):
    try:
        u = urlsplit(raw)
        if u.scheme != "https" or u.username or u.password or u.port not in (None,443) or u.fragment:
            return False
        if source:
            return u.hostname == "www.inaturalist.org" and len(u.path.split("/")) == 3 and u.path.split("/")[1] == "observations" and u.path.split("/")[2].isdecimal()
        return u.hostname in HOSTS and bool(u.path.strip("/"))
    except ValueError:
        return False

def stage_csv(path):
    source = Path(path)
    if source.stat().st_size > 2_000_000:
        raise ValueError("CSV too large")
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames) or set(reader.fieldnames) != set(FIELDS):
            raise ValueError("Unexpected or duplicate CSV headers")
        records = []
        seen = set()
        for n, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Line {n}: malformed CSV")
            pid = row["photo_id"]
            if not pid.isascii() or not pid.isdecimal() or pid in seen:
                raise ValueError(f"Line {n}: invalid/duplicate photo ID")
            seen.add(pid)
            if row["species_candidate"] not in SPECIES or not safe_url(row["source_url"], True) or not safe_url(row["image_url"]):
                raise ValueError(f"Line {n}: invalid species or URL")
            if row["decision"] not in DECISIONS:
                raise ValueError(f"Line {n}: unknown decision")
            if any(row[key] not in {"PENDING","YES","NO"} for key in ("license_rechecked","species_verified","image_quality_checked","bounding_box_checked")):
                raise ValueError(f"Line {n}: invalid review field")
            records.append({
                "photo_id":pid,"observation_id":row["observation_id"],"species_candidate":row["species_candidate"],
                "source_url":row["source_url"],"image_url":row["image_url"],"claimed_license":row["claimed_license"],
                "mobile_review":{key:row[key] for key in ("license_rechecked","species_verified","image_quality_checked","bounding_box_checked","reviewer","review_date","review_notes","decision")},
                "training_eligible":False,
                "expert_checks_required":["verify_species","verify_media_license_and_rightsholder","verify_image_pixels_and_quality","verify_actual_bounding_boxes","independent_expert_signoff"]
            })
    if not records:
        raise ValueError("Empty review CSV")
    return {"format":"vespaguard-csv-expert-queue-v1","training_eligible":False,"records":records,"warning":"Mobile decisions are unverified assertions; no training approval, image download or labels."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    if Path(args.input).resolve() == Path(args.output).resolve():
        raise SystemExit("Refusing to overwrite input")
    payload=stage_csv(args.input)
    output=Path(args.output)
    if output.exists():
        raise SystemExit("Refusing to overwrite existing queue")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Staged {len(payload['records'])} candidates for expert review; training approvals: 0")

if __name__=="__main__":
    main()
