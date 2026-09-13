import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import * as Router from 'react-router-dom';

// Real TSX components/router. Synthetic data only; no browser, HTTP or email.
const require = createRequire(import.meta.url);
const source = path => readFileSync(new URL(`../src/${path}`, import.meta.url), 'utf8');
const visible = node => typeof node === 'string' || typeof node === 'number' ? String(node)
  : Array.isArray(node) ? node.map(visible).join(' ') : node ? visible(node.children) : '';
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((a, b) => { resolve = a; reject = b; });
  return { promise, resolve, reject };
};
class ApiError extends Error { constructor(status, message) { super(message); this.status = status; } }
const empty = { __esModule: true, default: () => null };
const wrapper = { __esModule: true, default: ({ children }) => React.createElement('section', null, children) };
const realModules = {
  './lib/loginReturn': 'lib/loginReturn.ts', '../lib/loginReturn': 'lib/loginReturn.ts',
  './lib/pageTitle': 'lib/pageTitle.ts', './clinicalRouteRegistry': 'lib/clinicalRouteRegistry.ts',
  './components/LoginReturn': 'components/LoginReturn.tsx',
};

function compile(path, overrides = {}, extra = {}) {
  const compiled = ts.transpileModule(source(path), { compilerOptions: {
    module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX,
  } }).outputText;
  const module = { exports: {} };
  const globals = { URL, URLSearchParams, Error, setTimeout: () => 0,
    window: { sessionStorage: { getItem: () => null } }, document: { title: '' }, ...extra };
  vm.runInNewContext(compiled, {
    module, exports: module.exports, ...globals,
    require: name => Object.hasOwn(overrides, name) ? overrides[name]
      : Object.hasOwn(realModules, name) ? compile(realModules[name], overrides, globals)
      : name === './aiFeatureFlags' ? overrides['./lib/aiFeatureFlags']
      : name.endsWith('.css') ? {} : name.includes('/components/') ? empty
      : name.startsWith('./pages/') ? { __esModule: true, default: () => React.createElement('div', null, name) }
      : require(name),
  });
  return module.exports;
}

function recovery(post) {
  const calls = [];
  const api = { post: (path, payload) => { calls.push({ path, payload }); return post(path, payload); } };
  const Component = compile('pages/EsqueciSenha.tsx', {
    '../lib/api': { api, ApiError }, '../components/PublicCardiologyFrame': wrapper,
  }).default;
  return { Component, calls };
}
async function mount(Component) {
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(Router.MemoryRouter, null, React.createElement(Component))); });
  return renderer;
}
const email = renderer => renderer.root.findByProps({ id: 'email' });
const submit = renderer => renderer.root.findByType('form').props.onSubmit({ preventDefault() {} });

for (const [label, failure, expected] of [
  ['503', new ApiError(503, 'PRIVATE_ACCOUNT_DETAIL'), /Não foi possível solicitar a recuperação/],
  ['network', new TypeError('PRIVATE_NETWORK_DETAIL'), /Não foi possível solicitar a recuperação/],
  ['429', new ApiError(429, 'PRIVATE_RATE_DETAIL'), /Muitas tentativas/],
]) test(`recovery: ${label} stays on form, preserves address and allows successful retry`, async () => {
  let attempts = 0;
  const h = recovery(() => ++attempts === 1 ? Promise.reject(failure) : Promise.resolve({ ok: true }));
  const r = await mount(h.Component);
  try {
    await act(async () => { email(r).props.onChange({ target: { value: 'RECOVERY@EXAMPLE.INVALID' } }); });
    await act(async () => { await submit(r); });
    assert.match(visible(r.toJSON()), expected);
    assert.doesNotMatch(visible(r.toJSON()), /Confira seu canal de recuperação|PRIVATE_/);
    assert.equal(email(r).props.value, 'RECOVERY@EXAMPLE.INVALID');
    assert.equal(r.root.findByType('button').props.disabled, false);
    assert.equal(r.root.findAllByProps({ role: 'alert' }).length, 1);
    await act(async () => { await submit(r); });
    assert.match(visible(r.toJSON()), /Confira seu canal de recuperação/);
    assert.equal(h.calls.length, 2);
    assert.equal(h.calls[1].path, '/auth/esqueci-senha');
    assert.equal(h.calls[1].payload.email, 'recovery@example.invalid');
  } finally { act(() => r.unmount()); }
});

test('recovery: pending request blocks same-frame duplicate submissions and does not show success early', async () => {
  const pending = deferred();
  const h = recovery(() => pending.promise);
  const r = await mount(h.Component);
  try {
    await act(async () => { email(r).props.onChange({ target: { value: 'demo@example.invalid' } }); });
    await act(async () => { void submit(r); void submit(r); });
    assert.equal(h.calls.length, 1);
    assert.equal(r.root.findByType('button').props.disabled, true);
    assert.equal(email(r).props.disabled, true);
    assert.doesNotMatch(visible(r.toJSON()), /Confira seu canal de recuperação/);
    await act(async () => { pending.resolve({ ok: true }); });
    assert.match(visible(r.toJSON()), /Confira seu canal de recuperação/);
  } finally { act(() => r.unmount()); }
});

