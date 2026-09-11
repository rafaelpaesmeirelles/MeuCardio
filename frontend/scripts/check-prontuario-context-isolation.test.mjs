import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';

// Real component; API, routing and browser events are isolated. No clinical data,
// backend, external calls or persistence is used by this runner.
const require = createRequire(import.meta.url);
const source = readFileSync(new URL('../src/pages/Prontuario.tsx', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: {
  module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX,
} }).outputText;
const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return { promise, resolve, reject }; };
const encounter = (id, title) => ({ id, encounter_type: 'consulta', status: 'draft', started_at: '2026-09-11T12:00:00Z', chief_complaint: title, vital_signs: {} });
const patients = [701, 702].map(id => ({ id, full_name: `Paciente fictício ${id}` }));
const visible = node => typeof node === 'string' || typeof node === 'number' ? String(node) : Array.isArray(node) ? node.map(visible).join(' ') : node ? visible(node.children) : '';
function setup(overrides = {}) {
  const route = {}, calls = [], events = new Map();
  const api = Object.fromEntries(['get', 'post', 'patch'].map(method => [method, (path, payload) => {
    calls.push({ method, path, payload });
    if (overrides[method]) { const result = overrides[method](path, payload); if (result !== undefined) return result; }
    if (method !== 'get') return Promise.reject(new Error('Unexpected mutation in fixture'));
    if (path === '/pacientes') return Promise.resolve(patients);
    if (path === '/agenda-clinica/hoje' || /\/atendimentos(?:\/\d+\/artefatos(?:\/candidatos)?)?$/.test(path)) return Promise.resolve([]);
    return Promise.reject(new Error(`Unexpected request ${path}`));
  }]));
  const module = { exports: {} };
  const context = vm.createContext({ module, exports: module.exports, URLSearchParams, Error,
    window: { addEventListener: (name, fn) => events.set(name, fn), removeEventListener: (name, fn) => { if (events.get(name) === fn) events.delete(name); } },
    require: name => name === '../lib/api' ? { api } : name === 'react-router-dom' ? {
      useSearchParams: () => {
        const [qs, set] = React.useState(new URLSearchParams('paciente=701'));
        route.set = value => set(typeof value === 'function' ? value : new URLSearchParams(value));
        route.qs = qs;
        return [qs, route.set];
      },
    } : name === '../components/PatientClinicalSummary' ? { default: () => null, __esModule: true } : name.endsWith('.css') ? {} : require(name),
  });
  vm.runInContext(compiled, context);
  return { Component: module.exports.default, calls, events, route };
}
const button = (renderer, name) => renderer.root.findAllByType('button').find(node => visible(node.toJSON ? node.toJSON() : { children: node.children.map(c => typeof c === 'string' ? c : '') }).trim() === name);
const click = async (renderer, name) => act(async () => { const target = button(renderer, name); assert.ok(target, `Missing button: ${name}`); target.props.onClick(); });

test('prontuario: delayed history cannot cross patient selection; errors are not empty history', async () => {
  const a = deferred(), b = deferred();
  const { Component, route } = setup({ get: path => path === '/pacientes/701/atendimentos' ? a.promise : path === '/pacientes/702/atendimentos' ? b.promise : undefined });
  let r;
  try {
    await act(async () => { r = TestRenderer.create(React.createElement(Component)); });
    await act(async () => { route.set('paciente=702'); });
    await act(async () => { b.resolve([encounter(7021, 'HISTORICO B DEMO')]); a.resolve([encounter(7011, 'HISTORICO A ATRASADO')]); });
    assert.match(visible(r.toJSON()), /HISTORICO B DEMO/);
    assert.doesNotMatch(visible(r.toJSON()), /HISTORICO A ATRASADO/);
  } finally { if (r) act(() => r.unmount()); }
});

test('prontuario: failed history has a retry, not a false empty record', async () => {
  let attempts = 0;
  const { Component } = setup({ get: path => path === '/pacientes/701/atendimentos' ? (++attempts === 1 ? Promise.reject(new Error('503 fixture')) : Promise.resolve([encounter(7011, 'RECUPERADO DEMO')])) : undefined });
  let r;
  try {
    await act(async () => { r = TestRenderer.create(React.createElement(Component)); });
    assert.doesNotMatch(visible(r.toJSON()), /Ainda não há atendimentos/);
    await click(r, 'Recarregar histórico');
    assert.equal(attempts, 2);
    assert.match(visible(r.toJSON()), /RECUPERADO DEMO/);
  } finally { if (r) act(() => r.unmount()); }
});

