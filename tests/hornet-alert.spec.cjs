const {test,expect}=require('@playwright/test');


test('alert is off by default with a 100 percent threshold',async({page})=>{
 await page.goto('/');
 await expect(page.locator('#alert-enabled')).not.toBeChecked();
 await expect(page.locator('#alert-threshold')).toHaveValue('100');
 await expect(page.locator('#alert-status')).toContainText('ausgeschaltet');
});

test('settings persist after reload',async({page})=>{
 await page.goto('/');
 await page.locator('#alert-enabled').check();
 await page.locator('#alert-threshold').fill('90');
 await page.locator('#alert-threshold').dispatchEvent('change');
 await page.reload();
 await expect(page.locator('#alert-enabled')).toBeChecked();
 await expect(page.locator('#alert-threshold')).toHaveValue('90');
});

test('test alert is clearly marked as a test',async({page})=>{
 await page.goto('/');
 await page.locator('#alert-test').click();
 await expect(page.locator('#alert-list li').first()).toContainText('TEST');
});

test('qualifying detection raises exactly one unconfirmed warning',async({page})=>{
 await page.goto('/');
 await page.locator('#alert-enabled').check();
 const result=await page.evaluate(()=>{
  const mk=(c,conf,label='vespa_velutina')=>{const now=new Date().toISOString();return {event_id:c.repeat(64),received_at:now,event:{kind:'camera_detection',device_id:'station-1',timestamp:now,payload:{label,confidence:conf}}};};
  window.BeekeeperAlerts.process([mk('a',0.99),mk('b',1,'vespa_crabro'),mk('c',1)]);
  const first=document.querySelectorAll('#alert-list li').length;
  window.BeekeeperAlerts.process([mk('c',1)]);
  return {first,second:document.querySelectorAll('#alert-list li').length};
 });
 expect(result).toEqual({first:1,second:1});
 await expect(page.locator('#alert-list li').first()).toContainText('unbestätigt');
});

test('disabled alert stays silent for qualifying detections',async({page})=>{
 await page.goto('/');
 const count=await page.evaluate(()=>{
  const now=new Date().toISOString();
  window.BeekeeperAlerts.process([{event_id:'d'.repeat(64),received_at:now,event:{kind:'camera_detection',device_id:'s',timestamp:now,payload:{label:'vespa_velutina',confidence:1}}}]);
  return document.querySelectorAll('#alert-list li').length;
 });
 expect(count).toBe(0);
});

test('alert scripts are part of the offline shell',async({page,browserName})=>{
 test.skip(browserName==='webkit','WebKit cache inspection is covered by the shell test');
 await page.goto('/');
 await page.evaluate(()=>navigator.serviceWorker.ready);
 const cached=await page.evaluate(async()=>({
  rules:!!(await caches.match(new URL('./alert-rules.js',location.href).href)),
  ui:!!(await caches.match(new URL('./alert-ui.js',location.href).href))
 }));
 expect(cached).toEqual({rules:true,ui:true});
});