test('recovery: every successful response has identical neutral anti-enumeration confirmation', async () => {
  const confirmations = [];
  for (const reply of [{ found: true, message: 'PRIVATE_FOUND_ACCOUNT' }, { found: false, message: 'PRIVATE_ABSENT_ACCOUNT' }]) {
    const h = recovery(() => Promise.resolve(reply));
    const r = await mount(h.Component);
    try {
      await act(async () => { email(r).props.onChange({ target: { value: 'demo@example.invalid' } }); });
      await act(async () => { await submit(r); });
      confirmations.push(visible(r.toJSON()));
    } finally { act(() => r.unmount()); }
  }
  assert.equal(confirmations[0], confirmations[1]);
  assert.match(confirmations[0], /Se o endereço estiver vinculado a uma conta ativa/);
  assert.doesNotMatch(confirmations[0], /PRIVATE_/);
});

function routedApp(user) {
  const calls = [], route = {};
  const api = { post: async (path, payload) => { calls.push({ path, payload }); return { ok: true }; } };
  const Reset = compile('pages/RedefinirSenha.tsx', {
    '../lib/api': { api, ApiError }, '../components/PublicCardiologyFrame': wrapper,
    '../components/CampoSenha': { __esModule: true, default: props => React.createElement('input', { ...props, type: 'password' }) },
  });
  const App = compile('App.tsx', {
    './lib/auth': { useAuth: () => ({ usuario: user, carregando: false }) },
    './lib/useActivityHeartbeat': { useActivityHeartbeat: () => {} },
    './lib/cardiologySpacesFeature': { cardiologySpacesEnabled: () => false },
    './lib/aiFeatureFlags': { heartTeamEnabled: () => false, whatsappAssistantEnabled: () => false },
    './components/Estado': { Carregando: () => React.createElement('p', null, 'Loading fixture') },
    './components/Shell': { __esModule: true, default: () => React.createElement(Router.Outlet) },
    './pages/RedefinirSenha': Reset,
  }).default;
  function Probe() { route.current = Router.useLocation(); route.action = Router.useNavigationType(); return null; }
  const Component = ({ initial }) => React.createElement(Router.MemoryRouter, { initialEntries: [initial] },
    React.createElement(Probe), React.createElement(App));
  return { Component, calls, route };
}

test('activation alias preserves the token/query/hash with replace, anonymous or with an existing session', async () => {
  for (const user of [null, { id: -1, role: 'admin', profile_completion_required: true, kyc_required: true }]) {
    const h = routedApp(user);
    let r;
    try {
      const search = '?token=DEMO%2BTOKEN%2F%3D%3D&alvo=email';
      await act(async () => { r = TestRenderer.create(React.createElement(h.Component, { initial: `/ativar-conta${search}#recuperacao` })); });
      assert.equal(h.route.current.pathname, '/redefinir-senha');
      assert.equal(h.route.current.search, search);
      assert.equal(h.route.current.hash, '#recuperacao');
      assert.equal(h.route.action, 'REPLACE');
      assert.match(visible(r.toJSON()), /Definir nova senha do CorVIA Mail/);
      await act(async () => {
        r.root.findByProps({ id: 'senha' }).props.onChange({ target: { value: 'SYNTHETIC-PASSWORD-123' } });
        r.root.findByProps({ id: 'confirmacao' }).props.onChange({ target: { value: 'SYNTHETIC-PASSWORD-123' } });
      });
      await act(async () => { submit(r); });
      assert.equal(h.calls.length, 1);
      assert.equal(h.calls[0].path, '/auth/redefinir-senha');
      assert.equal(h.calls[0].payload.token, 'DEMO+TOKEN/==');
    } finally { if (r) act(() => r.unmount()); }
  }
});

test('activation without a token shows invalid-link recovery, never makes a reset request', async () => {
  const h = routedApp(null);
  let r;
  try {
    await act(async () => { r = TestRenderer.create(React.createElement(h.Component, { initial: '/ativar-conta' })); });
    assert.match(visible(r.toJSON()), /Link inválido/);
    assert.equal(h.calls.length, 0);
  } finally { if (r) act(() => r.unmount()); }
});

test('public reset and activation paths retain React Router trailing-slash compatibility', async () => {
  for (const pathname of ['/ativar-conta/', '/redefinir-senha/']) {
    const h = routedApp(null);
    let r;
    try {
      await act(async () => { r = TestRenderer.create(React.createElement(h.Component, { initial: `${pathname}?token=DEMO-LOCAL` })); });
      assert.match(visible(r.toJSON()), /Definir nova senha/);
      assert.equal(h.route.current.search, '?token=DEMO-LOCAL');
      assert.equal(h.calls.length, 0);
    } finally { if (r) act(() => r.unmount()); }
  }
});

test('public token routes do not bypass existing profile gates on clinical routes', async () => {
  const h = routedApp({ id: -1, role: 'admin', profile_completion_required: true });
  let r;
  try {
    await act(async () => { r = TestRenderer.create(React.createElement(h.Component, { initial: '/prontuario' })); });
    assert.equal(h.route.current.pathname, '/minha-conta');
    assert.doesNotMatch(visible(r.toJSON()), /pages\/Prontuario|Definir nova senha/);
    assert.equal(h.calls.length, 0);
  } finally { if (r) act(() => r.unmount()); }
});
