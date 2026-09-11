import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';

const require = createRequire(import.meta.url);
const source = readFileSync(new URL('../src/components/PatientTimeline.tsx', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: {
  module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX,
} }).outputText;
const event = title => ({ tipo: 'documento', data: '2026-09-11T12:00:00Z', titulo: title, resumo: 'Conteúdo fictício de teste.' });
const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
const text = renderer => JSON.stringify(renderer.toJSON());
function load(get) {
  const module = { exports: {} };
  const context = vm.createContext({ module, exports: module.exports,
    require: name => name === '../lib/api' ? { api: { get } } : require(name),
  });
  vm.runInContext(compiled, context);
  return module.exports.default;
}

test('timeline: failure is explicit; a single user retry recovers without fabricated empty history', async () => {
  let attempts = 0;
  const Timeline = load(async path => {
    assert.equal(path, '/timeline/patient/701');
    if (++attempts === 1) throw new Error('503 fixture');
    return [event('Evento após recuperação')];
  });
  let renderer;
  try {
    await act(async () => { renderer = TestRenderer.create(React.createElement(Timeline, { patientId: 701 })); });
    assert.match(text(renderer), /Não foi possível carregar/);
    assert.doesNotMatch(text(renderer), /Nenhum evento registrado/);
    assert.equal(renderer.root.findByProps({ role: 'alert' }).type, 'p');
    await act(async () => { renderer.root.findByType('button').props.onClick(); });
    assert.equal(attempts, 2);
    assert.match(text(renderer), /Evento após recuperação/);
    assert.doesNotMatch(text(renderer), /Não foi possível carregar/);
  } finally { if (renderer) act(() => renderer.unmount()); }
});

test('timeline: switching patients hides old data and discards both delayed success and error', async () => {
  const requests = [];
  const Timeline = load(path => { const pending = deferred(); requests.push({ path, ...pending }); return pending.promise; });
  let renderer;
  try {
    await act(async () => { renderer = TestRenderer.create(React.createElement(Timeline, { patientId: 701 })); });
    await act(async () => { requests[0].resolve([event('PACIENTE A DEMO')]); });
    assert.match(text(renderer), /PACIENTE A DEMO/);
    await act(async () => { renderer.update(React.createElement(Timeline, { patientId: 702 })); });
    assert.doesNotMatch(text(renderer), /PACIENTE A DEMO/);
    await act(async () => { renderer.update(React.createElement(Timeline, { patientId: 703 })); });
    await act(async () => { requests[2].resolve([event('PACIENTE C DEMO')]); requests[1].resolve([event('PACIENTE B ATRASADO')]); });
    assert.match(text(renderer), /PACIENTE C DEMO/);
    assert.doesNotMatch(text(renderer), /PACIENTE B ATRASADO|PACIENTE A DEMO/);
    await act(async () => { renderer.update(React.createElement(Timeline, { patientId: 704 })); });
    await act(async () => { renderer.update(React.createElement(Timeline, { patientId: 705 })); });
    await act(async () => { requests[4].resolve([]); requests[3].reject(new Error('Erro atrasado anterior')); });
    assert.match(text(renderer), /Nenhum evento registrado/);
    assert.doesNotMatch(text(renderer), /Não foi possível carregar|PACIENTE C DEMO/);
  } finally { if (renderer) act(() => renderer.unmount()); }
});

test('timeline: unmount ignores the pending rejection without an unhandled promise', async () => {
  const pending = deferred();
  const Timeline = load(() => pending.promise);
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(Timeline, { patientId: 701 })); });
  act(() => renderer.unmount());
  await act(async () => { pending.reject(new Error('503 after unmount')); });
  assert.equal(renderer.toJSON(), null);
});
