import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import React from 'react';
import { MemoryRouter, useNavigate } from 'react-router-dom';
import TestRenderer from 'react-test-renderer';
import ts from 'typescript';
const { act } = TestRenderer;
const root = fileURLToPath(new URL('../', import.meta.url));
const temp = await mkdtemp(path.join(tmpdir(), 'corvia-private-favorite-'));
await symlink(path.join(root, 'node_modules'), path.join(temp, 'node_modules'));
after(() => rm(temp, { recursive: true, force: true }));
const compile = source => ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX } }).outputText;
let source = await readFile(path.join(root, 'src/pages/ScientificDocumentAI.tsx'), 'utf8');
source = source.replace('import { api, ApiError, READ_TIMEOUT_MS } from "../lib/api";', 'const READ_TIMEOUT_MS = 15000; const api = globalThis.privateFixture.api; class ApiError extends Error {}');
source = source.replace('import { useAuth } from "../lib/auth";', 'const useAuth = () => ({ usuario: globalThis.privateFixture.user });');
source = source.replace('import { formatBRL } from "../lib/commercialPlans";', 'const formatBRL = value => String(value);');
source = source.replace('import BotaoFavorito from "../components/BotaoFavorito";', 'const BotaoFavorito = props => <span data-favorite={props.itemId} />;');
source = source.replace('import PrivateScientificOriginal from "../components/PrivateScientificOriginal";', 'const PrivateScientificOriginal = props => <span data-original={props.documentId} />;');
source = source.replace('import { ClinicalPageHeader, ClinicalSection } from "../components/ClinicalCommandPrimitives";', 'const ClinicalPageHeader = () => null; const ClinicalSection = props => <section><h2>{props.title}</h2>{props.children}</section>;');
await writeFile(path.join(temp, 'Page.mjs'), compile(source));
const calls = [];
let responder;
globalThis.privateFixture = { user: { id: 1 }, api: new Proxy({}, { get: (_, method) => (...args) => { calls.push([method, ...args]); return method === 'get' ? responder(...args) : Promise.reject(Error('Mutation not authorized by reading')); } }) };
globalThis.document = { getElementById: () => null };
const { default: Page } = await import(pathToFileURL(path.join(temp, 'Page.mjs')));
let navigate;
function Nav() { navigate = useNavigate(); return React.createElement(Page); }
const view = url => React.createElement(MemoryRouter, { initialEntries: [url], future: { v7_startTransition: true, v7_relativeSplatPath: true } }, React.createElement(Nav));
const row = id => ({ id, title: `Private ${id}`, document_type: 'artigo', media_type: 'application/pdf', analysis_status: 'pendente', incorporation_status: 'privado', incorporation_recommended: false });
const defaultResponse = async url => url === '/documentos-cientificos-ia' ? [row(1), row(2)] : row(Number(url.split('/').at(-1)));
async function mount(t, url) {
  calls.length = 0; responder ??= defaultResponse;
  let renderer; await act(async () => { renderer = TestRenderer.create(view(url)); });
  t.after(async () => { await act(async () => renderer.unmount()); responder = defaultResponse; });
  return renderer;
}

test('favorite summary selects only its private document without AI or incorporation', async t => {
  responder = defaultResponse;
  const renderer = await mount(t, '/documentos-cientificos-ia?document=2&leitura=resumo');
  assert.equal(renderer.root.findByProps({ 'data-favorite': 2 }).props['data-favorite'], 2);
  assert.ok(calls.some(call => call[1] === '/documentos-cientificos-ia/2'));
  assert.ok(calls.every(call => call[0] === 'get'));
  assert.equal(renderer.root.findAllByProps({ 'data-original': 2 }).length, 0);
  assert.ok(renderer.root.findByProps({ id: 'leitura-privada-resumo' }));
});

test('original and missing translation open the requested section without authorizing paid work', async t => {
  responder = defaultResponse;
  const renderer = await mount(t, '/documentos-cientificos-ia?document=1&leitura=original');
  assert.equal(renderer.root.findAllByProps({ 'data-original': 1 }).length, 1);
  await act(async () => navigate('/documentos-cientificos-ia?document=1&leitura=traduzido'));
  assert.equal(renderer.root.findAllByProps({ 'data-original': 1 }).length, 0);
  assert.ok(renderer.root.findByProps({ id: 'leitura-privada-traduzido' }));
  assert.ok(calls.every(call => call[0] === 'get'));
});

test('malformed private identity never issues a detail request', async t => {
  responder = defaultResponse;
  const renderer = await mount(t, '/documentos-cientificos-ia?document=../../another');
  assert.deepEqual(calls.map(call => call[1]), ['/documentos-cientificos-ia']);
  assert.equal(renderer.root.findAllByType('span').filter(node => node.props['data-favorite']).length, 0);
});

test('late private document response cannot replace a newly selected document', async t => {
  let resolveOld;
  responder = url => url.endsWith('/1') ? new Promise(resolve => { resolveOld = resolve; }) : defaultResponse(url);
  const renderer = await mount(t, '/documentos-cientificos-ia?document=1&leitura=original');
  await act(async () => navigate('/documentos-cientificos-ia?document=2&leitura=resumo'));
  await act(async () => resolveOld(row(1)));
  assert.equal(renderer.root.findAllByProps({ 'data-favorite': 2 }).length, 1);
  assert.equal(renderer.root.findAllByProps({ 'data-favorite': 1 }).length, 0);
});
