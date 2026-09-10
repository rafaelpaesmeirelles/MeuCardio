import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import React from 'react';
import TestRenderer from 'react-test-renderer';
import { MemoryRouter } from 'react-router-dom';
import ts from 'typescript';
const { act }=TestRenderer;
const root=fileURLToPath(new URL('../',import.meta.url));
const temp=await mkdtemp(path.join(tmpdir(),'corvia-approval-ui-'));
await symlink(path.join(root,'node_modules'),path.join(temp,'node_modules'));
after(()=>rm(temp,{recursive:true,force:true}));
const compile=source=>ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ES2022,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX}}).outputText;
let source=await readFile(path.join(root,'src/pages/AdminClinicalChanges.tsx'),'utf8');
source=source.replace('import { api, ApiError } from "../lib/api";','const api={get:(...args)=>globalThis.approvalFixture.get(...args),post:(...args)=>globalThis.approvalFixture.post(...args)}; export class ApiError extends Error { constructor(public status:number,message:string){super(message)} }');
source=source.replace('import { useAuth } from "../lib/auth";','const useAuth=()=>({usuario:globalThis.approvalFixture.user});').replace(/import "\.\.\/styles\/[^"]+";/g,'');
await writeFile(path.join(temp,'Approval.mjs'),compile(source));
const {default:Approval,ApiError}=await import(pathToFileURL(path.join(temp,'Approval.mjs')));
let notice=await readFile(path.join(root,'src/components/ClinicalChangeApprovalNotice.tsx'),'utf8');
notice=notice.replace('import { api, ApiError } from "../lib/api";','import { ApiError } from "./Approval.mjs"; const api={get:(...args)=>globalThis.approvalFixture.get(...args)};').replace('import { useAuth } from "../lib/auth";','const useAuth=()=>({usuario:globalThis.approvalFixture.user});');
await writeFile(path.join(temp,'Notice.mjs'),compile(notice));
const {default:Notice}=await import(pathToFileURL(path.join(temp,'Notice.mjs')));

let registry=await readFile(path.join(root,'src/lib/clinicalRouteRegistry.ts'),'utf8');
registry=registry.replace('import { heartTeamEnabled, whatsappAssistantEnabled } from "./aiFeatureFlags";','const heartTeamEnabled=()=>false; const whatsappAssistantEnabled=()=>false;');
await writeFile(path.join(temp,'registry.mjs'),compile(registry));
const {CLINICAL_ROUTES}=await import(pathToFileURL(path.join(temp,'registry.mjs')));
let favorite=await readFile(path.join(root,'src/components/FavoriteFunctionControl.tsx'),'utf8');
favorite=favorite.replace('"../lib/clinicalRouteRegistry"','"./registry.mjs"').replace('import BotaoFavorito from "./BotaoFavorito";','const BotaoFavorito=(props:any)=><button data-slug={props.itemSlug} data-type={props.itemType}>{props.label}</button>;');
await writeFile(path.join(temp,'Function.mjs'),compile(favorite));
const {default:FunctionControl,favoriteFunctionSlug}=await import(pathToFileURL(path.join(temp,'Function.mjs')));
const text=node=>typeof node==='string'?node:(node?.children??[]).map(text).join('');
const button=(renderer,label)=>renderer.root.findAllByType('button').find(item=>text(item).includes(label));
const proposal=(overrides={})=>({id:12,version:3,status:'pending',created_at:'2026-09-10T12:00:00Z',guideline:{id:2,slug:'test',title:'Publicação para revisão',url:'https://example.org/publication'},proposed_changes:[{item_type:'doenca',item_id:5,label:'Fibrilação atrial',before_text:'Conduta atual',after_text:'Conduta proposta',change_summary_pt:'Nova evidência',before:'Conduta atual',after:'Conduta proposta',source_url:'https://example.org/source'}],...overrides});
function setup(overrides={}){globalThis.window=new EventTarget();const calls=[];globalThis.approvalFixture={user:{id:1,role:'admin'},get:async url=>{calls.push(['get',url]);return url.includes('?')?{items:[proposal()],total:1}:proposal()},post:async(...args)=>{calls.push(['post',...args]);return proposal({status:args[0].endsWith('approve')?'approved':'rejected',reviewed_at:'2026-09-10T13:00:00Z',reviewer_name:'Administrador responsável'})},...overrides};return calls;}
async function mount(t){let renderer;await act(async()=>{renderer=TestRenderer.create(React.createElement(Approval))});t.after(async()=>{await act(async()=>renderer.unmount())});return renderer;}
async function open(renderer){await act(async()=>button(renderer,'Fibrilação atrial').props.onClick());}
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject}};

