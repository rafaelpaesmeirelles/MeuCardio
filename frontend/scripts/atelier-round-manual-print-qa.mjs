/** Round manual-print QA: synthetic UI only; window.print is counted, not executed.
 * Generates separate Chrome print-to-PDF A4 evidence; never uses a real printer.
 * ATELIER_QA_URL must be loopback; ATELIER_ROUND_PRINT_OUT must be below /tmp.
 */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const base=new URL(process.env.ATELIER_QA_URL||'http://127.0.0.1:4322');
assert(base.protocol==='http:'&&['127.0.0.1','localhost'].includes(base.hostname)&&!base.username&&!base.password);
const out=process.env.ATELIER_ROUND_PRINT_OUT||'/tmp/corvia-round-manual-print-20260911';
assert(out.startsWith('/tmp/'));fs.mkdirSync(out,{recursive:true});assert(/^\/(private\/)?tmp\//.test(fs.realpathSync(out)));
const python=process.env.PYTHON_BIN||'/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
const institutionPath='backend/app/services/pdf/identidade_institucional.py';
const institutionSource=fs.readFileSync(path.join(root,institutionPath),'utf8');
const operator=JSON.parse(execFileSync(python,['-B','-c','import ast,json,sys; tree=ast.parse(sys.stdin.read()); node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="EMPRESA" for t in n.targets)); print(json.dumps(ast.literal_eval(node.value),ensure_ascii=False))'],{input:institutionSource,encoding:'utf8'}));
const clinicalHarness=fs.readFileSync(path.join(root,'frontend/scripts/atelier-clinical-functional-qa.mjs'),'utf8');
const extract=name=>{const m=clinicalHarness.match(new RegExp('^const '+name+' = (.+);$','m'));assert(m,'Existing fixture missing: '+name);return vm.runInNewContext('('+m[1]+')');};
const patient=extract('roundPatient');
const profile={...extract('profile'),full_name:'Médica Demonstrativa de Interface',professional_title:'Dra.',profession:'Médica',council_name:'CRM',council_number:'000000',council_state:'SP',rqe:'00000',specialty:'Cardiologia',document_logo_url:'/atelier/corvia-mark-atelier.svg',document_logo_dark_background:false,workplace_name:'CONSULTÓRIO DEMONSTRATIVO — TESTE LOCAL',include_workplace_on_documents:true};
const prescription={id:-911,items:[{drug_name:'DEMO — NÃO É MEDICAMENTO',presentation:'ITEM FICTÍCIO DE TESTE',posology:'SEM VALIDADE CLÍNICA — NÃO UTILIZAR',orientation:'Teste técnico de composição, sem prescrição ou tratamento real.'}],notes:'DEMONSTRAÇÃO LOCAL. NÃO UTILIZAR COMO DOCUMENTO CLÍNICO.',created_at:'2026-09-11T12:00:00Z'};
const report={scope:'Actual /round React flow with existing synthetic patient contract. No real drugs/patients/API/printer. Professional logo reuses the existing CorVIA mark solely as a containment fixture, not actual clinician branding.',operatorSource:{path:institutionPath,sha256:createHash('sha256').update(institutionSource).digest('hex')},operator,rows:[]};
const pdfAudit=String.raw`
import hashlib,json,sys
from pathlib import Path
from pypdf import PdfReader
import pypdfium2
p=Path(sys.argv[1]); reader=PdfReader(p); doc=pypdfium2.PdfDocument(str(p)); pages=[]
for index,page in enumerate(reader.pages):
    text=page.extract_text() or ""
    image=p.with_name(p.stem+"-page-"+str(index+1)+".png")
    doc[index].render(scale=1.3).to_pil().save(image)
    pages.append(dict(number=index+1,width=float(page.mediabox.width),height=float(page.mediabox.height),characters=len(text.strip()),text=text,image=str(image)))
print(json.dumps(dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pageCount=len(pages),pages=pages),ensure_ascii=False))
`;
function inspectPDF(row){
 row.pdfInspection=JSON.parse(execFileSync(python,['-B','-c',pdfAudit,row.pdf],{encoding:'utf8',timeout:30000}));
 if(row.pdfInspection.pageCount!==1)row.issues.push({kind:'print-pagination',expected:1,actual:row.pdfInspection.pageCount,blankTextPages:row.pdfInspection.pages.filter(p=>p.characters===0).map(p=>p.number)});
 const text=row.pdfInspection.pages.map(p=>p.text).join(' ').replace(/\s+/g,' ');
 for(const expected of [operator.razao_social,operator.cnpj,operator.logradouro,operator.numero,operator.bairro,operator.cidade,operator.uf,operator.cep,profile.full_name,'CRM 000000/SP',patient.record_number,'DEMO — NÃO É MEDICAMENTO'])if(!text.includes(expected))row.issues.push({kind:'pdf-missing-text',expected});
 if(row.pdfInspection.pages.some(p=>Math.abs(p.width-595.28)>1||Math.abs(p.height-841.89)>1))row.issues.push({kind:'not-A4'});
 if(row.printDOM?.images.some(i=>i.box.width<=0||i.box.height<=0))row.issues.push({kind:'print-logo-zero-size',images:row.printDOM.images.filter(i=>i.box.width<=0||i.box.height<=0)});
}
if(process.argv.includes('--audit-existing')){
 const existing=JSON.parse(fs.readFileSync(out+'/report.json','utf8'));for(const row of existing.rows.filter(r=>r.pdf)){inspectPDF(row);console.log(JSON.stringify({width:row.width,pages:row.pdfInspection.pageCount,issues:row.issues}));}fs.writeFileSync(out+'/report.json',JSON.stringify(existing,null,2));process.exit(existing.rows.some(r=>r.issues.length)?1:0);
}
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs');
const browser=await chromium.launch({headless:true,channel:'chrome',args:['--disable-gpu']});
async function printMetrics(page){return page.locator('.folha-impressao').evaluate(sheet=>{
 const rgba=s=>{const a=s.match(/[\d.]+/g)?.map(Number)||[];return [a[0]||0,a[1]||0,a[2]||0,a[3]??1];};
 const blend=(f,b)=>f.slice(0,3).map((v,i)=>v*f[3]+b[i]*(1-f[3]));
 const lum=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
 const box=e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
 const s=box(sheet),header=sheet.querySelector('.doc-cabecalho'),h=box(header);
 const texts=[...header.querySelectorAll('strong,span')].filter(e=>!e.children.length&&e.textContent.trim()).map(e=>{const c=getComputedStyle(e),chain=[];for(let p=e;p;p=p.parentElement)chain.unshift(p);let bg=[255,255,255];for(const p of chain)bg=blend(rgba(getComputedStyle(p).backgroundColor),bg);const fg=blend(rgba(c.webkitTextFillColor||c.color),bg),l1=lum(fg),l2=lum(bg);return{text:e.textContent.trim(),class:e.className,color:c.color,textFill:c.webkitTextFillColor,fontSize:c.fontSize,background:bg,contrast:(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05),box:box(e)};});
 const images=[...header.querySelectorAll('img')].map(e=>({src:e.getAttribute('src'),complete:e.complete,naturalWidth:e.naturalWidth,naturalHeight:e.naturalHeight,box:box(e),objectFit:getComputedStyle(e).objectFit}));
 return {viewport:{width:innerWidth,height:innerHeight},sheet:s,header:h,texts,images,operatorText:header.querySelector('.doc-cabecalho__operadora')?.textContent,professionalText:header.querySelector('.doc-cabecalho__profissional')?.textContent,sheetText:sheet.textContent,visibleOutsideSheet:[...document.body.querySelectorAll('h1,h2,button,a')].filter(e=>!sheet.contains(e)&&getComputedStyle(e).visibility==='visible'&&e.getBoundingClientRect().height>0).map(e=>e.textContent.trim()).slice(0,15)};
});}
const scenarios=(process.env.ATELIER_ROUND_PRINT_SCENARIOS||'complete,missing-operator,api-error').split(',');assert(scenarios.every(s=>['complete','missing-operator','api-error'].includes(s)));
try{for(const width of [1440,390])for(const scenario of scenarios){
 const row={route:'/round',width,height:width===1440?900:844,scenario,checks:[],issues:[],requests:[],blockedExternal:[],unmodeled:[],pageErrors:[]};
 const ctx=await browser.newContext({viewport:{width,height:row.height},locale:'pt-BR',timezoneId:'America/Sao_Paulo',serviceWorkers:'block',reducedMotion:'reduce'});
 await ctx.addInitScript(id=>{localStorage.setItem('corvia:cardiology-spaces:theme:v1:'+id,'light');window.__qaPrintCalls=[];window.print=()=>window.__qaPrintCalls.push({sheetCount:document.querySelectorAll('.folha-impressao').length,operator:document.querySelector('.doc-cabecalho__operadora')?.textContent,images:[...document.querySelectorAll('.folha-impressao img')].map(i=>({complete:i.complete,width:i.naturalWidth}))});},profile.id);
 await ctx.route('**/*',async route=>{
  const req=route.request(),u=new URL(req.url()),p=u.pathname;const json=(body,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
  if(!p.startsWith('/api/')){if(u.origin===base.origin&&['GET','HEAD'].includes(req.method()))return route.continue();row.blockedExternal.push({host:u.hostname,path:p});return route.abort('blockedbyclient');}
  row.requests.push({method:req.method(),path:p});if(req.method()!=='GET')return json({detail:'All mutations blocked by isolated QA, including heartbeat.'},403);
  if(p==='/api/auth/session-status')return json({authenticated:true});if(p==='/api/auth/me')return json(profile);if(p==='/api/version')return json({commit:'local-round-print-fixture'});
  if(p==='/api/clinical-change-approvals/count')return json({pending:0});if(p==='/api/favorites/status')return json({favorited:false,available:true});
  if(p==='/api/round/patients')return json(u.searchParams.has('archived')?[]:[patient]);
  if(p==='/api/prescriptions/patient/-910')return json([prescription]);
  if(p==='/api/prescriptions/-911/imprimir'){if(scenario==='api-error')return json({detail:'Falha503 demonstrativa ao preparar impressão.'},503);return json({medico:profile,paciente:{initials:patient.initials,record_number:patient.record_number},prescricao:prescription,...(scenario==='complete'?{operadora:operator}:{})});}
  if(['/api/round/patients/-910/ai-assist','/api/document-templates','/api/timeline/patient/-910','/api/assinatura/provedores','/api/prescricao-especial/minhas','/api/admin/users'].includes(p))return json([]);
  if(p==='/api/prescricao-especial/capacidades')return json({enabled:false,allows_self:false,rafael_signer:false});if(p==='/api/chat/nao-lidas')return json({total:0,conversas:[]});
  if(p==='/api/billing/status')return json({status:'inativo',acesso_administrativo:true,entitlements:{ai:false,mail:false}});
  row.unmodeled.push(p);return json({detail:'Dependency not modelled for Round print QA.'},503);
 });
 const page=await ctx.newPage();page.setDefaultTimeout(9000);page.on('pageerror',e=>row.pageErrors.push(String(e)));page.on('dialog',d=>d.dismiss());
 try{
  await page.goto(base.origin+'/round',{waitUntil:'domcontentloaded'});await page.getByRole('button',{name:'Abrir command center de DEMO',exact:true}).click();
  await page.locator('#pc-round-editor').getByRole('button',{name:'Abrir',exact:true}).click();
  const button=page.getByRole('button',{name:'Imprimir para assinatura manual',exact:true});await button.waitFor();await button.scrollIntoViewIfNeeded();
  row.button=await button.boundingBox();await page.screenshot({path:out+'/round-'+width+'-'+scenario+'-before.png'});await button.click();
  if(scenario==='complete'){
   await page.waitForFunction(()=>window.__qaPrintCalls?.length===1);row.printCalls=await page.evaluate(()=>window.__qaPrintCalls);assert(row.printCalls[0].images.every(i=>i.complete&&i.width>0));
   assert.equal(await page.locator('.folha-impressao').count(),1);const operatorText=await page.locator('.doc-cabecalho__operadora').textContent();for(const v of Object.values(operator))assert(operatorText.includes(v),v+' missing from operator');
   assert((await page.locator('.doc-cabecalho__profissional').textContent()).includes('CRM 000000/SP'));row.checks.push('Real Round patient/history opened; print stub called exactly once after institutional header and images loaded.');
   await page.emulateMedia({media:'print'});row.printDOM=await printMetrics(page);await page.screenshot({path:out+'/round-'+width+'-print-media.png',fullPage:true});
   row.pdf=out+'/round-'+width+'-A4.pdf';await page.pdf({path:row.pdf,format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false});inspectPDF(row);row.checks.push('Separate native Chrome print-to-PDF generated with A4 CSS; page count, exact operator/professional and synthetic patient/item text audited. No physical printer used.');
   if(row.printDOM.texts.some(t=>t.contrast<4.5))row.issues.push({kind:'print-text-contrast',texts:row.printDOM.texts.filter(t=>t.contrast<4.5)});
  }else{
   const alert=page.getByRole('alert').filter({hasText:scenario==='missing-operator'?'identificação institucional está incompleta':'Falha503 demonstrativa'});await alert.waitFor();await alert.scrollIntoViewIfNeeded();await page.waitForTimeout(150);row.alert=await alert.textContent();row.printCalls=await page.evaluate(()=>window.__qaPrintCalls);assert.equal(row.printCalls.length,0);assert.equal(await page.locator('.folha-impressao').count(),0);assert(await button.isEnabled());row.checks.push('Failure alert visible, printCount0, no printable sheet, control remains available for retry.');await page.screenshot({path:out+'/round-'+width+'-'+scenario+'-alert.png'});
  }
  if(row.pageErrors.length)row.issues.push({kind:'pageerror',errors:row.pageErrors});
 }catch(e){row.issues.push({kind:'runner',message:String(e.message).slice(0,1800)});}
 finally{report.rows.push(row);await ctx.close();fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));console.log(JSON.stringify({width,scenario,checks:row.checks,issues:row.issues,unmodeled:row.unmodeled,pdf:row.pdf}));}
}}finally{await browser.close();}
report.browserClosed=true;fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));
process.exitCode=report.rows.some(r=>r.issues.length)?1:0;
