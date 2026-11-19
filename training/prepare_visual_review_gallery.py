#!/usr/bin/env python3
"""Generate a read-only visual review gallery; never approve training images."""
import argparse
import csv
import html
from pathlib import Path
from urllib.parse import urlparse

def gallery(source, output, species="Vespa velutina"):
    with open(source, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r.get("species_candidate") == species]
    if not rows:
        raise ValueError("No candidates for selected species")
    cards = []
    for row in rows:
        image = row.get("image_url", "")
        source_url = row.get("source_url", "")
        if urlparse(image).scheme != "https" or urlparse(source_url).scheme != "https":
            raise ValueError("Only HTTPS image and observation URLs are permitted")
        esc = lambda x: html.escape(str(x), quote=True)
        cards.append('<article><img loading="lazy" referrerpolicy="no-referrer" src="'+esc(image)+'" alt="Unreviewed candidate photo"><p><strong>'+esc(row["photo_id"])+'</strong> · '+esc(row["species_candidate"])+'</p><p><a href="'+esc(source_url)+'" target="_blank" rel="noopener noreferrer">Original observation</a></p><p>Species: PENDING · Quality: PENDING · Training: NO</p></article>')
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>VespaGuard visual review (unapproved)</title><style>body{font:16px system-ui;margin:2rem;background:#f7f7f7;color:#222}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem}article{background:white;padding:1rem;border:1px solid #ddd;border-radius:12px}img{width:100%;height:200px;object-fit:contain}p{overflow-wrap:anywhere}</style><h1>VespaGuard: unreviewed photo candidates</h1><p>No images have been verified or approved. External images are loaded only when this file is opened online. Review species, image quality, rights and annotation independently.</p><main>'+''.join(cards)+'</main></html>'
    dest=Path(output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(page,encoding="utf-8")
    print(f"Visual review gallery: {len(rows)} UNREVIEWED candidates; 0 training approvals.")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--species",default="Vespa velutina")
    a=p.parse_args()
    gallery(a.input,a.output,a.species)
