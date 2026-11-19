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
 await page.setContent(html);
});
test('mobile gallery: review persists when switching images',async({page})=>{
 await expect(page.locator('#counter')).toContainText('1/2');
 await page.locator('#decision').selectOption('LIKELY');
 await page.locator('#next').click();
 await page.locator('#decision').selectOption('REJECT');
 await page.locator('#prev').click();
 await expect(page.locator('#decision')).toHaveValue('LIKELY');
 await expect(page.locator('#state')).toContainText('KEINE Trainingsfreigabe');
});
test('mobile gallery: finger drag creates and clears a box',async({page})=>{
 const rect=await page.locator('#viewer').boundingBox();
 expect(rect).toBeTruthy();
 const a={x:rect.x+rect.width*.2,y:rect.y+rect.height*.2},b={x:rect.x+rect.width*.7,y:rect.y+rect.height*.7};
 await page.evaluate(([a,b])=>{
  const el=document.querySelector('#viewer');
  el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerId:1,pointerType:'touch',clientX:a.x,clientY:a.y}));
  el.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:1,pointerType:'touch',clientX:b.x,clientY:b.y}));
 },[a,b]);
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
