import {chromium} from '/tmp/corvia-spaces-reference-qa/node_modules/playwright-core/index.mjs';
import fs from 'node:fs';
const out='/tmp/corvia-theme-contrast-20260911/docs/qa/theme-contrast-20260911/header';fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});const report={cases:[],errors:[]};
const profile={id:99001,email:'qa@example.invalid',full_name:'Médico Teste',role:'medico',professional_title:'Dr.',crm:'0000',profile_completion_required:false,kyc_required:false,onboarding_pendente:false,boas_vindas_pendente:false,convidado:true,investidor:false,socio:false,product_access:true};
const overlap=(a,b)=>a&&b&&Math.min(a.right,b.right)-Math.max(a.x,b.x)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y)>1;
try{for(const theme of ['dark','light']){
 const ctx=await browser.newContext({viewport:{width:1440,height:900},serviceWorkers:'block'});
 await ctx.addInitScript(theme=>{localStorage.setItem('corvia:cardiology-spaces:theme:v1:99001',theme);sessionStorage.setItem('corvia:cardiology-spaces:mode','complete');},theme);
 await ctx.route('**/*',async route=>{const u=new URL(route.request().url());if(u.hostname!=='127.0.0.1')return route.abort();if(!u.pathname.startsWith('/api/')&&!u.pathname.startsWith('/mobility/'))return route.continue();let body=[];
 if(u.pathname==='/api/auth/session-status')body={authenticated:true};else if(u.pathname==='/api/auth/me')body=profile;else if(u.pathname==='/api/version')body={version:'qa-static',git_sha:'d48df1a9'};else if(u.pathname.includes('activity')||u.pathname.includes('heartbeat'))body={ok:true};else if(u.pathname.startsWith('/mobility/'))body={};
 return route.fulfill({contentType:'application/json',body:JSON.stringify(body)});});
 const page=await ctx.newPage();page.on('pageerror',e=>report.errors.push(String(e)));await page.goto('http://127.0.0.1:4785/');await page.locator('.spaces-home__topbar').waitFor();await page.evaluate(()=>document.fonts.ready);
 for(const width of [1440,1280,1024,901]){
 await page.setViewportSize({width,height:900});await page.waitForTimeout(150);
 const m=await page.evaluate(()=>{const box=s=>{const e=document.querySelector(s),r=e.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};return{theme:document.documentElement.dataset.corviaTheme,scroll:document.documentElement.scrollWidth,brand:box('.spaces-home__brand-cluster .spaces-brand'),galaxy:box('.spaces-home__brand-cluster .galaxy-theme-toggle'),search:box('.spaces-everything-search'),avatar:box('.spaces-home__topbar > .spaces-user'),header:box('.spaces-home__topbar'),position:getComputedStyle(document.querySelector('.spaces-home__brand-cluster .galaxy-theme-toggle')).position};});
 const fail=[];if(m.theme!==theme)fail.push('theme');if(m.scroll>width+1)fail.push('overflow');if(overlap(m.brand,m.galaxy))fail.push('brand overlap');if(overlap(m.galaxy,m.search))fail.push('search overlap');if(overlap(m.galaxy,m.avatar))fail.push('avatar overlap');if(m.galaxy.x<m.brand.right-1)fail.push('not beside');if(Math.abs(m.brand.y+m.brand.h/2-m.galaxy.y-m.galaxy.h/2)>2)fail.push('vertical misalignment');
 report.cases.push({theme,width,fail,m});console.log(theme,width,fail.length?fail:'PASS',JSON.stringify(m));if([1440,1280,390].includes(width))await page.screenshot({path:`${out}/${theme}-${width}.png`});
 }
 await ctx.close();
}}catch(e){report.errors.push(String(e));console.log(String(e));}finally{await browser.close();fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));if(report.errors.length||report.cases.some(c=>c.fail.length))process.exitCode=1;}