test('approval requires detail, explicit consent and submits the inspected version once',async t=>{
 const pending=deferred();const calls=setup({post:(...args)=>{calls.push(['post',...args]);return pending.promise}});const r=await mount(t);
 assert.equal(calls.filter(x=>x[0]==='post').length,0);await open(r);
 assert.match(text(r.toJSON()),/Conduta atual/);assert.match(text(r.toJSON()),/Conduta proposta/);
 assert.equal(r.root.findByType('input').props.checked,false);assert.equal(button(r,'Aprovar e aplicar').props.disabled,true);
 await act(async()=>r.root.findByType('input').props.onChange({target:{checked:true}}));
 const click=button(r,'Aprovar e aplicar').props.onClick;await act(async()=>{click();click()});
 assert.equal(calls.filter(x=>x[0]==='post').length,1);assert.deepEqual(calls.find(x=>x[0]==='post').slice(1),['/clinical-change-approvals/12/approve',{expected_version:3}]);
 await act(async()=>pending.resolve(proposal({status:'approved',reviewed_at:'2026-09-10T13:00:00Z',reviewer_name:'Responsável'})));
 assert.match(text(r.toJSON()),/Mudanças aprovadas e aplicadas/);assert.equal(button(r,'Aprovar e aplicar'),undefined);
});

test('rejection requires an explicit reason and preserves false approval consent',async t=>{
 const calls=setup();const r=await mount(t);await open(r);assert.equal(button(r,'Rejeitar proposta').props.disabled,true);
 await act(async()=>r.root.findByType('textarea').props.onChange({target:{value:' Evidência insuficiente '}}));
 assert.equal(r.root.findByType('input').props.checked,false);await act(async()=>button(r,'Rejeitar proposta').props.onClick());
 assert.deepEqual(calls.find(x=>x[0]==='post').slice(1),['/clinical-change-approvals/12/reject',{expected_version:3,reason:'Evidência insuficiente'}]);
});

test('CAS conflict blocks decisions until detail reload and fresh explicit consent',async t=>{
 let version=3;const calls=setup({get:async url=>url.includes('?')?{items:[proposal()],total:1}:proposal({version}),post:async(...args)=>{calls.push(['post',...args]);throw new ApiError(409,'changed')}});const r=await mount(t);await open(r);
 await act(async()=>r.root.findByType('input').props.onChange({target:{checked:true}}));await act(async()=>button(r,'Aprovar e aplicar').props.onClick());
 assert.equal(button(r,'Aprovar e aplicar').props.disabled,true);assert.equal(r.root.findByType('input').props.checked,false);assert.match(text(r.toJSON()),/mudou durante a revisão/);
 version=4;await act(async()=>button(r,'Recarregar proposta').props.onClick());assert.equal(r.root.findByType('input').props.checked,false);
 await act(async()=>r.root.findByType('input').props.onChange({target:{checked:true}}));await act(async()=>button(r,'Aprovar e aplicar').props.onClick());assert.equal(calls.filter(x=>x[0]==='post').at(-1)[2].expected_version,4);
});

test('stale pending list cannot replace the selected rejected category',async t=>{
 const old=deferred();setup({get:async url=>url.includes('status=pending')?old.promise:{items:[proposal({status:'rejected',guideline:{id:2,slug:'rejected',title:'Proposta rejeitada'}})],total:1}});const r=await mount(t);
 await act(async()=>button(r,'Rejeitadas').props.onClick());await act(async()=>old.resolve({items:[proposal()],total:1}));assert.match(text(r.toJSON()),/Proposta rejeitada/);assert.doesNotMatch(text(r.toJSON()),/Publicação para revisão/);
});

test('non-admin makes no requests and owner-only refusal is explained',async t=>{
 const calls=setup({user:{id:2,role:'medico'}});const r=await mount(t);assert.equal(calls.length,0);assert.match(text(r.toJSON()),/Acesso restrito/);
 globalThis.approvalFixture.user={id:3,role:'admin'};globalThis.approvalFixture.get=async()=>{throw new ApiError(403,'owner only')};await act(async()=>r.update(React.createElement(Approval)));assert.match(text(r.toJSON()),/administrador responsável/);
});

test('canonical favorite function targets exactly match backend registry, excluding every dynamic/admin route',async()=>{
 const expected=JSON.parse(await readFile(path.join(root,'../backend/app/data/favorite_functions.json'),'utf8')).entries.map(x=>x.slug).sort();
 const actual=CLINICAL_ROUTES.map(favoriteFunctionSlug).filter(Boolean).sort();assert.deepEqual(actual,expected);assert.equal(actual.length,44);
 for(const path of ['/admin','/admin/mudancas-clinicas','/doencas/:slug','/heart-team/:caseId','/ecg-ia','/','/favoritos']) assert.equal(favoriteFunctionSlug(CLINICAL_ROUTES.find(x=>x.path===path)),null);
});

