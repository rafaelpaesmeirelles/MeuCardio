import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { transform } from 'esbuild';

// Real page/components and React effects; every API call, prompt, navigation
// and download is intercepted. Fixtures are fictitious, with no clinical use.
const root = fileURLToPath(new URL('../', import.meta.url));
const temp = await mkdtemp(path.join(tmpdir(), 'corvia-internal-functions-tests-'));
await symlink(path.join(root, 'node_modules'), path.join(temp, 'node_modules'));
after(() => rm(temp, { recursive: true, force: true }));
const fixturePrelude = `
const READ_TIMEOUT_MS = 15000;
class ApiError extends Error {}
const api = { get: (...a) => globalThis.internalFunctionsFixture.get(...a),
  post: (...a) => globalThis.internalFunctionsFixture.post(...a),
  blob: (...a) => globalThis.internalFunctionsFixture.blob(...a) };
const todasAsPaginas = (...a) => globalThis.internalFunctionsFixture.catalogue(...a);
const useAuth = () => ({ usuario: { id: -900, assinatura_metodo_preferido: 'MANUAL' } });
`;
async function load(relative, name) {
  let source = await readFile(path.join(root, relative), 'utf8');
  source = source.replace(/^import .* from "\.\.\/lib\/(api|auth)";$/gm, '');
  source = source.replace(/^import (\w+)(?:,.*)? from "\.\.\/components\/[^"\n]+";$/gm, (_, component) =>
    component === 'FinalizarDocumentoGerado' ? `import FinalizarDocumentoGerado from './Finalize.mjs';`
      : `const ${component} = () => null;`);
  source = source.replace(/^import \{[^\n]+\} from "\.\.\/components\/Estado";$/gm,
    `const Carregando = ({texto}) => <p role="status">{texto || 'Carregando'}</p>;
     const Erro = ({mensagem}) => <p role="alert">{mensagem}</p>; const Vazio = () => null;`);
  source = source.replace('from "../lib/calculatorValidation"', 'from "./calculatorValidation.mjs"');
  source = source.replace(/^import (\w+) from "\.\/(AssinaturaExternaITI|OfertaEnvioEmailPaciente)";$/gm,
    (_, component) => `const ${component} = () => null;`);
  const output = await transform(fixturePrelude + source, { loader: 'tsx', format: 'esm', jsx: 'automatic' });
  const file = path.join(temp, name + '.mjs');
  await writeFile(file, output.code);
  return (await import(pathToFileURL(file))).default;
}
await writeFile(path.join(temp, 'calculatorValidation.mjs'), (await transform(
  await readFile(path.join(root, 'src/lib/calculatorValidation.ts'), 'utf8'), { loader: 'ts', format: 'esm' })).code);
const Finalize = await load('src/components/FinalizarDocumentoGerado.tsx', 'Finalize');
const Calculator = await load('src/pages/Calculadora.tsx', 'Calculator');
const Checklists = await load('src/pages/Checklists.tsx', 'Checklists');

