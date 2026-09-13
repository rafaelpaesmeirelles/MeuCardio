import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { MemoryRouter } from 'react-router-dom';

// Real pages, router, effects and API client. Only fetch and the debounce clock
// are controlled; no network, users, clinical data or backend writes are used.
const require = createRequire(import.meta.url);
const rendered = renderer => JSON.stringify(renderer.toJSON());
const textOf = node => typeof node === 'string' ? node : (node.children ?? []).map(textOf).join('');
const button = (renderer, text) => renderer.root.findAllByType('button').find(node => textOf(node).includes(text));
const response = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const userPage = name => ({ items: [{ id: 900001, full_name: name, email: 'fixture@example.test', status: 'aprovado', created_at: '2026-01-01T00:00:00Z' }], page: 1, page_size: 20, total: 21, has_more: true });
const diseasePage = (name, extra = {}) => ({ items: [{ slug: name, name, area: 'geral', category: 'fixture', aliases: [], summary: 'Fixture técnica, sem uso clínico', tags: [] }], page: 1, page_size: 60, total: 1, has_more: false, ...extra });
const facets = label => ({ areas: [{ id: label, count: 3 }], clinical_domains: [{ id: label, label, count: 3 }], categories: [] });

function harness({ respectAbort = false } = {}) {
  const calls = [], modules = new Map(), timers = new Map();
  let nextTimer = 0;
  const window = { localStorage: { removeItem() {} }, location: { pathname: '/', assign() { throw Error('Unexpected redirect'); } } };
  function load(relative) {
    if (modules.has(relative)) return modules.get(relative);
    const source = readFileSync(new URL(`../src/${relative}`, import.meta.url), 'utf8').replaceAll('import.meta.env', '({})');
    const compiled = ts.transpileModule(source, { fileName: relative, compilerOptions: {
      module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true,
    } }).outputText;
    const module = { exports: {} };
    vm.runInNewContext(compiled, {
      module, exports: module.exports, window, Headers, Response, FormData, AbortController, DOMException, URLSearchParams, URL,
      setTimeout: (fn, ms) => { const id = ++nextTimer; timers.set(id, { fn, ms }); return id; },
      clearTimeout: id => timers.delete(id),
      fetch: (url, init) => new Promise((resolve, reject) => {
        // Ignoring abort by default proves the effect guard independently of
        // fetch cancellation. The abort-aware case exercises the real signal.
        const call = { url, init, resolve, reject, aborted: false };
        calls.push(call);
        if (respectAbort && init.signal) {
          const abort = () => { call.aborted = true; reject(new DOMException('Aborted fixture', 'AbortError')); };
          if (init.signal.aborted) abort();
          else init.signal.addEventListener('abort', abort, { once: true });
        }
      }),
      require: name => {
        if (name.endsWith('.css')) return {};
        if (name === './clinicalCache') return { clearLegacyClinicalCaches() {} };
        if (name.startsWith('.')) {
          const target = path.posix.normalize(path.posix.join(path.posix.dirname(relative), name));
          return load(`${target}.${target.startsWith('components/') ? 'tsx' : 'ts'}`);
        }
        return require(name);
      },
    }, { filename: relative });
    modules.set(relative, module.exports);
    return module.exports;
  }
  return {
    calls,
    requests(endpoint) { return calls.filter(call => new URL(call.url, 'http://fixture.invalid').pathname === `/api${endpoint}`); },
    async mount(t, name, url = '/') {
      const Page = load(`pages/${name}.tsx`).default;
      let renderer;
      await act(async () => { renderer = TestRenderer.create(React.createElement(MemoryRouter,
        { initialEntries: [url], future: { v7_startTransition: true, v7_relativeSplatPath: true } }, React.createElement(Page))); });
      t.after(async () => { await act(async () => renderer.unmount()); });
      return renderer;
    },
    async reply(call, body, status = 200) { await act(async () => call.resolve(response(body, status))); },
    async reject(call) { await act(async () => call.reject(new Error('FALHA OBSOLETA'))); },
    async change(node, value) { await act(async () => node.props.onChange({ target: { value } })); },
    async advance(ms) { await act(async () => {
      for (const [id, timer] of [...timers]) if (timer.ms <= ms && timers.has(id)) { timers.delete(id); timer.fn(); }
    }); },
  };
}
const adminRequests = h => h.requests('/admin/usuarios');
const facetRequests = h => h.requests('/specialty-guides/disease-facets');
const diseaseRequests = h => h.requests('/specialty-guides/diseases');
const adminStatus = renderer => renderer.root.findByProps({ id: 'aa-status' });
const diseaseArea = renderer => renderer.root.findAllByType('select')[0];

test('AdminAssinantes: a late response cannot replace the latest filter even if fetch ignores abort', async t => {
  const h = harness(), renderer = await h.mount(t, 'AdminAssinantes');
  const old = adminRequests(h)[0];
  await h.change(adminStatus(renderer), 'aprovado');
  const current = adminRequests(h).at(-1);
  await h.reply(current, userPage('ASSINANTE NOVO'));
  await h.reply(old, userPage('ASSINANTE ANTIGO'));
  assert.match(rendered(renderer), /ASSINANTE NOVO/);
  assert.doesNotMatch(rendered(renderer), /ASSINANTE ANTIGO/);
  assert.equal(old.init.signal?.aborted, true);
});

