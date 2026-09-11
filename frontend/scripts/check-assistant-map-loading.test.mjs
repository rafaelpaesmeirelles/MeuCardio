import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';

// Real loader component with an in-memory module promise. No API, location,
// Google Maps, browser, account or external network is accessed.
const require = createRequire(import.meta.url);
const source = readFileSync(new URL('../src/components/DeferredAssistantMap.tsx', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: {
  module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX,
} }).outputText;
const props = { rotas: [], origem: null, destino: { name: 'Destino sintético A', latitude: -23, longitude: -46 } };
const visible = node => typeof node === 'string' ? node : Array.isArray(node) ? node.map(visible).join(' ') : node ? visible(node.children) : '';
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
};
const FakeMap = mapProps => React.createElement('output', { 'data-map': true }, mapProps.destino.name);
function setup(loadMap) {
  const module = { exports: {} };
  let imports = 0, focuses = 0;
  vm.runInNewContext(compiled, {
    module, exports: module.exports,
    require: name => name === './MapaDeslocamento' ? (++imports, loadMap()) : require(name),
  });
  return {
    Component: module.exports.default,
    imports: () => imports,
    focuses: () => focuses,
    createNodeMock: () => ({ focus: () => { focuses += 1; } }),
  };
}

test('assistant map: loads on mount, keeps latest props, and caches only the component for reopening', async t => {
  const pending = deferred();
  const harness = setup(() => pending.promise);
  assert.equal(harness.imports(), 0);
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(harness.Component, props)); });
  assert.equal(harness.imports(), 1);
  assert.match(visible(renderer.toJSON()), /Carregando mapa/);
  const latest = { ...props, destino: { ...props.destino, name: 'Destino sintético B' } };
  await act(async () => { renderer.update(React.createElement(harness.Component, latest)); });
  await act(async () => { pending.resolve({ default: FakeMap }); await pending.promise; });
  assert.equal(visible(renderer.toJSON()), latest.destino.name);
  await act(async () => { renderer.unmount(); });
  await act(async () => { renderer = TestRenderer.create(React.createElement(harness.Component, props)); });
  t.after(() => act(() => renderer.unmount()));
  assert.equal(harness.imports(), 1);
  assert.equal(visible(renderer.toJSON()), props.destino.name);
});

test('assistant map: import failure is local and retry keeps focus in the dialog before succeeding', async t => {
  let attempts = 0;
  const pending = deferred();
  const harness = setup(() => ++attempts === 1 ? Promise.reject(new Error('synthetic module failure')) : pending.promise);
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(harness.Component, props), { createNodeMock: harness.createNodeMock }); });
  t.after(() => act(() => renderer.unmount()));
  assert.match(visible(renderer.root.findByProps({ role: 'alert' })), /outras funções do Apoio continuam disponíveis/);
  const retry = renderer.root.findByType('button');
  assert.equal(retry.props.type, 'button');
  assert.equal(Boolean(retry.props.disabled), false);
  await act(async () => { retry.props.onClick(); });
  assert.equal(harness.focuses(), 1);
  assert.equal(renderer.root.findByProps({ role: 'group' }).props.tabIndex, -1);
  assert.match(visible(renderer.toJSON()), /Carregando mapa/);
  await act(async () => { pending.resolve({ default: FakeMap }); await pending.promise; });
  assert.equal(harness.imports(), 2);
  assert.equal(visible(renderer.toJSON()), props.destino.name);
});

test('assistant map: closing before resolution cannot reopen it or publish a late failure', async () => {
  const pending = deferred();
  const harness = setup(() => pending.promise);
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(harness.Component, props)); });
  await act(async () => { renderer.unmount(); });
  await act(async () => { pending.reject(new Error('synthetic late module failure')); await pending.promise.catch(() => undefined); });
  assert.equal(renderer.toJSON(), null);
  assert.equal(harness.focuses(), 0);
});