const textOf = node => typeof node === 'string' ? node : (node.children ?? []).map(textOf).join('');
const buttons = (renderer, pattern) => renderer.root.findAllByType('button').filter(b => pattern.test(textOf(b)));
function button(renderer, pattern) { const matches = buttons(renderer, pattern); assert.equal(matches.length, 1, String(pattern)); return matches[0]; }
function deferred() { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return { promise, resolve, reject }; }
const providers = ['MANUAL', 'A1_ARQUIVO', 'GOVBR'].map(codigo => ({ codigo, nome: codigo, disponivel: true }));
const generated = [];
function fixtures(overrides = {}) {
  const calls = { posts: [], downloads: [], navigations: [], prompts: 0 };
  generated.length = 0;
  globalThis.window = {
    prompt: () => { calls.prompts++; return 'REFERÊNCIA FICTÍCIA'; },
    location: { assign: url => calls.navigations.push(url) },
  };
  globalThis.document = { createElement: () => ({ click() {} }) };
  const state = {
    get: async url => {
      if (url === '/calculators/qa-score') return { slug: 'qa-score', name: 'Calculadora fictícia', kind: 'score', theme: 'QA',
        purpose: 'Sem validade clínica', reference: 'Fixture de interface', limitations: [], fields: [] };
      if (url === '/assinatura/provedores') return providers;
      if (/^\/document-templates\/gerados\/-\d+$/.test(url)) return { assinatura: null };
      if (url === '/checklists/aplicacoes/minhas') return [];
      throw Error('Unmodelled read: ' + url);
    },
    post: async (url, body) => {
      calls.posts.push({ url, body: structuredClone(body) });
      if (url.endsWith('/run')) return { result: { valor: 1 }, interpretation: 'DEMONSTRAÇÃO SEM VALIDADE CLÍNICA' };
      if (url.endsWith('/gerar-documento')) { const item = { id: -901 - generated.length, body: structuredClone(body) }; generated.push(item); return { id: item.id }; }
      throw Error('Unmodelled mutation: ' + url);
    },
    blob: async url => { calls.downloads.push(url); return new Blob(['INERT FIXTURE; NOT A CLINICAL PDF']); },
    catalogue: async () => [{ slug: 'checklist-ficticio', condicao: 'Checklist fictício', scope_type: 'doenca', total_itens: 1, obrigatorios: 1 }],
    ...overrides,
  };
  globalThis.internalFunctionsFixture = state;
  return { calls, state };
}
async function mount(t, component, route) {
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(MemoryRouter,
    { initialEntries: [route], future: { v7_startTransition: true, v7_relativeSplatPath: true } },
    React.createElement(Routes, null, React.createElement(Route, { path: component === Calculator ? '/calculadoras/:slug' : '/checklists', element: React.createElement(component) })))); });
  t.after(async () => { await act(async () => renderer.unmount()); });
  return renderer;
}
async function draft(t, overrides) {
  const fixture = fixtures(overrides);
  const renderer = await mount(t, Calculator, '/calculadoras/qa-score');
  await act(async () => { await button(renderer, /^Calcular$/).props.onClick(); });
  await act(async () => { button(renderer, /^Gerar laudo deste resultado$/).props.onClick(); });
  return { ...fixture, renderer };
}
function field(renderer, name) {
  if (name === 'patient_name') return renderer.root.findByProps({ placeholder: 'Usado só para organizar o histórico' });
  if (name === 'contexto_clinico') return renderer.root.findAllByType('input').find(i => i.props.placeholder?.startsWith('Ex.: colecistectomia'));
  if (name === 'conduta_recomendada') return renderer.root.findByType('textarea');
  return renderer.root.findAllByType('select').find(s => s.findAllByType('option').some(o => o.props.value === 'profissional'));
}
const change = async (renderer, name, value) => act(async () => { field(renderer, name).props.onChange({ target: { value } }); });
const generate = async renderer => act(async () => { await button(renderer, /^Gerar (?:novo )?documento$/).props.onClick(); });

for (const [name, first, second] of [
  ['patient_name', 'PACIENTE FICTÍCIO A', 'PACIENTE FICTÍCIO B'],
  ['contexto_clinico', 'CONTEXTO FICTÍCIO A', 'CONTEXTO FICTÍCIO B'],
  ['conduta_recomendada', 'CONDUTA FICTÍCIA A', 'CONDUTA FICTÍCIA B'],
  ['endereco', 'profissional', 'residencial'],
]) test(`editing ${name} regenerates a new document and preserves the emitted snapshot`, async t => {
  const { renderer, calls } = await draft(t);
  await change(renderer, name, first); await generate(renderer);
  await act(async () => { await button(renderer, /Emitir sem assinatura digital e baixar/).props.onClick(); });
  const original = structuredClone(generated[0]);
  await change(renderer, name, second);
  assert.equal(renderer.root.findAllByType(Finalize).length, 0);
  assert.equal(button(renderer, /^Gerar (?:novo )?documento$/).props.disabled, false);
  await generate(renderer);
  assert.deepEqual(generated[0], original);
  assert.equal(generated.length, 2);
  assert.equal(generated[1].body[name], second);
  await act(async () => { await button(renderer, /Emitir sem assinatura digital e baixar/).props.onClick(); });
  assert.equal(calls.downloads.length, 2);
  assert.match(calls.downloads[0], /gerados\/-901\/pdf\?metodo=MANUAL$/);
  assert.match(calls.downloads[1], /gerados\/-902\/pdf\?metodo=MANUAL$/);
});

test('manual emission can be recreated with identical data and a different signature method', async t => {
  const { renderer, calls } = await draft(t);
  await change(renderer, 'patient_name', 'PACIENTE FICTÍCIO');
  await change(renderer, 'contexto_clinico', 'CONTEXTO FICTÍCIO PRESERVADO');
  await generate(renderer);
  await act(async () => { await button(renderer, /Emitir sem assinatura digital e baixar/).props.onClick(); });
  const original = structuredClone(generated[0]);
  await act(async () => { button(renderer, /^Recriar baseado neste$/).props.onClick(); });
  assert.equal(renderer.root.findAllByType(Finalize).length, 0);
  await generate(renderer);
  assert.equal(generated.length, 2);
  assert.deepEqual(generated[0], original);
  assert.deepEqual(generated[1].body, original.body);
  assert.notEqual(generated[1].id, original.id);
  const signature = renderer.root.findAllByType('select').find(s => s.findAllByType('option').some(o => o.props.value === 'A1_ARQUIVO'));
  assert.equal(signature.props.disabled, false);
  await act(async () => { signature.props.onChange({ target: { value: 'A1_ARQUIVO' } }); });
  await act(async () => { await button(renderer, /Assinar digitalmente e baixar PDF/).props.onClick(); });
  assert.deepEqual(calls.downloads, [
    '/document-templates/gerados/-901/pdf?metodo=MANUAL',
    '/document-templates/gerados/-902/pdf?metodo=A1_ARQUIVO',
  ]);
});

