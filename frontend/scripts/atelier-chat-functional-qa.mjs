import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const base=new URL(process.env.ATELIER_QA_URL||'http://127.0.0.1:4322');
assert(['127.0.0.1','localhost'].includes(base.hostname)&&!base.username&&!base.password);
const out=path.resolve(process.env.ATELIER_QA_OUT||'/tmp/corvia-chat-functional');assert(out.startsWith('/tmp/'));fs.mkdirSync(out,{recursive:true});
assert(/^\/(?:private\/)?tmp\//.test(fs.realpathSync(out)));
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE||'playwright');
const browser=await chromium.launch({headless:true,channel:'chrome',args:['--disable-gpu']});
const rows=[],errors=[],requests=[];
let releaseHistory,releaseSend,delayHistory=false,delaySend=false,extraHistory=[];
const user={id:990192,email:'chat-audit@example.invalid',full_name:'Pessoa Fictícia',role:'admin',product_access:true,profile_completion_required:false,kyc_required:false,onboarding_pendente:false,boas_vindas_pendente:false};
const messages=id=>[{id:id+10,sender_id:id,recipient_id:user.id,body:id===990201?'Histórico fictício Alpha':'Histórico fictício Beta',created_at:'2026-09-11T12:00:00Z'},...extraHistory.filter(m=>m.sender_id===id)];
try{
 for(const width of (process.env.ATELIER_QA_WIDTHS||'1366,390').split(',').map(Number)){
  extraHistory=[];
  const context=await browser.newContext({viewport:{width,height:844},locale:'pt-BR',serviceWorkers:'block'});
  await context.addInitScript(()=>{window.WebSocket=class{static OPEN=1;readyState=1;constructor(){window.__qaSocket=this;}send(){}close(){this.readyState=3;}};});
  await context.route('**/*',async route=>{
   const req=route.request(),url=new URL(req.url());
   if(!url.pathname.startsWith('/api/'))return url.origin===base.origin&&['GET','HEAD'].includes(req.method())?route.continue():route.abort();
   requests.push({width,path:url.pathname,method:req.method()});
   const reply=(body,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
   if(url.pathname==='/api/auth/session-status')return reply({authenticated:true});
   if(url.pathname==='/api/auth/me')return reply(user);
   if(url.pathname==='/api/version')return reply({commit:'chat-isolated-qa'});
   if(url.pathname==='/api/chat/nao-lidas')return reply({total:2});
   if(url.pathname==='/api/chat/conversas')return reply([990201,990202].map((id,i)=>({user_id:id,full_name:`Conversa ${i?'Beta':'Alpha'}`,photo_url:null,ultima_mensagem:'Mensagem fictícia',ultima_em:'2026-09-11T12:00:00Z',de_mim:false,nao_lidas:1})));
   if(url.pathname==='/api/chat/suporte')return reply(null);
   if(url.pathname==='/api/chat/orgaos-de-classe')return reply(['CRM']);
   if(url.pathname==='/api/favorites/status')return reply({favorited:false,favorite_id:null,available:true});
   if(url.pathname==='/api/clinical-change-approvals/count')return reply({pending:0});
   if(/\/chat\/mensagens\/\d+\/marcar-lidas$/.test(url.pathname))return reply({ok:true});
   const id=Number(url.pathname.match(/\/chat\/mensagens\/(\d+)$/)?.[1]);
   if(id){
    if(req.method()==='GET'){
     if(id===990201&&delayHistory){delayHistory=false;await new Promise(resolve=>releaseHistory=resolve);}
     return reply(messages(id));
    }
    if(req.method()==='POST'){
     if(delaySend){delaySend=false;await new Promise(resolve=>releaseSend=resolve);}
     return reply({id:990301,sender_id:user.id,recipient_id:id,body:'Mensagem enviada fictícia',created_at:'2026-09-11T12:01:00Z'});
    }
   }
   return reply({detail:'Serviço indisponível no teste isolado.'},503);
  });
  const page=await context.newPage();page.setDefaultTimeout(12000);page.on('pageerror',e=>errors.push({width,message:String(e)}));
  const check=(name,pass,detail)=>rows.push({width,name,pass,detail});
  await page.goto(base.origin+'/privacidade',{waitUntil:'networkidle'});
  const launcher=page.locator('.corvia-chat-launch');await launcher.waitFor();
  check('unread badge',await launcher.innerText().then(t=>t.includes('2')));
  await launcher.click();const panel=page.locator('.corvia-chat-panel');await panel.waitFor();
  await panel.getByRole('button',{name:/Conversa Alpha/}).waitFor();
  delayHistory=true;await panel.getByRole('button',{name:/Conversa Alpha/}).click();
  while(!releaseHistory)await new Promise(r=>setTimeout(r,10));
  await panel.getByRole('button',{name:'Voltar',exact:true}).click();
  await panel.getByRole('button',{name:/Conversa Beta/}).click();
  await panel.locator('.corvia-chat-panel__message').filter({hasText:'Histórico fictício Beta'}).waitFor();
  releaseHistory();releaseHistory=null;
  await page.waitForLoadState('networkidle');
  check('late Alpha history cannot replace Beta',!(await panel.locator('.corvia-chat-panel__message').filter({hasText:'Histórico fictício Alpha'}).count())&&await panel.locator('.corvia-chat-panel__message').filter({hasText:'Histórico fictício Beta'}).isVisible());
  const input=panel.getByRole('textbox',{name:'Mensagem',exact:true});await input.fill('Rascunho Beta');
  delaySend=true;await panel.getByRole('button',{name:'Enviar',exact:true}).click();
  while(!releaseSend)await new Promise(r=>setTimeout(r,10));
  await panel.getByRole('button',{name:'Voltar',exact:true}).click();
  await panel.getByRole('button',{name:/Conversa Alpha/}).click();
  await panel.locator('.corvia-chat-panel__message').filter({hasText:'Histórico fictício Alpha'}).waitFor();
  await input.fill('Rascunho Alpha preservado');releaseSend();releaseSend=null;
  await page.waitForLoadState('networkidle');
  check('late Beta send cannot enter Alpha or erase its draft',!(await panel.locator('.corvia-chat-panel__message').filter({hasText:'Mensagem enviada fictícia'}).count())&&(await input.inputValue())==='Rascunho Alpha preservado');
  await panel.getByRole('button',{name:'Voltar',exact:true}).click();
  delayHistory=true;await panel.getByRole('button',{name:/Conversa Alpha/}).click();
  while(!releaseHistory)await new Promise(r=>setTimeout(r,10));
  await page.evaluate(()=>window.__qaSocket.onmessage({data:JSON.stringify({tipo:'mensagem',id:990500,sender_id:990201,recipient_id:990192,body:'Mensagem recebida durante histórico',created_at:'2026-09-11T12:01:30Z'})}));
  releaseHistory();releaseHistory=null;
  await page.waitForLoadState('networkidle');
  check('history response preserves a message arriving through the socket',await panel.locator('.corvia-chat-panel__message').filter({hasText:'Mensagem recebida durante histórico'}).isVisible());
  await page.screenshot({path:path.join(out,`chat-${width}.png`)});
  await input.focus();await page.keyboard.press('Escape');
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  check('Escape closes chat and restores launcher focus',!(await panel.isVisible())&&await launcher.evaluate(e=>e===document.activeElement));
  if(await panel.isVisible())await panel.getByRole('button',{name:'Fechar o chat'}).click();
  const readBefore=requests.filter(r=>r.width===width&&r.path.endsWith('/marcar-lidas')).length;
  await page.evaluate(()=>window.__qaSocket.onmessage({data:JSON.stringify({tipo:'mensagem',id:990501,sender_id:990201,recipient_id:990192,body:'Mensagem fictícia com chat minimizado',created_at:'2026-09-11T12:02:00Z'})}));
  await page.waitForLoadState('networkidle');
  check('minimized chat does not mark incoming messages as read',requests.filter(r=>r.width===width&&r.path.endsWith('/marcar-lidas')).length===readBefore);
  extraHistory.push({id:990501,sender_id:990201,recipient_id:990192,body:'Mensagem fictícia com chat minimizado',created_at:'2026-09-11T12:02:00Z'});
  await launcher.click();await page.waitForLoadState('networkidle');
  check('reopening conversation refreshes missed messages and keeps its draft',await panel.locator('.corvia-chat-panel__message').filter({hasText:'Mensagem fictícia com chat minimizado'}).isVisible()&&(await input.inputValue())==='Rascunho Alpha preservado'&&requests.filter(r=>r.width===width&&r.path.endsWith('/marcar-lidas')).length>readBefore);
  await context.close();console.log(JSON.stringify({width,checks:rows.filter(r=>r.width===width)}));
 }
}catch(e){rows.push({name:'test harness exception',pass:false,detail:String(e.stack||e)});}
finally{releaseHistory?.();releaseSend?.();await browser.close();fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({kind:'isolated-chat-state-and-keyboard-test',limitation:'HTTP fixtures and inert WebSocket; no actual messages, recipients or external operations.',rows,errors,requests},null,2));}
console.log(JSON.stringify({out,checks:rows.length,failures:rows.filter(r=>!r.pass).length,errors:errors.length}));process.exitCode=rows.some(r=>!r.pass)||errors.length?1:0;
