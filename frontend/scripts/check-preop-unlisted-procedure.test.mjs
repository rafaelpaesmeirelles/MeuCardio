import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';

// Real component, synthetic calculator responses. No clinical-model validation,
// API/network, account, document issuance, signature or email is exercised.
const require = createRequire(import.meta.url);
const source = readFileSync(new URL('../src/pages/AvaliacaoPreOperatoria.tsx', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: {
  module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX,
} }).outputText;
const visible = node => typeof node === 'string' || typeof node === 'number' ? String(node)
  : Array.isArray(node) ? node.map(visible).join(' ') : node ? visible(node.children) : '';
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
};
class ApiError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}
const responses = {
  '/calculators/rcri/run': { result: { pontos: 1, classe: 'II', evento_pct: 'fixture' }, interpretation: 'RCRI FICTICIO' },
  '/calculators/gupta-mica/run': { result: { risco_pct: 1.23, procedimento: 'hernia' }, interpretation: 'MICA FICTICIO' },
  '/calculators/dasi/run': { result: { score: 20, max: 58.2, capacidade_funcional: 'fixture', ponto_decisao: 34 }, interpretation: 'DASI FICTICIO' },
  '/avaliacao-preoperatoria/gerar': { id: 91001 },
};
async function setup(t, postOverride) {
  const calls = [];
  const api = {
    get: path => {
      calls.push({ method: 'get', path });
      assert.equal(path, '/assinatura/provedores');
      return Promise.resolve([{ codigo: 'MANUAL', nome: 'Manual DEMO', disponivel: true }]);
    },
    post: (path, payload) => {
      calls.push({ method: 'post', path, payload });
      const override = postOverride?.(path, payload);
      if (override !== undefined) return override;
      assert.ok(Object.hasOwn(responses, path), `Unexpected fixture request ${path}`);
      return Promise.resolve(structuredClone(responses[path]));
    },
    blob: () => { throw new Error('PDF download is outside this isolated test'); },
  };
  const module = { exports: {} };
  vm.runInNewContext(compiled, {
    module, exports: module.exports, Error,
    require: name => name === '../lib/api' ? { api, ApiError }
      : name === '../lib/auth' ? { useAuth: () => ({ usuario: { id: 91000, assinatura_metodo_preferido: 'MANUAL' } }) }
      : name === 'react-router-dom' ? { Link: ({ to, children }) => React.createElement('a', { href: to }, children) }
      : name.startsWith('../components/') ? { __esModule: true, default: () => null }
      : require(name),
  });
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(module.exports.default)); });
  t.after(() => act(() => renderer.unmount()));
  return { renderer, calls };
}
const button = (renderer, name) => renderer.root.findAllByType('button').find(node => visible(node).trim() === name);
const change = async (node, value) => act(async () => { node.props.onChange({ target: { value } }); });
const click = async (renderer, name) => act(async () => {
  const node = button(renderer, name);
  assert.ok(node, `Missing button ${name}`);
  assert.equal(Boolean(node.props.disabled), false, `${name} must be enabled`);
  await node.props.onClick();
});
const selectProcedure = (renderer, value) => change(renderer.root.findByProps({ id: 'gupta-procedimento' }), value);
async function identify(renderer) {
  await change(renderer.root.findByProps({ placeholder: 'Usado só para organizar o histórico' }), 'Pessoa sintética DEMO');
  await change(renderer.root.findAllByType('input').find(node => node.props.type === 'number' && node.props.min === 0), '60');
  await change(renderer.root.findByProps({ placeholder: 'Ex.: colecistectomia videolaparoscópica eletiva' }), 'Procedimento sintético para teste');
}
const toggleMethod = (renderer, prefix, checked) => act(async () => {
  const label = renderer.root.findAllByType('label').find(node => visible(node).trim().startsWith(prefix));
  assert.ok(label, `Missing method ${prefix}`);
  label.findByType('input').props.onChange({ target: { checked } });
});
const posts = calls => calls.filter(call => call.method === 'post');

test('preop: listed procedure keeps real MICA request and all selected raw inputs in generation', async t => {
  const { renderer, calls } = await setup(t);
  await identify(renderer);
  await click(renderer, 'Calcular método(s)');
  assert.deepEqual(posts(calls).map(call => call.path), Object.keys(responses).slice(0, 3));
  const mica = posts(calls)[1].payload;
  assert.equal(mica.tipo_procedimento, 'hernia');
  assert.equal(mica.idade, 60);
  assert.equal(mica.asa, 2);
  assert.match(visible(renderer.toJSON()), /Gupta MICA:.*1\.23\s*%/);
  await click(renderer, 'Gerar documento');
  const payload = posts(calls).at(-1).payload;
  assert.deepEqual(payload.gupta, mica);
  assert.equal(payload.gupta_nao_estimado, false);
  assert.ok(payload.rcri && payload.dasi);
  assert.equal(payload.aub_has2, null);
  assert.equal(payload.vsg_cri, null);
  assert.match(visible(renderer.toJSON()), /Documento gerado\./);
});

test('preop: Outras skips MICA, keeps RCRI/DASI, and records the limitation without a fabricated percentage', async t => {
  const { renderer, calls } = await setup(t);
  await identify(renderer);
  await selectProcedure(renderer, 'outras_baixo_risco');
  const selector = renderer.root.findByProps({ id: 'gupta-procedimento' });
  assert.equal(selector.props['aria-describedby'], 'gupta-limite-modelo');
  assert.equal(renderer.root.findByProps({ id: 'gupta-limite-modelo' }).props.role, 'status');
  await click(renderer, 'Calcular método(s)');
  assert.deepEqual(posts(calls).map(call => call.path), ['/calculators/rcri/run', '/calculators/dasi/run']);
  assert.match(visible(renderer.toJSON()), /Gupta MICA:.*não estimado/);
  assert.doesNotMatch(visible(renderer.toJSON()), /MICA FICTICIO|Gupta MICA:\s*0(?:[.,]0+)?%/);
  await click(renderer, 'Gerar documento');
  const payload = posts(calls).at(-1).payload;
  assert.equal(payload.gupta, null);
  assert.equal(payload.gupta_nao_estimado, true);
  assert.ok(payload.rcri && payload.dasi);
});

