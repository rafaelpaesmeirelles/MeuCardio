import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { stripTypeScriptTypes } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';

const read = file => readFileSync(new URL(`../src/${file}`, import.meta.url), 'utf8');
const assistant = read('pages/Assistente.tsx');
const prescription = read('components/PrescricaoLivreEspecial.tsx');
const templates = read('pages/Templates.tsx');
const calculators = read('pages/Calculadoras.tsx');
const exams = read('pages/Exames.tsx');
function between(source, start, end) {
  const from = source.indexOf(start); assert.notEqual(from, -1);
  const to = source.indexOf(end, from + start.length); assert.notEqual(to, -1);
  return source.slice(from, to);
}
const tick = () => new Promise(resolve => setImmediate(resolve));

test('personal consent: only successful persistence calls onDecidir; failure stays closed and retry works', async () => {
  const code = between(assistant, '  async function decidir(', '\n\n  return');
  const decisions = [], state = {};
  let fail = true;
  const ctx = vm.createContext({ api: { put: async () => { if (fail) throw new Error('503 fixture'); } },
    setEnviando: value => { state.busy = value; }, setErroConsentimento: value => { state.error = value; }, onDecidir: value => decisions.push(value) });
  vm.runInContext(stripTypeScriptTypes(code), ctx);
  await vm.runInContext('decidir(true)', ctx);
  assert.deepEqual(decisions, []); assert.equal(state.busy, false); assert.match(state.error, /Nenhuma nova autorização/);
  fail = false; await vm.runInContext('decidir(true)', ctx);
  assert.deepEqual(decisions, [true]); assert.equal(state.error, '');
});

test('prescription first-render error handler is initialized before early return and catches rejected load', async () => {
  const prefix = between(prescription, ' const[c,setC]', ' if(!c)return');
  const effects = [], messages = [];
  const ctx = vm.createContext({ queueOnly: false, useState: initial => [initial, value => messages.push(value)],
    useEffect: effect => effects.push(effect), api: { get: async () => { throw new Error('503 fixture'); } } });
  vm.runInContext(stripTypeScriptTypes(`function initialRender(){${prefix}}; initialRender();`), ctx);
  effects.forEach(effect => effect()); await tick();
  assert(messages.some(value => typeof value === 'string' && /Falha na operação|503 fixture/.test(value)));
});

for (const [name, source, start, end, setter] of [
  ['calculator catalog', calculators, '  useEffect(() => {\n    let ativo', '\n\n  const temas', 'setErro'],
  ['assistant status', assistant, '  useEffect(() => {\n    let ativo', '\n  useEffect', 'setErroStatus'],
]) {
  test(`${name}: API failure produces explicit error; retry can accept real-shaped success`, async () => {
    const code = between(source, start, end); const state = {}; let fail = true;
    const ctx = vm.createContext({ useEffect: fn => fn(), tentativa: 0, tentativaStatus: 0,
      api: { get: async () => { if (fail) throw new Error('503 fixture'); return name === 'assistant status' ? { ativo: false } : []; } },
      [setter]: value => { state.error = value; }, setLista: value => { state.value = value; }, setStatus: value => { state.value = value; } });
    vm.runInContext(stripTypeScriptTypes(code), ctx); await tick(); assert(state.error); assert.equal(state.value, undefined);
    fail = false; vm.runInContext(stripTypeScriptTypes(code), ctx); await tick(); assert.equal(state.error, ''); assert.notEqual(state.value, undefined);
  });
}

test('document catalog and refresh catch rejected GET without fabricating an empty catalog', async () => {
  const code = between(templates, '  const recarregar = async', '\n\n  function caminhoGerados');
  const state = {};
  const ctx = vm.createContext({ api: { get: async () => { throw new Error('503 fixture'); } }, ApiError: Error,
    setErroModelos: value => { state.error = value; }, setLista: value => { state.items = value; } });
  vm.runInContext(stripTypeScriptTypes(code), ctx); await vm.runInContext('recarregar()', ctx);
  assert(state.error); assert.equal(state.items, undefined);
});

