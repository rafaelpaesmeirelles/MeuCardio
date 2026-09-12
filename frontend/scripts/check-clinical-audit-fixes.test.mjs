import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer,{act} from 'react-test-renderer';
const require=createRequire(import.meta.url);
const read=file=>readFileSync(new URL(`../src/${file}`,import.meta.url),'utf8');
const compile=source=>ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX}}).outputText;
const inputs={exports:{}};vm.runInNewContext(compile(read('lib/clinicalInput.ts')),{module:inputs,exports:inputs.exports});
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
const visible=n=>typeof n==='string'||typeof n==='number'?String(n):Array.isArray(n)?n.map(visible).join(' '):n?visible(n.children):'';
const buttons=(r,text)=>r.root.findAllByType('button').filter(n=>visible(n).includes(text));
const click=async(r,text,index=0)=>act(async()=>{const b=buttons(r,text)[index];assert.ok(b,`Missing ${text}`);b.props.onClick();});
function component(file,api,route={}){
  const module={exports:{}};
  const browser={addEventListener:()=>{},removeEventListener:()=>{}};
  const navigate=()=>{};
  vm.runInNewContext(compile(read(file)),{module,exports:module.exports,Error,URLSearchParams,setTimeout,clearTimeout,console,
    document:browser,window:{...browser,setTimeout,clearTimeout},
    require:name=>name==='../lib/api'?{api,todasAsPaginas:()=>Promise.resolve([])}:name==='../lib/clinicalInput'?inputs.exports:name==='react-router-dom'?{Link:p=>React.createElement('a',p,p.children),useParams:()=>route,useLocation:()=>({pathname:'/receituario',search:route.search||'',state:null}),useNavigate:()=>navigate}:name==='../lib/auth'?{useAuth:()=>({usuario:{}})}:name.includes('Estado')?{Carregando:()=>React.createElement('p',null,'Carregando'),Erro:p=>React.createElement('p',{role:'alert'},p.mensagem),Vazio:()=>null}:name.startsWith('../components/')||name.startsWith('./')?{default:()=>null,__esModule:true}:require(name)});
  return module.exports.default;
}

test('clinical numeric inputs preserve decimal comma and reject invalid values rather than serializing null',()=>{
  assert.equal(inputs.exports.parseVitalSigns({temperatura:'36,5',spo2:'98'}).temperatura,36.5);
  for(const value of ['abc','Infinity','1e999','-1'])assert.throws(()=>inputs.exports.parseVitalSigns({fc:value}));
  assert.throws(()=>inputs.exports.parseVitalSigns({spo2:'101'}));
  assert.equal(inputs.exports.incompletePrescription([{drug_name:'Exemplo',presentation:'comprimido',posology:' '}]),true);
  assert.equal(inputs.exports.incompletePrescription([{drug_name:'Exemplo',presentation:'comprimido',posology:'Posologia fictícia'}]),false);
});

test('round discards delayed GET/POST suggestions after switching patients and shows initial load failures',async()=>{
  const patients=[1,2].map(id=>({id,initials:`P${id}`,record_number:`TESTE${id}`,problems:[],vital_signs:{},pending:[],medications:[]}));
  const oldGet=deferred(),oldPost=deferred();
  const suggestion=(id,text)=>({id,created_at:'2026-09-12T12:00:00Z',differential_diagnosis:text,suggested_workup:'',treatment_considerations:'',sources:[],sources_pubmed:[]});
  const C=component('pages/Round.tsx',{get:path=>path==='/round/patients'?Promise.resolve(patients):path.includes('/1/')?oldGet.promise:Promise.resolve([suggestion(2,'SUGESTAO PACIENTE B')]),post:()=>oldPost.promise});let r;
  try{
    await act(async()=>{r=TestRenderer.create(React.createElement(C));});await click(r,'Abrir',0);
    const ia=buttons(r,'Gerar sugestão').find(b=>b.props.onClick&&!b.props.disabled);assert.ok(ia);
    await act(async()=>{ia.props.onClick();});await click(r,'Abrir');
    await act(async()=>{oldGet.resolve([suggestion(1,'A GET ATRASADO')]);oldPost.resolve(suggestion(3,'A POST ATRASADO'));});
    assert.match(visible(r.toJSON()),/SUGESTAO PACIENTE B/);assert.doesNotMatch(visible(r.toJSON()),/A GET ATRASADO|A POST ATRASADO/);
  }finally{if(r)act(()=>r.unmount());}
  const Failure=component('pages/Round.tsx',{get:()=>Promise.reject(new Error('503 sintetico'))});
  try{await act(async()=>{r=TestRenderer.create(React.createElement(Failure));});assert.match(visible(r.toJSON()),/503 sintetico/);assert.equal(buttons(r,'Tentar novamente').length,1);}finally{if(r)act(()=>r.unmount());}
});

