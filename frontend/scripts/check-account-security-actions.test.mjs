import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { MemoryRouter, useLocation, useNavigate } from 'react-router-dom';

// Real settings/recovery pages, router and API client; authentication context,
// fetch, confirmation and clock are fixtures. Never opens a real session or
// sends an email. The two mutations are exercised only by controlled fetch.
const require = createRequire(import.meta.url);
const source = relative => readFileSync(new URL(`../src/${relative}`, import.meta.url), 'utf8');
const textOf = node => typeof node === 'string' ? node : (node.children ?? []).map(textOf).join('');
const visible = renderer => JSON.stringify(renderer.toJSON());
const button = (renderer, label) => renderer.root.findAllByType('button').find(node => textOf(node).includes(label));
const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return { promise, resolve, reject }; };
const changed = async (renderer, id, value) => { await act(async () => renderer.root.findByProps({ id }).props.onChange({ target: { value } })); };
const submit = renderer => renderer.root.findByType('form').props.onSubmit({ preventDefault() {} });

function harness(transport, { realAuth = false } = {}) {
  const calls = [], modules = new Map(), route = {}, removed = [];
  const state = { confirm: false, confirmations: 0, signouts: 0, cachesCleared: 0 };
  let navigate;
  const storage = { getItem: () => null, setItem() {}, removeItem: key => removed.push(key) };
  const window = { localStorage: storage, sessionStorage: storage,
    location: { pathname: '/minha-conta', search: '', hash: '', assign() { throw Error('Unexpected auth redirect'); } },
    confirm(message) { state.confirmations++; assert.match(message, /incluindo a sessão em uso/); return state.confirm; },
  };
  const auth = { usuario: { id: 900001, email: 'account-a@example.test' }, entrar: async () => {}, async sair() { state.signouts++; await load('lib/api.ts').api.logout(); } };
  function load(relative) {
    if (modules.has(relative)) return modules.get(relative);
    const compiled = ts.transpileModule(source(relative).replaceAll('import.meta.env', '({})'), { fileName: relative,
      compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true } }).outputText;
    const module = { exports: {} };
    vm.runInNewContext(compiled, {
      module, exports: module.exports, window, sessionStorage: storage, Headers, Response, FormData, AbortController, DOMException, URL, URLSearchParams,
      setTimeout: () => 1, clearTimeout() {}, console,
      fetch: (url, init) => { calls.push({ url, method: init.method ?? 'GET', body: init.body ? JSON.parse(init.body) : undefined, signal: init.signal }); return transport(url, init); },
      require: name => {
        if (name.endsWith('.css')) return {};
        if (name === '../lib/auth') return realAuth ? load('lib/auth.tsx') : { useAuth: () => auth };
        if (name === './clinicalCache') return { clearLegacyClinicalCaches: async () => { state.cachesCleared++; } };
        if (name === '../components/Icone') return { __esModule: true, default: () => null };
        if (name === '../components/PublicCardiologyFrame') return { __esModule: true, default: ({ children }) => React.createElement('main', null, children) };
        if (name === '../lib/corviaTheme') return { CORVIA_LOGIN_THEME_KEY: 'theme-fixture' };
        if (name.startsWith('.')) {
          const target = path.posix.normalize(path.posix.join(path.posix.dirname(relative), name));
          return load(`${target}.${existsSync(new URL(`../src/${target}.tsx`, import.meta.url)) ? 'tsx' : 'ts'}`);
        }
        return require(name);
      },
    }, { filename: relative });
    modules.set(relative, module.exports);
    return module.exports;
  }
  function Probe() { Object.assign(route, useLocation()); navigate = useNavigate(); return null; }
  return { state, route, calls, removed, load, auth,
    async mount(t, relative, exportName = 'default', props = {}, entry = '/') {
      const Component = load(relative)[exportName];
      let renderer;
      const tree = () => React.createElement(MemoryRouter,
        { initialEntries: [entry], future: { v7_startTransition: true, v7_relativeSplatPath: true } },
        React.createElement(Probe), React.createElement(Component, props));
      await act(async () => { renderer = TestRenderer.create(tree()); });
      renderer.refreshIdentity = async () => { await act(async () => renderer.update(tree())); };
      t.after(async () => { await act(async () => renderer.unmount()); });
      return renderer;
    },
    async mountAuthenticated(t) {
      const { AuthProvider, useAuth } = load('lib/auth.tsx');
      const Settings = load('components/AccountSecuritySettings.tsx').SessoesConta;
      const Login = load('pages/Entrar.tsx').default;
      function Account() {
        const { usuario, carregando } = useAuth();
        return carregando ? null : React.createElement(usuario ? Settings : Login);
      }
      let renderer;
      await act(async () => { renderer = TestRenderer.create(React.createElement(MemoryRouter,
        { initialEntries: ['/minha-conta'], future: { v7_startTransition: true, v7_relativeSplatPath: true } },
        React.createElement(Probe), React.createElement(AuthProvider, null, React.createElement(Account)))); });
      t.after(async () => { await act(async () => renderer.unmount()); });
      return renderer;
    },
    async go(url) { await act(async () => navigate(url)); },
  };
}
const settings = 'components/AccountSecuritySettings.tsx';
const recovery = 'pages/EsqueciSenha.tsx';
const emailTransport = (url, init) => {
  assert.equal(url, '/api/auth/email-recuperacao');
  assert.equal(init.method, undefined);
  return Promise.resolve(json({ recovery_email: 'current@example.test' }));
};

