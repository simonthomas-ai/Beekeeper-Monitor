#!/usr/bin/env python3
"""Render unapproved CC0 hornet candidates as a mobile, manual review gallery."""
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
        key = html.escape(row.get('observation_id', '') + ':' + row.get('photo_id', ''), quote=True)
        cards.append('<article data-key="' + key + '">' + photo + '<p><b>UNREVIEWED — NOT FOR TRAINING</b></p><p>' +
                     html.escape(row.get("api_taxon", "")) + ' · observation ' +
                     html.escape(row.get("observation_id", "")) + ' · photo ' +
                     html.escape(row.get("photo_id", "")) + '</p><p>License metadata: ' +
                     html.escape(row.get("api_photo_license", "")) + ' · ' +
                     html.escape(row.get("api_attribution", "")) + '</p><p>' + link + '</p>' +
                     '<label>Artbestimmung: <select aria-label="Artbestimmung"><option value="UNREVIEWED">Noch nicht geprüft</option><option value="CONFIRMED">Art bestätigt</option><option value="WRONG_SPECIES">Falsche Art</option><option value="UNCERTAIN">Unklar</option></select></label>' +
                     '<label>Notiz: <textarea aria-label="Prüfnotiz" maxlength="1000" rows="2"></textarea></label></article>')
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="referrer" content="no-referrer"><title>VespaGuard — unreviewed photo candidates</title>'
            '<style>body{font:1rem system-ui;margin:1rem auto;max-width:1100px;padding:0 1rem}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}article{border:1px solid #888;border-radius:10px;padding:1rem;overflow-wrap:anywhere}img{width:100%;height:240px;object-fit:contain}p{line-height:1.5}label{display:block;margin:.7rem 0}select,textarea,button{font:inherit;padding:.5rem;max-width:100%;box-sizing:border-box}textarea{display:block;width:100%}</style>'
            '<h1>Vespa velutina — visual review candidates</h1><p>All entries are UNREVIEWED. License metadata does not establish species identity, image quality or training approval. Images load from iNaturalist when opened online; review manually before any use.</p>'
            '<p>Candidate count: ' + str(len(cards)) + '</p><p>Markierungen bleiben bis zum CSV-Export nur in dieser geöffneten Seite. Keine automatische Trainingsfreigabe.</p>'
            '<button id="export" type="button">Prüfergebnisse als CSV exportieren</button><main>' + ''.join(cards) + '</main>'
            '<script>'
            'document.getElementById("export").addEventListener("click",()=>{'
            'const data=[["observation_id","photo_id","species_review","review_notes","training_approved"]];'
            'for(const card of document.querySelectorAll("article[data-key]")){'
            'const parts=card.dataset.key.split(":");'
            'const status=card.querySelector("select").value;'
            'const note=card.querySelector("textarea").value;'
            'data.push([parts[0],parts[1],status,note,"NO"]);}'
            'const safe=x=>{let v=String(x);if(/^[\\s]*[=+@-]/.test(v))v="\\u0027"+v;return "\\u0022"+v.replaceAll("\\u0022","\\u0022\\u0022")+"\\u0022"};'
            'const csv=data.map(row=>row.map(safe).join(",")).join("\\r\\n");'
            'const blob=new Blob(["\\ufeff",csv],{type:"text/csv;charset=utf-8"});'
            'const url=URL.createObjectURL(blob);const a=document.createElement("a");'
            'a.href=url;a.download="vespa-velutina-manual-review.csv";document.body.append(a);a.click();a.remove();'
            'setTimeout(()=>URL.revokeObjectURL(url),30000);});'
            '</script></html>')

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
