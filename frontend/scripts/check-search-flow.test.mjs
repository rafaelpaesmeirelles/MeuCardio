import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import ts from 'typescript';

const require = createRequire(import.meta.url);
// Optional isolated dependency location for installations missing dev packages.
const rendererRequire = process.env.CORVIA_TEST_RENDERER_ROOT
  ? createRequire(path.join(process.env.CORVIA_TEST_RENDERER_ROOT, 'package.json'))
  : require;
const TestRenderer = rendererRequire('react-test-renderer');
const { act } = TestRenderer;
const root = fileURLToPath(new URL('../', import.meta.url));
const temp = await mkdtemp(path.join(tmpdir(), 'corvia-search-flow-'));
await symlink(path.join(root, 'node_modules'), path.join(temp, 'node_modules'));
after(() => rm(temp, { recursive: true, force: true }));

function transpile(source, name) {
  return ts.transpileModule(source, {
    fileName: name,
    compilerOptions: {
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
      jsx: ts.JsxEmit.ReactJSX,
    },
  }).outputText;
}
const anchors = await readFile(path.join(root, 'src/lib/searchAnchors.ts'), 'utf8');
await writeFile(path.join(temp, 'searchAnchors.mjs'), transpile(anchors, 'searchAnchors.ts'));
let source = await readFile(path.join(root, 'src/pages/Busca.tsx'), 'utf8');
assert.ok(source.includes('import { api, ApiError, PaginaDe } from "../lib/api";'));
source = source.replace('import { api, ApiError, PaginaDe } from "../lib/api";', `
const api = { get: (...args) => globalThis.corviaSearchFixture.get(...args) };
class ApiError extends Error {}
`);
source = source.replace('import { Carregando, Erro, Vazio } from "../components/Estado";', `
const Carregando = () => <p role="status">Carregando</p>;
const Erro = ({ mensagem }) => <p role="alert">{mensagem}</p>;
const Vazio = ({ titulo }) => <p>{titulo}</p>;
`);
source = source.replace('"../lib/searchAnchors"', '"./searchAnchors.mjs"');
await writeFile(path.join(temp, 'Busca.mjs'), transpile(source, 'Busca.tsx'));
const { default: Busca } = await import(pathToFileURL(path.join(temp, 'Busca.mjs')));

const tick = () => new Promise(resolve => setImmediate(resolve));
const nodeText = node => typeof node === 'string' ? node : (node.children ?? []).map(nodeText).join('');
const more = renderer => renderer.root.findAllByType('button')
  .find(button => /Carregar mais|Conectando mais/.test(nodeText(button)));
const item = (slug, title, frente = 'documento') => ({
  slug, title, frente, kind: 'protocolo', theme: 'Teste', snippet: '',
});
const page = (results, total = results.length, next_offset = null, extra = {}) => ({
  results, total, next_offset, por_frente: {}, ...extra,
});
function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
}
async function mount(t, query, get) {
  const calls = [];
  globalThis.corviaSearchFixture = {
    get: url => { calls.push(url); return get(url); },
  };
  let renderer;
  await act(async () => {
    renderer = TestRenderer.create(React.createElement(MemoryRouter, {
      initialEntries: [`/busca?q=${encodeURIComponent(query)}`],
      future: { v7_startTransition: true, v7_relativeSplatPath: true },
    }, React.createElement(Busca)));
    await tick();
  });
  t.after(async () => { await act(async () => renderer.unmount()); });
  return { renderer, calls };
}
async function submit(renderer, query) {
  await act(async () => renderer.root.findByType('input').props.onChange({ target: { value: query } }));
  await act(async () => {
    renderer.root.findByType('form').props.onSubmit({ preventDefault() {} });
    await tick();
  });
}

test('changing subject during pagination unlocks the new page and rejects stale results', async t => {
  const pending = deferred();
  const { renderer, calls } = await mount(t, 'alfa', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    const params = new URL(url, 'https://test.invalid').searchParams;
    if (params.get('q') === 'alfa') return params.has('offset')
      ? pending.promise : page([item('alfa-inicial', 'Conteúdo inicial alfa')], 2, 1);
    if (params.get('q') === 'beta') return params.has('offset')
      ? page([item('beta-final', 'Conteúdo final beta')], 2)
      : page([item('beta-inicial', 'Conteúdo inicial beta')], 2, 1);
    throw Error(`Unexpected request: ${url}`);
  });
  await act(async () => { void more(renderer).props.onClick(); await tick(); });
  assert.equal(more(renderer).props.disabled, true);
  await submit(renderer, 'beta');
  assert.equal(more(renderer).props.disabled, false);
  await act(async () => {
    pending.resolve(page([item('obsoleto', 'Resultado obsoleto alfa')], 2));
    await tick();
  });
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Resultado obsoleto/);
  assert.equal(more(renderer).props.disabled, false);
  await act(async () => more(renderer).props.onClick());
  assert.match(nodeText(renderer.toJSON()), /Conteúdo final beta/);
  assert.ok(calls.some(url => url.includes('q=beta') && url.includes('offset=1')));
});

test('a later lexical page removes the same item from connected groups', async t => {
  const document = item('monitorizacao-prolongada', 'Monitorização prolongada');
  const { renderer } = await mount(t, 'Holter 24h', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url.startsWith('/relacionados/ecossistema?')) return {
      total: 1,
      grupos: [{ tipo: 'documento', rotulo: 'Documentos', rota_lista: '/biblioteca', itens: [{
        slug: document.slug, titulo: document.title, rota: `/biblioteca/${document.slug}`,
      }] }],
    };
    if (url.startsWith('/search?')) return url.includes('offset=')
      ? page([document], 2)
      : page([item('holter-24h', 'Holter 24h', 'exame')], 2, 1);
    throw Error(`Unexpected request: ${url}`);
  });
  const links = () => renderer.root.findAllByType('a')
    .filter(link => link.props.href === `/biblioteca/${document.slug}`);
  assert.equal(links().length, 1);
  await act(async () => more(renderer).props.onClick());
  assert.equal(links().length, 1);
  assert.equal(more(renderer), undefined);
});

test('a primary drug uses the paginated search and does not request a second ecosystem', async t => {
  const drug = {
    slug: 'olmesartana', generic_name: 'Olmesartana', drug_class: 'BRA',
    presentations: [], dosing: {}, indications: [], contraindications: [],
    interactions: [], monitoring: [], adverse_effects: [],
  };
  const { renderer, calls } = await mount(t, 'olmesartana', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url === '/drug-insights/olmesartana') return drug;
    if (url.startsWith('/search?')) return page(
      [item(drug.slug, drug.generic_name, 'medicamento')], 1, null,
      { primary_drug: drug, supplementary_groups: [] },
    );
    throw Error(`Unexpected request: ${url}`);
  });
  assert.match(nodeText(renderer.toJSON()), /Medicamento identificado/);
  assert.equal(calls.filter(url => url === '/drug-insights/olmesartana').length, 1);
  assert.equal(calls.filter(url => url.startsWith('/relacionados/') || url.startsWith('/grafo/')).length, 0);
});