test('function favorite follows canonical route once and never favorites query or private detail identity',async t=>{
 let r;await act(async()=>{r=TestRenderer.create(React.createElement(MemoryRouter,{initialEntries:['/trilhas/timeline?tema=fibrilacao-atrial'],future:{v7_startTransition:true,v7_relativeSplatPath:true}},React.createElement(FunctionControl)))});t.after(()=>r.unmount());
 const buttons=r.root.findAllByType('button');assert.equal(buttons.length,1);assert.equal(buttons[0].props['data-type'],'funcao');assert.equal(buttons[0].props['data-slug'],'trilhas-timeline');
});


test('owner notice uses only count and clears on permission/account change without leaking stale counts',async t=>{
 globalThis.document=new EventTarget();globalThis.document.visibilityState='visible';
 const old=deferred();const calls=setup({get:url=>{calls.push(['get',url]);return old.promise}});
 const view=()=>React.createElement(MemoryRouter,{future:{v7_startTransition:true,v7_relativeSplatPath:true}},React.createElement(Notice));
 let r;await act(async()=>{r=TestRenderer.create(view())});t.after(async()=>{await act(async()=>r.unmount())});
 assert.deepEqual(calls,[['get','/clinical-change-approvals/count']]);
 globalThis.approvalFixture.user={id:2,role:'admin'};globalThis.approvalFixture.get=async()=>{throw new ApiError(403,'owner-only')};
 await act(async()=>r.update(view()));await act(async()=>old.resolve({pending:42}));assert.equal(r.toJSON(),null);
 globalThis.approvalFixture.user={id:1,role:'admin'};globalThis.approvalFixture.get=async()=>({pending:3});await act(async()=>r.update(view()));assert.match(text(r.toJSON()),/3 mudanças de conduta aguardam sua aprovação/);
 globalThis.approvalFixture.user={id:3,role:'medico'};globalThis.approvalFixture.get=async()=>{throw Error('must not query')};await act(async()=>r.update(view()));assert.equal(r.toJSON(),null);
});

test('clinical comparison renders changed Markdown fields and makes inconclusive verification explicit',async t=>{
 const item=proposal({verification_status:'needs_verification',proposed_changes:[{item_type:'doenca',item_id:5,label:'Fibrilação atrial',before:{body_md:'Conduta **atual**',source_tier:'INTERNAL_UNCHANGED'},after:{body_md:'Conduta **nova**',source_tier:'INTERNAL_UNCHANGED'},changed_fields:['body_md'],effect_kind:'clinical_content',change_summary_pt:'Nova evidência',source_url:'javascript:alert(1)'}]});
 setup({get:async url=>url.includes('?')?{items:[item],total:1}:item});const r=await mount(t);await open(r);
 assert.match(text(r.toJSON()),/inconclusiva/);assert.doesNotMatch(text(r.toJSON()),/INTERNAL_UNCHANGED/);assert.ok(r.root.findAllByType('strong').some(node=>text(node)==='nova'));assert.equal(r.root.findAllByType('a').filter(node=>String(node.props.href).startsWith('javascript:')).length,0);
});


test('changing administrators remounts the review workspace before a new owner request resolves',async t=>{
 setup();const r=await mount(t);await open(r);assert.match(text(r.toJSON()),/Conduta atual/);
 const next=deferred();globalThis.approvalFixture.user={id:2,role:'admin'};globalThis.approvalFixture.get=()=>next.promise;
 await act(async()=>r.update(React.createElement(Approval)));assert.doesNotMatch(text(r.toJSON()),/Conduta atual|Fibrilação atrial|Publicação para revisão/);assert.match(text(r.toJSON()),/Carregando propostas/);
 await act(async()=>next.reject(new ApiError(403,'owner only')));assert.match(text(r.toJSON()),/administrador responsável/);
});


test('an unconfirmed suggestion explains its block, prevents approval even through the handler, and permits rejection',async t=>{
 const item=proposal({can_approve:false,blocking_reason:'O alvo desta sugestão não foi confirmado.',proposed_changes:[{...proposal().proposed_changes[0],impact_scope:{}}]});
 const calls=setup({get:async url=>url.includes('?')?{items:[item],total:1}:item});const r=await mount(t);await open(r);
 assert.match(text(r.toJSON()),/O alvo desta sugestão não foi confirmado/);assert.equal(r.root.findByType('input').props.disabled,true);assert.equal(button(r,'Aprovar e aplicar').props.disabled,true);
 await act(async()=>r.root.findByType('input').props.onChange({target:{checked:true}}));await act(async()=>button(r,'Aprovar e aplicar').props.onClick());assert.equal(calls.filter(x=>x[0]==='post').length,0);
 await act(async()=>r.root.findByType('textarea').props.onChange({target:{value:'Alvo não confirmado'}}));assert.equal(button(r,'Rejeitar proposta').props.disabled,false);await act(async()=>button(r,'Rejeitar proposta').props.onClick());assert.deepEqual(calls.find(x=>x[0]==='post').slice(1),['/clinical-change-approvals/12/reject',{expected_version:3,reason:'Alvo não confirmado'}]);
});
