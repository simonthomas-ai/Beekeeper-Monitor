#!/usr/bin/env python3
"""Offline-capable mobile review of remote candidate images; never self-approves."""
import argparse
import csv
import html
import json
from pathlib import Path
from urllib.parse import urlparse

def gallery(source, output, species="Vespa velutina"):
    with open(source, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if species == "ALL" or r.get("species_candidate") == species]
    if not rows:
        raise ValueError("No candidates")
    items = []
    for row in rows:
        if any(urlparse(row.get(k, "")).scheme != "https" for k in ("image_url", "source_url")):
            raise ValueError("HTTPS required")
        items.append({k: row.get(k, "") for k in ("photo_id", "observation_id", "species_candidate", "image_url", "source_url", "license", "creator")})
    if len({item["photo_id"] for item in items}) != len(items):
        raise ValueError("Duplicate photo IDs across species")
    data = json.dumps(items, ensure_ascii=False).replace("<", "\\u003c")
    title = html.escape(species)
    page = """<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VespaGuard – mobile Bildprüfung</title>
<style>body{font:17px system-ui;margin:0 auto;padding:1rem;max-width:750px;background:#f7f8fa;color:#19232c}h1{font-size:1.5rem}button,select,input{font:inherit;min-height:44px}button{padding:.6rem;border-radius:9px;border:1px solid #777;background:white}button:focus{outline:3px solid #1469aa}.actions{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0}.viewer{position:relative;background:#ddd;touch-action:none;min-height:240px}.viewer img{display:block;width:100%;height:auto;max-height:65vh;object-fit:contain;pointer-events:none;user-select:none;-webkit-user-drag:none}.viewer svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}.viewer rect{fill:#22aaff33;stroke:#0674ae;stroke-width:2}small{color:#555}a{overflow-wrap:anywhere}#state{font-weight:600}</style>
<h1>VespaGuard – Bildprüfung: __SPECIES__</h1>
<p><strong>Keine automatische Freigabe.</strong> Bilder werden von iNaturalist geladen; ohne Internet sind sie eventuell nicht sichtbar. Prüfentscheidungen bleiben auf diesem Gerät, bis du sie exportierst. Markierungen sind nur Vorschläge und müssen fachlich bestätigt werden.</p>
<div id="unified-controls" hidden><label for="species-filter">Art auswählen</label> <select id="species-filter"><option value="ALL">Alle fünf Arten</option><option value="Vespa velutina">Asiatische Hornisse</option><option value="Vespa crabro">Europäische Hornisse</option><option value="Apis mellifera">Honigbiene</option><option value="Bombus terrestris">Hummel</option><option value="Vespula vulgaris">Wespe</option></select><p id="progress" role="status"></p><progress id="progress-bar" max="100" value="0" style="width:100%"></progress></div>
<p id="counter"></p><div class="viewer" id="viewer"><img id="photo" alt="Ungeprüftes Insektenfoto"><svg id="overlay" viewBox="0 0 1000 1000" preserveAspectRatio="none"></svg></div>
<p><a id="source" target="_blank" rel="noopener noreferrer">Originalbeobachtung ansehen</a></p>
<p id="state"></p>
<label for="decision">Visuelle Prüfung</label>
<select id="decision"><option value="PENDING">Noch ungeprüft</option><option value="LIKELY">Art wahrscheinlich – Expertenprüfung nötig</option><option value="REJECT">Bild ungeeignet / falsche Art</option></select>
<p><small>Zum Markieren: einen Rahmen mit dem Finger über das Tier ziehen. Die Box wird relativ zur Bildfläche gespeichert; bei Letterboxing muss sie vor Training korrigiert werden.</small></p>
<div class="actions"><button id="clear">Markierungen löschen</button><button id="prev">Zurück</button><button id="next">Weiter</button><button id="export">Prüfliste als JSON speichern</button></div>
<script>
const items=__DATA__;
const key="vespaguard-review-v1-"+__SPECIES_JSON__;
let saved={};try{saved=JSON.parse(localStorage.getItem(key)||"{}")}catch(e){saved={}}
const unified=__SPECIES_JSON__==="ALL";
let index=0,start=null;
let visible=items.map((_,i)=>i);
if(unified){
  $("unified-controls").hidden=false;
  for(const species of ["Vespa velutina","Vespa crabro","Apis mellifera","Bombus terrestris","Vespula vulgaris"]){
    const oldKey="vespaguard-review-v1-"+species;
    try{
      const prior=JSON.parse(localStorage.getItem(oldKey)||"{}");
      for(const item of items.filter(x=>x.species_candidate===species)){
        if(!Object.prototype.hasOwnProperty.call(saved,item.photo_id)&&prior[item.photo_id]){
          saved[item.photo_id]=prior[item.photo_id];
        }
      }
    }catch(e){}
  }
  try{localStorage.setItem(key,JSON.stringify(saved))}catch(e){}
}
function selected(){return items[visible[index]]}
function refreshFilter(){
  const filter=$("species-filter").value;
  visible=items.map((_,i)=>i).filter(i=>filter==="ALL"||items[i].species_candidate===filter);
  index=0;render();
}
function updateProgress(){
  if(!unified)return;
  const done=items.filter(item=>saved[item.photo_id]&&["LIKELY","REJECT"].includes(saved[item.photo_id].decision)).length;
  $("progress").textContent=done+" von "+items.length+" Fotos bewertet";
  $("progress-bar").max=items.length;$("progress-bar").value=done;
}

const $=id=>document.getElementById(id);
function current(){const item=selected();return saved[item.photo_id]||{decision:"PENDING",boxes:[]}}
function persist(v){saved[selected().photo_id]=v;try{localStorage.setItem(key,JSON.stringify(saved))}catch(e){$("state").textContent="Speichern nicht möglich – bitte JSON exportieren."}}
function render(){const item=selected(),v=current();$("counter").textContent=(index+1)+"/"+visible.length+" – "+item.species_candidate+" – Foto "+item.photo_id;updateProgress();$("photo").src=item.image_url;$("source").href=item.source_url;$("decision").value=v.decision;$("state").textContent="Status: "+v.decision+" · Markierungen: "+v.boxes.length+" · KEINE Trainingsfreigabe";$("overlay").replaceChildren();for(const b of v.boxes){const rect=document.createElementNS("http://www.w3.org/2000/svg","rect");rect.setAttribute("x",(b.x-b.width/2)*1000);rect.setAttribute("y",(b.y-b.height/2)*1000);rect.setAttribute("width",b.width*1000);rect.setAttribute("height",b.height*1000);$("overlay").append(rect)}}
$("species-filter").onchange=refreshFilter;
$("decision").onchange=()=>{const v=current();v.decision=$("decision").value;persist(v);render()};
$("prev").onclick=()=>{index=(index-1+visible.length)%visible.length;render()};
$("next").onclick=()=>{index=(index+1)%visible.length;render()};
$("clear").onclick=()=>{const v=current();v.boxes=[];persist(v);render()};
function pos(e){const r=$("viewer").getBoundingClientRect();return{x:Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),y:Math.max(0,Math.min(1,(e.clientY-r.top)/r.height))}}
$("viewer").onpointerdown=e=>{if(e.pointerType==="mouse"&&e.button!==0)return;start=pos(e);$("viewer").setPointerCapture(e.pointerId)};
$("viewer").onpointerup=e=>{if(!start)return;const end=pos(e),x=Math.min(start.x,end.x),y=Math.min(start.y,end.y),w=Math.abs(end.x-start.x),h=Math.abs(end.y-start.y);start=null;if(w<.015||h<.015)return;const v=current();v.boxes.push({x:x+w/2,y:y+h/2,width:w,height:h});persist(v);render()};
$("viewer").onpointercancel=()=>{start=null};
$("export").onclick=()=>{const records=items.map(item=>({...item,review:saved[item.photo_id]||{decision:"PENDING",boxes:[]},training_eligible:false}));const blob=new Blob([JSON.stringify({format:"vespaguard-unverified-mobile-review-v1",species:__SPECIES_JSON__,records},null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="vespaguard-review-"+__SLUG__+".json";a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
render();
</script></html>"""
    page = page.replace("__SPECIES__", title).replace("__SPECIES_JSON__", json.dumps(species)).replace("__DATA__", data).replace("__SLUG__", json.dumps(species.lower().replace(" ", "-")))
    dest = Path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    print(f"Mobile visual review: {len(rows)} UNREVIEWED candidates; zero approvals")

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--species", default="Vespa velutina")
    a=p.parse_args()
    gallery(a.input,a.output,a.species)
