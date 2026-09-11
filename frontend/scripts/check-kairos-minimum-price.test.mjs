import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { stripTypeScriptTypes } from 'node:module';
import vm from 'node:vm';
import test from 'node:test';

const source = readFileSync(new URL('../src/pages/Receituario.tsx', import.meta.url), 'utf8');
function section(start, end) {
  const from = source.indexOf(start); const to = source.indexOf(end, from + start.length);
  assert(from >= 0 && to > from); return source.slice(from, to);
}
const functions = section('function formatarPreco(', 'function precoCmedExibivel(')
  + section('function rotuloPrecoItem(', 'function baixarBlob(');
const brl = value => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

test('Kairos item shows minimum PMC, not the maximum, range, PF or an obsolete label', () => {
  const context = vm.createContext({});
  vm.runInContext(stripTypeScriptTypes(functions), context);
  context.item = { price_source: 'kairos', price_min: 42.58, price_max: 46.84,
    price_label: 'old range', pmc_snapshot: 999, pf: 30.89 };
  assert.equal(vm.runInContext('rotuloPrecoItem(item)', context), brl(42.58));
  context.item = { price_source: 'kairos', price_max: 46.84, price_label: 'not a known minimum' };
  assert.equal(vm.runInContext('rotuloPrecoItem(item)', context), 'Preço não publicado');
});

test('unrelated CMED item and missing prices keep their existing semantics', () => {
  const context = vm.createContext({}); vm.runInContext(stripTypeScriptTypes(functions), context);
  context.item = { price_source: 'cmed', pmc_snapshot: 55.1 };
  assert.equal(vm.runInContext('rotuloPrecoItem(item)', context), brl(55.1));
  context.item = {};
  assert.equal(vm.runInContext('rotuloPrecoItem(item)', context), 'Sem preço vinculado');
});

test('choosing a presentation preserves its full source range and identity while displaying the minimum', () => {
  const state = { items: [{ descricao: 'generic fixture' }, { descricao: 'untouched fixture' }], preview: 'old' };
  const context = vm.createContext({
    setPrevia: value => { state.preview = value; },
    setItens: update => { state.items = update(state.items); },
    ap: { produto: 'BRAND FIXTURE', laboratorio: 'LAB FIXTURE', apresentacao: '10 mg — 30 tablets fixture', preco_minimo: 21.25, preco_maximo: 29.8, pagina_fonte: 22 },
    fonte: { edicao: 453, competencia: '2026-08' },
  });
  vm.runInContext(stripTypeScriptTypes(functions + section('  function escolherApresentacaoKairos(', '  function voltarParaGenerico(')), context);
  vm.runInContext('escolherApresentacaoKairos(0, ap, fonte)', context);
  assert.equal(state.items[0].price_label, brl(21.25));
  assert.equal(state.items[0].price_min, 21.25); assert.equal(state.items[0].price_max, 29.8);
  assert.equal(state.items[0].price_source_page, 22); assert.equal(state.items[0].price_source, 'kairos');
  assert.equal(state.items[0].apresentacao, context.ap.apresentacao);
  assert.equal(state.items[0].pmc_snapshot, undefined); assert.equal(state.items[0].uf, undefined);
  assert.equal(state.items[1].descricao, 'untouched fixture'); assert.equal(state.preview, null);
});
