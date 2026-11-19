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
