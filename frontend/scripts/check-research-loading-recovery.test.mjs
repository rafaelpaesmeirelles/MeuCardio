import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';

// Real React components and API client; no server, account, database or network.
const require = createRequire(import.meta.url);
const text = renderer => JSON.stringify(renderer.toJSON());
const deferred = () => { let resolve; const promise = new Promise(yes => { resolve = yes; }); return { promise, resolve }; };
const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
function harness(fetcher) {
  const timers = new Map(); let timerId = 0;
  const window = Object.assign(new EventTarget(), {
    localStorage: { removeItem() {}, getItem() { return null; } },
    location: { pathname: '/biblioteca/demo', assign() {} },
    setTimeout: (fn, ms) => { const id = ++timerId; timers.set(id, { fn, ms }); return id; },
    clearTimeout: id => timers.delete(id),
  });
  const fixture = { slug: 'caso-a', user: { id: 990001 } };
  const cache = new Map();
  const stubs = {
    '../lib/auth': { useAuth: () => ({ usuario: fixture.user }) },
    './clinicalCache': { clearLegacyClinicalCaches() {} },
    '../lib/favorites': { FAVORITES_CHANGED: 'favorites-changed', announceFavoriteChange() {} },
    'react-router-dom': { Link: ({ to, children, ...props }) => React.createElement('a', { ...props, href: to }, children), useParams: () => ({ slug: fixture.slug }) },
    'react-markdown': { default: ({ children }) => React.createElement('div', null, children) },
    'remark-gfm': { default: () => {} },
    '../components/ScientificReadingAccess': { default: () => null },
    '../components/TudoSobreEsteTema': { default: () => null },
    '../components/GrafoRelacionados': { default: () => null },
    '../components/Fluxograma': { default: () => null },
    '../components/ExportarApresentacao': { default: () => null },
  };
  function load(relative) {
    if (cache.has(relative)) return cache.get(relative);
    const source = readFileSync(new URL(`../src/${relative}`, import.meta.url), 'utf8').replaceAll('import.meta.env', '({})');
    const compiled = ts.transpileModule(source, { fileName: relative, compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true } }).outputText;
    const module = { exports: {} };
    vm.runInNewContext(compiled, {
      module, exports: module.exports, window, Headers, Response, FormData, AbortController, DOMException, URL, URLSearchParams,
      setTimeout: window.setTimeout, clearTimeout: window.clearTimeout, fetch: fetcher,
      require: name => {
        if (stubs[name]) return { __esModule: true, ...stubs[name] };
        if (name.endsWith('.css')) return {};
        if (name === '../lib/api') return load('lib/api.ts');
        if (name === './loginReturn') return load('lib/loginReturn.ts');
        if (name === '../lib/commercialPlans') return load('lib/commercialPlans.ts');
        if (name === '../lib/taxonomiaCardiologia') return load('lib/taxonomiaCardiologia.ts');
        if (name === '../components/Estado') return load('components/Estado.tsx');
        if (name === '../components/BotaoFavorito') return load('components/BotaoFavorito.tsx');
        return require(name);
      },
    }, { filename: relative });
    cache.set(relative, module.exports); return module.exports;
  }
  return { load, fixture, timers, async advance(ms) {
    await act(async () => { for (const [id, timer] of [...timers]) if (timer.ms <= ms) { timers.delete(id); timer.fn(); } });
  } };
}
async function mount(t, Component, props = {}) {
  let renderer; await act(async () => { renderer = TestRenderer.create(React.createElement(Component, props)); });
  t.after(() => act(() => renderer.unmount())); return renderer;
}
const pendingFetch = (_url, init) => new Promise((_resolve, reject) => {
  init.signal?.addEventListener('abort', () => reject(new DOMException('Aborted fixture', 'AbortError')), { once: true });
});
const button = (renderer, label) => renderer.root.findAllByType('button').find(node => JSON.stringify(node.children).includes(label));

test('GET deadline is opt-in, aborts transport and leaves normal POST without a deadline', async () => {
  const calls = [];
  const h = harness((url, init) => { calls.push({ url, init }); return pendingFetch(url, init); });
  const { api } = h.load('lib/api.ts');
  const read = api.get('/billing/status', { timeoutMs: 15000 });
  const rejected = assert.rejects(read, error => error.status === 504);
  await h.advance(15000); await rejected;
  assert.equal(calls[0].init.signal.aborted, true);
  void api.post('/demo-no-real-write', {});
  assert.equal(calls[1].init.signal, undefined);
  assert.equal(h.timers.size, 0);
});

