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
const rendererRequire = process.env.CORVIA_TEST_RENDERER_ROOT ? createRequire(path.join(process.env.CORVIA_TEST_RENDERER_ROOT, 'package.json')) : require;
const { default: TestRenderer } = { default: rendererRequire('react-test-renderer') };
const { act } = TestRenderer;
const root = fileURLToPath(new URL('../', import.meta.url));
const temp = await mkdtemp(path.join(tmpdir(), 'corvia-scientific-reading-'));
await symlink(path.join(root, 'node_modules'), path.join(temp, 'node_modules'));
after(() => rm(temp, { recursive: true, force: true }));
let source = await readFile(path.join(root, 'src/components/ScientificReadingAccess.tsx'), 'utf8');
source = source.replace('import { api } from "../lib/api";', 'const api = { get: (...args) => globalThis.readingFixture.get(...args), blob: (...args) => globalThis.readingFixture.blob(...args) };');
source = source.replace('import "../styles/scientific-reading-access.css";', '');
await writeFile(path.join(temp, 'Reading.mjs'), ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX } }).outputText);
const { default: Reading } = await import(pathToFileURL(path.join(temp, 'Reading.mjs')));
const text = n => typeof n === 'string' ? n : (n?.children ?? []).map(text).join('');
const button = (r, label) => r.root.findAllByType('button').find(b => text(b.toJSON?.() ?? { children: b.children.map(x => typeof x === 'string' ? x : '') }).includes(label));
const fixture = (slug = 'trial') => ({ entity_type: 'estudo', slug, summary_pt: { status: 'available', text: 'Síntese editorial do conjunto', origin: 'corvia_editorial' }, sources: [{ key: 'a', doi: '10.1/a', original: { status: 'source_only', url: 'https://publisher.test/a' }, translation_pt: { status: 'pending' }, summary_pt: { status: 'unavailable', text: null } }, { key: 'b', doi: '10.1/b', original: { status: 'available', url: '/api/scientific-reading/estudo/trial/sources/b/original', media_type: 'application/xml' }, translation_pt: { status: 'available', url: '/api/scientific-reading/estudo/trial/sources/b/translation' }, summary_pt: { status: 'available', text: 'Resumo específico B' } }] });
async function mount(t, get = async () => fixture(), props = {}, blob = async () => new Blob(['Texto integral B'], { type: 'text/plain' })) {
  const calls = [], blobs = [];
  globalThis.readingFixture = { get: p => { calls.push(p); return get(p); }, blob: p => { blobs.push(p); return blob(p); } };
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(MemoryRouter, { future: { v7_startTransition: true, v7_relativeSplatPath: true } }, React.createElement(Reading, { entityType: 'estudo', slug: 'trial', ...props }))); });
  t.after(async () => { await act(async () => renderer.unmount()); });
  return { renderer, calls, blobs };
}

test('list cards load no scientific source until explicitly opened', async t => {
  const { renderer, calls } = await mount(t, undefined, { lazy: true });
  assert.equal(calls.length, 0);
  await act(async () => { button(renderer, 'Resumo em português').props.onClick(); });
  assert.equal(calls.length, 1);
  assert.match(text(renderer.toJSON()), /Em processamento/);
});

test('editorial summary never impersonates a source summary or full translation', async t => {
  const { renderer } = await mount(t);
  assert.equal(button(renderer, 'Tradução integral').props.disabled, true);
  assert.equal(button(renderer, 'Resumo em português').props.disabled, true);
  await act(async () => { button(renderer, 'Resumo editorial').props.onClick(); });
  assert.match(text(renderer.toJSON()), /Resumo editorial CorVIA em português/);
  assert.match(text(renderer.toJSON()), /Síntese editorial do conjunto/);
  assert.equal(renderer.root.findAllByType('a').find(a => a.props.href.startsWith('https:')).props.href, 'https://publisher.test/a');
});

test('multiple sources retain their own summary and authenticated translation', async t => {
  const { renderer, blobs } = await mount(t);
  await act(async () => { renderer.root.findByType('select').props.onChange({ target: { value: 'b' } }); });
  await act(async () => { button(renderer, 'Resumo em português').props.onClick(); });
  assert.match(text(renderer.toJSON()), /Resumo específico B/);
  assert.match(text(renderer.toJSON()), /Baixar original \(XML\)/);
  await act(async () => { await button(renderer, 'Tradução integral').props.onClick(); });
  assert.deepEqual(blobs, ['/scientific-reading/estudo/trial/sources/b/translation']);
  assert.match(text(renderer.toJSON()), /Texto integral B/);
});

