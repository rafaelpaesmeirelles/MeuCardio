import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { MemoryRouter, Routes, Route, useNavigate } from 'react-router-dom';

// Componentes, router e cliente API reais. Fetch/relógio são inteiramente
// locais; conteúdo técnico fictício, sem rede, paciente, IA ou escrita real.
const require = createRequire(import.meta.url);
const text = renderer => JSON.stringify(renderer.toJSON());
const textOf = node => typeof node === 'string' ? node : (node.children ?? []).map(textOf).join('');
const button = (renderer, label) => renderer.root.findAllByType('button').find(node => textOf(node).includes(label));
const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const deferred = () => { let resolve; const promise = new Promise(done => { resolve = done; }); return { promise, resolve }; };
const pending = (_url, init) => new Promise((_resolve, reject) => {
  const abort = () => reject(new DOMException('Aborted fixture', 'AbortError'));
  if (init.signal?.aborted) abort();
  else init.signal?.addEventListener('abort', abort, { once: true });
});
const emptyPage = { items: [], total: 0, next_offset: null, has_more: false };
const technical = (slug, extra = {}) => ({ slug, title: `TÍTULO ${slug}`, statement: `TÍTULO ${slug}`, summary: '',
  body_md: `CORPO ${slug}`, theme: 'Coleção técnica demonstrativa', kind: 'documento', review_status: 'revisado',
  source_refs: [], version: 1, study_type: 'ensaio_clinico', journal: 'Fixture de interface', year: 2026,
  recommendation_class: 'I', evidence_level: 'A', society: 'Fixture', key_findings: `CORPO ${slug}`,
  clinical_implications: '', reference: 'Fixture técnica, sem recomendação clínica', tags: [], ...extra });

function harness(fetcher) {
  const timers = new Map(), calls = [], cache = new Map();
  let timerId = 0, navigate;
  const window = Object.assign(new EventTarget(), {
    localStorage: { removeItem() {}, getItem() { return null; } },
    location: { pathname: '/biblioteca', assign() { throw Error('Unexpected auth redirect'); } },
    setTimeout: (fn, ms) => { const id = ++timerId; timers.set(id, { fn, ms }); return id; },
    clearTimeout: id => timers.delete(id), confirm: () => false,
  });
  const passthrough = ({ children, title, description }) => React.createElement('section', null,
    title && React.createElement('h2', null, title), description && React.createElement('p', null, description), children);
  const noSideEffects = new Set(['BotaoFavorito', 'ScientificReadingAccess', 'TudoSobreEsteTema', 'GrafoRelacionados',
    'Fluxograma', 'ExportarApresentacao', 'ClinicalUpdates', 'PrivateScientificOriginal']);
  function load(relative) {
    if (cache.has(relative)) return cache.get(relative);
    const source = readFileSync(new URL(`../src/${relative}`, import.meta.url), 'utf8').replaceAll('import.meta.env', '({})');
    const compiled = ts.transpileModule(source, { fileName: relative, compilerOptions: {
      module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true,
    } }).outputText;
    const module = { exports: {} };
    vm.runInNewContext(compiled, {
      module, exports: module.exports, window, document: { getElementById: () => null },
      requestAnimationFrame: () => 0, Headers, Response, FormData, AbortController, DOMException, URLSearchParams,
      setTimeout: window.setTimeout, clearTimeout: window.clearTimeout,
      fetch: (url, init) => { calls.push({ url, init }); return fetcher(url, init); },
      require: name => {
        if (name.endsWith('.css')) return {};
        if (name === '../lib/auth') return { useAuth: () => ({ usuario: { id: 990001 } }) };
        if (name === './clinicalCache') return { clearLegacyClinicalCaches() {} };
        const base = name.split('/').at(-1);
        if (noSideEffects.has(base)) return { __esModule: true, default: () => null };
        if (base === 'ClinicalText') return { __esModule: true, default: ({ children }) => React.createElement('p', null, children) };
        if (base === 'Icone') return { __esModule: true, default: () => null };
        if (base === 'ClinicalCommandPrimitives') return Object.fromEntries(
          ['ClinicalContextLink', 'ClinicalEmpty', 'ClinicalMetric', 'ClinicalPageHeader', 'ClinicalSection'].map(key => [key, passthrough]));
        if (name === 'react-markdown') return { __esModule: true, default: ({ children }) => React.createElement('div', null, children) };
        if (name === 'remark-gfm') return { __esModule: true, default: () => {} };
        if (name.startsWith('.')) {
          const target = path.posix.normalize(path.posix.join(path.posix.dirname(relative), name));
          return load(`${target}.${target.startsWith('components/') ? 'tsx' : 'ts'}`);
        }
        return require(name);
      },
    }, { filename: relative });
    cache.set(relative, module.exports); return module.exports;
  }
  function Navigation() { navigate = useNavigate(); return null; }
  return { calls, load, timers,
    async mount(t, relative, { url = '/', route = '*', props = {} } = {}) {
      const Component = load(relative).default;
      let renderer;
      await act(async () => { renderer = TestRenderer.create(React.createElement(MemoryRouter,
        { initialEntries: [url], future: { v7_startTransition: true, v7_relativeSplatPath: true } },
        React.createElement(Navigation), React.createElement(Routes, null,
          React.createElement(Route, { path: route, element: React.createElement(Component, props) })))); });
      t.after(async () => { await act(async () => renderer.unmount()); });
      return renderer;
    },
    async go(url) { await act(async () => navigate(url)); },
    async advance(ms) { await act(async () => {
      for (const [id, timer] of [...timers]) if (timer.ms <= ms && timers.has(id)) { timers.delete(id); timer.fn(); }
    }); },
  };
}

