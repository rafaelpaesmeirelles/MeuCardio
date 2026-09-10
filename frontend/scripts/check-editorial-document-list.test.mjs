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
let source = await readFile(path.join(root, 'src/components/EditorialDocumentList.tsx'), 'utf8');
source = source.replace('import { api, ApiError } from "../lib/api";', `
const api = { get: (...args) => globalThis.corviaSearchFixture.get(...args) };
class ApiError extends Error {}
`);
await writeFile(path.join(temp, 'EditorialDocumentList.mjs'), transpile(source, 'EditorialDocumentList.tsx'));
const { default: EditorialDocumentList } = await import(pathToFileURL(path.join(temp, 'EditorialDocumentList.mjs')));
const tick = () => new Promise(resolve => setTimeout(resolve, 220));
const nodeText = node => typeof node === 'string' ? node : (node.children ?? []).map(nodeText).join('');
function deferred() { let resolve; const promise = new Promise(done => { resolve = done; }); return { promise, resolve }; }
async function mount(t, get, props = {}) {
  const calls = [];
  globalThis.corviaSearchFixture = { get: url => { calls.push(url); return get(url); } };
  let renderer;
  await act(async () => {
    renderer = TestRenderer.create(React.createElement(MemoryRouter, { future: { v7_startTransition: true, v7_relativeSplatPath: true } },
      React.createElement(EditorialDocumentList, { section: 'diretriz', title: 'Diretrizes e consensos da Biblioteca', ...props })));
  });
  // Flush mount effects before waiting for the component's debounce timer.
  await act(async () => { await tick(); });
  t.after(async () => { await act(async () => renderer.unmount()); });
  return { renderer, calls };
}
const doc = (slug, kind = 'consenso') => ({ slug, title: slug, theme: 'FA', kind });

test('guidelines collection includes consensus and independently paginates canonical Library links', async t => {
  const { renderer, calls } = await mount(t, async url => {
    const p = new URL(url, 'https://test.invalid').searchParams;
    assert.equal(p.get('secao'), 'diretriz');
    assert.equal(p.has('kind'), false);
    return p.get('offset') === '0' ? { items: [doc('consenso')], total: 2, next_offset: 1 }
      : { items: [doc('consenso'), doc('diretriz', 'diretriz')], total: 2, next_offset: null };
  });
  assert.match(nodeText(renderer.toJSON()), /1 de 2 documentos carregados/);
  await act(async () => { renderer.root.findByType('button').props.onClick(); await tick(); });
  assert.match(nodeText(renderer.toJSON()), /2 de 2 documentos carregados/);
  assert.deepEqual(renderer.root.findAllByType('a').map(a => a.props.href), ['/biblioteca/consenso', '/biblioteca/diretriz']);
  assert.equal(renderer.root.findAllByType('button').length, 0);
  assert.ok(calls.some(url => url.includes('offset=1')));
});

test('filter change discards stale pagination and retries its own failed request', async t => {
  const stale = deferred(); let newCalls = 0;
  const { renderer } = await mount(t, async url => {
    const p = new URL(url, 'https://test.invalid').searchParams;
    if (p.get('q') === 'novo') {
      if (++newCalls === 1) throw Error('temporary');
      return { items: [doc('resultado-novo')], total: 1, next_offset: null };
    }
    return p.get('offset') === '0' ? { items: [doc('inicial')], total: 2, next_offset: 1 } : stale.promise;
  });
  await act(async () => { renderer.root.findByType('button').props.onClick(); await Promise.resolve(); });
  await act(async () => { renderer.root.findByType('input').props.onChange({ target: { value: 'novo' } }); });
  await act(async () => { await tick(); });
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 1);
  await act(async () => { stale.resolve({ items: [doc('obsoleto')], total: 2, next_offset: null }); await tick(); });
  assert.doesNotMatch(nodeText(renderer.toJSON()), /obsoleto/);
  await act(async () => { renderer.root.findByType('button').props.onClick(); await tick(); });
  assert.match(nodeText(renderer.toJSON()), /resultado-novo/);
  assert.doesNotMatch(nodeText(renderer.toJSON()), /inicial|obsoleto/);
});


test('controlled study search and theme reach Library without a second input', async t => {
  const { renderer, calls } = await mount(t, async () => ({ items: [doc('trial', 'estudo')], total: 1, next_offset: null }),
    { section: 'estudo', title: 'Estudos e revisões da Biblioteca', query: 'fibrilação', theme: 'FA' });
  assert.equal(renderer.root.findAllByType('input').length, 0);
  const params = new URL(calls[0], 'https://test.invalid').searchParams;
  assert.equal(params.get('q'), 'fibrilação', JSON.stringify(calls)); assert.equal(params.get('theme'), 'FA');
  assert.equal(params.get('secao'), 'estudo');
  assert.equal(renderer.root.findByType('a').props.href, '/biblioteca/trial');
});

test('formal ScientificStudy entries use the studies API and preserve their canonical route', async t => {
  const { renderer, calls } = await mount(t, async () => ({ items: [{ slug: 'sepsis-3', title: 'Sepsis-3', study_type: 'consenso', theme: 'Sepse' }], total: 1, next_offset: null }),
    { source: 'studies', query: 'sepse' });
  assert.ok(calls[0].startsWith('/studies?'));
  assert.equal(new URL(calls[0], 'https://test.invalid').searchParams.get('secao'), 'diretriz');
  assert.equal(renderer.root.findByType('a').props.href, '/estudos/sepsis-3');
});
