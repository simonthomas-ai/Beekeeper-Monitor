'use strict';
const CACHE='beekeeper-shell-v8';
const FILES=['./','./index.html','./style.css','./app.js','./integrations-ui.js','./alert-rules.js','./alert-ui.js','./live-media.js','./manifest.webmanifest','./icon.svg'];
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