for (const [name, route, endpoint] of [
  ['Documento', '/biblioteca', '/library/documents'], ['Estudo', '/estudos', '/studies'], ['Evidencia', '/evidencias', '/evidence'],
]) {
  test(`${name}: pending detail ends in visible error and manual retry`, async t => {
    let retry = false;
    const h = harness((url, init) => retry ? Promise.resolve(json(technical('b'))) : pending(url, init));
    const renderer = await h.mount(t, `pages/${name}.tsx`, { url: `${route}/b`, route: `${route}/:slug` });
    await h.advance(15000);
    assert.match(text(renderer), /demorou mais/); assert.ok(button(renderer, 'Tentar novamente'));
    retry = true;
    await act(async () => button(renderer, 'Tentar novamente').props.onClick());
    assert.match(text(renderer), /TÍTULO b/);
    assert.equal(h.calls.length, 2); assert.equal(h.calls[0].url, `/api${endpoint}/b`);
  });
  test(`${name}: A is absent immediately on B and late A cannot replace B`, async t => {
    const old = deferred();
    const h = harness(url => url.endsWith('/a') ? old.promise : Promise.resolve(json(technical('b'))));
    const renderer = await h.mount(t, `pages/${name}.tsx`, { url: `${route}/a`, route: `${route}/:slug` });
    await h.go(`${route}/b`);
    assert.match(text(renderer), /TÍTULO b/);
    await act(async () => old.resolve(json(technical('a'))));
    assert.doesNotMatch(text(renderer), /TÍTULO a|CORPO a/);
    assert.equal(h.calls[0].init.signal.aborted, true);
  });
}

