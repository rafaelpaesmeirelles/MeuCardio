/** Focused profile/manual-photo QA: loopback only, no real account or upload.
 * Synthetic API declarations are reused without executing the wider runner.
 * All writes are intercepted; unknown APIs return the fixture's explicit error.
 * Run with PLAYWRIGHT_MODULE, QA_BASE (default4322), optional QA_OUTPUT (/tmp).
 * Real schema/handler regressions run separately in test_profile_photo_contract_no_db.py.
 */
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const base=process.env.QA_BASE||'http://127.0.0.1:4322';
assert.ok(['localhost','127.0.0.1','[::1]'].includes(new URL(base).hostname));
assert.equal(new URL(base).protocol,'http:');
const out=process.env.QA_OUTPUT||'/tmp/corvia-profile-photo-qa';
assert.ok(out.startsWith('/tmp/'),'QA artifacts must remain temporary');
fs.mkdirSync(out,{recursive:true});
const shared=fs.readFileSync(new URL('./atelier-management-functional-qa.mjs',import.meta.url),'utf8');
const start=shared.indexOf('const now='),end=shared.indexOf('const browser=');
assert.ok(start>=0&&end>start,'Synthetic fixture declaration boundaries changed');
const rows=[];
const image=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aTrEAAAAASUVORK5CYII=','base64');
const browser=await chromium.launch({headless:true,channel:'chrome',args:['--disable-gpu']});
try{
 for(const [width,theme] of [[1366,'light'],[390,'dark']]){
  const fixture=vm.runInNewContext(shared.slice(start,end)+';({user,apiFixture,unknown})');
  fixture.user.photo_url='/fotos/qa-original.png';
  const row={route:'/minha-conta',width,theme,actions:[],issues:[],blocked:[],pageErrors:[],requests:[],limitations:['API responses and upload bytes are synthetic; no production database, storage, email or external service is exercised.','Profile API serialization and input schemas are exercised separately by the no-DB Python tests.']};
  rows.push(row);
  let photoMode='error',patchMode='error',uploads=0,patchStarted=false,releasePatch;
  const context=await browser.newContext({viewport:{width,height:900},locale:'pt-BR',serviceWorkers:'block'});
  await context.addInitScript(({theme})=>{
   localStorage.setItem('corvia:cardiology-spaces:theme:v1:990091',theme);
   localStorage.setItem('corvia:cardiology-spaces:theme:v1',theme);
  },{theme});
  await context.route('**/*',async route=>{
   const request=route.request(),url=new URL(request.url());
   if(url.origin!==base){row.blocked.push(url.hostname);return route.abort('blockedbyclient');}
   if(url.pathname.startsWith('/fotos/qa-'))return route.fulfill({status:200,contentType:'image/png',body:image});
   if(!url.pathname.startsWith('/api/')){
    if(['GET','HEAD'].includes(request.method()))return route.continue();
    return route.abort('blockedbyclient');
   }
   row.requests.push({method:request.method(),path:url.pathname});
   if(url.pathname==='/api/auth/me/foto'&&request.method()==='POST'){
    uploads++;
    await new Promise(resolve=>setTimeout(resolve,450));
    if(photoMode==='error')return route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Armazenamento indisponível nesta simulação. Sua foto anterior foi preservada.'})});
    fixture.user.photo_url='/fotos/qa-updated.png';
    return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(fixture.user)});
   }
   if(url.pathname==='/api/auth/me'&&request.method()==='PATCH'){
    const data=request.postDataJSON();
    assert.equal(Object.keys(data).some(key=>/instagram/i.test(key)),false,'No retired field may be sent');
    if(patchMode==='delayed'){
     patchStarted=true;
     await new Promise(resolve=>{releasePatch=resolve;});
     return route.fulfill({status:422,contentType:'application/json',body:JSON.stringify({detail:'Falha de validação simulada após atraso.'})});
    }
    if(patchMode==='error')return route.fulfill({status:422,contentType:'application/json',body:JSON.stringify({detail:'Dados profissionais inválidos nesta simulação.'})});
    Object.assign(fixture.user,data);
    return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(fixture.user)});
   }
   const [body,status=200]=fixture.apiFixture(url,request.method());
   return route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
  });
  const page=await context.newPage();page.setDefaultTimeout(12000);
  page.on('pageerror',error=>row.pageErrors.push(error.message));
  try{
   const open=async()=>{
    await page.goto(base+'/minha-conta',{waitUntil:'domcontentloaded',timeout:30000});
    await page.locator('#conta-nome').waitFor({state:'visible'});
   };
   await open();
   const field=page.locator('#conta-nome');
   assert.equal(await page.getByText(/instagram/i).count(),0);
   assert.equal(await page.locator('[id*="instagram"], [href*="instagram"]').count(),0);
   await field.fill('Rascunho Profissional Demonstrativo');
   const choose=async()=>{
    const button=page.getByRole('button',{name:'Trocar foto',exact:true});
    await button.scrollIntoViewIfNeeded();await button.focus();
    const chooserPromise=page.waitForEvent('filechooser');
    await page.keyboard.press('Space');
    const chooser=await chooserPromise;
    await chooser.setFiles({name:'foto-ficticia.png',mimeType:'image/png',buffer:image});
    await page.waitForFunction(()=>Array.from(document.querySelectorAll('button')).some(b=>b.textContent?.trim()==='Enviando…'&&b.disabled));
   };
   await choose();
   await page.getByRole('alert').filter({hasText:'Armazenamento indisponível'}).waitFor();
   assert.equal(await field.inputValue(),'Rascunho Profissional Demonstrativo');
   assert.match(await page.getByAltText('Sua foto de perfil').getAttribute('src'),/qa-original/);
   row.actions.push('Native photo button activates with Space; busy state; simulated503 preserves photo and unsaved professional draft');
   photoMode='success';await choose();
   await page.waitForFunction(()=>document.querySelector('img[alt="Sua foto de perfil"]')?.getAttribute('src')?.includes('qa-updated'));
   assert.equal(await field.inputValue(),'Rascunho Profissional Demonstrativo');assert.equal(uploads,2);
   row.actions.push('Successful simulated manual upload updates avatar without resetting unsaved profile');
   await page.getByRole('button',{name:'Salvar dados',exact:true}).click();
   await page.getByRole('alert').filter({hasText:'Dados profissionais inválidos'}).waitFor();
   assert.equal(await field.inputValue(),'Rascunho Profissional Demonstrativo');
   row.actions.push('Profile422 stays visible and retains draft; payload contains no retired field');
   patchMode='delayed';
   await page.getByRole('button',{name:'Salvar dados',exact:true}).click();
   await page.waitForFunction(()=>Array.from(document.querySelectorAll('button')).some(b=>b.textContent?.trim()==='Salvando…'&&b.disabled));
   assert.equal(patchStarted,true);
   await field.fill('Rascunho Posterior Demonstrativo');
   releasePatch();
   await page.getByRole('alert').filter({hasText:'Falha de validação simulada após atraso.'}).waitFor();
   assert.equal(await field.inputValue(),'Rascunho Posterior Demonstrativo');
   row.actions.push('Delayed failure retains newer profile draft and restores save control');
   patchMode='success';
   await page.getByRole('button',{name:'Salvar dados',exact:true}).click();
   await page.waitForURL(url=>url.pathname==='/',{timeout:12000});await open();
   assert.equal(await field.inputValue(),'Rascunho Posterior Demonstrativo');
   assert.match(await page.getByAltText('Sua foto de perfil').getAttribute('src'),/qa-updated/);
   row.actions.push('Successful fixture save/reload retains professional data and manual photo');
   await field.scrollIntoViewIfNeeded();
   row.overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
   assert.equal(row.overflow,false);assert.equal(row.pageErrors.length,0);
   assert.equal(row.requests.some(request=>/instagram/i.test(request.path)),false);
   row.screenshot=`${out}/profile-${width}-${theme}.png`;
   await page.screenshot({path:row.screenshot});
  }catch(error){row.issues.push(String(error));}
  finally{
   releasePatch?.();
   row.unmodeled=fixture.unknown;await context.close();
   fs.writeFileSync(`${out}/report.json`,JSON.stringify({rows},null,2));console.log(JSON.stringify(row));
  }
 }
}finally{await browser.close();}
if(rows.some(row=>row.issues.length))process.exitCode=1;
