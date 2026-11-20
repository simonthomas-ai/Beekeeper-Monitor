#!/usr/bin/env python3
"""Fail-closed structural audit of unreviewed iNaturalist CC0 candidate metadata."""
import argparse
import collections
import csv
import json
import re
from pathlib import Path
from urllib.parse import urlparse

SPECIES = {"Vespa velutina", "Vespa crabro", "Apis mellifera", "Bombus terrestris", "Vespula vulgaris"}
FIELDS = {"source_id", "source_url", "image_url", "creator", "license", "license_url", "attribution", "observation_id", "photo_id", "species_candidate", "review_status"}
def audit(path):
    errors = []
    counts = collections.Counter()
    seen_photos, seen_observations, seen_urls = set(), set(), set()
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or set(reader.fieldnames) != FIELDS:
            return {"status":"blocked","errors":["Unexpected CSV columns"],"counts":{},"total":0,"approved":0}
        for line, row in enumerate(reader, 2):
            species = row["species_candidate"]
            counts[species] += 1
            if species not in SPECIES: errors.append(f"line {line}: unknown species")
            if row["license"] != "CC0-1.0" or row["license_url"] != "https://creativecommons.org/publicdomain/zero/1.0/":
                errors.append(f"line {line}: license metadata mismatch")
            if row["review_status"] != "UNREVIEWED": errors.append(f"line {line}: invalid review status")
            if not row["photo_id"].isdecimal() or row["source_id"] != "inat-photo-" + row["photo_id"]:
                errors.append(f"line {line}: invalid photo ID")
            if not row["observation_id"].isdecimal() or row["source_url"] != "https://www.inaturalist.org/observations/" + row["observation_id"]:
                errors.append(f"line {line}: invalid observation URL")
            url = urlparse(row["image_url"])
            if url.scheme != "https" or url.hostname not in {"static.inaturalist.org","inaturalist-open-data.s3.amazonaws.com","inaturalist-open-data.s3.us-west-2.amazonaws.com","www.inaturalist.org","inaturalist.org"} or url.username or url.password:
                errors.append(f"line {line}: unexpected image host")
            for label, value, seen in (("photo",row["photo_id"],seen_photos),("observation",row["observation_id"],seen_observations),("image URL",row["image_url"],seen_urls)):
                if value in seen: errors.append(f"line {line}: duplicate {label}")
                seen.add(value)
    if not seen_photos: errors.append("No candidate records")
    return {"status":"metadata_passed_human_review_required" if not errors else "blocked","errors":errors[:100],"counts":dict(sorted(counts.items())),"total":len(seen_photos),"approved":0,"note":"Structural metadata audit only. Does not verify live licenses, image contents, species labels or image quality."}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    result=audit(args.input)
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["errors"]: raise SystemExit(1)
if __name__=="__main__": main()