const listConfigs = [
  { name: 'Biblioteca', endpoint: '/library/documents', initial: '/', more: 'Carregar mais documentos', retry: 'Tentar carregar documentos novamente' },
  { name: 'Estudos', endpoint: '/studies', initial: '/', more: 'Carregar mais ·', retry: 'Tentar carregar estudos novamente' },
  { name: 'Evidencias', endpoint: '/evidence', initial: '/', more: 'Revelar mais recomendações', retry: 'Revelar mais recomendações' },
];
function auxiliary(url) {
  if (url.includes('secao=')) return emptyPage;
  if (url.endsWith('/catalog')) return { total: 0, fronts: [] };
  if (url.endsWith('/area-counts')) return { areas: [] };
  return [];
}
for (const config of listConfigs) {
  const primary = url => url.split('?')[0] === `/api${config.endpoint}` && !url.includes('secao=');
  test(`${config.name}: pending first page exits loading and explicit retry recovers`, async t => {
    let retry = false;
    const h = harness((url, init) => !primary(url) ? Promise.resolve(json(auxiliary(url)))
      : retry ? Promise.resolve(json({ ...emptyPage, items: [technical('first')], total: 1 })) : pending(url, init));
    const renderer = await h.mount(t, `pages/${config.name}.tsx`);
    await h.advance(300); await h.advance(15000);
    assert.match(text(renderer), /demorou mais/);
    retry = true;
    await act(async () => button(renderer, config.name === 'Evidencias' ? 'Tentar novamente' : config.retry).props.onClick());
    await h.advance(300);
    assert.match(text(renderer), /TÍTULO first/);
    assert.equal(h.calls.filter(call => primary(call.url)).length, 2);
  });
  test(`${config.name}: next-page deadline preserves earlier items and cursor without double dispatch`, async t => {
    let retry = false;
    const h = harness((url, init) => {
      if (!primary(url)) return Promise.resolve(json(auxiliary(url)));
      if (!url.includes('offset=1')) return Promise.resolve(json({ items: [technical('first')], total: 2, next_offset: 1 }));
      return retry ? Promise.resolve(json({ ...emptyPage, items: [technical('second')], total: 2 })) : pending(url, init);
    });
    const renderer = await h.mount(t, `pages/${config.name}.tsx`);
    await h.advance(300);
    const next = button(renderer, config.more); assert.ok(next);
    await act(async () => { next.props.onClick(); next.props.onClick(); });
    await h.advance(15000);
    assert.match(text(renderer), /TÍTULO first/); assert.match(text(renderer), /demorou mais/);
    assert.equal(h.calls.filter(call => primary(call.url) && call.url.includes('offset=1')).length, 1);
    retry = true;
    await act(async () => button(renderer, config.retry).props.onClick());
    assert.match(text(renderer), /TÍTULO first/); assert.match(text(renderer), /TÍTULO second/);
  });
}

test('editorial collection: next-page timeout preserves its own collection and retries', async t => {
  let retry = false;
  const h = harness((url, init) => !url.includes('offset=1') ? Promise.resolve(json({ items: [technical('first')], total: 2, next_offset: 1 }))
    : retry ? Promise.resolve(json({ ...emptyPage, items: [technical('second')], total: 2 })) : pending(url, init));
  const renderer = await h.mount(t, 'components/EditorialDocumentList.tsx', { props: { section: 'diretriz', title: 'Coleção técnica' } });
  await h.advance(200);
  await act(async () => button(renderer, 'Carregar mais documentos').props.onClick());
  await h.advance(15000);
  assert.match(text(renderer), /TÍTULO first/); assert.ok(button(renderer, 'Tentar novamente'));
  retry = true;
  await act(async () => button(renderer, 'Tentar novamente').props.onClick());
  assert.match(text(renderer), /TÍTULO second/);
});

test('Diretrizes: a personal-alert timeout never hides the available publication list', async t => {
  let retry = false;
  const publication = { id: 1, slug: 'demo', org: 'Fixture', title: 'PUBLICAÇÃO TÉCNICA', published_at: '2026-01-01',
    key_changes: [], limitations: [], impacts: [], status: 'detected' };
  const h = harness((url, init) => {
    if (url === '/api/guideline-updates') return Promise.resolve(json({ cutoff: '2026-01-01', items: [publication] }));
    if (url.includes('/guideline-updates/me')) return retry ? Promise.resolve(json({ items: [] })) : pending(url, init);
    return Promise.resolve(json(emptyPage));
  });
  const renderer = await h.mount(t, 'pages/Diretrizes.tsx');
  assert.match(text(renderer), /PUBLICAÇÃO TÉCNICA/);
  await h.advance(15000);
  assert.match(text(renderer), /PUBLICAÇÃO TÉCNICA/); assert.match(text(renderer), /demorou mais/);
  retry = true;
  await act(async () => button(renderer, 'Tentar novamente').props.onClick());
  assert.match(text(renderer), /PUBLICAÇÃO TÉCNICA/); assert.doesNotMatch(text(renderer), /demorou mais/);
});

test('scientific monitor: pending status becomes an explicit retry without inventing health', async t => {
  let retry = false;
  const h = harness((url, init) => retry ? Promise.resolve(json({ enabled: false, health: 'inactive', cadence_hours: 4,
    recent_discoveries: [], total_discovered: 0, pending_analysis: 0 })) : pending(url, init));
  const renderer = await h.mount(t, 'components/ScientificIntelligenceMonitor.tsx');
  await h.advance(15000);
  assert.match(text(renderer), /Não foi possível confirmar/); assert.doesNotMatch(text(renderer), /Consultando o monitoramento/);
  retry = true;
  await act(async () => button(renderer, 'Tentar novamente').props.onClick());
  assert.equal(button(renderer, 'Tentar novamente'), undefined);
});

