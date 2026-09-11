/** Four bounded synthetic-only Round document scenarios. No real generation,
 * signing, delivery or PDF download: fixture payloads and download-click counter.
 */
import fs from 'node:fs';import path from 'node:path';import vm from 'node:vm';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),base='http://127.0.0.1:4322';
const out=process.env.ATELIER_DOCUMENT_QA_OUT||'/tmp/corvia-document-finalization-before-20260911';assert(out.startsWith('/tmp/'));fs.mkdirSync(out,{recursive:true});assert(/^\/(private\/)?tmp\//.test(fs.realpathSync(out)));
const harness=fs.readFileSync(root+'/frontend/scripts/atelier-clinical-functional-qa.mjs','utf8');
const extract=name=>vm.runInNewContext('('+harness.match(new RegExp('^const '+name+' = (.+);$','m'))[1]+')');
const patient=extract('roundPatient'),profile=extract('profile');
const templates=[{id:-920,title:'MODELO DEMONSTRATIVO A — SEM VALIDADE CLÍNICA',doc_type:'atestado',body:'TESTE DE INTERFACE {{anotacao}}'},{id:-921,title:'MODELO DEMONSTRATIVO B — SEM VALIDADE CLÍNICA',doc_type:'laudo',body:'TESTE DE INTERFACE {{observacao}}'}];
const providers=[{codigo:'MANUAL',nome:'Manual — demonstração local',nivel:'manual',familia:'manual',disponivel:true,motivo:null}];
const report={scope:'Four UI-only scenarios across PatientDocumentos and FinalizarDocumentoGerado. Existing synthetic Round patient. Generated-document metadata is a fixture, not an emitted clinical document. PDF response is inert test bytes; all actual download clicks are blocked and counted.',rows:[]};
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs');
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--disable-gpu']});
const configs=[{name:'patient-errors-and-labels',width:1366,height:900,theme:'light'},{name:'patient-switch-template',width:390,height:844,theme:'dark'},{name:'finalizer-api-errors',width:1366,height:900,theme:'light'},{name:'finalizer-close-download',width:390,height:844,theme:'dark'}].filter(c=>!process.env.ATELIER_DOCUMENT_QA_CASE||c.name===process.env.ATELIER_DOCUMENT_QA_CASE);
assert(configs.length,'Requested scenario must be one of the four declared scenarios');
try{for(const config of configs){
 const row={...config,route:'/round',checks:[],issues:[],requests:[],blocked:[],pageErrors:[]};
 let catalogFail=config.name==='patient-errors-and-labels',generationFail=config.name==='patient-errors-and-labels',releaseGeneration=null,releasePDF=null;
 const ctx=await browser.newContext({viewport:{width:config.width,height:config.height},locale:'pt-BR',serviceWorkers:'block',reducedMotion:'reduce'});
 await ctx.addInitScript(({id,theme})=>{localStorage.setItem('corvia:cardiology-spaces:theme:v1:'+id,theme);window.__qaDownloads=[];const original=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){if(this.download){window.__qaDownloads.push({name:this.download,url:this.href.startsWith('blob:')?'local-blob':'other'});return;}return original.call(this);};},{id:profile.id,theme:config.theme});
 await ctx.route('**/*',async route=>{
  const req=route.request(),u=new URL(req.url()),p=u.pathname,json=(body,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
  if(!p.startsWith('/api/')){if(u.origin===base&&['GET','HEAD'].includes(req.method()))return route.continue();row.blocked.push({host:u.hostname,path:p});return route.abort('blockedbyclient');}
  row.requests.push({method:req.method(),path:p});
  if(p==='/api/document-templates/gerar'&&req.method()==='POST'){
   const payload=req.postDataJSON();assert.equal(payload.patient_id,patient.id);const t=templates.find(t=>t.id===payload.template_id);assert(t);const body={id:t.id===-920?-930:-931,title:t.title,doc_type:t.doc_type,rendered_body:'DEMONSTRAÇÃO INERTE; NENHUM DOCUMENTO CLÍNICO FOI EMITIDO.',medico:profile};
   if(generationFail)return json({detail:'Falha503 demonstrativa ao gerar documento.'},503);
   if(config.name==='patient-switch-template')return new Promise(resolve=>{releaseGeneration=async()=>{await json(body);resolve();};});
   return json(body);
  }
  if(/^\/api\/document-templates\/gerados\/-93[01]\/enviar-email$/.test(p)&&req.method()==='POST')return json({detail:'Falha503 demonstrativa de envio; nada enviado.'},503);
  if(req.method()!=='GET')return json({detail:'Mutation blocked by isolated fixture, including heartbeat.'},403);
  if(p==='/api/auth/session-status')return json({authenticated:true});if(p==='/api/auth/me')return json(profile);if(p==='/api/clinical-change-approvals/count')return json({pending:0});if(p==='/api/favorites/status')return json({favorited:false,available:true});
  if(p==='/api/round/patients')return json(u.searchParams.has('archived')?[]:[patient]);if(['/api/round/patients/-910/ai-assist','/api/prescriptions/patient/-910','/api/timeline/patient/-910','/api/admin/users'].includes(p))return json([]);
  if(p==='/api/document-templates')return catalogFail?json({detail:'Falha503 demonstrativa de catálogo.'},503):json(templates);
  if(p==='/api/prescricao-especial/capacidades')return json({enabled:false,allows_self:false,rafael_signer:false});if(p==='/api/assinatura/provedores')return json(providers);if(p==='/api/chat/nao-lidas')return json({total:0,conversas:[]});
  if(/^\/api\/document-templates\/gerados\/-93[01]$/.test(p))return json({assinatura:config.name==='finalizer-api-errors'?{metodo:'MANUAL',assinado_em:null}:null});
  if(/^\/api\/document-templates\/gerados\/-93[01]\/pdf$/.test(p)){
   if(config.name==='finalizer-api-errors')return json({detail:'Falha503 demonstrativa do PDF.'},503);
   return new Promise(resolve=>{releasePDF=async()=>{await route.fulfill({status:200,contentType:'application/pdf',body:Buffer.from('INERT DOWNLOAD FIXTURE — NOT A VALID CLINICAL PDF')});resolve();};});
  }
  if(p==='/api/billing/status')return json({status:'inativo',acesso_administrativo:true,entitlements:{ai:false,mail:false}});
  row.blocked.push({api:p,reason:'not modelled'});return json({detail:'API not modelled for this bounded fixture.'},503);
 });
 const page=await ctx.newPage();page.setDefaultTimeout(4500);page.on('pageerror',e=>row.pageErrors.push(String(e)));
 const panel=()=>page.locator('#pc-round-editor .cartao').filter({has:page.locator(':scope > p.eyebrow').filter({hasText:'Atestado / laudo'})});
 const finalizer=()=>panel().locator('.cartao').filter({has:page.locator(':scope > p').filter({hasText:'Documento gerado.'})});
 const step=async(name,fn)=>{try{await fn();row.checks.push({name,status:'pass'});}catch(e){row.issues.push({name,message:String(e.message).split('Call log:')[0].slice(0,800)});}};
 const open=async()=>{await page.goto(base+'/round',{waitUntil:'domcontentloaded'});await page.locator('#pc-round-editor').getByRole('button',{name:'Abrir',exact:true}).click();await panel().waitFor();};
 try{
  await open();
  if(config.name==='patient-errors-and-labels'){
   await page.waitForTimeout(350);
   await step('503 catalogue is visible and has its own retry',async()=>{await panel().getByRole('alert').waitFor();catalogFail=false;await panel().getByRole('button',{name:/Tentar novamente|Recarregar modelos/}).click();await panel().locator('select').waitFor();});
   if(await panel().locator('select').count()===0){catalogFail=false;row.checks.push({name:'Harness reload only to continue later independent checks; not product retry evidence',status:'instrumentation'});await open();}
   await panel().locator('select').selectOption('-920');await panel().getByPlaceholder('anotacao',{exact:true}).fill('ANOTAÇÃO FICTÍCIA PRESERVADA');await panel().getByRole('button',{name:'Gerar documento',exact:true}).click();
   await step('503 generation preserves fields and reports error accessibly',async()=>{await panel().getByRole('alert').filter({hasText:'Falha503 demonstrativa ao gerar documento.'}).waitFor();assert.equal(await panel().getByPlaceholder('anotacao',{exact:true}).inputValue(),'ANOTAÇÃO FICTÍCIA PRESERVADA');assert(await panel().getByRole('button',{name:'Gerar documento',exact:true}).isEnabled());});
   await step('model and template variable have associated labels and keyboard access',async()=>{const unlabeled=await panel().locator('select,input').evaluateAll(es=>es.filter(e=>!e.labels?.length&&!e.getAttribute('aria-label')&&!e.getAttribute('aria-labelledby')).map(e=>({tag:e.tagName,placeholder:e.getAttribute('placeholder')})));assert.deepEqual(unlabeled,[]);await panel().locator('select').focus();await page.keyboard.press('Tab');assert(await panel().getByPlaceholder('anotacao',{exact:true}).evaluate(e=>e===document.activeElement));});
  }else{
   await panel().locator('select').selectOption('-920');await panel().getByPlaceholder('anotacao',{exact:true}).fill('DEMONSTRAÇÃO SEM DOCUMENTO REAL');await panel().getByRole('button',{name:'Gerar documento',exact:true}).click();
   if(config.name==='patient-switch-template'){
    await page.waitForTimeout(150);assert(releaseGeneration);await panel().locator('select').selectOption('-921');await panel().getByPlaceholder('observacao',{exact:true}).fill('CONTEXTO B');await releaseGeneration();await page.waitForTimeout(200);
    await step('late result A is discarded after selecting model B',async()=>{assert.equal(await finalizer().count(),0);assert.equal(await panel().locator('select').inputValue(),'-921');assert.equal(await panel().getByPlaceholder('observacao',{exact:true}).inputValue(),'CONTEXTO B');assert(await panel().getByRole('button',{name:'Gerar documento',exact:true}).isEnabled());});
   }else{
    await finalizer().getByRole('button',{name:config.name==='finalizer-api-errors'?'Baixar PDF':'Emitir sem assinatura digital e baixar',exact:true}).waitFor();
    if(config.name==='finalizer-api-errors'){
     await step('PDF503 is explicit and keeps retry available without download',async()=>{await finalizer().getByRole('button',{name:'Baixar PDF',exact:true}).click();await finalizer().getByRole('alert').filter({hasText:'Falha503 demonstrativa do PDF.'}).waitFor();assert(await finalizer().getByRole('button',{name:'Baixar PDF',exact:true}).isEnabled());assert.equal(await page.evaluate(()=>window.__qaDownloads.length),0);});
     const email=finalizer().locator('input[type=email]');await email.fill('paciente-ficticio@example.invalid');await finalizer().getByRole('button',{name:'Enviar por e-mail',exact:true}).click();
     await step('email503 retains recipient without false delivery; label and Tab associated',async()=>{await finalizer().getByRole('alert').filter({hasText:'Falha503 demonstrativa de envio'}).waitFor();assert.equal(await email.inputValue(),'paciente-ficticio@example.invalid');assert.equal(await finalizer().getByText('E-mail enviado.',{exact:true}).count(),0);assert(await email.evaluate(e=>!!e.labels?.length||!!e.getAttribute('aria-label')||!!e.getAttribute('aria-labelledby')));await email.focus();await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.textContent.trim()),'Enviar por e-mail');});
    }else{
     await finalizer().getByRole('button',{name:'Emitir sem assinatura digital e baixar',exact:true}).click();await page.waitForTimeout(150);assert(releasePDF);await finalizer().getByRole('button',{name:'Fechar',exact:true}).click();await releasePDF();await page.waitForTimeout(200);
     await step('close invalidates pending download response',async()=>{assert.equal(await finalizer().count(),0);assert.equal(await page.evaluate(()=>window.__qaDownloads.length),0);});
    }
   }
  }
  row.labels=await panel().locator('label').evaluateAll(es=>{
   const rgb=s=>s.match(/[\d.]+/g)?.map(Number)||[0,0,0];
   const luminance=c=>c.slice(0,3).map(v=>v/255).map(v=>v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[0.2126,0.7152,0.0722][i],0);
   return es.map(e=>{const cs=getComputedStyle(e);let bg=[255,255,255],node=e;while(node){const candidate=rgb(getComputedStyle(node).backgroundColor);if(candidate.length===3||candidate[3]===1){bg=candidate;break;}node=node.parentElement;}const fg=rgb(cs.color),l=[luminance(fg),luminance(bg)].sort((a,b)=>b-a);return{text:e.textContent.trim(),color:cs.color,background:bg.slice(0,3),contrast:(l[0]+0.05)/(l[1]+0.05)};});
  });
  await step('persistent document labels have at least 4.5:1 contrast',async()=>assert(row.labels.every(l=>l.contrast>=4.5),JSON.stringify(row.labels)));
  row.downloadAttempts=await page.evaluate(()=>window.__qaDownloads);await panel().scrollIntoViewIfNeeded();await page.screenshot({path:out+'/'+config.name+'.png',fullPage:false});
  if(row.pageErrors.length)row.issues.push({name:'unhandled page error',errors:row.pageErrors});
 }catch(e){row.issues.push({name:'runner',message:String(e.message).slice(0,1000)});}
 finally{report.rows.push(row);await ctx.close();fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));console.log(JSON.stringify({name:row.name,checks:row.checks,issues:row.issues,downloadAttempts:row.downloadAttempts}));}
}}finally{await browser.close();}
report.browserClosed=true;fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));process.exitCode=report.rows.some(r=>r.issues.length)?1:0;