test('commercial access: pending GET ends in retry and never mounts unverified children', async t => {
  let allowed = false, mounts = 0, calls = 0;
  const h = harness((url, init) => {
    assert.equal(url, '/api/billing/status'); calls++;
    return allowed ? Promise.resolve(json({ entitlements: { ai: true } })) : pendingFetch(url, init);
  });
  const Gate = h.load('components/CommercialFeatureGate.tsx').default;
  const Child = () => { mounts++; return React.createElement('p', null, 'AUTHORIZED CHILD'); };
  const renderer = await mount(t, Gate, { feature: 'ai', children: React.createElement(Child) });
  await h.advance(15000);
  assert.equal(mounts, 0);
  assert.doesNotMatch(text(renderer), /Verificando seu acesso/);
  assert.ok(renderer.root.findAllByProps({ role: 'alert' }).length);
  allowed = true;
  await act(async () => button(renderer, 'Tentar novamente').props.onClick());
  assert.equal(calls, 2); assert.match(text(renderer), /AUTHORIZED CHILD/);
});

test('favorite: rejected status is not labelled as still loading and cannot mutate until retry', async t => {
  let retry = false, reads = 0;
  const h = harness(async (_url, init) => {
    assert.equal(init.method, undefined); reads++;
    return retry ? json({ favorited: false, favorite_id: null, available: true }) : json({ detail: 'fixture unavailable' }, 503);
  });
  const renderer = await mount(t, h.load('components/BotaoFavorito.tsx').default, { itemType: 'documento', itemSlug: 'demo' });
  assert.doesNotMatch(text(renderer), /Consultando favorito/);
  assert.equal(renderer.root.findAllByType('button')[0].props.disabled, true);
  retry = true;
  await act(async () => button(renderer, 'Tentar novamente').props.onClick());
  assert.equal(reads, 2); assert.equal(button(renderer, 'Favoritar').props.disabled, false);
});

test('favorite: pending status is aborted at the deadline and explicit retry recovers', async t => {
  let retry = false;
  const h = harness((url, init) => retry ? Promise.resolve(json({ favorited: true, favorite_id: 9902, available: true })) : pendingFetch(url, init));
  const renderer = await mount(t, h.load('components/BotaoFavorito.tsx').default, { itemType: 'documento', itemSlug: 'demo' });
  await h.advance(15000);
  assert.doesNotMatch(text(renderer), /Consultando favorito/);
  assert.ok(renderer.root.findAllByProps({ role: 'alert' }).length);
  retry = true;
  await act(async () => button(renderer, 'Tentar novamente').props.onClick());
  assert.equal(button(renderer, 'Favoritado').props['aria-pressed'], true);
});

test('clinical cases: first page stays visible when a following page fails or stalls', async t => {
  const h = harness((url, init) => {
    if (url.includes('/themes')) return Promise.resolve(json([]));
    if (url.includes('offset=0')) return Promise.resolve(json({ items: [{ slug: 'caso-demo', titulo: 'CASO EXISTENTE DEMO', tema: 'Hipertensão', nivel: null, tentativas: 0, acertou_na_ultima: null }], total: 2, has_more: true, next_offset: 1 }));
    return pendingFetch(url, init);
  });
  const renderer = await mount(t, h.load('pages/CasosClinicos.tsx').default);
  await h.advance(220);
  assert.match(text(renderer), /CASO EXISTENTE DEMO/);
  await h.advance(15000);
  assert.match(text(renderer), /CASO EXISTENTE DEMO/);
  assert.ok(renderer.root.findAllByProps({ role: 'alert' }).length);
  assert.ok(button(renderer, 'Tentar novamente'));
});