const privateDoc = id => ({ id, title: `PRIVADO ${id}`, document_type: 'Fixture técnica', analysis_status: 'pendente',
  incorporation_status: 'privado', incorporation_recommended: false });
test('private scientific list: timeout is not an empty library, retry stays read-only', async t => {
  let retry = false;
  const h = harness((url, init) => retry ? Promise.resolve(json([privateDoc(1)])) : pending(url, init));
  const renderer = await h.mount(t, 'pages/ScientificDocumentAI.tsx');
  assert.doesNotMatch(text(renderer), /Nenhum documento enviado/);
  await h.advance(15000);
  assert.doesNotMatch(text(renderer), /Nenhum documento enviado/); assert.match(text(renderer), /demorou mais/);
  retry = true;
  await act(async () => button(renderer, 'Tentar carregar biblioteca novamente').props.onClick());
  assert.match(text(renderer), /PRIVADO 1/);
  assert.ok(h.calls.every(call => call.init.method === undefined));
});
test('private scientific detail: timeout has a local retry, A → B discards late A', async t => {
  let retry = false;
  const a = deferred();
  const h = harness((url, init) => {
    if (url === '/api/documentos-cientificos-ia') return Promise.resolve(json([privateDoc(1), privateDoc(2)]));
    if (url.endsWith('/1')) return a.promise;
    return retry ? Promise.resolve(json(privateDoc(2))) : pending(url, init);
  });
  const renderer = await h.mount(t, 'pages/ScientificDocumentAI.tsx', { url: '/?document=1' });
  await h.go('/?document=2'); await h.advance(15000);
  assert.match(text(renderer), /demorou mais/); assert.ok(button(renderer, 'Tentar carregar documento novamente'));
  retry = true;
  await act(async () => button(renderer, 'Tentar carregar documento novamente').props.onClick());
  await act(async () => a.resolve(json(privateDoc(1))));
  const headings = renderer.root.findAllByType('h2').map(textOf);
  assert.ok(headings.includes('PRIVADO 2')); assert.ok(!headings.includes('PRIVADO 1'));
});

test('Diretrizes: a stale retry cannot resurrect an alert after a confirmed read', async t => {
  const oldAlerts = deferred();
  const publication = { id: 1, slug: 'demo', org: 'Fixture', title: 'ALERTA TÉCNICO', published_at: '2026-01-01',
    key_changes: [], limitations: [], impacts: [], status: 'detected' };
  const alerts = { items: [{ notification_id: 41, read_at: null, guideline: publication, message: 'Fixture técnica' }] };
  let reads = 0, publications = 0;
  const h = harness(url => {
    if (url.endsWith('/41/read')) return Promise.resolve(json({ notification_id: 41, read_at: '2026-09-11T00:00:00Z' }));
    if (url.includes('/guideline-updates/me')) return ++reads === 1 ? Promise.resolve(json(alerts)) : oldAlerts.promise;
    if (url === '/api/guideline-updates') return Promise.resolve(++publications === 1 ? json({ detail: 'indisponível' }, 503) : json({ cutoff: '2026-01-01', items: [] }));
    return Promise.resolve(json(emptyPage));
  });
  const renderer = await h.mount(t, 'pages/Diretrizes.tsx');
  assert.ok(button(renderer, 'Marcar como lido'));
  await act(async () => button(renderer, 'Tentar novamente').props.onClick());
  await act(async () => button(renderer, 'Marcar como lido').props.onClick());
  assert.equal(button(renderer, 'Marcar como lido'), undefined);
  await act(async () => oldAlerts.resolve(json(alerts)));
  assert.equal(button(renderer, 'Marcar como lido'), undefined);
  assert.equal(h.calls.filter(call => call.init.method === 'POST').length, 1);
});