test('changing a draft while generation is pending discards its obsolete response', async t => {
  const pending = deferred();
  const { renderer, state } = await draft(t);
  const post = state.post;
  state.post = (url, body) => url.endsWith('/gerar-documento') ? pending.promise : post(url, body);
  await act(async () => { void button(renderer, /^Gerar documento$/).props.onClick(); });
  await change(renderer, 'contexto_clinico', 'CONTEXTO MAIS RECENTE FICTÍCIO');
  await act(async () => { pending.resolve({ id: -999 }); });
  assert.equal(renderer.root.findAllByType(Finalize).length, 0);
  assert.equal(button(renderer, /^Gerar (?:novo )?documento$/).props.disabled, false);
  assert.doesNotMatch(textOf(renderer.toJSON()), /Documento gerado\./);
});

test('calculator uses real finalizer emission and email gates without sending anything', async t => {
  const { renderer, calls } = await draft(t); await generate(renderer);
  const email = renderer.root.findByProps({ type: 'email' });
  await act(async () => { email.props.onChange({ target: { value: 'fixture@example.invalid' } }); });
  assert.equal(button(renderer, /^Enviar por e-mail$/).props.disabled, true);
  const signature = renderer.root.findAllByType('select').find(s => s.findAllByType('option').some(o => o.props.value === 'A1_ARQUIVO'));
  await act(async () => { signature.props.onChange({ target: { value: 'A1_ARQUIVO' } }); });
  await act(async () => { await button(renderer, /Assinar digitalmente e baixar PDF/).props.onClick(); });
  assert.equal(signature.props.disabled, true);
  assert.equal(button(renderer, /^Enviar por e-mail$/).props.disabled, false);
  assert.match(calls.downloads[0], /metodo=A1_ARQUIVO$/);
  assert.equal(calls.posts.filter(p => p.url.endsWith('/enviar-email')).length, 0);
});

test('checklist history failure is visible and can be retried independently of its catalogue', async t => {
  let attempts = 0;
  fixtures({ get: async () => { if (++attempts === 1) throw Error('503 fixture'); return [{ id: -700, condicao: 'ALTA FICTÍCIA RECUPERADA', marcados: 0, total: 1 }]; } });
  const renderer = await mount(t, Checklists, '/checklists');
  assert.ok(renderer.root.findAllByProps({ role: 'alert' }).length);
  await act(async () => { button(renderer, /Tentar carregar histórico novamente/).props.onClick(); });
  assert.equal(attempts, 2);
  assert.match(textOf(renderer.toJSON()), /ALTA FICTÍCIA RECUPERADA/);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
});

test('checklist start has an immediate lock, releases it on failure, and can then retry', async t => {
  const pending = deferred(); let attempts = 0;
  const { calls } = fixtures({ post: async () => { attempts++; return attempts === 1 ? pending.promise : { id: -800 }; } });
  const renderer = await mount(t, Checklists, '/checklists');
  await act(async () => { await new Promise(resolve => setTimeout(resolve, 280)); });
  const start = button(renderer, /^Usar nesta alta$/).props.onClick;
  await act(async () => { void start(); void start(); });
  assert.equal(attempts, 1); assert.equal(calls.prompts, 1);
  assert.equal(button(renderer, /Iniciando|Usar nesta alta/).props.disabled, true);
  await act(async () => { pending.reject(Error('503 fixture')); });
  assert.equal(button(renderer, /^Usar nesta alta$/).props.disabled, false);
  await act(async () => { await button(renderer, /^Usar nesta alta$/).props.onClick(); });
  assert.equal(attempts, 2); assert.deepEqual(calls.navigations, ['/checklists/alta/-800']);
});

test('canceling checklist identification never starts a request and unlocks the action', async t => {
  const { calls } = fixtures({ post: async () => { calls.posts.push('start'); return { id: -800 }; } });
  const renderer = await mount(t, Checklists, '/checklists');
  await act(async () => { await new Promise(resolve => setTimeout(resolve, 280)); });
  window.prompt = () => null;
  await act(async () => { await button(renderer, /^Usar nesta alta$/).props.onClick(); });
  assert.equal(calls.posts.length, 0);
  window.prompt = () => 'REFERÊNCIA FICTÍCIA';
  await act(async () => { await button(renderer, /^Usar nesta alta$/).props.onClick(); });
  assert.equal(calls.posts.length, 1);
});