test('prontuario: delayed save/finalize cannot reopen another patient or finalize after leaving', async () => {
  const save = deferred();
  const { Component, route, calls } = setup({ post: path => path === '/pacientes/701/atendimentos' ? save.promise : undefined });
  let r;
  try {
    await act(async () => { r = TestRenderer.create(React.createElement(Component)); });
    await click(r, '+ Iniciar atendimento');
    const field = r.root.findAllByType('input').find(node => node.props.value === '' && !node.props['aria-label']);
    await act(async () => { field.props.onChange({ target: { value: 'ANOTACAO A DEMO' } }); });
    await click(r, 'Finalizar');
    await act(async () => { route.set('paciente=702'); });
    await act(async () => { save.resolve(encounter(7011, 'ANOTACAO A DEMO')); });
    assert.doesNotMatch(visible(r.toJSON()), /ANOTACAO A DEMO/);
    assert.equal(calls.filter(c => c.path.endsWith('/finalizar')).length, 0);
    assert.equal(route.qs.get('paciente'), '702');
    assert.ok(button(r, 'Iniciar'));
  } finally { if (r) act(() => r.unmount()); }
});

test('prontuario: late artifacts cannot appear after changing encounter', async () => {
  const old = deferred(), current = deferred();
  const { Component } = setup({ get: path => path === '/pacientes/701/atendimentos' ? Promise.resolve([encounter(1, 'DEMO UM'), encounter(2, 'DEMO DOIS')]) : path === '/pacientes/701/atendimentos/1/artefatos' ? old.promise : path === '/pacientes/701/atendimentos/2/artefatos' ? current.promise : undefined });
  let r;
  try {
    await act(async () => { r = TestRenderer.create(React.createElement(Component)); });
    await click(r, 'Continuar');
    await click(r, '+ Iniciar atendimento');
    const continues = r.root.findAllByType('button').filter(b => b.children.includes('Continuar'));
    await act(async () => { continues[1].props.onClick(); });
    await act(async () => { old.resolve([{ tipo: 'documento', artifact_id: 1, titulo: 'ARTEFATO ANTIGO DEMO', created_at: '2026-09-11T12:00:00Z' }]); });
    assert.doesNotMatch(visible(r.toJSON()), /ARTEFATO ANTIGO DEMO/);
    await act(async () => { current.resolve([]); });
  } finally { if (r) act(() => r.unmount()); }
});

test('prontuario: saving during history load refreshes all encounters, not just the saved one', async () => {
  const old = deferred(); let historyReads = 0;
  const { Component } = setup({
    get: path => path === '/pacientes/701/atendimentos' ? (++historyReads === 1 ? old.promise : Promise.resolve([encounter(2, 'NOVO SALVO'), encounter(1, 'ANTERIOR PRESERVADO')])) : undefined,
    post: path => path === '/pacientes/701/atendimentos' ? Promise.resolve(encounter(2, 'NOVO SALVO')) : undefined,
  });
  let r;
  try {
    await act(async () => { r = TestRenderer.create(React.createElement(Component)); });
    await click(r, '+ Iniciar atendimento');
    await click(r, 'Salvar rascunho');
    await act(async () => { old.resolve([encounter(1, 'RESPOSTA ANTIGA')]); });
    assert.equal(historyReads, 2);
    assert.match(visible(r.toJSON()), /NOVO SALVO/);
    assert.match(visible(r.toJSON()), /ANTERIOR PRESERVADO/);
    assert.doesNotMatch(visible(r.toJSON()), /RESPOSTA ANTIGA/);
  } finally { if (r) act(() => r.unmount()); }
});

test('prontuario: double save is blocked; failed finalization retries the existing draft', async () => {
  const firstSave = deferred(); let attempts = 0;
  const { Component, calls } = setup({
    post: path => path === '/pacientes/701/atendimentos' ? firstSave.promise : path === '/pacientes/701/atendimentos/9/finalizar' ? (++attempts === 1 ? Promise.reject(new Error('FINALIZACAO INDISPONIVEL')) : Promise.resolve({ ...encounter(9, 'FINAL DEMO'), status: 'finalized' })) : undefined,
    patch: path => path === '/pacientes/701/atendimentos/9' ? Promise.resolve(encounter(9, 'RASCUNHO DEMO')) : undefined,
  });
  let r;
  try {
    await act(async () => { r = TestRenderer.create(React.createElement(Component)); });
    await click(r, '+ Iniciar atendimento');
    await act(async () => { button(r, 'Finalizar').props.onClick(); button(r, 'Finalizar').props.onClick(); });
    assert.equal(calls.filter(c => c.method === 'post' && c.path === '/pacientes/701/atendimentos').length, 1);
    assert.equal(r.root.findByType('fieldset').props.disabled, true);
    await act(async () => { firstSave.resolve(encounter(9, 'RASCUNHO DEMO')); });
    assert.match(visible(r.toJSON()), /FINALIZACAO INDISPONIVEL/);
    assert.equal(r.root.findByType('fieldset').props.disabled, false);
    await click(r, 'Finalizar');
    assert.equal(calls.filter(c => c.method === 'post' && c.path === '/pacientes/701/atendimentos').length, 1);
    assert.equal(calls.filter(c => c.method === 'patch').length, 1);
    assert.equal(attempts, 2);
    assert.ok(button(r, 'Iniciar'));
    assert.doesNotMatch(visible(r.toJSON()), /FINALIZACAO INDISPONIVEL/);
  } finally { if (r) act(() => r.unmount()); }
});

