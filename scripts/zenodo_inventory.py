#!/usr/bin/env python3
"""Fetch real Zenodo metadata and optionally download a named artifact.
Never generates training examples or invents weights.
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

RECORDS={"varroa-v2":"23276947","varroa-original":"4085044","varroa-ev2":"13771384"}

# Dataset files remain blocked until a separate per-file rights review is approved.
DOWNLOADS_ENABLED = False
def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"BeekeeperMonitorResearch/1.0"}),timeout=40) as resp:
        return json.load(resp)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("record",choices=RECORDS)
    p.add_argument("--download",help="Blocked until a separately reviewed per-file rights authorization enables downloads")
    p.add_argument("--output-dir",default="downloads")
    args=p.parse_args()
    if args.download and DOWNLOADS_ENABLED is not True:
        p.error("External dataset downloads are disabled in code pending per-file license, provenance and use-rights review")
    record=get_json("https://zenodo.org/api/records/"+RECORDS[args.record])
    files=record.get("files",[])
    for f in files:
        print(f.get("key"),f.get("size"),f.get("checksum"))
    if not args.download:return
    item=next((f for f in files if f.get("key")==args.download),None)
    if item is None:raise SystemExit("File not in record; download refused")
    link=item.get("links",{}).get("self") or item.get("links",{}).get("content")
    if not link or not link.startswith("https://"):raise SystemExit("No secure download link")
    dest=Path(args.output_dir)/args.record/Path(args.download).name
    dest.parent.mkdir(parents=True,exist_ok=True)
    h=hashlib.md5()
    with urllib.request.urlopen(link,timeout=90) as response,open(dest,"wb") as out:
        while chunk:=response.read(1024*1024):
            out.write(chunk);h.update(chunk)
    checksum=item.get("checksum","")
    if checksum.startswith("md5:") and h.hexdigest()!=checksum.split(":",1)[1]:
        dest.unlink(missing_ok=True)
        raise SystemExit("Checksum mismatch: discarded downloaded file")
    print("Verified download:",dest,"md5:",h.hexdigest())
if __name__=="__main__":main()