test('case detail: changing slug discards delayed content', async t => {
  const a = deferred();
  const data = slug => ({ slug, titulo: `TITLE ${slug}`, tema: null, nivel: null, enunciado: `BODY ${slug}`, pergunta: 'QUESTION DEMO', opcoes: ['OPTION DEMO'], source_refs: [] });
  const h = harness(url => url.endsWith('/caso-a') ? a.promise : Promise.resolve(json(data('caso-b'))));
  const Case = h.load('pages/CasoClinico.tsx').default;
  const renderer = await mount(t, Case);
  h.fixture.slug = 'caso-b';
  await act(async () => renderer.update(React.createElement(Case)));
  await act(async () => a.resolve(json(data('caso-a'))));
  assert.match(text(renderer), /BODY caso-b/); assert.doesNotMatch(text(renderer), /BODY caso-a/);
});

test('GET deadline covers stalled JSON body; caller cancellation stays AbortError and clears its timer', async () => {
  const h = harness((_url, init) => Promise.resolve({ status: 200, ok: true,
    json: () => pendingFetch('', init),
  }));
  const { api } = h.load('lib/api.ts');
  const read = api.get('/demo', { timeoutMs: 15000 });
  const rejected = assert.rejects(read, error => error.status === 504);
  await act(async () => {}); await h.advance(15000); await rejected;
  assert.equal(h.timers.size, 0);
  const cancellation = new AbortController();
  const other = api.get('/demo', { timeoutMs: 15000, signal: cancellation.signal });
  const cancelled = assert.rejects(other, error => error.name === 'AbortError' && error.status === undefined);
  await act(async () => {}); cancellation.abort(); await cancelled;
  assert.equal(h.timers.size, 0);
});

test('commercial denial never mounts the gated feature and is not treated as a transport failure', async t => {
  let mounts = 0;
  const h = harness(async () => json({ entitlements: { ai: false } }));
  const Child = () => { mounts++; return React.createElement('p', null, 'FORBIDDEN CHILD'); };
  const renderer = await mount(t, h.load('components/CommercialFeatureGate.tsx').default, { feature: 'ai', children: React.createElement(Child) });
  assert.equal(mounts, 0); assert.match(text(renderer), /Conheça os planos/);
  assert.equal(button(renderer, 'Tentar novamente'), undefined);
});

test('case detail: an empty successful payload is not an empty lesson and can be reloaded', async t => {
  let valid = false, calls = 0;
  const h = harness(async url => {
    if (url.includes('/favorites/')) return json({ available: true, favorited: false, favorite_id: null });
    calls++;
    return json({ slug: 'caso-a', titulo: 'CASE DEMO', enunciado: valid ? 'BODY AVAILABLE' : '', pergunta: 'QUESTION', opcoes: ['OPTION'], source_refs: [] });
  });
  const renderer = await mount(t, h.load('pages/CasoClinico.tsx').default);
  assert.ok(renderer.root.findAllByProps({ role: 'alert' }).length);
  assert.equal(button(renderer, 'Confirmar resposta'), undefined);
  valid = true;
  await act(async () => button(renderer, 'Tentar novamente').props.onClick());
  assert.equal(calls, 2); assert.match(text(renderer), /BODY AVAILABLE/);
});

test('case answer: a late submission cannot populate a different case and double click sends once', async t => {
  const response = deferred(); let posts = 0;
  const h = harness((url, init) => {
    if (init.method === 'POST') { posts++; return response.promise; }
    if (url.includes('/favorites/')) return Promise.resolve(json({ available: true, favorited: false, favorite_id: null }));
    const slug = url.split('/').at(-1);
    return Promise.resolve(json({ slug, titulo: slug, enunciado: `BODY ${slug}`, pergunta: 'QUESTION', opcoes: ['OPTION'], source_refs: [] }));
  });
  const Case = h.load('pages/CasoClinico.tsx').default;
  const renderer = await mount(t, Case);
  await act(async () => button(renderer, 'OPTION').props.onClick());
  const submit = button(renderer, 'Confirmar resposta').props.onClick;
  await act(async () => { void submit(); void submit(); });
  assert.equal(posts, 1);
  h.fixture.slug = 'caso-b';
  await act(async () => renderer.update(React.createElement(Case)));
  await act(async () => response.resolve(json({ acertou: true, resposta_correta: 0, explicacao: 'EXPLANATION FROM CASE A' })));
  assert.match(text(renderer), /BODY caso-b/); assert.doesNotMatch(text(renderer), /EXPLANATION FROM CASE A/);
  assert.equal(button(renderer, 'Confirmar resposta').props.disabled, true);
});
