#!/usr/bin/env python3
"""Render unapproved CC0 hornet candidates as an accessible, read-only review gallery."""
import argparse
import csv
import html
from pathlib import Path

def render(rows):
    cards = []
    for row in rows:
        if row.get("training_approved") != "NO":
            continue
        image_url = row.get("large_review_url", "")
        if not image_url.startswith("https://static.inaturalist.org/") and not image_url.startswith("https://inaturalist.org/"):
            # The URL is a review hint, not a validated image.
            image_url = ""
        photo = ('<img loading="lazy" referrerpolicy="no-referrer" alt="Unverified hornet photo candidate" src="' +
                 html.escape(image_url, quote=True) + '">' if image_url else '<p>Image URL unavailable</p>')
        source = row.get("source_url", "")
        if not source.startswith("https://www.inaturalist.org/") and not source.startswith("https://inaturalist.org/"):
            source = ""
        link = ('<a href="' + html.escape(source, quote=True) + '" rel="noopener noreferrer" target="_blank">Original observation</a>' if source else "Source URL unavailable")
        cards.append('<article>' + photo + '<p><b>UNREVIEWED — NOT FOR TRAINING</b></p><p>' +
                     html.escape(row.get("api_taxon", "")) + ' · observation ' +
                     html.escape(row.get("observation_id", "")) + ' · photo ' +
                     html.escape(row.get("photo_id", "")) + '</p><p>License metadata: ' +
                     html.escape(row.get("api_photo_license", "")) + ' · ' +
                     html.escape(row.get("api_attribution", "")) + '</p><p>' + link + '</p></article>')
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="referrer" content="no-referrer"><title>VespaGuard — unreviewed photo candidates</title>'
            '<style>body{font:1rem system-ui;margin:1rem auto;max-width:1100px;padding:0 1rem}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}article{border:1px solid #888;border-radius:10px;padding:1rem;overflow-wrap:anywhere}img{width:100%;height:240px;object-fit:contain}p{line-height:1.5}</style>'
            '<h1>Vespa velutina — visual review candidates</h1><p>All entries are UNREVIEWED. License metadata does not establish species identity, image quality or training approval. Images load from iNaturalist when opened online; review manually before any use.</p>'
            '<p>Candidate count: ' + str(len(cards)) + '</p><main>' + ''.join(cards) + '</main></html>')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with open(args.input, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(rows), encoding="utf-8")
    print(f"Read-only review gallery written: {len(rows)} input rows; zero approvals.")

if __name__ == "__main__":
    main()
