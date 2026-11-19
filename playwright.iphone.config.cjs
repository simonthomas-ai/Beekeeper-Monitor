const {defineConfig,devices}=require('@playwright/test');
const base=require('./playwright.config.cjs');
module.exports=defineConfig({
 ...base,
 use:{...base.use,...devices['iPhone 13'],browserName:'webkit'},
});
