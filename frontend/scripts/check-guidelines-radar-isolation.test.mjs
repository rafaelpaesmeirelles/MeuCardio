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
source = source.replace('import { api, ApiError, READ_TIMEOUT_MS } from "../lib/api";', `
const READ_TIMEOUT_MS = 15000;
const api = { get: (...args) => globalThis.corviaSearchFixture.get(...args) };
class ApiError extends Error {}
`);
await writeFile(path.join(temp, 'EditorialDocumentList.mjs'), transpile(source, 'EditorialDocumentList.tsx'));
const { default: EditorialDocumentList } = await import(pathToFileURL(path.join(temp, 'EditorialDocumentList.mjs')));

let pageSource = await readFile(path.join(root, 'src/pages/Diretrizes.tsx'), 'utf8');
pageSource = pageSource.replace('"../components/EditorialDocumentList"', '"./EditorialDocumentList.mjs"');
pageSource = pageSource.replace('import ScientificIntelligenceMonitor from "../components/ScientificIntelligenceMonitor";', 'const ScientificIntelligenceMonitor = () => null;');
pageSource = pageSource.replace('import ScientificReadingAccess from "../components/ScientificReadingAccess";', 'const ScientificReadingAccess = () => null;');
pageSource = pageSource.replace('import BotaoFavorito from "../components/BotaoFavorito";', 'const BotaoFavorito = () => null;');
pageSource = pageSource.replace('import AlertasDiretrizesFavoritas from "../components/AlertasDiretrizesFavoritas";', 'const AlertasDiretrizesFavoritas = () => null;');
pageSource = pageSource.replace('import { api, ApiError, READ_TIMEOUT_MS } from "../lib/api";', `
const READ_TIMEOUT_MS = 15000;
const api = { get: (...args) => globalThis.corviaSearchFixture.get(...args) };
class ApiError extends Error {}
`);
pageSource = pageSource.replace('import { Carregando, Erro } from "../components/Estado";', `
const Carregando = ({ texto }) => <p role="status">{texto}</p>;
const Erro = ({ mensagem }) => <p role="alert">{mensagem}</p>;
`);
pageSource = pageSource.replace(/import \{\s*ClinicalContextLink,[\s\S]*?\} from "\.\.\/components\/ClinicalCommandPrimitives";/, `
const ClinicalContextLink = ({ to, title }) => <a href={to}>{title}</a>;
const ClinicalEmpty = ({ title }) => <p>{title}</p>;
const ClinicalMetric = ({ label, value }) => <p>{label}: {value}</p>;
const ClinicalPageHeader = ({ title }) => <h1>{title}</h1>;
const ClinicalSection = ({ title, children }) => <section><h2>{title}</h2>{children}</section>;
`);
await writeFile(path.join(temp, 'Diretrizes.mjs'), transpile(pageSource, 'Diretrizes.tsx'));
const { default: Diretrizes } = await import(pathToFileURL(path.join(temp, 'Diretrizes.mjs')));
const tick = () => new Promise(resolve => setTimeout(resolve, 230));
const nodeText = node => typeof node === 'string' ? node : (node.children ?? []).map(nodeText).join('');

for (const radar of ['pending', 'failed']) {
  test(`Library and formal study collections remain accessible when radar is ${radar}`, async t => {
    globalThis.corviaSearchFixture = { get: async url => {
      if (url.startsWith('/guideline-updates')) {
        if (radar === 'failed') throw Error('radar indisponível');
        return new Promise(() => {});
      }
      if (url.startsWith('/library/documents?')) return { items: [{ slug: 'sbc', title: 'Diretriz SBC', kind: 'diretriz', theme: 'FA' }], total: 1, next_offset: null };
      if (url.startsWith('/studies?')) return { items: [{ slug: 'sepsis', title: 'Sepsis-3', study_type: 'consenso', theme: 'Sepse' }], total: 1, next_offset: null };
      throw Error(url);
    } };
    let renderer;
    await act(async () => { renderer = TestRenderer.create(React.createElement(MemoryRouter, {
      future: { v7_startTransition: true, v7_relativeSplatPath: true },
    }, React.createElement(Diretrizes))); });
    t.after(async () => { await act(async () => renderer.unmount()); });
    await act(async () => { await tick(); });
    const links = renderer.root.findAllByType('a').map(link => link.props.href);
    assert.ok(links.includes('/biblioteca/sbc'));
    assert.ok(links.includes('/estudos/sepsis'));
    assert.match(nodeText(renderer.toJSON()), /Diretrizes e consensos da Biblioteca/);
    if (radar === 'failed') assert.ok(renderer.root.findAllByProps({ role: 'alert' }).length);
    else assert.match(nodeText(renderer.toJSON()), /Verificando publicações oficiais/);
  });
}
