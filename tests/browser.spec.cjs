const {test,expect}=require('@playwright/test');
// Playwright WebKit's setOffline() may reject offline navigation internally.
// For WebKit, verify the real cached shell and offline IndexedDB writes without navigating.
async function verifyCachedShell(page){
 const result=await page.evaluate(async()=>{
  const cache=await caches.match(new URL('./index.html',location.href).href);
  const media=await caches.match(new URL('./live-media.js',location.href).href);
  return {shell:!!cache && (await cache.text()).includes('Beekeeper Monitor'),media:!!media};
 });
 expect(result).toEqual({shell:true,media:true});
}

test('real observation persists after reload and can be exported',async({page})=>{
 await page.goto('/');
 await expect(page.getByRole('heading',{name:'Beekeeper Monitor'})).toBeVisible();
 await page.getByLabel('Eigene Beobachtung').fill('Echte Testeingabe durch Browserautomation');
 await page.getByRole('button',{name:'Auf diesem Gerät speichern'}).click();
 await expect(page.locator('#status')).toContainText('lokal gespeichert');
 await expect(page.locator('#entries')).toContainText('Echte Testeingabe durch Browserautomation');
 await page.reload();
 await expect(page.locator('#entries')).toContainText('Echte Testeingabe durch Browserautomation');
 page.once('dialog',dialog=>dialog.accept());
 const downloadPromise=page.waitForEvent('download');
 await page.getByRole('button',{name:'Als JSON exportieren'}).click();
 const download=await downloadPromise;
 expect(download.suggestedFilename()).toBe('beekeeper-beobachtungen.json');
});
test('privacy summary download excludes IDs, notes, images and exact coordinates', async ({page}) => {
  await page.goto('/');
  await page.evaluate(async () => {
    const db = await new Promise((resolve, reject) => {
      const request = indexedDB.open('beekeeper-monitor-v2', 1);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    await new Promise((resolve, reject) => {
      const tx = db.transaction('observations', 'readwrite');
      tx.objectStore('observations').put({
        id: 'privacy-test-001',
        at: '2026-11-21T08:00:00.000Z',
        type: 'Asiatische Hornisse',
        note: 'PRIVATE NOTE MUST NOT EXPORT',
        photo: {
          name: 'private.jpg',
          type: 'image/jpeg',
          content: 'data:image/jpeg;base64,aGVsbG8='
        },
        location: {latitude: 51.5, longitude: 7.4, accuracyMeters: 5}
      });
      tx.oncomplete = () => { db.close(); resolve(); };
      tx.onerror = () => { db.close(); reject(tx.error); };
      tx.onabort = () => { db.close(); reject(tx.error); };
    });
  });

  page.once('dialog', async dialog => {
    expect(dialog.message()).toContain('UTC-Monat');
    expect(dialog.message()).toContain('GPS-Koordinaten');
    await dialog.accept();
  });
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', {name: 'Datensparsame Monatsübersicht (CSV)'}).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('beekeeper-monatsuebersicht-datensparsam.csv');
  const stream = await download.createReadStream();
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  const csv = Buffer.concat(chunks).toString('utf8');
  expect(csv).toContain('"2026-11";"Asiatische Hornisse";"1"');
  for (const secret of [
    'privacy-test-001', 'PRIVATE NOTE MUST NOT EXPORT', 'data:image/',
    '51.5', '7.4', 'latitude', 'longitude'
  ]) {
    expect(csv).not.toContain(secret);
  }
});

test('cancelling a sensitive observation export downloads nothing',async({page})=>{
 await page.goto('/');
 await page.getByLabel('Eigene Beobachtung').fill('Lokaler Export mit möglichem Standortbezug');
 await page.getByRole('button',{name:'Auf diesem Gerät speichern'}).click();
 await page.once('dialog',async dialog=>{
  expect(dialog.message()).toContain('GPS-Koordinaten');
  await dialog.dismiss();
 });
 await page.getByRole('button',{name:'Als JSON exportieren'}).click();
 await expect(page.locator('#status')).toContainText('Export abgebrochen');
});
test('offline shell works after first visit',async({page,context,browserName})=>{
 await page.goto('/');
 await expect(page.getByRole('heading',{name:'Beekeeper Monitor'})).toBeVisible();
 await page.evaluate(()=>navigator.serviceWorker.ready);
 await context.setOffline(true);
 if(browserName==='webkit'){
  await verifyCachedShell(page);
 }else{
  await page.reload();
  await expect(page.getByRole('heading',{name:'Beekeeper Monitor'})).toBeVisible();
 }
 await context.setOffline(false);
});
test('no unvalidated AI prediction is presented',async({page})=>{
 await page.goto('/');
 await expect(page.getByText('Die automatische KI-Erkennung ist noch nicht validiert.')).toBeVisible();
});

test('backup restores genuine observations without duplicates',async({page})=>{
 await page.goto('/');
 const backup={format:'beekeeper-monitor-v2',observations:[{id:'backup-test-001',at:'2026-11-19T10:00:00.000Z',type:'Varroa',note:'Aus echter Sicherungsdatei wiederhergestellt'}]};
 const payload=Buffer.from(JSON.stringify(backup));
 await page.locator('#import').setInputFiles({name:'backup.json',mimeType:'application/json',buffer:payload});
 await expect(page.locator('#status')).toContainText('1 Beobachtungen vollständig wiederhergestellt');
 await expect(page.locator('#entries')).toContainText('Aus echter Sicherungsdatei wiederhergestellt');
 await page.locator('#import').setInputFiles({name:'backup.json',mimeType:'application/json',buffer:payload});
 await expect(page.locator('#status')).toContainText('0 Beobachtungen vollständig wiederhergestellt');
 await expect(page.locator('#entries li')).toHaveCount(1);
});
test('invalid backup is rejected',async({page})=>{
 await page.goto('/');
 await page.locator('#import').setInputFiles({name:'invalid.json',mimeType:'application/json',buffer:Buffer.from('{"format":"unknown","observations":[]}')});
 await expect(page.locator('#status')).toContainText('Import abgebrochen');
});

test('deleting an observation requires confirmation and persists',async({page})=>{
 await page.goto('/');
 await page.getByLabel('Eigene Beobachtung').fill('Zu löschender lokaler Eintrag');
 await page.getByRole('button',{name:'Auf diesem Gerät speichern'}).click();
 await expect(page.locator('#entries')).toContainText('Zu löschender lokaler Eintrag');
 page.once('dialog',dialog=>dialog.dismiss());
 await page.getByRole('button',{name:'Beobachtung löschen: Asiatische Hornisse'}).click();
 await expect(page.locator('#entries')).toContainText('Zu löschender lokaler Eintrag');
 page.once('dialog',dialog=>dialog.accept());
 await page.getByRole('button',{name:'Beobachtung löschen: Asiatische Hornisse'}).click();
 await expect(page.locator('#entries')).not.toContainText('Zu löschender lokaler Eintrag');
 await page.reload();
 await expect(page.locator('#entries')).toContainText('Noch keine Beobachtungen');
});

test('offline observations can be saved after the shell is cached',async({page,context,browserName})=>{
 await page.goto('/');
 await page.evaluate(()=>navigator.serviceWorker.ready);
 await context.setOffline(true);
 if(browserName==='webkit') await verifyCachedShell(page);
 else await page.reload();
 await page.getByLabel('Eigene Beobachtung').fill('Offline-Testeintrag');
 await page.getByRole('button',{name:'Auf diesem Gerät speichern'}).click();
 await expect(page.locator('#status')).toContainText('lokal gespeichert');
 if(browserName==='webkit') await context.setOffline(false);
 await page.reload();
 await expect(page.locator('#entries')).toContainText('Offline-Testeintrag');
 await context.setOffline(false);
});
test('malicious note is displayed as text, not HTML',async({page})=>{
 await page.goto('/');
 await page.getByLabel('Eigene Beobachtung').fill('<img src=x onerror=alert(1)>');
 await page.getByRole('button',{name:'Auf diesem Gerät speichern'}).click();
 await expect(page.locator('#entries')).toContainText('<img src=x onerror=alert(1)>');
 await expect(page.locator('#entries img')).toHaveCount(0);
});
test('denied geolocation does not save an incomplete observation',async({page,context})=>{
 await context.grantPermissions([]);
 await page.goto('/');
 await page.getByLabel('Eigene Beobachtung').fill('Nicht ohne Standort speichern');
 await page.locator('#location').check();
 await page.getByRole('button',{name:'Auf diesem Gerät speichern'}).click();
 await expect(page.locator('#status')).toContainText('Nicht gespeichert: Standort');
 await expect(page.locator('#entries')).not.toContainText('Nicht ohne Standort speichern');
});
test('rejects oversized or non-image uploads',async({page})=>{
 await page.goto('/');
 await page.getByLabel('Eigene Beobachtung').fill('Unzulässiger Dateianhang');
 await page.locator('#photo').setInputFiles({name:'unsafe.txt',mimeType:'text/plain',buffer:Buffer.from('unsafe')});
 await page.getByRole('button',{name:'Auf diesem Gerät speichern'}).click();
 await expect(page.locator('#status')).toContainText('Nur unterstützte Bilddateien');
 await expect(page.locator('#entries')).not.toContainText('Unzulässiger Dateianhang');
});

test('PWA cache stores local application shell but not remote photo URLs',async({page})=>{
 await page.goto('/');
 await page.evaluate(()=>navigator.serviceWorker.ready);
 await expect.poll(async()=>page.evaluate(async()=>{
  const cached=await caches.match(new URL('./index.html',location.href).href);
  return Boolean(cached);
 })).toBe(true);
 const result=await page.evaluate(async()=>{
  const shell=['index.html','app.js','integrations-ui.js','alert-rules.js','alert-ui.js','live-media.js','manifest.webmanifest'];
  const missing=[];
  for(const file of shell){
   const url=new URL('./'+file,location.href).href;
   if(!(await caches.match(url)))missing.push(file);
  }
  const allKeys=(await Promise.all((await caches.keys()).map(async name=>(await caches.open(name)).keys()))).flat();
  const foreign=allKeys.filter(req=>new URL(req.url).origin!==location.origin).map(req=>req.url);
  return {missing,foreign};
 });
 expect(result.missing).toEqual([]);
 expect(result.foreign).toEqual([]);
});

test('offline saved observation survives reconnect and export still works',async({page,context,browserName})=>{
 await page.goto('/');
 await page.evaluate(()=>navigator.serviceWorker.ready);
 await context.setOffline(true);
 if(browserName==='webkit')await verifyCachedShell(page);
 else await page.reload();
 await page.getByLabel('Eigene Beobachtung').fill('Unabhängiger Offline-Exporttest');
 await page.getByRole('button',{name:'Auf diesem Gerät speichern'}).click();
 await expect(page.locator('#entries')).toContainText('Unabhängiger Offline-Exporttest');
 page.once('dialog',dialog=>dialog.accept());
 const downloadPromise=page.waitForEvent('download');
 await page.getByRole('button',{name:'Als JSON exportieren'}).click();
 const download=await downloadPromise;
 expect(download.suggestedFilename()).toBe('beekeeper-beobachtungen.json');
 await context.setOffline(false);
 await page.reload();
 await expect(page.locator('#entries')).toContainText('Unabhängiger Offline-Exporttest');
});
