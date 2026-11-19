'use strict';
const DB='beekeeper-monitor-v2',STORE='observations';
const form=document.getElementById('form'),entries=document.getElementById('entries'),status=document.getElementById('status');
function database(){return new Promise((resolve,reject)=>{const request=indexedDB.open(DB,1);request.onupgradeneeded=()=>request.result.createObjectStore(STORE,{keyPath:'id'});request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error)})}
async function all(){const db=await database();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readonly'),req=tx.objectStore(STORE).getAll();req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);tx.oncomplete=()=>db.close()})}
async function save(item){const db=await database();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).put(item);tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>{db.close();reject(tx.error)}})}
async function remove(id){const db=await database();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).delete(id);tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>{db.close();reject(tx.error)}})}
async function render(){entries.replaceChildren();try{const items=await all();if(!items.length){const li=document.createElement('li');li.textContent='Noch keine Beobachtungen';entries.append(li)}for(const item of items.sort((a,b)=>b.at.localeCompare(a.at))){const li=document.createElement('li');li.textContent=new Date(item.at).toLocaleString('de-DE')+' – '+item.type+': '+item.note+(item.photo?' (Foto vorhanden)':'')+(item.location?' (Standort vorhanden)':'');const del=document.createElement('button');del.type='button';del.textContent='Löschen';del.setAttribute('aria-label','Beobachtung löschen: '+item.type);del.addEventListener('click',async()=>{if(!window.confirm('Diese Beobachtung und ihr Foto dauerhaft von diesem Gerät löschen?'))return;try{await remove(item.id);status.textContent='Beobachtung gelöscht.';await render()}catch{status.textContent='Löschen fehlgeschlagen.'}});li.append(' ',del);entries.append(li)}}catch{status.textContent='Lokaler Datenspeicher nicht verfügbar.'}}
function locationOnce(){return new Promise((resolve,reject)=>{if(!navigator.geolocation){reject(Error('Standort nicht unterstützt'));return}navigator.geolocation.getCurrentPosition(p=>resolve({latitude:p.coords.latitude,longitude:p.coords.longitude,accuracyMeters:p.coords.accuracy}),reject,{enableHighAccuracy:false,timeout:12000,maximumAge:0})})}
function dataURL(file){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.readAsDataURL(file)})}
form.addEventListener('submit',async e=>{e.preventDefault();const button=form.querySelector('button');button.disabled=true;status.textContent='Speichere Beobachtung …';try{const data=new FormData(form),note=String(data.get('note')||'').trim();if(!note)throw Error('Bitte eine Beobachtung eingeben.');const photo=document.getElementById('photo').files[0];if(photo&&(!photo.type.startsWith('image/')||photo.size>8*1024*1024))throw Error('Nur Bilddateien bis 8 MB erlaubt.');const item={id:crypto.randomUUID(),at:new Date().toISOString(),type:String(data.get('type')),note};if(photo){item.photo={name:photo.name,type:photo.type,content:await dataURL(photo)}}if(document.getElementById('location').checked){try{item.location=await locationOnce()}catch{throw Error('Standort nicht verfügbar oder nicht freigegeben. Bitte Standortwahl deaktivieren oder erneut versuchen.')}}await save(item);form.reset();status.textContent='Beobachtung lokal gespeichert.';await render()}catch(err){status.textContent='Nicht gespeichert: '+err.message}finally{button.disabled=false}});
document.getElementById('export').addEventListener('click',async()=>{try{const items=await all();const blob=new Blob([JSON.stringify({format:'beekeeper-monitor-v2',exportedAt:new Date().toISOString(),observations:items},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='beekeeper-beobachtungen.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);status.textContent='Export vorbereitet. Bitte die Datei sicher aufbewahren.'}catch{status.textContent='Export fehlgeschlagen.'}});

const TYPES=new Set(['Asiatische Hornisse','Varroa','Drohnenbrut','Pollen','Schwarm','Königin']);
function validObservation(item){
 if(!item||typeof item!=='object'||typeof item.id!=='string'||item.id.length>100||!/^[-a-zA-Z0-9]+$/.test(item.id))return false;
 if(typeof item.at!=='string'||!Number.isFinite(Date.parse(item.at)))return false;
 if(!TYPES.has(item.type)||typeof item.note!=='string'||item.note.length>2000)return false;
 if(item.photo!==undefined&&(!item.photo||typeof item.photo.content!=='string'||!/^data:image\/(?:png|jpeg|webp|gif);base64,[A-Za-z0-9+/=]+$/.test(item.photo.content)||item.photo.content.length>12000000))return false;
 if(item.location!==undefined&&(!item.location||!Number.isFinite(item.location.latitude)||!Number.isFinite(item.location.longitude)||Math.abs(item.location.latitude)>90||Math.abs(item.location.longitude)>180))return false;
 return true;
}
document.getElementById('import').addEventListener('change',async event=>{
 const input=event.target,file=input.files&&input.files[0];
 if(!file)return;
 try{
  if(file.size>30*1024*1024)throw Error('Sicherung größer als 30 MB.');
  const backup=JSON.parse(await file.text());
  if(!backup||backup.format!=='beekeeper-monitor-v2'||!Array.isArray(backup.observations)||backup.observations.length>10000)throw Error('Ungültiges Sicherungsformat.');
  if(!backup.observations.every(validObservation))throw Error('Ungültige Beobachtungen in der Sicherung.');
  const existing=new Set((await all()).map(item=>item.id));
  let added=0;
  for(const item of backup.observations){if(!existing.has(item.id)){await save(item);existing.add(item.id);added++}}
  status.textContent=added+' Beobachtungen wiederhergestellt; vorhandene Einträge beibehalten.';
  await render();
 }catch(err){status.textContent='Import fehlgeschlagen: '+err.message}
 finally{input.value=''}
});

if('serviceWorker'in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));render();