'use strict';
(()=>{
 const mode=document.getElementById('varroa-mode');
 const description=document.getElementById('varroa-description');
 const model=document.getElementById('varroa-model');
 const photo=document.getElementById('varroa-photo');
 const preview=document.getElementById('varroa-preview');
 const status=document.getElementById('varroa-photo-status');
 const count=document.getElementById('varroa-manual');
 const countStatus=document.getElementById('varroa-count');
 let url=null;
 function updateMode(){
  const board=mode.value==='board';
  description.textContent=board?'Foto der Varroa-Bodeneinlage: Milbenfall manuell kontrollieren.':'Nahaufnahme einer Biene: sichtbare Milben manuell kontrollieren.';
  model.textContent=board?'Ausgewählt: VarroDetector – KI-Import noch gesperrt.':'Ausgewählt: Gratheon Varroa-on-bee – KI-Import noch gesperrt.';
 }
 function clear(){if(url){URL.revokeObjectURL(url);url=null}preview.hidden=true;preview.removeAttribute('src');photo.value='';status.textContent='Noch kein Foto ausgewählt.'}
 mode.addEventListener('change',updateMode);
 photo.addEventListener('change',()=>{
  clearPreview();
  const file=photo.files&&photo.files[0];
  if(!file){status.textContent='Noch kein Foto ausgewählt.';return}
  if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>20*1024*1024){photo.value='';status.textContent='Nur JPEG, PNG oder WebP bis 20 MB erlaubt.';return}
  url=URL.createObjectURL(file);preview.src=url;preview.hidden=false;
  status.textContent='Lokale Fotovorschau – keine automatische KI-Auswertung.';
 });
 function clearPreview(){if(url){URL.revokeObjectURL(url);url=null}preview.hidden=true;preview.removeAttribute('src')}
 document.getElementById('varroa-clear').addEventListener('click',clear);
 count.addEventListener('input',()=>{const n=Number(count.value);countStatus.textContent=Number.isSafeInteger(n)&&n>=0&&n<=100000?'Manuelle Zählung: '+n:'Bitte eine ganze Zahl zwischen 0 und 100000 eingeben.'});
 window.addEventListener('pagehide',clearPreview);
 updateMode();
})();