test('assistant conversation open/delete errors preserve current messages and conversation', async () => {
  const code = between(assistant, '  async function abrirConversa', '\n  async function enviar');
  const state = { conversation: 41, messages: ['preserved'] };
  const ctx = vm.createContext({ api: { get: async () => { throw new Error('503 fixture'); }, delete: async () => { throw new Error('503 fixture'); } },
    conversa: 41, modo: 'clinica', setErro: value => { state.error = value; },
    setConversa: value => { state.conversation = value; }, setMensagens: value => { state.messages = value; }, setMostrarHistorico() {}, recarregarHistorico() {} });
  vm.runInContext(stripTypeScriptTypes(code), ctx);
  await vm.runInContext('abrirConversa(42)', ctx); assert.equal(state.conversation, 41); assert.deepEqual(state.messages, ['preserved']); assert(state.error);
  await vm.runInContext('apagarConversa(41, {stopPropagation(){}})', ctx); assert.equal(state.conversation, 41); assert.deepEqual(state.messages, ['preserved']); assert(state.error);
});

test('exam taxonomy failure is explicit and does not replace catalog results', async () => {
  const state = {};
  const code = between(exams, '  useEffect(() => {\n    let ativo', '\n\n  useEffect');
  const ctx = vm.createContext({ useEffect: fn => fn(), tentativaTaxonomia: 0,
    api: { get: async () => { throw new Error('503 fixture'); } },
    setErroTaxonomia: value => { state.error = value; }, setTaxonomia: () => assert.fail('No fabricated taxonomy') });
  vm.runInContext(stripTypeScriptTypes(code), ctx); await tick(); assert.match(state.error, /busca por nome continua disponível/);
});

test('exam search failure leaves filters intact and retry accepts successful data', async () => {
  const state = {}, item = { slug: 'canonical-fixture' }; let fail = true;
  const code = between(exams, '  useEffect(() => {\n    const id =', '\n\n  async function carregarMais');
  const ctx = vm.createContext({ useEffect: fn => fn(), requisicao: { current: 0 }, categoria: 'laboratorial', subtipo: '', busca: 'teste', tentativa: 0,
    URLSearchParams, setTimeout: fn => { fn(); return 1; }, clearTimeout() {},
    api: { get: async () => { if (fail) throw new Error('503 fixture'); return { items: [item], total: 1, next_offset: null }; } },
    setItens: value => { state.items = value; }, setTotalEncontrados() {}, setNextOffset() {}, setCarregandoMais() {}, setErro: value => { state.error = value; }, setParams: value => { state.params = value; } });
  vm.runInContext(stripTypeScriptTypes(code), ctx); await tick(); assert.match(state.error, /filtros foram preservados/); assert.equal(state.items, null); assert.equal(state.params.get('q'), 'teste');
  fail = false; vm.runInContext(stripTypeScriptTypes(code), ctx); await tick(); assert.equal(state.error, ''); assert.equal(state.items[0], item);
});

test('exam pagination failure preserves loaded items/offset and releases busy state', async () => {
  const state = {};
  const code = between(exams, '  async function carregarMais()', '\n\n  const subtiposDisponiveis');
  const ctx = vm.createContext({ nextOffset: 200, carregandoMais: false, requisicao: { current: 4 }, categoria: '', subtipo: '', busca: '', URLSearchParams,
    api: { get: async () => { throw new Error('503 fixture'); } },
    setItens: () => assert.fail('Loaded items must remain unchanged'), setNextOffset: () => assert.fail('Failed page must not advance'), setTotalEncontrados() {},
    setCarregandoMais: value => { state.busy = value; }, setErro: value => { state.error = value; } });
  vm.runInContext(stripTypeScriptTypes(code), ctx); await vm.runInContext('carregarMais()', ctx);
  assert.equal(state.busy, false); assert.match(state.error, /já carregados foram preservados/);
});
