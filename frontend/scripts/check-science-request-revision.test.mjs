import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { stripTypeScriptTypes } from "node:module";
import test from "node:test";
import vm from "node:vm";
import React from "react";
import TestRenderer, { act } from "react-test-renderer";

const read = (path) => readFileSync(new URL(`../src/${path}`, import.meta.url), "utf8");
const load = async (path) => import(`data:text/javascript;base64,${Buffer.from(stripTypeScriptTypes(read(path))).toString("base64")}`);
const { createRequestRevision } = await load("lib/requestRevision.ts");
const { validateCalculatorFields, calculatorFieldRequired } = await load("lib/calculatorValidation.ts");
const settle = () => new Promise(resolve => setImmediate(resolve));
const extract = (source, start) => {
  const from = source.indexOf(start);
  assert.notEqual(from, -1, start);
  const to = source.indexOf("\n  }", from);
  assert.notEqual(to, -1);
  return source.slice(from, to + 4);
};

test("Hook cancela imediatamente ao mudar identidade e ao desmontar", () => {
  const hookCode = stripTypeScriptTypes(read("lib/useRequestRevision.ts").replace(/^import .*;\s*$/gm, "").replace("export function", "function"));
  const scope = vm.createContext({ useRef: React.useRef, useEffect: React.useEffect, createRequestRevision });
  vm.runInContext(hookCode, scope);
  let guard;
  function Probe({ identity }) { guard = scope.useRequestRevision(identity); return null; }
  let renderer;
  act(() => { renderer = TestRenderer.create(React.createElement(Probe, { identity: "A" })); });
  const old = guard.begin();
  act(() => renderer.update(React.createElement(Probe, { identity: "B" })));
  assert.equal(old(), false);
  const latest = guard.begin();
  assert.equal(latest(), true);
  act(() => renderer.unmount());
  assert.equal(latest(), false);
});

for (const [page, functionName] of [["GuiaDoenca", "assess"], ["TriagemSintomas", "assess"], ["Interacoes", "checar"], ["Condicoes", "checar"], ["MedicamentosClinicalCommand", "visualizar"], ["MedicamentosClinicalCommand", "comparar"]]) {
  function environment() {
    const pending = [], state = { busy: false, error: "", result: null };
    const guard = createRequestRevision();
    const start = (...args) => new Promise((resolve, reject) => pending.push({ args, resolve, reject }));
    const scope = vm.createContext({
      assessmentRequests: guard, checkRequests: guard, insightRequests: guard,
      api: { get: start, post: start }, ApiError: Error, Error,
      disease: { slug: "demo" }, detail: { slug: "demo" }, slug: "demo", selectedSlug: "demo",
      selecionados: ["demo-A", "demo-B"], escolhidos: ["demo-A", "demo-B"], farmacos: ["demo-A"], condicoes: ["demo-C"], context: "ambulatorio", answers: {},
      setAssessing: value => state.busy = value, setChecando: value => state.busy = value, setCarregando: value => state.busy = value,
      setError: value => state.error = value, setErro: value => state.error = value,
      setAssessment: value => state.result = value, setResultado: value => state.result = value,
      setDetalhe: value => state.result = value, setComparacao: value => state.result = value,
      requestAnimationFrame: cb => cb(), document: { getElementById: () => null },
    });
    const source = extract(read(`pages/${page}.tsx`), `  async function ${functionName}(`);
    vm.runInContext(stripTypeScriptTypes(source), scope);
    return { pending, state, guard, start: () => scope[functionName]("demo") };
  }
  test(`${page}/${functionName}: resposta antiga não substitui a atual`, async () => {
    const env = environment();
    const first = env.start(), second = env.start();
    env.pending[1].resolve({ id: "novo" }); await second;
    env.pending[0].resolve({ id: "antigo" }); await first;
    assert.equal(env.state.result.id, "novo");
    assert.equal(env.state.busy, false);
  });
  test(`${page}/${functionName}: erro/finalização antiga não encerra nova requisição`, async () => {
    const env = environment();
    const first = env.start(), second = env.start();
    env.pending[0].reject(new Error("obsoleto")); await first;
    assert.equal(env.state.error, ""); assert.equal(env.state.busy, true);
    env.guard.invalidate(); // entrada alterada ou componente desmontado
    env.pending[1].resolve({ id: "também obsoleto" }); await second;
    assert.equal(env.state.result, null);
  });
}