async function fillRecovery(renderer, address = 'NEW@EXAMPLE.TEST') {
  await changed(renderer, 'email-recuperacao', address);
  await changed(renderer, 'email-recuperacao-senha', 'SYNTHETIC-CURRENT-PASSWORD');
}

test('recovery email reads the current channel and rejects login address or missing password locally', async t => {
  const h = harness(emailTransport), r = await h.mount(t, settings, 'EmailRecuperacao', { loginEmail: 'login@example.test' });
  assert.match(visible(r), /current@example.test/);
  await changed(r, 'email-recuperacao', 'LOGIN@EXAMPLE.TEST');
  await act(async () => submit(r));
  assert.match(visible(r), /diferente do e-mail de login/);
  await changed(r, 'email-recuperacao', 'new@example.test');
  await act(async () => submit(r));
  assert.equal(h.calls.length, 1);
  assert.equal(button(r, 'Salvar e-mail').props.disabled, true);
});

test('recovery email failed read has an explicit retry and never pretends the channel is absent', async t => {
  let reads = 0;
  const h = harness(() => Promise.resolve(++reads === 1 ? json({ detail: 'unavailable' }, 503) : json({ recovery_email: 'restored@example.test' })));
  const r = await h.mount(t, settings, 'EmailRecuperacao', { loginEmail: 'login@example.test' });
  assert.equal(r.root.findAllByType('form').length, 0);
  assert.doesNotMatch(visible(r), /Nenhum e-mail/);
  assert.equal(r.root.findAllByProps({ role: 'alert' }).length, 1);
  await act(async () => button(r, 'Tentar consultar').props.onClick());
  assert.match(visible(r), /restored@example.test/);
  assert.equal(r.root.findAllByProps({ role: 'alert' }).length, 0);
});

test('recovery email requires server success, blocks duplicate writes and clears the password', async t => {
  const pending = deferred();
  const h = harness((url, init) => init.method === 'PUT' ? pending.promise : emailTransport(url, init));
  const r = await h.mount(t, settings, 'EmailRecuperacao', { loginEmail: 'login@example.test' });
  await fillRecovery(r, '  NEW@EXAMPLE.TEST  ');
  await act(async () => { void submit(r); void submit(r); });
  const writes = h.calls.filter(call => call.method === 'PUT');
  assert.equal(writes.length, 1);
  assert.deepEqual(writes[0].body, { recovery_email: 'new@example.test', senha_atual: 'SYNTHETIC-CURRENT-PASSWORD' });
  assert.equal(button(r, 'Salvando').props.disabled, true);
  assert.doesNotMatch(visible(r), /E-mail de recuperação atualizado/);
  await act(async () => pending.resolve(json({ recovery_email: 'new@example.test' })));
  assert.match(visible(r), /E-mail de recuperação atualizado/);
  assert.equal(r.root.findByProps({ id: 'email-recuperacao-senha' }).props.value, '');
  assert.equal(r.root.findByProps({ id: 'email-recuperacao' }).props.value, 'new@example.test');
});

