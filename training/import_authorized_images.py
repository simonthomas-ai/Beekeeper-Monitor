#!/usr/bin/env python3
"""Import explicitly authorized image URLs with attribution and checksums.

Input CSV columns: source_id,source_url,image_url,creator,license,license_url,attribution
Only CC0-1.0 and CC-BY-4.0 are eligible. This script cannot verify ownership.
"""
import argparse
import csv
import hashlib
import ipaddress
import socket
import urllib.parse
import urllib.request
from pathlib import Path

ALLOWED = {"CC0-1.0", "CC-BY-4.0"}
FIELDS = ["source_id", "source_url", "image_url", "creator", "license", "license_url", "attribution"]
OUTPUT = FIELDS[:2] + ["image_path"] + FIELDS[3:] + ["sha256"]

def public_https(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("public HTTPS URL required")
    for entry in socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM):
        address = ipaddress.ip_address(entry[4][0])
        if not address.is_global:
            raise ValueError("non-public address prohibited")
    return url

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("redirects require manual source review")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV of individually reviewed, authorized images")
    ap.add_argument("--output", default="datasets/hornet")
    ap.add_argument("--limit", type=int, default=50)
    args = ap.parse_args()
    if not 1 <= args.limit <= 500:
        raise SystemExit("limit must be 1..500")
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    manifest = root / "licenses.csv"
    if manifest.exists():
        raise SystemExit("Existing manifest found: refusing to overwrite")
    with open(args.input, newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not set(FIELDS).issubset(reader.fieldnames or []):
            raise SystemExit("Missing required input columns")
        rows = list(reader)
    if not rows:
        raise SystemExit("No authorized source records")
    opener = urllib.request.build_opener(NoRedirect())
    accepted = []
    seen = set()
    for row in rows[:args.limit]:
        if row["license"] not in ALLOWED or not all(row[k].strip() for k in FIELDS):
            raise SystemExit("Unapproved license or missing attribution")
        for key in ("source_url", "image_url", "license_url"):
            public_https(row[key])
        req = urllib.request.Request(row["image_url"], headers={"User-Agent": "BeekeeperMonitor-AuthorizedResearch/1.0"})
        with opener.open(req, timeout=20) as response:
            if response.headers.get_content_type() not in ("image/jpeg", "image/png", "image/webp"):
                raise SystemExit("Not a supported image MIME type")
            data = response.read(10 * 1024 * 1024 + 1)
        if not 0 < len(data) <= 10 * 1024 * 1024:
            raise SystemExit("Image exceeds 10MB or is empty")
        digest = hashlib.sha256(data).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        suffix = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[response.headers.get_content_type()]
        dest = root / "unreviewed" / (digest + suffix)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        accepted.append({k: row[k] for k in FIELDS if k != "image_url"} | {"image_path": str(dest), "sha256": digest})
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT)
        writer.writeheader()
        writer.writerows(accepted)
    print(f"Downloaded {len(accepted)} unique candidate images into UNREVIEWED. No training approved.")
    print("Manual image, ownership, species and annotation checks are still mandatory.")

if __name__ == "__main__":
    main()
