'use strict';
const DB='beekeeper-monitor-v2',STORE='observations';
const form=document.getElementById('form'),entries=document.getElementById('entries'),status=document.getElementById('status');
function database(){return new Promise((resolve,reject)=>{const request=indexedDB.open(DB,1);request.onupgradeneeded=()=>request.result.createObjectStore(STORE,{keyPath:'id'});request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error)})}
async function all(){const db=await database();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readonly'),req=tx.objectStore(STORE).getAll();req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);tx.oncomplete=()=>db.close()})}
async function save(item){const db=await database();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).put(item);tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>{db.close();reject(tx.error)}})}
async function remove(id){const db=await database();return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,'readwrite');tx.objectStore(STORE).delete(id);tx.oncomplete=()=>{db.close();resolve()};tx.onerror=()=>{db.close();reject(tx.error)}})}
async function restoreMissing(items){
 const db=await database();
 return new Promise((resolve,reject)=>{
  let tx,added=0,settled=false;
  const fail=error=>{if(settled)return;settled=true;db.close();reject(error||Error('Import wurde nicht vollständig gespeichert.'))};
  try{tx=db.transaction(STORE,'readwrite')}catch(error){db.close();reject(error);return}
  tx.oncomplete=()=>{if(settled)return;settled=true;db.close();resolve(added)};
  tx.onabort=()=>fail(tx.error);
  for(const item of items){
   const request=tx.objectStore(STORE).get(item.id);
   request.onsuccess=()=>{if(request.result===undefined){tx.objectStore(STORE).add(item);added++}};
  }
 });
}
async function render(){entries.replaceChildren();try{const items=await all();if(!items.length){const li=document.createElement('li');li.textContent='Noch keine Beobachtungen';entries.append(li)}for(const item of items.sort((a,b)=>b.at.localeCompare(a.at))){const li=document.createElement('li');li.textContent=new Date(item.at).toLocaleString('de-DE')+' – '+item.type+': '+item.note+(item.photo?' (Foto vorhanden)':'')+(item.location?' (Standort vorhanden)':'');const del=document.createElement('button');del.type='button';del.textContent='Löschen';del.setAttribute('aria-label','Beobachtung löschen: '+item.type);del.addEventListener('click',async()=>{if(!window.confirm('Diese Beobachtung und ihr Foto dauerhaft von diesem Gerät löschen?'))return;try{await remove(item.id);status.textContent='Beobachtung gelöscht.';await render()}catch{status.textContent='Löschen fehlgeschlagen.'}});li.append(' ',del);entries.append(li)}}catch{status.textContent='Lokaler Datenspeicher nicht verfügbar.'}}
function locationOnce(){return new Promise((resolve,reject)=>{if(!navigator.geolocation){reject(Error('Standort nicht unterstützt'));return}navigator.geolocation.getCurrentPosition(p=>resolve({latitude:p.coords.latitude,longitude:p.coords.longitude,accuracyMeters:p.coords.accuracy}),reject,{enableHighAccuracy:false,timeout:12000,maximumAge:0})})}
function dataURL(file){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.readAsDataURL(file)})}
form.addEventListener('submit',async e=>{e.preventDefault();const button=form.querySelector('button');button.disabled=true;status.textContent='Speichere Beobachtung …';try{const data=new FormData(form),note=String(data.get('note')||'').trim();if(!note)throw Error('Bitte eine Beobachtung eingeben.');const photo=document.getElementById('photo').files[0];if(photo&&(!window.BeekeeperBackupContract.isSupportedImageType(photo.type)||photo.size===0||photo.size>window.BeekeeperBackupContract.MAX_PHOTO_BYTES))throw Error('Nur unterstützte Bilddateien (PNG, JPEG, WebP, GIF, AVIF, HEIC, HEIF, BMP oder TIFF) bis 8 MB erlaubt.');const item={id:crypto.randomUUID(),at:new Date().toISOString(),type:String(data.get('type')),note};if(photo){item.photo={name:photo.name,type:photo.type.toLowerCase(),content:await dataURL(photo)}}if(document.getElementById('location').checked){try{item.location=await locationOnce()}catch{throw Error('Standort nicht verfügbar oder nicht freigegeben. Bitte Standortwahl deaktivieren oder erneut versuchen.')}}await save(item);form.reset();status.textContent='Beobachtung lokal gespeichert.';await render()}catch(err){status.textContent='Nicht gespeichert: '+err.message}finally{button.disabled=false}});
document.getElementById('export').addEventListener('click',async()=>{try{const items=await all();const blob=new Blob([JSON.stringify({format:'beekeeper-monitor-v2',exportedAt:new Date().toISOString(),observations:items},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='beekeeper-beobachtungen.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);status.textContent='Export vorbereitet. Bitte die Datei sicher aufbewahren.'}catch{status.textContent='Export fehlgeschlagen.'}});
document.getElementById('import').addEventListener('change',async event=>{
 const input=event.target,file=input.files&&input.files[0];
 if(!file)return;
 try{
  if(file.size>window.BeekeeperBackupContract.MAX_BACKUP_BYTES)throw Error('Sicherung größer als 30 MB.');
  const observations=window.BeekeeperBackupContract.parseBackupText(await file.text());
  const added=await restoreMissing(observations);
  status.textContent=added+' Beobachtungen vollständig wiederhergestellt; vorhandene Einträge beibehalten.';
  await render();
 }catch(err){status.textContent='Import abgebrochen: '+err.message}
 finally{input.value=''}
});
if('serviceWorker'in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));render();