test('checklist locks fields during finalization and applies the canonical PATCH snapshot',async()=>{
  const request=deferred();let patches=0;
  const C=component('pages/ChecklistAlta.tsx',{get:()=>Promise.resolve({id:5,condicao:'DEMO',itens:[{id:'x',texto:'ITEM DEMO'}],marcados:[],observacoes:'',finalizado_em:null}),patch:()=>{patches++;return request.promise;}},{id:'5'});let r;
  try{
    await act(async()=>{r=TestRenderer.create(React.createElement(C));});await click(r,'Finalizar alta');
    assert.equal(r.root.findByType('textarea').props.disabled,true);assert.equal(r.root.findByType('input').props.disabled,true);
    await click(r,'Finalizar alta');assert.equal(patches,1);
    await act(async()=>request.resolve({id:5,marcados:['x'],observacoes:'CANONICO',finalizado_em:'2026-09-12T12:00:00Z',faltando_obrigatorios:0}));
    assert.equal(r.root.findByType('input').props.checked,true);assert.equal(r.root.findByType('textarea').props.value,'CANONICO');assert.equal(r.root.findByType('textarea').props.disabled,true);
  }finally{if(r)act(()=>r.unmount());}
});

test('agenda displays appointments despite failed auxiliary functions; old commitment requests are discarded',async()=>{
  const source=read('pages/Agenda.tsx');
  const load=source.slice(source.indexOf('  async function carregar()'),source.indexOf('  async function solicitarTesteGoogle()'));
  const state={};const ctx={api:{get:path=>path.includes('google-teste')?Promise.reject(new Error('503')):Promise.resolve(path.endsWith('/appointments')?[{id:77}]:[])},consultaAgenda:{current:0},withoutReservedSmokeTestRecords:x=>x,Error};
  for(const key of ['Agendamentos','Locais','Servicos','Integracoes','Capacidades','Mobilidade','Rotinas','Series','StatusTesteGoogle','Erro','ErrosAuxiliares'])ctx[`set${key}`]=value=>{state[key]=value;};
  vm.createContext(ctx);vm.runInContext(compile(load),ctx);await ctx.carregar();assert.equal(state.Agendamentos[0].id,77);assert.equal(state.ErrosAuxiliares.length,1);assert.equal(state.ErrosAuxiliares[0],'Conexão com Google');
  const old=deferred();const code=source.slice(source.indexOf('  async function carregarCompromissos('),source.indexOf('  async function atualizarAgenda()'));
  Object.assign(ctx,{consultaCompromissos:{current:0},referencia:'old',somaDias:v=>v,dataApi:v=>v,setCompromissos:v=>{state.compromissos=v;},api:{get:path=>path.includes('old')?old.promise:Promise.resolve([{id:2}])}});
  vm.runInContext(compile(code),ctx);const pending=ctx.carregarCompromissos('old');await ctx.carregarCompromissos('new');old.resolve([{id:1}]);await pending;assert(state.compromissos.every(x=>x.id===2));
});

test('multimodal datetime uses local offset at date boundaries',()=>{
  const source=read('components/PatientMultimodalAssistant.tsx');const helper=source.match(/function localDateTime[^\n]+/)[0];const ctx={Date};vm.createContext(ctx);vm.runInContext(compile(helper),ctx);
  for(const offset of [180,-330]){const date=new Date('2026-09-12T01:30:00Z');date.getTimezoneOffset=()=>offset;assert.equal(ctx.localDateTime(date),new Date(date.getTime()-offset*60000).toISOString().slice(0,16));}
});

test('receituario resolves profile and encounter context, exposes named fields, and links only on explicit action',async()=>{
  const calls=[];
  const C=component('pages/Receituario.tsx',{
    get:path=>Promise.resolve(path==='/pacientes/901'?{id:901,full_name:'PACIENTE SINTETICO DEMO',cpf:'00000000000',endereco:{logradouro:'RUA DEMO'}}:path==='/pacientes/901/atendimentos/902'?{id:902,status:'draft'}:[]),
    post:(path,payload)=>{calls.push({path,payload});return Promise.resolve({prescricao_id:55,documentos:[],exige_revisao:true});},
  },{search:'?paciente=901&atendimento=902'});let r;
  try{
    await act(async()=>{r=TestRenderer.create(React.createElement(C));});
    const fields=r.root.findAllByType('input');assert.ok(fields.some(f=>f.props.value==='PACIENTE SINTETICO DEMO'));assert.ok(fields.some(f=>f.props.value==='00000000000'));assert.ok(fields.some(f=>f.props.value==='RUA DEMO'));
    const labels=r.root.findAllByType('label').filter(l=>l.props.htmlFor);
    assert(labels.length>=15);
    for(const label of labels)assert.equal(r.root.findAll(n=>['input','select','textarea'].includes(n.type)&&n.props.id===label.props.htmlFor).length,1);
    await act(async()=>fields.find(f=>f.props.placeholder==='Digite o nome genérico ou comercial').props.onChange({target:{value:'Medicamento sintético'}}));
    await click(r,'Criar receituário');assert.equal(calls.length,1);assert.equal(calls[0].payload.patient_id,undefined);assert.equal(calls[0].payload.destinatario.nome,'PACIENTE SINTETICO DEMO');
    await click(r,'Vincular esta receita');assert.equal(calls[1].path,'/pacientes/901/atendimentos/902/artefatos');assert.equal(calls[1].payload.artifact_id,55);
  }finally{if(r)act(()=>r.unmount());}
});