test('wrong password preserves the proposed address, shows the server error and permits retry', async t => {
  let writes = 0;
  const h = harness((url, init) => init.method === 'PUT'
    ? Promise.resolve(++writes === 1 ? json({ detail: 'Senha atual incorreta.' }, 400) : json({ recovery_email: 'new@example.test' }))
    : emailTransport(url, init));
  const r = await h.mount(t, settings, 'EmailRecuperacao', { loginEmail: 'login@example.test' });
  await fillRecovery(r);
  await act(async () => submit(r));
  assert.match(visible(r), /Senha atual incorreta/);
  assert.doesNotMatch(visible(r), /E-mail de recuperação atualizado/);
  assert.equal(r.root.findByProps({ id: 'email-recuperacao' }).props.value, 'NEW@EXAMPLE.TEST');
  assert.equal(r.root.findByProps({ id: 'email-recuperacao-senha' }).props.value, '');
  await changed(r, 'email-recuperacao-senha', 'SYNTHETIC-CORRECT-PASSWORD');
  await act(async () => submit(r));
  assert.match(visible(r), /E-mail de recuperação atualizado/);
  assert.equal(writes, 2);
});

test('recovery email aborts a pending read on unmount', async t => {
  const h = harness((_url, init) => new Promise((_resolve, reject) => init.signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')), { once: true })));
  const r = await h.mount(t, settings, 'EmailRecuperacao', { loginEmail: 'login@example.test' });
  assert.match(visible(r), /Consultando e-mail/);
  await act(async () => r.unmount());
  assert.equal(h.calls[0].signal.aborted, true);
});

test('activation resend is reachable from the existing recovery page and uses the correct public endpoint', async t => {
  const h = harness(async () => json({ nota: 'PRIVATE_RESPONSE_NOT_RENDERED' }, 202));
  const r = await h.mount(t, recovery);
  assert.ok(r.root.findAllByType('a').some(node => node.props.href === '/esqueci-senha?modo=ativacao'));
  await h.go('/esqueci-senha?modo=ativacao');
  await changed(r, 'email', 'ACTIVATION@EXAMPLE.TEST');
  await act(async () => submit(r));
  assert.deepEqual(h.calls.map(({ url, method, body }) => ({ url, method, body })), [{ url: '/api/auth/reenviar-ativacao', method: 'POST', body: { email: 'activation@example.test' } }]);
  assert.match(visible(r), /Se houver uma conta elegível/);
  assert.doesNotMatch(visible(r), /PRIVATE_RESPONSE/);
});

for (const status of [429, 503]) test(`activation resend ${status} preserves the form without exposing account details`, async t => {
  const h = harness(async () => json({ detail: 'PRIVATE_ACCOUNT_DETAIL' }, status));
  const r = await h.mount(t, recovery, 'default', {}, '/esqueci-senha?modo=ativacao');
  await changed(r, 'email', 'activation@example.test');
  await act(async () => submit(r));
  assert.equal(r.root.findByProps({ id: 'email' }).props.value, 'activation@example.test');
  assert.equal(r.root.findByType('button').props.disabled, false);
  assert.equal(r.root.findAllByProps({ role: 'alert' }).length, 1);
  assert.doesNotMatch(visible(r), /PRIVATE_ACCOUNT_DETAIL|Solicitação recebida/);
});

test('activation duplicate submit dispatches once; changing mode cannot receive the old success', async t => {
  const pending = deferred(), h = harness(() => pending.promise);
  const r = await h.mount(t, recovery, 'default', {}, '/esqueci-senha?modo=ativacao');
  await changed(r, 'email', 'activation@example.test');
  await act(async () => { void submit(r); void submit(r); });
  assert.equal(h.calls.length, 1);
  assert.equal(r.root.findByType('button').props.disabled, true);
  await h.go('/esqueci-senha');
  await act(async () => pending.resolve(json({}, 202)));
  assert.match(visible(r), /Esqueci minha senha/);
  assert.equal(r.root.findAllByType('form').length, 1);
  assert.doesNotMatch(visible(r), /Solicitação recebida|Confira seu canal de recuperação/);
});

test('session cancellation makes no request and successful confirmation dispatches only once', async t => {
  const pending = deferred();
  const h = harness(url => url === '/api/auth/encerrar-todas-sessoes' ? pending.promise : Promise.resolve(json({})));
  const r = await h.mount(t, settings, 'SessoesConta');
  await act(async () => button(r, 'Encerrar todas').props.onClick());
  assert.equal(h.calls.length, 0);
  h.state.confirm = true;
  await act(async () => { void button(r, 'Encerrar todas').props.onClick(); void button(r, 'Encerrar todas').props.onClick(); });
  assert.equal(h.calls.length, 1);
  assert.equal(h.calls[0].url, '/api/auth/encerrar-todas-sessoes');
  assert.equal(h.state.signouts, 0);
  assert.equal(h.route.pathname, '/');
  await act(async () => pending.resolve(json({ nota: 'Todas as sessões da conta foram encerradas.' })));
  assert.equal(h.state.signouts, 1);
  assert.equal(h.state.cachesCleared, 1);
  assert.equal(h.route.pathname, '/entrar');
  assert.equal(h.route.state.todasSessoesEncerradas, true);
});

test('failed revocation shows error, keeps the session and requires confirmation again on retry', async t => {
  let attempts = 0;
  const h = harness(url => Promise.resolve(url === '/api/auth/encerrar-todas-sessoes' && ++attempts === 1 ? json({ detail: 'Falha ao encerrar sessões.' }, 503) : json({})));
  h.state.confirm = true;
  const r = await h.mount(t, settings, 'SessoesConta');
  await act(async () => button(r, 'Encerrar todas').props.onClick());
  assert.match(visible(r), /Falha ao encerrar sessões/);
  assert.equal(h.state.signouts, 0);
  assert.equal(h.route.pathname, '/');
  assert.equal(button(r, 'Encerrar todas').props.disabled, false);
  await act(async () => button(r, 'Encerrar todas').props.onClick());
  assert.equal(h.state.confirmations, 2);
  assert.equal(h.route.pathname, '/entrar');
});

test('confirmed revocation still returns to login if the extra logout transport fails', async t => {
  const h = harness(url => url === '/api/auth/sair' ? Promise.reject(new Error('offline')) : Promise.resolve(json({})));
  h.state.confirm = true;
  const r = await h.mount(t, settings, 'SessoesConta');
  await act(async () => button(r, 'Encerrar todas').props.onClick());
  assert.equal(h.state.signouts, 1);
  assert.equal(h.state.cachesCleared, 1);
  assert.ok(h.removed.includes('corvia:login-return:v1'));
  assert.equal(h.route.pathname, '/entrar');
  assert.equal(h.route.state.todasSessoesEncerradas, true);
});

test('login displays the confirmed-session notice', async t => {
  const h = harness(() => { throw Error('No request expected'); });
  const r = await h.mount(t, 'pages/Entrar.tsx', 'default', {}, { pathname: '/entrar', state: { todasSessoesEncerradas: true } });
  assert.match(visible(r), /Todas as sessões da conta foram encerradas/);
  assert.equal(r.root.findAllByProps({ role: 'status' }).length, 1);
});

test('MinhaConta keeps one recovery and session section across profile and identity refreshes', async t => {
  const profile = deferred();
  const h = harness(async (url, init) => {
    assert.equal(init.method, undefined, 'the account integration fixture only reads data');
    if (url === '/api/auth/me') return profile.promise;
    if (url === '/api/auth/email-recuperacao') return json({ recovery_email: `recovery-${h.auth.usuario.id}@example.test` });
    if (['/api/agenda/integrations', '/api/assinatura/provedores', '/api/assinatura/certificadoras'].includes(url)) return json([]);
    if (url === '/api/assinatura/certificado-a1') return json({ conectado: false });
    if (url === '/api/email/assinatura') return json({ ativa: false });
    if (url === '/api/billing/status') return json({ status: 'ativo', current_period_end: null, plano: null });
    if (url === '/api/billing/faturas') return json({ faturas: [] });
    throw Error('Unexpected account request: ' + url);
  });
  h.auth.usuario = { ...h.auth.usuario, full_name: 'QA account A' };
  const r = await h.mount(t, 'pages/MinhaConta.tsx');
  // Inspect rendered host output, including any orphan left by duplicate-key
  // reconciliation, instead of only inspecting the current component fibers.
  function expectSections(recoveryCount = 1) {
    const nodes = [];
    function visit(node) {
      if (!node || typeof node === 'string') return;
      if (Array.isArray(node)) { node.forEach(visit); return; }
      nodes.push(node);
      node.children?.forEach(visit);
    }
    visit(r.toJSON());
    const count = (type, property, value) => nodes.filter(node => node.type === type && node.props[property] === value).length;
    assert.equal(count('section', 'aria-labelledby', 'email-recuperacao-titulo'), recoveryCount, 'one visible recovery section for the current identity');
    assert.equal(count('h2', 'id', 'email-recuperacao-titulo'), recoveryCount, 'recovery heading IDs must be unique');
    assert.equal(count('input', 'id', 'email-recuperacao'), recoveryCount, 'recovery inputs must not accumulate');
    assert.equal(count('section', 'aria-labelledby', 'sessoes-conta-titulo'), 1, 'one visible session section');
    assert.equal(count('h2', 'id', 'sessoes-conta-titulo'), 1, 'session heading IDs must be unique');
  }
  expectSections();
  await changed(r, 'email-recuperacao', 'draft@example.test');
  await changed(r, 'email-recuperacao-senha', 'SYNTHETIC-CURRENT-PASSWORD');
  await act(async () => profile.resolve(json({ ...h.auth.usuario, full_name: 'QA updated profile' })));
  h.auth.usuario = { ...h.auth.usuario, full_name: 'QA refreshed identity' };
  await r.refreshIdentity();
  expectSections();
  assert.equal(r.root.findByProps({ id: 'email-recuperacao' }).props.value, 'draft@example.test', 'same-account refresh preserves the pending form');

  h.auth.usuario = { id: 900002, email: 'account-b@example.test' };
  await r.refreshIdentity();
  expectSections();
  assert.equal(r.root.findByProps({ id: 'email-recuperacao' }).props.value, 'recovery-900002@example.test');
  assert.equal(r.root.findByProps({ id: 'email-recuperacao-senha' }).props.value, '', 'a different identity starts with an empty password');

  h.auth.usuario = { ...h.auth.usuario, investidor: true };
  await r.refreshIdentity();
  expectSections(0);
  h.auth.usuario = { ...h.auth.usuario, investidor: false };
  await r.refreshIdentity();
  expectSections();
});

for (const outcome of ['success', 'error']) {
  for (const departure of ['unmount', 'different-account']) {
    test(`late revocation ${outcome} after ${departure} cannot log out, navigate or alter the newer UI`, async t => {
      const pending = deferred();
      const h = harness(url => url === '/api/auth/encerrar-todas-sessoes' ? pending.promise : Promise.resolve(json({})));
      h.state.confirm = true;
      const r = await h.mount(t, settings, 'SessoesConta');
      await act(async () => { void button(r, 'Encerrar todas').props.onClick(); });
      if (departure === 'unmount') await act(async () => r.unmount());
      else {
        h.auth.usuario = { id: 900002, email: 'account-b@example.test' };
        await r.refreshIdentity();
        assert.equal(button(r, 'Encerrar todas').props.disabled, false);
      }
      await act(async () => pending.resolve(outcome === 'success' ? json({}) : json({ detail: 'ERRO DA CONTA ANTIGA' }, 503)));
      assert.equal(h.state.signouts, 0);
      assert.equal(h.state.cachesCleared, 0);
      assert.equal(h.calls.filter(call => call.url === '/api/auth/sair').length, 0);
      assert.equal(h.route.pathname, '/');
      if (departure === 'different-account') {
        assert.doesNotMatch(visible(r), /ERRO DA CONTA ANTIGA/);
        assert.equal(button(r, 'Encerrar todas').props.disabled, false);
      }
    });
  }
}

test('navigation from logout also stops if the account changes while local logout is pending', async t => {
  const logout = deferred();
  const h = harness(url => url === '/api/auth/sair' ? logout.promise : Promise.resolve(json({})));
  h.state.confirm = true;
  const r = await h.mount(t, settings, 'SessoesConta');
  await act(async () => { void button(r, 'Encerrar todas').props.onClick(); });
  assert.equal(h.state.signouts, 1);
  h.auth.usuario = { id: 900002, email: 'account-b@example.test' };
  await r.refreshIdentity();
  await act(async () => logout.resolve(json({})));
  assert.equal(h.route.pathname, '/');
});


test('real AuthProvider clears the React identity and preserves the successful login notice', async t => {
  const h = harness(async url => {
    if (url === '/api/auth/session-status') return json({ authenticated: true });
    if (url === '/api/auth/me') return json({ id: 900001, email: 'account-a@example.test' });
    if (url === '/api/auth/encerrar-todas-sessoes' || url === '/api/auth/sair') return json({});
    throw Error('Unexpected request: ' + url);
  }, { realAuth: true });
  h.state.confirm = true;
  const r = await h.mountAuthenticated(t);
  await act(async () => button(r, 'Encerrar todas').props.onClick());
  assert.equal(h.route.pathname, '/entrar');
  assert.ok(r.root.findByProps({ id: 'email' }));
  assert.match(visible(r), /Todas as sessões da conta foram encerradas/);
  assert.equal(h.state.cachesCleared, 1);
});