test('obsolete response cannot reveal previous document after route change', async t => {
  let finish;
  const pending = new Promise(resolve => { finish = resolve; });
  const { renderer } = await mount(t, p => p.endsWith('/trial') ? pending : Promise.resolve({ ...fixture('new'), summary_pt: { status: 'available', text: 'New summary' } }));
  await act(async () => { renderer.update(React.createElement(MemoryRouter, { future: { v7_startTransition: true, v7_relativeSplatPath: true } }, React.createElement(Reading, { entityType: 'estudo', slug: 'new' }))); });
  await act(async () => { finish({ ...fixture(), sources: [{ ...fixture().sources[0], doi: 'OLD_SOURCE' }] }); });
  assert.doesNotMatch(text(renderer.toJSON()), /OLD_SOURCE/);
  await act(async () => { button(renderer, 'Resumo editorial').props.onClick(); });
  assert.match(text(renderer.toJSON()), /New summary/);
});

test('unsafe source URLs and untrusted download paths are not rendered as available actions', async t => {
  const f = fixture(); f.sources = [{ ...f.sources[0], original: { status: 'available', url: 'javascript:alert(1)' }, translation_pt: { status: 'available', url: 'https://external.test/private-translation' } }];
  const { renderer, blobs } = await mount(t, async () => f);
  assert.equal(renderer.root.findAllByType('a').filter(a => !a.props.href.startsWith('/busca?')).length, 0);
  assert.equal(button(renderer, 'Tradução integral').props.disabled, true);
  assert.equal(button(renderer, 'Original').props.disabled, true);
  assert.equal(blobs.length, 0);
});

test('metadata errors remain local and can be retried without paid work', async t => {
  let count = 0;
  const { renderer, calls, blobs } = await mount(t, async () => { if (++count === 1) throw Error('offline'); return fixture(); });
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 1);
  await act(async () => { button(renderer, 'Tentar novamente').props.onClick(); });
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
  assert.equal(calls.length, 2); assert.equal(blobs.length, 0);
});


test('artifact URL must match selected entity source and variant exactly', async t => {
  const f = fixture();
  f.sources = [{ ...f.sources[1], original: { status: 'available', url: '/api/scientific-reading/estudo/trial/sources/b/../../../../private' }, translation_pt: { status: 'available', url: '/api/scientific-reading/estudo/trial/sources/b/translation?other=1' } }];
  const { renderer, blobs } = await mount(t, async () => f);
  assert.equal(button(renderer, 'Tradução integral').props.disabled, true);
  assert.equal(button(renderer, 'Original').props.disabled, true);
  assert.equal(blobs.length, 0);
});


test('study alias opens only the canonical artifact returned for that request', async t => {
  const f = fixture('canonical-study');
  f.sources = [{ ...f.sources[1], original: { ...f.sources[1].original, url: '/api/scientific-reading/estudo/canonical-study/sources/b/original' }, translation_pt: { ...f.sources[1].translation_pt, url: '/api/scientific-reading/estudo/canonical-study/sources/b/translation' } }];
  const { renderer, calls, blobs } = await mount(t, async () => f, { slug: 'legacy-alias' });
  assert.deepEqual(calls, ['/scientific-reading/estudo/legacy-alias']);
  assert.equal(button(renderer, 'Tradução integral').props.disabled, false);
  assert.match(text(renderer.toJSON()), /Baixar original \(XML\)/);
  await act(async () => { await button(renderer, 'Tradução integral').props.onClick(); });
  assert.deepEqual(blobs, ['/scientific-reading/estudo/canonical-study/sources/b/translation']);
  assert.match(text(renderer.toJSON()), /Texto integral B/);
});

test('canonical identity cannot switch entity type or introduce encoded traversal', async t => {
  for (const f of [fixture('%2e%2e'), { ...fixture('canonical'), entity_type: 'documento' }]) {
    const { renderer, blobs } = await mount(t, async () => f, { slug: 'alias' });
    assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 1);
    assert.equal(button(renderer, 'Tradução integral'), undefined);
    assert.deepEqual(blobs, []);
  }
});
