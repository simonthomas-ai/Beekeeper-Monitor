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
 const downloadPromise=page.waitForEvent('download');
 await page.getByRole('button',{name:'Als JSON exportieren'}).click();
 const download=await downloadPromise;
 expect(download.suggestedFilename()).toBe('beekeeper-beobachtungen.json');
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
 await expect(page.locator('#status')).toContainText('1 Beobachtungen wiederhergestellt');
 await expect(page.locator('#entries')).toContainText('Aus echter Sicherungsdatei wiederhergestellt');
 await page.locator('#import').setInputFiles({name:'backup.json',mimeType:'application/json',buffer:payload});
 await expect(page.locator('#status')).toContainText('0 Beobachtungen wiederhergestellt');
 await expect(page.locator('#entries li')).toHaveCount(1);
});
test('invalid backup is rejected',async({page})=>{
 await page.goto('/');
 await page.locator('#import').setInputFiles({name:'invalid.json',mimeType:'application/json',buffer:Buffer.from('{"format":"unknown","observations":[]}')});
 await expect(page.locator('#status')).toContainText('Import fehlgeschlagen');
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
 await expect(page.locator('#status')).toContainText('Nur Bilddateien');
 await expect(page.locator('#entries')).not.toContainText('Unzulässiger Dateianhang');
});