test('preop: changing procedure invalidates calculated results and generated document; returning does not omit selected MICA', async t => {
  const { renderer, calls } = await setup(t);
  await identify(renderer);
  await click(renderer, 'Calcular método(s)');
  await click(renderer, 'Gerar documento');
  await selectProcedure(renderer, 'outras_baixo_risco');
  assert.doesNotMatch(visible(renderer.toJSON()), /Resultado integrado|MICA FICTICIO|Documento gerado\./);
  assert.equal(button(renderer, 'Gerar documento'), undefined);
  assert.equal(button(renderer, 'Baixar PDF'), undefined);
  await selectProcedure(renderer, 'hernia');
  assert.doesNotMatch(visible(renderer.toJSON()), /Resultado integrado/,
    'Returning to an earlier procedure must not restore a generation-ready partial result');
  assert.equal(button(renderer, 'Gerar documento'), undefined);
  await click(renderer, 'Calcular método(s)');
  await click(renderer, 'Gerar documento');
  assert.equal(posts(calls).at(-1).payload.gupta.tipo_procedimento, 'hernia');
});

test('preop: Outras alone cannot calculate or generate an empty assessment', async t => {
  const { renderer, calls } = await setup(t);
  await identify(renderer);
  await selectProcedure(renderer, 'outras_baixo_risco');
  await toggleMethod(renderer, 'RCRI —', false);
  await toggleMethod(renderer, 'DASI —', false);
  assert.equal(button(renderer, 'Calcular método(s)').props.disabled, true);
  assert.equal(button(renderer, 'Gerar documento'), undefined);
  assert.match(visible(renderer.toJSON()), /Selecione ao menos um dos outros métodos aplicáveis/);
  assert.deepEqual(posts(calls), []);
});

test('preop: a late calculation after editing cannot expose results or generation for different inputs', async t => {
  const pending = deferred();
  let delayed = true;
  const { renderer, calls } = await setup(t, path => path === '/calculators/rcri/run' && delayed ? pending.promise : undefined);
  await identify(renderer);
  let calculation;
  await act(async () => { calculation = button(renderer, 'Calcular método(s)').props.onClick(); });
  await selectProcedure(renderer, 'outras_baixo_risco');
  await act(async () => { pending.resolve(structuredClone(responses['/calculators/rcri/run'])); await calculation; });
  assert.doesNotMatch(visible(renderer.toJSON()), /Resultado integrado|MICA FICTICIO/);
  assert.equal(button(renderer, 'Gerar documento'), undefined);
  delayed = false;
  calls.length = 0;
  await click(renderer, 'Calcular método(s)');
  assert.deepEqual(posts(calls).map(call => call.path), ['/calculators/rcri/run', '/calculators/dasi/run']);
  assert.match(visible(renderer.toJSON()), /Gupta MICA:.*não estimado/);
});

test('preop: partial calculator failure remains non-generatable and explicit retry recomputes all selected methods', async t => {
  let fail = true;
  const { renderer, calls } = await setup(t, path => path === '/calculators/dasi/run' && fail ? Promise.reject(new ApiError(503, 'Serviço sintético indisponível')) : undefined);
  await identify(renderer);
  await click(renderer, 'Calcular método(s)');
  assert.match(visible(renderer.toJSON()), /Serviço sintético indisponível/);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 1);
  assert.doesNotMatch(visible(renderer.toJSON()), /Resultado integrado|MICA FICTICIO/);
  assert.equal(button(renderer, 'Gerar documento'), undefined);
  fail = false;
  calls.length = 0;
  await click(renderer, 'Calcular método(s)');
  assert.deepEqual(posts(calls).map(call => call.path), Object.keys(responses).slice(0, 3));
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
  assert.ok(button(renderer, 'Gerar documento'));
});

test('preop: duplicate calculations and generation are blocked, and late generation cannot attach to edited data', async t => {
  const calculationResponse = deferred(), generationResponse = deferred();
  const { renderer, calls } = await setup(t, path => path === '/calculators/rcri/run' ? calculationResponse.promise
    : path === '/avaliacao-preoperatoria/gerar' ? generationResponse.promise : undefined);
  await identify(renderer);
  let calculation;
  const calculate = button(renderer, 'Calcular método(s)').props.onClick;
  await act(async () => { calculation = calculate(); calculate(); });
  assert.equal(posts(calls).length, 1);
  await act(async () => { calculationResponse.resolve(structuredClone(responses['/calculators/rcri/run'])); await calculation; });
  let generation;
  const generate = button(renderer, 'Gerar documento').props.onClick;
  await act(async () => { generation = generate(); generate(); });
  assert.equal(posts(calls).filter(call => call.path === '/avaliacao-preoperatoria/gerar').length, 1);
  assert.equal(button(renderer, 'Calcular método(s)').props.disabled, true);
  await change(renderer.root.findByProps({ placeholder: 'Usado só para organizar o histórico' }), 'Outra pessoa sintética DEMO');
  await act(async () => { generationResponse.resolve({ id: 91002 }); await generation; });
  assert.doesNotMatch(visible(renderer.toJSON()), /Documento gerado\./);
  assert.equal(button(renderer, 'Baixar PDF'), undefined);
});
