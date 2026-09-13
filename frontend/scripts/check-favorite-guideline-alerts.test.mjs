import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { MemoryRouter } from 'react-router-dom';

// Real alert and guideline-page components. Only fictitious scientific data;
// every API call stays in this fixture, with no account or content mutation.
const require = createRequire(import.meta.url);
const text = renderer => JSON.stringify(renderer.toJSON());
const deferred = () => { let resolve; const promise = new Promise(done => { resolve = done; }); return { promise, resolve }; };
const response = (title = 'Documento demonstrativo', url = 'https://example.org/guideline') => ({ alertas: [{
  diretriz_revisada: { titulo: 'Diretriz demonstrativa anterior', org: 'Organização de teste', ano: 2020 },
  nova_versao: { titulo: 'Nova versão demonstrativa', ano: 2026, doi: null, url },
  seus_documentos: [{ slug: 'documento-demonstrativo', titulo: title }],
  significado: 'A fonte foi revisada. Isto não quer dizer que o conteúdo esteja desatualizado; a revisão interna ainda não foi concluída.',
}] });

function harness(getAlerts) {
  const calls = [], fixture = { user: { id: -1 } }, cache = new Map();
  const api = { get: async (url, options) => {
    calls.push({ url, options, userId: fixture.user?.id });
    if (url === '/diretrizes/meus-alertas') return getAlerts();
    if (url.startsWith('/guideline-updates')) return { items: [], cutoff: '2026-01-01' };
    throw Error('Unexpected read: ' + url);
  } };
  const empty = { __esModule: true, default: () => null };
  const section = ({ title, children }) => React.createElement('section', null, React.createElement('h2', null, title), children);
  function load(relative) {
    if (cache.has(relative)) return cache.get(relative);
    const code = ts.transpileModule(readFileSync(new URL('../src/' + relative, import.meta.url), 'utf8'), {
      compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX },
    }).outputText;
    const module = { exports: {} };
    vm.runInNewContext(code, { module, exports: module.exports, AbortController, URL, console,
      require: name => {
        if (name === '../lib/api') return { api, READ_TIMEOUT_MS: 15000, ApiError: Error };
        if (name === '../lib/auth') return { useAuth: () => ({ usuario: fixture.user }) };
        if (name === '../components/AlertasDiretrizesFavoritas') return load('components/AlertasDiretrizesFavoritas.tsx');
        if (name === '../components/EditorialDocumentList') return { __esModule: true, default: () => React.createElement('p', null, 'Coleção científica disponível') };
        if (name === '../components/Estado') return { Carregando: () => null, Erro: ({ mensagem }) => React.createElement('p', { role: 'alert' }, mensagem) };
        if (name === '../components/ClinicalCommandPrimitives') return Object.fromEntries(
          ['ClinicalContextLink', 'ClinicalEmpty', 'ClinicalMetric', 'ClinicalPageHeader', 'ClinicalSection'].map(key => [key, section]));
        if (name.startsWith('../components/')) return empty;
        return require(name);
      },
    }, { filename: relative });
    cache.set(relative, module.exports);
    return module.exports;
  }
  return { calls, fixture, async mount(t, page = false, props = {}) {
    const Component = load(page ? 'pages/Diretrizes.tsx' : 'components/AlertasDiretrizesFavoritas.tsx').default;
    const element = () => React.createElement(MemoryRouter, {
      future: { v7_startTransition: true, v7_relativeSplatPath: true },
    }, React.createElement(Component, props));
    let renderer;
    await act(async () => { renderer = TestRenderer.create(element()); });
    t.after(async () => { await act(async () => renderer.unmount()); });
    return { renderer, async rerender() { await act(async () => renderer.update(element())); } };
  } };
}

test('guidelines page exposes favorite-source revisions with the full qualifier and canonical document link', async t => {
  const h = harness(() => response());
  const { renderer } = await h.mount(t, true);
  assert.match(text(renderer), /Documento demonstrativo/);
  assert.match(text(renderer), /Isto não quer dizer que o conteúdo esteja desatualizado; a revisão interna ainda não foi concluída/);
  const links = renderer.root.findAllByType('a').map(item => item.props.href);
  assert.ok(links.includes('/biblioteca/documento-demonstrativo'));
  assert.ok(links.includes('https://example.org/guideline'));
  const call = h.calls.find(item => item.url === '/diretrizes/meus-alertas');
  assert.equal(call.options.timeoutMs, 15000);
  assert.equal(call.options.signal.aborted, false);
});

test('failed favorite alerts leave scientific collections visible and retry recovers', async t => {
  let attempts = 0;
  const h = harness(() => { if (++attempts === 1) throw Error('fixture unavailable'); return response(); });
  const { renderer } = await h.mount(t, true);
  assert.match(text(renderer), /Coleção científica disponível/);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 1);
  const retry = renderer.root.findAllByType('button').find(item => item.children.join('').includes('alertas dos favoritos novamente'));
  await act(async () => retry.props.onClick());
  assert.equal(attempts, 2);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
  assert.match(text(renderer), /Documento demonstrativo/);
});

test('empty results are distinguished from loading and an unsafe source never becomes a link', async t => {
  let value = { alertas: [], nota: 'Alertas seguem seus documentos favoritos.' };
  const h = harness(() => value);
  const { renderer } = await h.mount(t);
  assert.match(text(renderer), /Nenhuma revisão de diretriz vinculada/);
  assert.doesNotMatch(text(renderer), /Consultando revisões/);
  value = response('Documento demonstrativo', 'javascript:alert(1)');
  await act(async () => renderer.root.findByType('button').props.onClick());
  assert.deepEqual(renderer.root.findAllByType('a').map(item => item.props.href), ['/biblioteca/documento-demonstrativo']);
});

test('switching accounts removes the previous interests before the next response', async t => {
  const next = deferred();
  const h = harness(() => h.fixture.user.id === -1 ? response('INTERESSE DA CONTA A') : next.promise);
  const { renderer, rerender } = await h.mount(t);
  assert.match(text(renderer), /INTERESSE DA CONTA A/);
  h.fixture.user = { id: -2 }; await rerender();
  assert.doesNotMatch(text(renderer), /INTERESSE DA CONTA A/);
  assert.equal(h.calls[0].options.signal.aborted, true);
  await act(async () => next.resolve(response('INTERESSE DA CONTA B')));
  assert.match(text(renderer), /INTERESSE DA CONTA B/);
});

test('an old account response cannot replace a newer account and sign-out clears the panel', async t => {
  const old = deferred();
  const h = harness(() => h.fixture.user.id === -1 ? old.promise : response('INTERESSE ATUAL'));
  const { renderer, rerender } = await h.mount(t);
  h.fixture.user = { id: -2 }; await rerender();
  await act(async () => old.resolve(response('INTERESSE ANTIGO')));
  assert.match(text(renderer), /INTERESSE ATUAL/);
  assert.doesNotMatch(text(renderer), /INTERESSE ANTIGO/);
  h.fixture.user = null; await rerender();
  assert.equal(renderer.toJSON(), null);
  assert.equal(h.calls.length, 2);
  assert.equal(h.calls[1].options.signal.aborted, true);
});

test('the publication-only Intelligence page does not request favorite-source alerts', async t => {
  const h = harness(() => { throw Error('Should not load favorite-source alerts here'); });
  await h.mount(t, true, { intelligenceOnly: true });
  assert.equal(h.calls.some(item => item.url === '/diretrizes/meus-alertas'), false);
});