for (const [page, setter] of [["Exame", "setT"], ["ImagemGaleria", "setImg"]]) {
  test(`${page}: troca de slug limpa detalhe/erro e descarta resposta anterior`, async () => {
    const source = read(`pages/${page}.tsx`);
    const begin = source.indexOf("  useEffect(() => {");
    const end = source.indexOf("  }, [slug, detailRequests]);", begin) + "  }, [slug, detailRequests]);".length;
    const pending = [], state = { detail: "old", error: "old" }, guard = createRequestRevision();
    let cleanup;
    const scope = vm.createContext({ slug: "A", detailRequests: guard, ApiError: Error,
      useEffect: cb => { cleanup = cb(); },
      [setter]: value => state.detail = value, setErro: value => state.error = value,
      api: { get: () => new Promise((resolve, reject) => pending.push({ resolve, reject })) },
    });
    const effect = stripTypeScriptTypes(source.slice(begin,end));
    vm.runInContext(effect,scope);
    assert.equal(state.detail,null); assert.equal(state.error,"");
    cleanup(); scope.slug = "B"; vm.runInContext(effect,scope);
    pending[1].resolve({slug:"B"}); await settle();
    pending[0].reject(new Error("antigo")); await settle();
    assert.equal(state.detail.slug,"B"); assert.equal(state.error,"");
  });
}

test("Exportação: resposta de busca anterior é descartada após mudança do filtro", async () => {
  const source = read("pages/ExportarConteudo.tsx");
  const begin = source.lastIndexOf("  useEffect(() => {",source.indexOf("const isCurrent = catalogRequests.begin()"));
  const marker = "  }, [busca, tipo, catalogRequests]);";
  const end = source.indexOf(marker,begin) + marker.length;
  const pending = [], timers = [], state = {}, guard = createRequestRevision(); let cleanup;
  const scope = vm.createContext({ busca:"A",tipo:"",catalogRequests:guard,URLSearchParams,ApiError:Error,
    useEffect: cb => {cleanup=cb()}, window:{setTimeout:cb=>{timers.push(cb);return timers.length},clearTimeout:()=>{}},
    setCarregando:v=>state.busy=v,setErro:v=>state.error=v,setCatalogo:v=>state.catalog=v,
    api:{get:()=>new Promise((resolve,reject)=>pending.push({resolve,reject}))},
  });
  const effect=stripTypeScriptTypes(source.slice(begin,end));
  vm.runInContext(effect,scope);timers.shift()();
  cleanup();scope.busca="B";vm.runInContext(effect,scope);timers.shift()();
  pending[1].resolve({itens:["B"]});await settle();
  pending[0].resolve({itens:["A"]});await settle();
  assert.deepEqual(state.catalog.itens,["B"]);assert.equal(state.busy,false);
});

test("Calculadora: valida limites/finitude/tipos e obrigatoriedade condicional", () => {
  const fields=[{name:"qt",label:"QT",type:"number",required:true,min:1,max:900},{name:"formula",label:"Fórmula",type:"select",options:[{value:"bazett"}],required:true}];
  assert.deepEqual(validateCalculatorFields(fields,{qt:420,formula:"bazett"}),{});
  for(const qt of [-1,0,901,Infinity,NaN,true,"texto"]){assert.ok(validateCalculatorFields(fields,{qt,formula:"bazett"}).qt);}
  assert.ok(validateCalculatorFields(fields,{qt:420,formula:"inventada"}).formula);
  const peso={name:"peso",label:"Peso",type:"number",required:false,min:1,required_when:{droga:["mcg/kg/min"]}};
  assert.equal(calculatorFieldRequired(peso,{droga:"mg/h"}),false);
  assert.equal(calculatorFieldRequired(peso,{droga:"mcg/kg/min"}),true);
  assert.ok(validateCalculatorFields([peso],{droga:"mcg/kg/min"}).peso);
  assert.deepEqual(validateCalculatorFields([peso],{droga:"mg/h"}),{});
});
