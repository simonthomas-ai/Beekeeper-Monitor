const {test,expect}=require('@playwright/test');
test('real observation persists after reload and can be exported',async({page})=>{
 await page.goto('/');
 await expect(page.getByRole('heading',{name:'Beekeeper Monitor'})).toBeVisible();
 await page.getByLabel('Eigene Beobachtung').fill('Echte Testeingabe durch Browserautomation');
 await page.getByRole('button',{name:'Auf diesem Gerät speichern'}).click();
 await expect(page.getByRole('status')).toContainText('lokal gespeichert');
 await expect(page.locator('#entries')).toContainText('Echte Testeingabe durch Browserautomation');
 await page.reload();
 await expect(page.locator('#entries')).toContainText('Echte Testeingabe durch Browserautomation');
 const downloadPromise=page.waitForEvent('download');
 await page.getByRole('button',{name:'Als JSON exportieren'}).click();
 const download=await downloadPromise;
 expect(download.suggestedFilename()).toBe('beekeeper-beobachtungen.json');
});
test('offline shell works after first visit',async({page,context})=>{
 await page.goto('/');
 await expect(page.getByRole('heading',{name:'Beekeeper Monitor'})).toBeVisible();
 await page.evaluate(()=>navigator.serviceWorker.ready);
 await context.setOffline(true);
 await page.reload();
 await expect(page.getByRole('heading',{name:'Beekeeper Monitor'})).toBeVisible();
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
 await expect(page.getByRole('status')).toContainText('1 Beobachtungen wiederhergestellt');
 await expect(page.locator('#entries')).toContainText('Aus echter Sicherungsdatei wiederhergestellt');
 await page.locator('#import').setInputFiles({name:'backup.json',mimeType:'application/json',buffer:payload});
 await expect(page.getByRole('status')).toContainText('0 Beobachtungen wiederhergestellt');
 await expect(page.locator('#entries li')).toHaveCount(1);
});
test('invalid backup is rejected',async({page})=>{
 await page.goto('/');
 await page.locator('#import').setInputFiles({name:'invalid.json',mimeType:'application/json',buffer:Buffer.from('{"format":"unknown","observations":[]}')});
 await expect(page.getByRole('status')).toContainText('Import fehlgeschlagen');
});