test('AdminAssinantes: stale failure cannot expose an error or finish the active loading state', async t => {
  const h = harness(), renderer = await h.mount(t, 'AdminAssinantes');
  await h.reply(adminRequests(h)[0], userPage('ASSINANTE INICIAL'));
  await h.change(adminStatus(renderer), 'pendente');
  const old = adminRequests(h).at(-1);
  await h.change(adminStatus(renderer), 'aprovado');
  const current = adminRequests(h).at(-1);
  await h.reject(old);
  assert.equal(button(renderer, 'Próxima').props.disabled, true);
  assert.match(rendered(renderer), /atualizando/);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
  await h.reply(current, userPage('ASSINANTE ATUAL'));
  assert.match(rendered(renderer), /ASSINANTE ATUAL/);
  assert.equal(button(renderer, 'Próxima').props.disabled, false);
});

test('AdminAssinantes: a late error after success does not taint the new result', async t => {
  const h = harness(), renderer = await h.mount(t, 'AdminAssinantes');
  const old = adminRequests(h)[0];
  await h.change(adminStatus(renderer), 'aprovado');
  await h.reply(adminRequests(h).at(-1), userPage('ASSINANTE ATUAL'));
  await h.reply(old, { detail: 'ERRO DA CONSULTA ANTIGA' }, 503);
  assert.match(rendered(renderer), /ASSINANTE ATUAL/);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
});

test('AdminAssinantes: debounced search cancels the previous request at the real fetch boundary', async t => {
  const h = harness({ respectAbort: true }), renderer = await h.mount(t, 'AdminAssinantes');
  const old = adminRequests(h)[0];
  await h.change(renderer.root.findByProps({ id: 'aa-busca' }), '  atual  ');
  await h.advance(400);
  const current = adminRequests(h).at(-1);
  assert.equal(new URL(current.url, 'http://fixture.invalid').searchParams.get('q'), 'atual');
  assert.equal(old.aborted, true);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
  await h.reply(current, userPage('ASSINANTE ATUAL'));
  assert.match(rendered(renderer), /ASSINANTE ATUAL/);
});

test('AdminAssinantes: current errors remain visible and changing filters recovers', async t => {
  const h = harness(), renderer = await h.mount(t, 'AdminAssinantes');
  await h.reply(adminRequests(h)[0], { detail: 'FALHA VIGENTE' }, 503);
  assert.match(rendered(renderer), /FALHA VIGENTE/);
  await h.change(adminStatus(renderer), 'aprovado');
  await h.reply(adminRequests(h).at(-1), userPage('ASSINANTE RECUPERADO'));
  assert.match(rendered(renderer), /ASSINANTE RECUPERADO/);
  assert.doesNotMatch(rendered(renderer), /FALHA VIGENTE/);
});

test('GuiaDoencas: late facets cannot replace the newer options', async t => {
  const h = harness(), renderer = await h.mount(t, 'GuiaDoencas');
  const old = facetRequests(h)[0];
  await h.change(diseaseArea(renderer), 'geral');
  await h.reply(facetRequests(h).at(-1), facets('GRUPO ATUAL'));
  await h.reply(old, facets('GRUPO ANTIGO'));
  assert.match(rendered(renderer), /GRUPO ATUAL/);
  assert.doesNotMatch(rendered(renderer), /GRUPO ANTIGO/);
  assert.equal(old.init.signal?.aborted, true);
});

test('GuiaDoencas: stale facet error cannot erase options from the current response', async t => {
  const h = harness(), renderer = await h.mount(t, 'GuiaDoencas');
  const old = facetRequests(h)[0];
  await h.change(diseaseArea(renderer), 'geral');
  await h.reply(facetRequests(h).at(-1), facets('GRUPO PRESERVADO'));
  await h.reject(old);
  assert.match(rendered(renderer), /GRUPO PRESERVADO/);
  assert.equal(renderer.root.findAllByType('option').filter(node => node.props.value === 'GRUPO PRESERVADO').length, 2);
});

test('GuiaDoencas: an old pagination response cannot append diseases to a newer search', async t => {
  const h = harness(), renderer = await h.mount(t, 'GuiaDoencas');
  await h.reply(diseaseRequests(h)[0], diseasePage('PRIMEIRA PÁGINA', { has_more: true, total: 2 }));
  await act(async () => button(renderer, 'Carregar mais').props.onClick());
  const oldPage = diseaseRequests(h).at(-1);
  assert.equal(new URL(oldPage.url, 'http://fixture.invalid').searchParams.get('page'), '2');
  await h.change(renderer.root.findByProps({ placeholder: 'Nome, sigla, sinônimo, sintoma ou tema…' }), 'novo');
  const current = diseaseRequests(h).at(-1);
  await h.reply(current, diseasePage('BUSCA ATUAL'));
  await h.reply(oldPage, diseasePage('PÁGINA ANTIGA'));
  assert.match(rendered(renderer), /BUSCA ATUAL/);
  assert.doesNotMatch(rendered(renderer), /PRIMEIRA PÁGINA|PÁGINA ANTIGA/);
  assert.equal(oldPage.init.signal?.aborted, true);
});

test('GuiaDoencas: an obsolete disease error cannot replace the newer success', async t => {
  const h = harness(), renderer = await h.mount(t, 'GuiaDoencas');
  const old = diseaseRequests(h)[0];
  await h.change(diseaseArea(renderer), 'geral');
  await h.reply(diseaseRequests(h).at(-1), diseasePage('RESULTADO ATUAL'));
  await h.reject(old);
  assert.match(rendered(renderer), /RESULTADO ATUAL/);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
});

for (const name of ['AdminAssinantes', 'GuiaDoencas']) {
  test(`${name}: unmount aborts every pending read`, async t => {
    const h = harness({ respectAbort: true }), renderer = await h.mount(t, name);
    assert.ok(h.calls.length > 0);
    await act(async () => renderer.unmount());
    assert.ok(h.calls.every(call => call.aborted));
  });
}