test('prontuario: queue opens the requested patient encounter and ignores late navigation', async () => {
  for (const leaveBeforeResponse of [false, true]) {
    const request = deferred();
    const { Component, route } = setup({
      get: path => path === '/agenda-clinica/hoje' ? Promise.resolve([{ appointment_id: 3, scheduled_at: '2026-09-11T12:00:00Z', patient_name: 'DEMO FILA', patient_profile_id: 702, state: 'called' }]) : path === '/pacientes/702/atendimentos/9' ? Promise.resolve(encounter(9, 'ATENDIMENTO FILA DEMO')) : undefined,
      post: path => path === '/agenda-clinica/3/transicao' ? request.promise : undefined,
    });
    let r;
    try {
      await act(async () => { r = TestRenderer.create(React.createElement(Component)); });
      await click(r, 'Atender');
      if (leaveBeforeResponse) { await act(async () => { route.set('paciente=702'); }); await act(async () => { route.set('paciente=701'); }); }
      await act(async () => { request.resolve({ patient_profile_id: 702, encounter_id: 9 }); });
      assert.equal(route.qs.get('paciente'), leaveBeforeResponse ? '701' : '702');
      if (leaveBeforeResponse) assert.ok(button(r, 'Iniciar'));
      else {
        assert.match(visible(r.toJSON()), /Em andamento/);
        assert.ok(r.root.findAllByType('input').some(node => node.props.value === 'ATENDIMENTO FILA DEMO'));
      }
    } finally { if (r) act(() => r.unmount()); }
  }
});

test('prontuario: opening the active encounter again preserves its artifacts and draft', async () => {
  const { Component, calls } = setup({ get: path => path === '/pacientes/701/atendimentos' ? Promise.resolve([encounter(1, 'DEMO')]) : path === '/pacientes/701/atendimentos/1/artefatos' ? Promise.resolve([{ tipo: 'documento', artifact_id: 1, titulo: 'VINCULADO DEMO', created_at: '2026-09-11T12:00:00Z' }]) : undefined });
  let r;
  try {
    await act(async () => { r = TestRenderer.create(React.createElement(Component)); });
    await click(r, 'Continuar');
    assert.match(visible(r.toJSON()), /VINCULADO DEMO/);
    const field = r.root.findAllByType('input').find(node => node.props.value === 'DEMO');
    await act(async () => { field.props.onChange({ target: { value: 'RASCUNHO MODIFICADO DEMO' } }); });
    await click(r, 'Continuar');
    assert.match(visible(r.toJSON()), /VINCULADO DEMO/);
    assert.ok(r.root.findAllByType('input').some(node => node.props.value === 'RASCUNHO MODIFICADO DEMO'));
    assert.equal(calls.filter(c => c.path === '/pacientes/701/atendimentos/1/artefatos').length, 1);
  } finally { if (r) act(() => r.unmount()); }
});

test('prontuario: queue start in the selected patient refreshes history and allows resuming', async () => {
  let reads = 0;
  const { Component } = setup({
    get: path => path === '/agenda-clinica/hoje' ? Promise.resolve([{ appointment_id: 3, scheduled_at: '2026-09-11T12:00:00Z', patient_name: 'DEMO FILA', patient_profile_id: 701, state: 'called' }]) : path === '/pacientes/701/atendimentos/9' ? Promise.resolve(encounter(9, 'ATENDIMENTO FILA DEMO')) : path === '/pacientes/701/atendimentos' ? Promise.resolve(++reads === 1 ? [] : [encounter(9, 'ATENDIMENTO FILA DEMO')]) : undefined,
    post: path => path === '/agenda-clinica/3/transicao' ? Promise.resolve({ patient_profile_id: 701, encounter_id: 9 }) : undefined,
  });
  let r;
  try {
    await act(async () => { r = TestRenderer.create(React.createElement(Component)); });
    await click(r, 'Atender');
    await click(r, 'Fechar');
    assert.equal(reads, 2);
    assert.match(visible(r.toJSON()), /ATENDIMENTO FILA DEMO/);
    assert.ok(button(r, 'Continuar'));
  } finally { if (r) act(() => r.unmount()); }
});
