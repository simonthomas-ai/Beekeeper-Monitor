const {test,expect}=require('@playwright/test');
const {spawnSync}=require('node:child_process');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
let dir,html;
test.beforeAll(()=>{
 dir=fs.mkdtempSync(path.join(os.tmpdir(),'vespaguard-review-'));
 const csv='photo_id,observation_id,species_candidate,image_url,source_url,license,creator\n101,201,Vespa velutina,https://static.inaturalist.org/photos/101/medium.jpg,https://www.inaturalist.org/observations/201,CC0-1.0,Test\n102,202,Vespa velutina,https://static.inaturalist.org/photos/102/medium.jpg,https://www.inaturalist.org/observations/202,CC0-1.0,Test\n';
 fs.writeFileSync(path.join(dir,'candidates.csv'),csv);
 const run=spawnSync('python3',['training/prepare_visual_review_gallery.py','--input',path.join(dir,'candidates.csv'),'--output',path.join(dir,'gallery.html')],{encoding:'utf8'});
 if(run.status!==0)throw Error(run.stderr||run.stdout);
 html=fs.readFileSync(path.join(dir,'gallery.html'),'utf8');
});
test.afterAll(()=>fs.rmSync(dir,{recursive:true,force:true}));
test.beforeEach(async({page})=>{
 await page.route('https://static.inaturalist.org/**',route=>route.fulfill({status:200,contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect width="400" height="300" fill="gray"/></svg>'}));
 await page.goto('/');
 // A review test must never inherit decisions from a previous test on this origin.
 await page.evaluate(() => localStorage.removeItem('vespaguard-review-v1-Vespa velutina'));
 await page.setContent(html);
});
test('mobile gallery: review persists when switching images',async({page})=>{
 await expect(page.locator('#counter')).toContainText('1/2');
 await page.locator('#decision').selectOption('LIKELY');
 // Ensure the first image's decision has reached the gallery's persistent state
 // before navigating; this is especially important in WebKit.
 await expect.poll(async()=>page.evaluate(()=>{
  const data=JSON.parse(localStorage.getItem('vespaguard-review-v1-Vespa velutina')||'{}');
  return data['101']?.decision;
 })).toBe('LIKELY');
 // Verify that navigation really changed the selected photo. A single WebKit
 // run previously remained on photo 101 despite the click (CI run 44920952042).
 await page.locator('#next').click();
 await expect(page.locator('#counter')).toContainText('2/2');
 await expect(page.locator('#counter')).toContainText('Foto 102');
 await expect(page.locator('#decision')).toHaveValue('PENDING');
 await page.locator('#decision').selectOption('REJECT');
 await expect.poll(async()=>page.evaluate(()=>{
  const data=JSON.parse(localStorage.getItem('vespaguard-review-v1-Vespa velutina')||'{}');
  return data['102']?.decision;
 })).toBe('REJECT');
 await page.locator('#prev').click();
 await expect(page.locator('#counter')).toContainText('1/2');
 await expect(page.locator('#counter')).toContainText('Foto 101');
 await expect(page.locator('#decision')).toHaveValue('LIKELY');
 await expect(page.locator('#state')).toContainText('KEINE Trainingsfreigabe');
});
test('mobile gallery: finger drag creates and clears a box',async({page})=>{
 const rect=await page.locator('#viewer').boundingBox();
 expect(rect).toBeTruthy();
 const a={x:rect.x+rect.width*.2,y:rect.y+rect.height*.2},b={x:rect.x+rect.width*.7,y:rect.y+rect.height*.7};
 await page.mouse.move(a.x,a.y);
 await page.mouse.down();
 await page.mouse.move(b.x,b.y,{steps:5});
 await page.mouse.up();
 await expect(page.locator('#overlay rect')).toHaveCount(1);
 await page.locator('#clear').click();
 await expect(page.locator('#overlay rect')).toHaveCount(0);
});
test('mobile gallery: JSON export remains explicitly unapproved',async({page})=>{
 await page.locator('#decision').selectOption('LIKELY');
 const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#export').click()]);
 expect(download.suggestedFilename()).toContain('vespaguard-review');
 const raw=fs.readFileSync(await download.path(),'utf8');
 const result=JSON.parse(raw);
 expect(result.records).toHaveLength(2);
 expect(result.records[0].review.decision).toBe('LIKELY');
 expect(result.records.every(x=>x.training_eligible===false)).toBe(true);
});