test('private scientific analysis: confirmed result survives refresh timeout and retry only reads', async t => {
  let analyzed = false, retry = false;
  const confirmed = { ...privateDoc(1), analysis_status: 'concluido', summary_pt: 'RESULTADO TÉCNICO CONFIRMADO', analysis: {} };
  const h = harness((url, init) => {
    if (url.endsWith('/orcamento')) return Promise.resolve(json({ quote_id: 31, maximum_credit_centavos: 650,
      available_credit_centavos: 4000, currency: 'BRL', expires_at: new Date(Date.now() + 600000).toISOString() }));
    if (url.endsWith('/analisar')) { analyzed = true; return Promise.resolve(json(confirmed)); }
    if (url === '/api/documentos-cientificos-ia') return Promise.resolve(json([privateDoc(1)]));
    return analyzed && !retry ? pending(url, init) : Promise.resolve(json(analyzed ? confirmed : privateDoc(1)));
  });
  const renderer = await h.mount(t, 'pages/ScientificDocumentAI.tsx', { url: '/?document=1' });
  await act(async () => button(renderer, 'Calcular orçamento').props.onClick());
  await act(async () => { button(renderer, 'Confirmar análise').props.onClick(); });
  assert.match(text(renderer), /RESULTADO TÉCNICO CONFIRMADO/);
  await h.advance(15000);
  assert.match(text(renderer), /Análise concluída/); assert.match(text(renderer), /RESULTADO TÉCNICO CONFIRMADO/);
  assert.match(text(renderer), /demorou mais/);
  assert.equal(button(renderer, 'Confirmar análise'), undefined);
  const writes = h.calls.filter(call => call.init.method === 'POST').length;
  await act(async () => { button(renderer, 'Tentar carregar documento novamente').props.onClick(); });
  assert.match(text(renderer), /RESULTADO TÉCNICO CONFIRMADO/);
  await h.advance(15000);
  retry = true;
  await act(async () => button(renderer, 'Tentar carregar documento novamente').props.onClick());
  assert.match(text(renderer), /RESULTADO TÉCNICO CONFIRMADO/); assert.doesNotMatch(text(renderer), /demorou mais/);
  assert.equal(h.calls.filter(call => call.init.method === 'POST').length, writes);
  assert.equal(writes, 2, 'only the explicit budget and analysis actions are POSTs');
});

test('private scientific detail retry and mutations cannot overlap in either direction', async t => {
  let analyzed = false, pendingQuote = false;
  const slowQuote = deferred();
  const quote = { quote_id: 31, maximum_credit_centavos: 650, available_credit_centavos: 4000,
    currency: 'BRL', expires_at: new Date(Date.now() + 600000).toISOString() };
  const confirmed = { ...privateDoc(1), analysis_status: 'concluido', summary_pt: 'RESULTADO CONFIRMADO',
    incorporation_recommended: true, incorporation_status: 'aguardando_consentimento', analysis: {} };
  const h = harness((url, init) => {
    if (url.endsWith('/orcamento')) return pendingQuote ? slowQuote.promise : Promise.resolve(json(quote));
    if (url.endsWith('/analisar')) { analyzed = true; return Promise.resolve(json(confirmed)); }
    if (url === '/api/documentos-cientificos-ia') return Promise.resolve(json([privateDoc(1)]));
    return analyzed ? pending(url, init) : Promise.resolve(json(privateDoc(1)));
  });
  const renderer = await h.mount(t, 'pages/ScientificDocumentAI.tsx', { url: '/?document=1' });
  await act(async () => button(renderer, 'Calcular orçamento').props.onClick());
  await act(async () => { button(renderer, 'Confirmar análise').props.onClick(); });
  await h.advance(15000);
  await act(async () => button(renderer, 'Tentar carregar documento novamente').props.onClick());
  const writesBefore = h.calls.filter(call => call.init.method === 'POST').length;
  for (const label of ['Calcular orçamento', 'Autorizar incorporação', 'Salvar na biblioteca']) {
    const control = button(renderer, label);
    assert.equal(control.props.disabled, true, label);
    await act(async () => control.props.onClick());
  }
  assert.equal(h.calls.filter(call => call.init.method === 'POST').length, writesBefore);
  assert.equal(button(renderer, 'Confirmar análise'), undefined);
  await h.advance(15000);
  pendingQuote = true;
  await act(async () => { button(renderer, 'Calcular orçamento').props.onClick(); });
  const retryControl = button(renderer, 'Tentar carregar documento novamente');
  assert.equal(retryControl.props.disabled, true);
  const callsBefore = h.calls.length;
  await act(async () => retryControl.props.onClick());
  assert.equal(h.calls.length, callsBefore, 'retry cannot invalidate an authorized POST in flight');
  await act(async () => slowQuote.resolve(json(quote)));
  assert.ok(button(renderer, 'Confirmar análise'), 'the confirmed quote was not discarded by a disabled retry');
  assert.match(text(renderer), /RESULTADO CONFIRMADO/);
});
