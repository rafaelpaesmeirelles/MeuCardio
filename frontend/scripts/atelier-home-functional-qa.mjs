import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { certifyAtelierReference } from './atelier-reference.mjs';

const base = new URL(process.env.ATELIER_QA_URL || 'http://127.0.0.1:4322');
assert(['127.0.0.1','localhost'].includes(base.hostname) && !base.username && !base.password);
const out=path.resolve(process.env.ATELIER_QA_OUT || '/tmp/corvia-home-functional');
assert(out.startsWith('/tmp/'));fs.mkdirSync(out,{recursive:true});
assert(/^\/(?:private\/)?tmp\//.test(fs.realpathSync(out)));
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser=await chromium.launch({headless:true,channel:'chrome',args:['--disable-gpu']});
const context=await browser.newContext({viewport:{width:1366,height:900},locale:'pt-BR',serviceWorkers:'block',reducedMotion:'reduce'});
const profile={id:990192,email:'home-audit@example.invalid',full_name:'Pessoa Fictícia',role:'admin',product_access:true,profile_completion_required:false,kyc_required:false,onboarding_pendente:false,boas_vindas_pendente:false,investidor:false};
const failures=[],errors=[],requests=[],blocked=[],actions=[];
await context.route('**/*',async route=>{
  const req=route.request(),url=new URL(req.url());
  if(!url.pathname.startsWith('/api/')){
    if(url.origin===base.origin&&['GET','HEAD'].includes(req.method()))return route.continue();
    blocked.push({origin:url.origin,path:url.pathname,method:req.method()});return route.abort();
  }
  requests.push({path:url.pathname,method:req.method()});
  const reply=(body,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
  if(req.method()==='GET'){
    if(url.pathname==='/api/auth/session-status')return reply({authenticated:true});
    if(url.pathname==='/api/auth/me')return reply(profile);
    if(url.pathname==='/api/version')return reply({commit:'isolated-home-functional-fixture'});
    if(url.pathname==='/api/agenda/mobility/day-context')return reply({stage:'no_commitments',first_target:null,last_target:null,start_location:null,end_location:null});
    if(url.pathname==='/api/agenda/mobility/preferences')return reply({enabled:false,traffic_configured:false});
    if(url.pathname==='/api/agenda/mobility/next-target')return reply(null);
    if(url.pathname==='/api/agenda/mobility/map-config')return reply({configured:false});
    if(['/api/agenda/appointments','/api/agenda/commitments','/api/agenda/work-routines','/api/agenda/integrations'].includes(url.pathname))return reply([]);
    if(url.pathname==='/api/clinical-change-approvals/count')return reply({pending:0});
    if(url.pathname==='/api/favorites/status')return reply({favorited:false,available:true});
  }
  return reply({detail:'Serviço desabilitado no teste isolado.'},503);
});
const page=await context.newPage();page.setDefaultTimeout(15000);
page.on('pageerror',e=>errors.push(String(e)));
try{
  await certifyAtelierReference({page,base:base.origin,out,failures});
  actions.push('five-spaces / three-modes / hover-boundary / shelf-cancel-save-reload-restore / task-focus-switch-return / four-responsive-viewports');
  // Exercise the actual shared theme controls, not synthetic CSS injection.
  await page.goto(base.origin+'/?espaco=consultorio&modo=complete',{waitUntil:'networkidle'});
  await page.locator('.atelier-space').waitFor();
  await page.getByRole('button',{name:'Personalizar',exact:true}).click();
  const dialog=page.locator('.spaces-personalizer');await dialog.waitFor();
  await page.keyboard.press('Control+k');assert(await dialog.evaluate(d=>d.contains(document.activeElement)),'Global search escaped personalization');
  await page.keyboard.press('Escape');assert(!(await dialog.isVisible()),'Personalizer Escape');
  actions.push('personalizer keyboard search containment and Escape');
  await page.goto(base.origin+'/tour',{waitUntil:'networkidle'});
  await page.locator('.cst--atelier').waitFor();
  await page.screenshot({path:path.join(out,'tour-mobile-start.png')});
  actions.push({tourInitial:await page.locator('.cst--atelier').innerText()});
  const forward=page.getByRole('button',{name:/Começar|Conhecer|Iniciar|Explorar|Próximo|Avançar|Ver como/i}).first();
  if(await forward.isVisible()){
    await forward.click();
    for(let step=0;step<15;step++){
      const text=await page.locator('.cst--atelier').innerText();
      actions.push({step,headings:await page.locator('.cst--atelier h1,.cst--atelier h2').allTextContents(),textLength:text.length});
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'Tour horizontal overflow');
      const next=page.getByRole('button',{name:/^Próximo|^Avançar/}).first();
      if(!(await next.isVisible())||await next.isDisabled())break;
      await next.click();
    }
    await page.screenshot({path:path.join(out,'tour-mobile-final.png')});
  }else failures.push('Tour entry control was not located; walkthrough is not certified');
}catch(e){failures.push(String(e.stack||e));await page.screenshot({path:path.join(out,'failure.png')}).catch(()=>{});}
finally{
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({kind:'isolated-home-and-tour-ui-functional',limitations:'No clinical data, backend writes or external services. Tour educational scenes only.',actions,failures,errors,requests,blocked},null,2));
  await browser.close();
}
console.log(JSON.stringify({out,actions:actions.length,failures,errors}));process.exitCode=failures.length||errors.length?1:0;
