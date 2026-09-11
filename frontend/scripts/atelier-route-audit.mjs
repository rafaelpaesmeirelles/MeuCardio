import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';

// Exhaustive route discovery and rendering/error-state audit. This is not a
// backend, clinical-content or end-to-end functional certification. Companion
// module suites exercise populated fixtures and their interactive workflows.
const base = new URL(process.env.ATELIER_QA_URL || 'http://127.0.0.1:4322');
assert(['localhost', '127.0.0.1'].includes(base.hostname) && !base.username && !base.password);
const out = path.resolve(process.env.ATELIER_QA_OUT || '/tmp/corvia-route-audit');
assert(out.startsWith('/tmp/'));
fs.mkdirSync(out, { recursive: true });
assert(/^\/(?:private\/)?tmp\//.test(fs.realpathSync(out)));
const source = fs.readFileSync('src/lib/clinicalRouteRegistry.ts', 'utf8');
const field = (body, name) => body.match(new RegExp(`(?:^|[,\\s])${name}:\\s*"([^"]*)"`))?.[1];
const routes = [...source.matchAll(/route\(\{([\s\S]*?)\}\)/g)].map(([, body]) => ({
  path: field(body, 'path'), name: field(body, 'name'), space: field(body, 'space'),
  kind: field(body, 'kind') || 'page', gate: field(body, 'gate') || null,
  redirectTo: field(body, 'redirectTo') || null,
}));
assert.equal(routes.length, 78, 'Update the deliberate inventory if product routes change');
const filter = process.env.ATELIER_QA_ROUTES?.split(',');
const targets = filter ? routes.filter(r => filter.includes(r.path)) : routes;
const themes = (process.env.ATELIER_QA_THEMES || 'light,dark').split(',');
const widths = (process.env.ATELIER_QA_WIDTHS || '1366,390').split(',').map(Number);
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser = await chromium.launch({ headless: true, channel: 'chrome', args: ['--disable-gpu'] });
const rows = [], failures = [], errors = [], requests = [], blocked = [];
let active = {};
const profile = { id: 990191, email: 'route-audit@example.invalid', full_name: 'Pessoa Fictícia — Auditoria Local', professional_title: 'Dr.', role: 'admin', product_access: true, profile_completion_required: false, kyc_required: false, onboarding_pendente: false, boas_vindas_pendente: false, investidor: false };
// Retain the contracts/provenance of the existing empty-state audit instead of
// guessing response shapes for arbitrary endpoints. Unknown endpoints fail.
const previous = fs.readFileSync('scripts/atelier-local-qa.mjs', 'utf8');
const emptyKeys = name => [...(previous.match(new RegExp(`const ${name} = new Map\\(\\[([\\s\\S]*?)\\]\\);`))?.[1] || '').matchAll(/\['([^']+)'/g)].map(m => m[1]);
const collections = new Set(emptyKeys('emptyCollections'));
const pages = new Set(emptyKeys('emptyPages'));
const isolatedMessage = 'Serviço indisponível no teste isolado — nenhum dado de produção foi consultado.';
const save = () => fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify({
  kind: 'all-authenticated-routes-rendering-audit', limitation: 'Local React, empty and unavailable service contracts. Not a functional/backend/corpus certification. No real identities, patient data or external operations.',
  inventory: routes, rows, failures, errors, requests, blocked,
}, null, 2));

async function metrics(page) {
  return page.evaluate(() => {
    const visible = e => { const r=e.getBoundingClientRect(),s=getComputedStyle(e); return r.width>0 && r.height>0 && s.visibility!=='hidden' && s.display!=='none'; };
    const root=document.querySelector('#conteudo-principal,.atelier-home,.cst--atelier') || document.body;
    const text=e=>(e.innerText||e.getAttribute('aria-label')||e.getAttribute('placeholder')||'').trim().replace(/\s+/g,' ').slice(0,140);
    const info=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {tag:e.tagName,cls:e.className?.baseVal??e.className,text:text(e),font:parseFloat(s.fontSize),fg:s.color,bg:s.backgroundColor,x:r.x,y:r.y,w:r.width,h:r.height,sw:e.scrollWidth,cw:e.clientWidth};};
    const controls=[...root.querySelectorAll('button,a,input,select,textarea')].filter(visible);
    const painted=controls.filter(e=>{const r=e.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth;});
    const scrollables=[...root.querySelectorAll('*'),root].filter(e=>{const s=getComputedStyle(e);return /(auto|scroll)/.test(s.overflowY)&&e.scrollHeight>e.clientHeight+3;}).map(e=>({tag:e.tagName,cls:e.className,height:e.clientHeight,scrollHeight:e.scrollHeight}));
    return {
      viewport:[innerWidth,innerHeight],theme:document.documentElement.dataset.corviaTheme,
      title:document.title,design:document.documentElement.dataset.corviaDesign,
      rootTextLength:root.innerText.length,contentExcerpt:root.innerText.slice(0,450),
      documentOverflow:Math.max(document.body.scrollWidth,document.documentElement.scrollWidth)-innerWidth,
      rootOverflow:root.scrollWidth-root.clientWidth,
      headings:[...root.querySelectorAll('h1,h2,h3')].filter(visible).map(info).slice(0,20),
      smallControls:painted.filter(e=>{const r=e.getBoundingClientRect();return r.width<43.5||r.height<43.5;}).map(info).slice(0,35),
      tinyText:[...root.querySelectorAll('p,label,button,a,small')].filter(visible).filter(e=>text(e)&&parseFloat(getComputedStyle(e).fontSize)<12).map(info).slice(0,20),
      clippingCandidates:controls.filter(e=>e.scrollWidth>e.clientWidth+3&&!['INPUT','TEXTAREA','SELECT'].includes(e.tagName)).map(info).slice(0,25),
      outsideViewport:painted.filter(e=>{const r=e.getBoundingClientRect();return r.x<-2||r.right>innerWidth+2;}).map(info).slice(0,15),
      brokenImages:[...document.images].filter(e=>visible(e)&&e.complete&&e.naturalWidth===0).map(e=>({alt:e.alt,path:new URL(e.currentSrc||e.src,location.href).pathname})),
      nestedInteractive:root.querySelectorAll('button button,button a,a button').length,
      alerts:[...root.querySelectorAll('[role="alert"],[role="status"]')].filter(visible).map(text),
      scrollables,
    };
  });
}
try {
  for (const theme of themes) {
    const context=await browser.newContext({viewport:{width:widths[0],height:900},locale:'pt-BR',serviceWorkers:'block',reducedMotion:'reduce'});
    await context.addInitScript(({theme,id})=>{
      localStorage.setItem(`corvia:cardiology-spaces:theme:v1:${id}`,theme);
      Object.defineProperty(navigator,'geolocation',{value:{getCurrentPosition(_ok,bad){bad?.({code:1,message:'Geolocalização desabilitada no teste isolado'});},watchPosition(){throw Error('Geolocation forbidden in route audit');}}});
    },{theme,id:profile.id});
    await context.route('**/*',async route=>{
      const req=route.request(),url=new URL(req.url());
      if(!url.pathname.startsWith('/api/')){
        if(url.origin===base.origin&&['GET','HEAD'].includes(req.method()))return route.continue();
        blocked.push({...active,origin:url.origin,path:url.pathname,method:req.method()});return route.abort();
      }
      const entry={...active,path:url.pathname,method:req.method()}; requests.push(entry);
      const reply=(body,status=200,fixture='contract-empty')=>{Object.assign(entry,{status,fixture});return route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});};
      if(req.method()==='GET'){
        if(url.pathname==='/api/auth/session-status')return reply({authenticated:true},200,'synthetic-session');
        if(url.pathname==='/api/auth/me')return reply(profile,200,'synthetic-profile');
        if(url.pathname==='/api/version')return reply({commit:'route-audit-isolated'},200,'synthetic-version');
        if(url.pathname==='/api/billing/status')return reply({status:'active',plano:'completo',current_period_end:null,entitlements:{ai:true,mail:true,tudo_com_tudo:true,source:'isolated-test',commercial_version:null}},200,'synthetic-entitlements');
        if(collections.has(url.pathname))return reply([]);
        if(pages.has(url.pathname))return reply({items:[],total:0,limit:50,offset:0,has_more:false,next_offset:null});
        if(url.pathname==='/api/library/catalog')return reply({total:0,fronts:[]});
        if(url.pathname==='/api/library/area-counts')return reply({areas:[]});
        if(url.pathname==='/api/admin/usuarios')return reply({items:[],page:1,page_size:25,total:0,has_more:false});
        if(url.pathname==='/api/agenda/mobility/day-context')return reply({stage:'no_commitments',first_target:null,last_target:null,start_location:null,end_location:null});
        if(url.pathname==='/api/agenda/mobility/next-target')return reply(null);
        if(url.pathname==='/api/agenda/mobility/preferences')return reply({enabled:false,traffic_configured:false});
        if(url.pathname==='/api/agenda/mobility/map-config')return reply({configured:false});
        if(url.pathname==='/api/favorites/status')return reply({favorited:false,available:true});
        if(url.pathname==='/api/clinical-change-approvals/count')return reply({pending:0});
      }
      return reply({detail:isolatedMessage},503,'intentional-unavailable');
    });
    const page=await context.newPage();page.setDefaultTimeout(12000);page.setDefaultNavigationTimeout(30000);
    page.on('pageerror',e=>errors.push({...active,message:String(e)}));
    for(const target of targets){
      const concrete=target.path.replace(/:slug/g,'qa-item-ausente').replace(/:(id|caseId)/g,'990991');
      active={route:target.path,theme};const errorStart=errors.length,requestStart=requests.length;
      try{
        await page.setViewportSize({width:widths[0],height:900});
        await page.goto(base.origin+concrete,{waitUntil:'domcontentloaded'});
        await page.waitForFunction(()=>!['Abrindo a Corvia…','Carregando a tela…'].some(t=>document.body.innerText.trim()===t)&&document.body.innerText.length>40);
        await page.waitForLoadState('networkidle',{timeout:12000}).catch(()=>{});
        for(const width of widths){
          active={route:target.path,theme,width};await page.setViewportSize({width,height:width>700?900:844});
          await page.evaluate(async()=>{await document.fonts.ready;await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));window.scrollTo(0,0);});
          const data=await metrics(page);
          const stem=target.path.replace(/[^a-z0-9]+/gi,'-').replace(/^-|-$/g,'')||'home';
          const screenshot=`${stem}-${theme}-${width}.png`;
          await page.screenshot({path:path.join(out,screenshot),fullPage:false});
          const row={...active,name:target.name,kind:target.kind,resolvedPath:new URL(page.url()).pathname,state:'rendering-error-or-empty-only',metrics:data,screenshot,pageerrors:errors.slice(errorStart),api:requests.slice(requestStart).map(({path,method,status,fixture})=>({path,method,status,fixture}))};rows.push(row);
          if(data.documentOverflow>2)failures.push({...active,kind:'document-overflow',pixels:data.documentOverflow});
          if(data.brokenImages.length)failures.push({...active,kind:'broken-images',images:data.brokenImages});
          if(data.nestedInteractive)failures.push({...active,kind:'nested-interactive',count:data.nestedInteractive});
          if(data.rootTextLength<20)failures.push({...active,kind:'blank-content'});
          if(row.pageerrors.length)failures.push({...active,kind:'javascript-error',errors:row.pageerrors});
        }
        console.log(JSON.stringify({theme,route:target.path,rows:rows.length,failures:failures.length}));
      }catch(error){failures.push({...active,kind:'audit-exception',error:String(error)});console.log(JSON.stringify({...active,error:String(error)}));}
      save();
    }
    await context.close();
  }
}finally{save();await browser.close();}
console.log(JSON.stringify({out,inventory:routes.length,rows:rows.length,failures:failures.length,errors:errors.length}));
process.exitCode=failures.length?1:0;
