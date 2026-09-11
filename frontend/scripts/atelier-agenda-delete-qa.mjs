// One previously uncovered flow: remove a personal commitment. Every API is
// intercepted; DELETE mutates only an in-memory synthetic fixture, never a DB.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const base='http://127.0.0.1:4322';
const out=process.env.ATELIER_AGENDA_DELETE_OUT||'/tmp/corvia-agenda-delete-before-20260911';
assert(out.startsWith('/tmp/'));fs.mkdirSync(out,{recursive:true});assert(/^\/(private\/)?tmp\//.test(fs.realpathSync(out)));
const pure=String.raw`
import ast,json,pathlib,sys
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
tree=ast.parse((pathlib.Path(sys.argv[1])/'backend/app/services/investidor_demo.py').read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_agenda_demo')
assert not any(isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.Name) and n.id in {'open','eval','exec','__import__'} for n in ast.walk(fn))
ns=dict(datetime=datetime,timedelta=timedelta,ZoneInfo=ZoneInfo)
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<pure-agenda-demo>','exec'),ns)
endpoints=['appointments','locations','services','integrations','capabilities','mobility/preferences','work-routines','work-routines/occurrences','commitment-series','commitments','google-teste/status']
print(json.dumps({'/api/agenda/'+p:ns['_agenda_demo']('/api/agenda/'+p) for p in endpoints}))
`;
const agenda=JSON.parse(execFileSync(process.env.PYTHON_BIN||'/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',['-B','-c',pure,root],{encoding:'utf8'}));
agenda['/api/agenda/appointments']=[];agenda['/api/agenda/work-routines']=[];
const commitment={...agenda['/api/agenda/commitments'][0],recurrence:'none'};
const series={...agenda['/api/agenda/commitment-series'][0],recurrence:'none',weekdays:[]};
assert.equal(commitment.series_id,series.id);assert.equal(typeof series.id,'number');assert.notEqual(commitment.id,series.id);
const source=fs.readFileSync(root+'/frontend/scripts/atelier-clinical-functional-qa.mjs','utf8');
const profile=vm.runInNewContext('('+source.match(/^const profile = (.+);$/m)[1]+')');
const cases=[{name:'desktop-delete-204',width:1366,theme:'light',failure:null},{name:'mobile-delete-503',width:390,theme:'dark',failure:'delete'},{name:'desktop-refresh-503',width:1366,theme:'light',failure:'refresh'},{name:'mobile-delete-204',width:390,theme:'dark',failure:null}].filter(c=>!process.env.ATELIER_AGENDA_DELETE_CASE||c.name===process.env.ATELIER_AGENDA_DELETE_CASE);
assert(cases.length);
const report={scope:'Personal commitment deletion only. Synthetic demo function extracted via AST without importing app/settings/DB. 204 follows the current backend soft-disable contract: numeric series ID, inactive series retained, occurrences absent. 503 cases are controlled fixtures, not production failures. No external calendar, patient, messages, signing or clinical record writes.',backendContract:['backend/app/api/agenda_integrada.py:disable_commitment_series','backend/tests/test_agenda_integrada.py:test_commitment_delete_uses_numeric_series_id_and_is_owner_scoped'],rows:[]};
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs');
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--disable-gpu']});
try{for(const config of cases){
 const row={...config,route:'/agenda',checks:[],issues:[],requests:[],blocked:[],dialogs:[],pageErrors:[]};let removed=false,deletes=0;
 const context=await browser.newContext({viewport:{width:config.width,height:900},locale:'pt-BR',serviceWorkers:'block',reducedMotion:'reduce'});
 await context.addInitScript(({id,theme})=>localStorage.setItem('corvia:cardiology-spaces:theme:v1:'+id,theme),{id:profile.id,theme:config.theme});
 await context.route('**/*',route=>{
  const req=route.request(),u=new URL(req.url()),p=u.pathname;
  if(u.origin!==base){row.blocked.push({host:u.hostname,path:p});return route.abort('blockedbyclient');}
  if(!p.startsWith('/api/'))return ['GET','HEAD'].includes(req.method())?route.continue():route.abort('blockedbyclient');
  const entry={method:req.method(),path:p};row.requests.push(entry);
  const json=(body,status=200)=>{entry.status=status;return route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});};
  if(req.method()==='DELETE'&&p===`/api/agenda/commitment-series/${series.id}`){deletes++;if(config.failure==='delete')return json({detail:'Falha503 demonstrativa ao excluir compromisso.'},503);removed=true;entry.status=204;return route.fulfill({status:204,body:''});}
  if(req.method()!=='GET')return json({detail:'Mutation blocked by local fixture, including heartbeat.'},403);
  if(p==='/api/agenda/commitment-series')return json([{...series,active:!removed}]);
  if(p==='/api/agenda/commitments'){if(removed&&config.failure==='refresh')return json({detail:'Falha503 demonstrativa de releitura.'},503);return json(removed?[]:[commitment]);}
  if(Object.hasOwn(agenda,p))return json(agenda[p]);
  if(p==='/api/auth/session-status')return json({authenticated:true});if(p==='/api/auth/me')return json(profile);
  if(p==='/api/clinical-change-approvals/count')return json({pending:0});if(p==='/api/favorites/status')return json({favorited:false,available:true});if(p==='/api/chat/nao-lidas')return json({total:0,conversas:[]});
  if(p==='/api/billing/status')return json({status:'inativo',acesso_administrativo:true,entitlements:{ai:false,mail:false}});
  row.blocked.push({api:p});return json({detail:'API not modelled in this bounded flow.'},503);
 });
 const page=await context.newPage();page.setDefaultTimeout(4500);page.on('pageerror',e=>row.pageErrors.push(String(e)));
 const modal=()=>page.getByRole('dialog',{name:'Editar compromisso',exact:true});
 const event=()=>page.getByRole('button',{name:`Editar compromisso ${commitment.title}`,exact:true});
 const step=async(name,fn)=>{try{await fn();row.checks.push({name,status:'pass'});}catch(e){row.issues.push({name,message:String(e.message).split('Call log:')[0].slice(0,900)});}};
 const confirmation=async accept=>{page.once('dialog',async dialog=>{row.dialogs.push({type:dialog.type(),text:dialog.message(),accepted:accept});if(accept)await dialog.accept();else await dialog.dismiss();});await modal().getByRole('button',{name:'Excluir compromisso',exact:true}).click();};
 try{
  await page.goto(base+'/agenda',{waitUntil:'domcontentloaded'});await page.locator('.agenda-visoes').getByRole('button',{name:'Lista',exact:true}).click();await event().waitFor();await event().focus();await page.keyboard.press('Enter');await modal().waitFor();
  await step('native confirmation can be dismissed without DELETE or closing editor',async()=>{await confirmation(false);assert.equal(deletes,0);assert(await modal().isVisible());assert.equal(await modal().getByLabel('Título',{exact:true}).inputValue(),commitment.title);});
  await confirmation(true);
  if(config.failure==='delete'){
   await step('DELETE503 is visible inside the active modal; item and form retained; no automatic retry',async()=>{const alert=modal().getByRole('alert').filter({hasText:'Falha503 demonstrativa ao excluir compromisso.'});await alert.waitFor();await alert.scrollIntoViewIfNeeded();assert.equal(await modal().getByLabel('Título',{exact:true}).inputValue(),commitment.title);assert(await modal().getByRole('button',{name:'Excluir compromisso',exact:true}).isEnabled());assert.equal(deletes,1);assert.equal(removed,false);assert.equal(await page.getByRole('status').filter({hasText:'O compromisso foi excluído.'}).count(),0);
    row.alert=await alert.evaluate(e=>{const cs=getComputedStyle(e),rect=e.getBoundingClientRect();let n=e,bg='rgb(255,255,255)';while(n){const b=getComputedStyle(n).backgroundColor;if(b!=='rgba(0, 0, 0, 0)'&&b!=='transparent'){bg=b;break;}n=n.parentElement;}const rgb=s=>s.match(/[\d.]+/g).map(Number),lum=c=>c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0),levels=[lum(rgb(cs.color)),lum(rgb(bg))].sort((a,b)=>b-a);return{color:cs.color,background:bg,contrast:(levels[0]+.05)/(levels[1]+.05),insideViewport:rect.top>=0&&rect.bottom<=innerHeight,insideDialog:!!e.closest('[role=dialog]'),unobscured:[.15,.5,.85].every(f=>e.contains(document.elementFromPoint(rect.x+rect.width/2,rect.y+rect.height*f)))};});
    assert(row.alert.contrast>=4.5);assert(row.alert.insideViewport&&row.alert.insideDialog&&row.alert.unobscured);assert.equal(await page.getByRole('alert').filter({hasText:'Falha503 demonstrativa ao excluir compromisso.'}).count(),1);await page.screenshot({path:out+'/'+config.name+'-active-error.png'});
   });
   await step('Escape after error closes only editor and returns focus to existing commitment',async()=>{await page.keyboard.press('Escape');await modal().waitFor({state:'hidden'});assert(await event().evaluate(e=>e===document.activeElement));assert.equal(deletes,1);});
  }else{
   await step('DELETE204 uses numeric series ID and closes editor with truthful completion',async()=>{await modal().waitFor({state:'hidden'});await page.getByRole('status').filter({hasText:'O compromisso foi excluído.'}).waitFor();assert.equal(deletes,1);assert.equal(removed,true);assert(row.requests.some(r=>r.method==='DELETE'&&r.path.endsWith('/-401')&&r.status===204));});
   if(config.failure==='refresh')await step('read failure after accepted DELETE is distinguished from failed deletion',async()=>{await page.getByRole('alert').filter({hasText:'A exclusão foi concluída, mas a Agenda não pôde ser atualizada.'}).waitFor();assert.equal(deletes,1);});
   else await step('successful reread removes the deleted occurrence',async()=>{await event().waitFor({state:'hidden'});assert(row.requests.filter(r=>r.path==='/api/agenda/commitments').length>=2);});
  }
  row.deletes=deletes;row.removedInFixture=removed;assert(row.dialogs.every(d=>d.type==='confirm'&&d.text===`Excluir o compromisso “${commitment.title}”?`));
  assert.deepEqual(row.pageErrors,[]);await page.screenshot({path:out+'/'+config.name+'.png'});
 }catch(e){row.issues.push({name:'runner',message:String(e.message).slice(0,1000)});}
 finally{report.rows.push(row);await context.close();fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));console.log(JSON.stringify({name:row.name,checks:row.checks,issues:row.issues,deletes}));}
}}finally{await browser.close();}
report.browserClosed=true;fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));process.exitCode=report.rows.some(r=>r.issues.length)?1:0;
