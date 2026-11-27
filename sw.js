'use strict';
const CACHE='beekeeper-shell-v23';
const FILES=['./','./index.html','./style.css','./backup-contract.js','./app.js','./integrations-ui.js','./alert-rules.js','./alert-ui.js','./live-media.js','./field-image-privacy.js','./field-dataset.js','./camera-model-selector.js','./models/candidates.json','./varroa.html','./varroa-ui.js','./manifest.webmanifest','./icon.svg','./wissen/wissenschaft-hornissen-bienen.html','./wissen/weltlage-vespa-velutina.html','./datenschutz.html','./impressum.html'];
const SHELL=new Set(FILES.map(path=>new URL(path,self.registration.scope).href));
self.addEventListener('install',event=>{
 event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',event=>{
 event.waitUntil(Promise.all([
  caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('beekeeper-shell-')&&key!==CACHE).map(key=>caches.delete(key)))),
  self.clients.claim()
 ]));
});
self.addEventListener('fetch',event=>{
 const request=event.request;
 if(request.method!=='GET')return;
 const url=new URL(request.url);
 if(url.origin!==self.location.origin||!SHELL.has(url.href))return;
 event.respondWith(
  caches.match(request).then(cached=>cached||fetch(request).then(response=>{
   if(response.ok){const copy=response.clone();event.waitUntil(caches.open(CACHE).then(cache=>cache.put(request,copy)));}
   return response;
  }))
 );
});
self.addEventListener('notificationclick',event=>{
 event.notification.close();
 event.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(list=>{
  for(const client of list){if('focus' in client)return client.focus();}
  return self.clients.openWindow(self.registration.scope);
 }));
});
