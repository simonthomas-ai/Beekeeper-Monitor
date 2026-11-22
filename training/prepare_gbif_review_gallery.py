#!/usr/bin/env python3
"""Build a mobile, metadata-only human review gallery for GBIF media candidates.

Only allowlisted iNaturalist original derivatives are auto-embedded. All other
HTTPS media references remain visible as untrusted host exceptions and are not
requested by the browser. No image bytes, annotations or training approvals
are created by this builder.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ALLOWED_LICENSES = {
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
}
INLINE_IMAGE_HOSTS = {
    "inaturalist-open-data.s3.amazonaws.com",
    "static.inaturalist.org",
}
REQUIRED_FIELDS = {
    "source_id", "source_url", "image_url", "media_license",
    "media_license_url", "media_creator", "rights_holder", "publisher",
    "format", "occurrence_id", "occurrence_license", "occurrence_license_url",
    "occurrence_rights_holder", "dataset_key", "scientific_name",
    "species_key", "review_status",
}
ORIGINAL_PATH = re.compile(r"^/photos/[0-9]+/original\.(?:jpe?g|png|webp)$", re.I)
MAX_QUEUE_BYTES = 16 * 1024 * 1024


def read_queue_snapshot(source):
    """Read one bounded byte snapshot so hashing and CSV parsing share exact bytes."""
    if isinstance(source, (bytes, bytearray, memoryview)):
        data = bytes(source)
    else:
        with Path(source).open("rb") as stream:
            data = stream.read(MAX_QUEUE_BYTES + 1)
    if len(data) > MAX_QUEUE_BYTES:
        raise ValueError(f"GBIF candidate queue exceeds the {MAX_QUEUE_BYTES}-byte safety limit")
    return data



def _json_for_inline_script(value):
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _https_url(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is missing")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username or parsed.password
        or parsed.port not in (None, 443)
        or parsed.fragment
    ):
        raise ValueError(f"{field} must be a credential-free HTTPS URL")
    return parsed


def _allowed_inline_image(url, media_format):
    parsed = _https_url(url, "image_url")
    if parsed.hostname.lower() not in INLINE_IMAGE_HOSTS:
        return False
    if parsed.query:
        return False
    if not ORIGINAL_PATH.fullmatch(parsed.path):
        return False
    extension = parsed.path.rsplit(".", 1)[-1].lower()
    expected = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    return expected.get(extension) == str(media_format or "").strip().lower()


def prepare_items(source):
    queue_bytes = read_queue_snapshot(source)
    try:
        queue_text = queue_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("GBIF review queue must be valid UTF-8") from exc
    with io.StringIO(queue_text, newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames or []
        if len(fieldnames) != len(set(fieldnames)):
            raise ValueError("GBIF review queue contains duplicate column names")
        if any(not name for name in fieldnames):
            raise ValueError("GBIF review queue contains an empty column name")
        fields = set(fieldnames)
        missing = sorted(REQUIRED_FIELDS - fields)
        if missing:
            raise ValueError("GBIF review queue missing columns: " + ", ".join(missing))
        rows = list(reader)
        for line_number, row in enumerate(rows, start=2):
            if None in row:
                raise ValueError(f"Row {line_number}: unexpected extra CSV columns")
            if any(value is None for value in row.values()):
                raise ValueError(f"Row {line_number}: CSV row has fewer values than its header")

    if not rows:
        raise ValueError("GBIF candidate queue is empty")
    if len(rows) > 500:
        raise ValueError("GBIF candidate queue exceeds the configured 500-row review limit")
    seen_ids = set()
    items = []
    for index, row in enumerate(rows, start=2):
        if row.get("review_status") != "UNREVIEWED_MEDIA_RIGHTS_AND_IMAGE":
            raise ValueError(f"Row {index}: candidate is not in the unreviewed state")
        if row.get("media_license") not in ALLOWED_LICENSES or row.get("occurrence_license") not in ALLOWED_LICENSES:
            raise ValueError(f"Row {index}: unsupported media or occurrence licence")
        if row.get("media_license_url") != ALLOWED_LICENSES[row["media_license"]]:
            raise ValueError(f"Row {index}: media licence URL mismatch")
        if row.get("occurrence_license_url") != ALLOWED_LICENSES[row["occurrence_license"]]:
            raise ValueError(f"Row {index}: occurrence licence URL mismatch")
        if row["media_license"] == "CC-BY-4.0" and not (row.get("media_creator") or row.get("rights_holder")):
            raise ValueError(f"Row {index}: CC-BY media attribution is missing")
        if row["occurrence_license"] == "CC-BY-4.0" and not row.get("occurrence_rights_holder"):
            raise ValueError(f"Row {index}: CC-BY occurrence rights holder is missing")
        occurrence_id = str(row.get("occurrence_id", ""))
        species_key = str(row.get("species_key", ""))
        if not occurrence_id.isdecimal() or not species_key.isdecimal():
            raise ValueError(f"Row {index}: invalid occurrence or species key")
        source = _https_url(row["source_url"], "source_url")
        if source.hostname != "www.gbif.org" or source.path != f"/occurrence/{occurrence_id}":
            raise ValueError(f"Row {index}: GBIF source URL does not bind to occurrence ID")
        if source.query:
            raise ValueError(f"Row {index}: GBIF source URL query parameters are not allowed")
        media = _https_url(row["image_url"], "image_url")
        if media.query:
            raise ValueError(f"Row {index}: media URL query parameters are not allowed")
        source_id = row["source_id"]
        if not source_id or source_id in seen_ids:
            raise ValueError(f"Row {index}: empty or duplicate GBIF source ID")
        seen_ids.add(source_id)
        inline = _allowed_inline_image(row["image_url"], row.get("format", ""))
        items.append({
            "source_id": source_id,
            "occurrence_id": occurrence_id,
            "source_url": row["source_url"],
            "image_url": row["image_url"],
            "inline_image_url": row["image_url"] if inline else None,
            "image_host": media.hostname.lower(),
            "inline_allowed": inline,
            "scientific_name": row["scientific_name"],
            "species_key": species_key,
            "format": row.get("format", ""),
            "media_license": row["media_license"],
            "media_license_url": row["media_license_url"],
            "media_creator": row.get("media_creator", ""),
            "media_rights_holder": row.get("rights_holder", ""),
            "publisher": row.get("publisher", ""),
            "occurrence_license": row["occurrence_license"],
            "occurrence_license_url": row["occurrence_license_url"],
            "occurrence_rights_holder": row.get("occurrence_rights_holder", ""),
            "dataset_key": row.get("dataset_key", ""),
            "review_status": "UNREVIEWED_MEDIA_RIGHTS_AND_IMAGE",
        })
    return items


def gallery(source, output):
    source_path = Path(source)
    source_queue_bytes = read_queue_snapshot(source_path)
    items = prepare_items(source_queue_bytes)
    source_queue_sha256 = hashlib.sha256(source_queue_bytes).hexdigest()
    payload = _json_for_inline_script(items)
    page = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src https://inaturalist-open-data.s3.amazonaws.com https://static.inaturalist.org; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'none'; base-uri 'none'; form-action 'none'">
<title>BeeKeeper Monitor – GBIF Bildprüfung</title>
<style>
:root{color-scheme:light dark}body{font:16px system-ui;max-width:1000px;margin:auto;padding:1rem}h1{font-size:1.5rem}.notice{padding:.8rem;border:1px solid #888;border-radius:.6rem;margin:.8rem 0}.image{min-height:35vh;display:grid;place-items:center;background:#7772;border-radius:.5rem;overflow:hidden}.image img{display:block;max-width:100%;max-height:72vh;width:auto;height:auto;object-fit:contain}.meta{display:grid;grid-template-columns:minmax(9rem,14rem) 1fr;gap:.4rem .8rem;overflow-wrap:anywhere}.meta dt{font-weight:650}.meta dd{margin:0}.actions{display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0}button,select{font:inherit;min-height:44px;padding:.5rem;border-radius:.4rem}small{opacity:.8}#warning{font-weight:600;color:#a65b00}
</style>
</head>
<body>
<h1>GBIF – mobile Sichtprüfung</h1>
<div class="notice"><strong>Keine Trainingsfreigabe.</strong> Die angezeigten Einträge sind unreviewte Metadatenkandidaten. Medien- und Vorkommenslizenz werden getrennt angezeigt. Eine Lizenzangabe ist kein unabhängiger Beweis der Urheberberechtigung und die GBIF-Artzuordnung ist keine visuelle Expertenbestimmung. Sichtentscheidungen bleiben lokal auf diesem Gerät und werden nur bei Export weitergegeben.</div>
<p id="counter" role="status"></p>
<div id="warning" role="status"></div>
<div class="image"><img id="photo" alt="GBIF Medienkandidat – noch nicht fachlich geprüft" loading="lazy"></div>
<p id="load-status" role="status">Bild wird geladen, falls der Medienhost freigegeben ist.</p>
<dl class="meta" id="metadata"></dl>
<label for="decision">Visuelle Einschätzung</label>
<select id="decision">
<option value="PENDING">Noch ungeprüft</option>
<option value="LIKELY">Art wahrscheinlich – Expertenprüfung nötig</option>
<option value="REJECT">Bild ungeeignet / falsche Art</option>
</select>
<p><small>LIKELY ist keine bestätigte Artbestimmung. Diese Galerie erzeugt keine Bounding Boxes, Labels oder YOLO-Dateien.</small></p>
<div class="actions">
<button id="previous">Zurück</button><button id="next">Weiter</button>
<button id="export">Review-Entscheidungen als JSON exportieren</button>
</div>
<p id="saved" role="status"></p>
<script>
const items=__ITEMS__;
const sourceQueueSha256="__QUEUE_SHA256__";
const storageKey="beekeeper-gbif-review-v2-"+sourceQueueSha256;
let index=0,decisions={};
try{decisions=JSON.parse(localStorage.getItem(storageKey)||"{}")}catch(e){decisions={}}
const $=id=>document.getElementById(id);
const fields=[
 ["Quelle / GBIF","source_url"],["Occurrence ID","occurrence_id"],["Scientific name","scientific_name"],
 ["Species key","species_key"],["Media format","format"],["Medienlizenz","media_license"],
 ["Medien-Lizenz-URL","media_license_url"],["Creator","media_creator"],
 ["Media Rights Holder","media_rights_holder"],["Publisher","publisher"],
 ["Vorkommenslizenz","occurrence_license"],["Vorkommens-Lizenz-URL","occurrence_license_url"],
 ["Occurrence Rights Holder","occurrence_rights_holder"],["Dataset key","dataset_key"],
 ["Medienhost","image_host"],["Medien-URL","image_url"]
];
function save(){try{localStorage.setItem(storageKey,JSON.stringify(decisions));$("saved").textContent="Entscheidung lokal gespeichert."}catch(e){$("saved").textContent="Lokaler Speicher nicht verfügbar – bitte regelmäßig JSON exportieren."}}
function render(){
 const item=items[index],decision=decisions[item.source_id]||"PENDING";
 $("counter").textContent=(index+1)+" / "+items.length+" – "+item.scientific_name+" – "+item.occurrence_id;
 $("decision").value=decision;
 $("photo").removeAttribute("src");
 $("load-status").textContent="";
 $("warning").textContent="";
 if(item.inline_allowed){
   $("photo").src=item.inline_image_url;
   $("load-status").textContent="Einbettung nur von einem freigegebenen iNaturalist-Originalhost und Originalpfad.";
 }else{
   $("warning").textContent="Externer oder nicht eindeutig originaler Medienhost: keine automatische Einbettung. URL wird nicht angefordert.";
   $("load-status").textContent="Bitte Medienhost und Originalvariante separat prüfen; die Galerie lädt dieses Bild absichtlich nicht.";
 }
 $("metadata").replaceChildren();
 for(const [label,key] of fields){
   const dt=document.createElement("dt"),dd=document.createElement("dd");
   dt.textContent=label;dd.textContent=String(item[key]||"–");
   if(key==="source_url"||key==="image_url"||key==="media_license_url"||key==="occurrence_license_url"){
     const a=document.createElement("a");a.href=String(item[key]||"#");a.target="_blank";a.rel="noopener noreferrer";a.textContent=String(item[key]||"–");dd.replaceChildren(a);
   }
   $("metadata").append(dt,dd);
 }
}
$("decision").onchange=()=>{decisions[items[index].source_id]=$("decision").value;save()};
$("previous").onclick=()=>{index=(index-1+items.length)%items.length;render()};
$("next").onclick=()=>{index=(index+1)%items.length;render()};
$("export").onclick=()=>{
 const records=items.map(item=>({...item,review:{decision:decisions[item.source_id]||"PENDING"},training_eligible:false}));
 const blob=new Blob([JSON.stringify({format:"beekeeper-gbif-unverified-review-v2",source_queue_sha256:sourceQueueSha256,records,training_eligible:false},null,2)],{type:"application/json"});
 const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="beekeeper-gbif-visual-review.json";a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
};
render();
</script>
</body></html>
""".replace("__ITEMS__", payload).replace("__QUEUE_SHA256__", source_queue_sha256)
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")
    return {
        "records": len(items),
        "source_queue_sha256": source_queue_sha256,
        "review_export_format": "beekeeper-gbif-unverified-review-v2",
        "inline_originals": sum(bool(row["inline_allowed"]) for row in items),
        "external_or_unverified_hosts": sum(not row["inline_allowed"] for row in items),
        "images_embedded_as_bytes": 0,
        "annotations_created": 0,
        "training_approvals": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(gallery(args.input, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
