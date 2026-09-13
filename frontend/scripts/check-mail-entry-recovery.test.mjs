import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import TestRenderer, { act } from 'react-test-renderer';
import { MemoryRouter, Route, Routes, useLocation, useNavigate } from 'react-router-dom';

// Página, abas, router e API reais. Somente autenticação, storage, relógio e
// fetch são controlados: nenhum e-mail, pagamento, usuário ou rede reais.
const require = createRequire(import.meta.url);
const text = renderer => JSON.stringify(renderer.toJSON());
const textOf = node => typeof node === 'string' ? node : (node.children ?? []).map(textOf).join('');
const button = (renderer, label) => renderer.root.findAllByType('button').find(node => textOf(node) === label);
const response = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { 'Content-Type': 'application/json' },
});
const storage = () => {
  const entries = new Map();
  return { getItem: key => entries.get(key) ?? null, setItem: (key, value) => entries.set(key, value), removeItem: key => entries.delete(key) };
};

function harness({ respectAbort = false, user = { id: -1 }, loading = false, mailboxSession = false } = {}) {
  const calls = [], modules = new Map(), timers = new Map(), redirects = [];
  const auth = { usuario: user, carregando: loading };
  const localStorage = storage(), sessionStorage = storage();
  if (mailboxSession) sessionStorage.setItem('corviamail.token', 'fixture-mail-session');
  let nextTimer = 0, navigate, pathname;
  const window = { localStorage, sessionStorage,
    location: { pathname: '/corvia-mail', search: '', hash: '', assign: url => redirects.push(url) },
  };
  function load(relative) {
    if (modules.has(relative)) return modules.get(relative);
    const source = readFileSync(new URL(`../src/${relative}`, import.meta.url), 'utf8').replaceAll('import.meta.env', '({})');
    const code = ts.transpileModule(source, { fileName: relative, compilerOptions: {
      module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true,
    } }).outputText;
    const module = { exports: {} };
    vm.runInNewContext(code, {
      module, exports: module.exports, window, localStorage, sessionStorage,
      Headers, Response, FormData, AbortController, DOMException, URL, URLSearchParams,
      setTimeout: (fn, ms) => { const id = ++nextTimer; timers.set(id, { fn, ms }); return id; },
      clearTimeout: id => timers.delete(id),
      fetch: (url, init) => new Promise((resolve, reject) => {
        assert.equal(init.method ?? 'GET', 'GET', 'esta verificação de entrada não deve enviar nada');
        calls.push({ url, init, resolve, reject });
        if (respectAbort && init.signal) {
          const abort = () => reject(new DOMException('Aborted fixture', 'AbortError'));
          if (init.signal.aborted) abort();
          else init.signal.addEventListener('abort', abort, { once: true });
        }
      }),
      require: name => {
        if (name.endsWith('.css')) return {};
        if (name === '../lib/auth') return { useAuth: () => auth };
        if (name === './clinicalCache') return { clearLegacyClinicalCaches() {} };
        if (name.startsWith('.')) {
          const target = path.posix.normalize(path.posix.join(path.posix.dirname(relative), name));
          return load(`${target}.${target.startsWith('components/') ? 'tsx' : 'ts'}`);
        }
        return require(name);
      },
    }, { filename: relative });
    modules.set(relative, module.exports);
    return module.exports;
  }
  function Location() { navigate = useNavigate(); pathname = useLocation().pathname; return null; }
  return {
    calls, auth, redirects,
    get pathname() { return pathname; },
    requests(endpoint = '/email/conta') { return calls.filter(call => call.url === `/api${endpoint}`); },
    async reply(call, body, status = 200) { assert.ok(call, 'a consulta precisa existir'); await act(async () => call.resolve(response(body, status))); },
    async go(url) { await act(async () => navigate(url)); },
    async advance(ms) { await act(async () => {
      for (const [id, timer] of [...timers]) if (timer.ms <= ms && timers.has(id)) { timers.delete(id); timer.fn(); }
    }); },
    async mount(t) {
      const Page = load('pages/CorviaMail.tsx').default;
      const element = () => React.createElement(MemoryRouter, {
        initialEntries: ['/corvia-mail'], future: { v7_startTransition: true, v7_relativeSplatPath: true },
      }, React.createElement(Location), React.createElement(Routes, null,
        React.createElement(Route, { path: '/corvia-mail', element: React.createElement(Page) }),
        React.createElement(Route, { path: '*', element: React.createElement('p', null, 'Outra página') })));
      let renderer;
      await act(async () => { renderer = TestRenderer.create(element()); });
      t.after(async () => { await act(async () => renderer.unmount()); });
      return { renderer, async updateAuth(usuario, carregando = false) {
        Object.assign(auth, { usuario, carregando });
        await act(async () => renderer.update(element()));
      } };
    },
  };
}

test('503 remains an explicit read failure and retry restores all active-account tabs', async t => {
  const h = harness(), { renderer } = await h.mount(t);
  assert.match(text(renderer), /Carregando/);
  assert.equal(renderer.root.findAllByType('input').length, 0);
  await h.reply(h.requests()[0], { detail: 'Serviço temporariamente indisponível.' }, 503);
  assert.match(text(renderer), /Serviço temporariamente indisponível/);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 1);
  assert.equal(renderer.root.findAllByType('input').length, 0);
  assert.equal(h.requests('/billing/status-email').length, 0);
  await act(async () => button(renderer, 'Tentar novamente').props.onClick());
  assert.match(text(renderer), /Carregando/);
  await h.reply(h.requests()[1], { ativa: true });
  for (const label of ['Entrar', 'Esqueci a senha', 'Gerenciar']) assert.ok(button(renderer, label), label);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
  assert.equal(renderer.root.findByProps({ type: 'checkbox' }).props.checked, true);
});

test('only a confirmed inactive account opens the existing subscription and activation flow', async t => {
  const h = harness(), { renderer } = await h.mount(t);
  await h.reply(h.requests()[0], { ativa: false });
  assert.equal(button(renderer, 'Esqueci a senha'), undefined);
  assert.equal(renderer.root.findAllByProps({ id: 'endereco-email' }).length, 0);
  assert.equal(h.requests('/billing/status-email').length, 1);
  assert.equal(h.requests('/email/termo-lgpd').length, 1);
  await h.reply(h.requests('/billing/status-email')[0], { status: 'inativo', preco_definido: true, preco_centavos: 10000, incluido_no_plano: false });
  await h.reply(h.requests()[1], { ativa: false });
  await h.reply(h.requests('/email/termo-lgpd')[0], { versao: 'fixture', texto: 'Termo demonstrativo' });
  assert.equal(button(renderer, 'Assinar o CorvIA Mail').props.disabled, false);
  assert.ok(h.requests('/email/sugestao-endereco')[0]);
  assert.equal(h.requests('/billing/checkout-email').length, 0);
});

for (const late of ['demo', '503', '401']) {
  test(`switching users ignores a late ${late} response after the current account succeeds`, async t => {
    const h = harness(), { renderer, updateAuth } = await h.mount(t);
    const old = h.requests()[0];
    await updateAuth({ id: -2 });
    assert.equal(old.init.signal.aborted, true);
    assert.match(text(renderer), /Carregando/);
    await h.reply(h.requests()[1], { ativa: true });
    await h.reply(old, late === 'demo' ? { ativa: false, modo_demonstracao: true } : { detail: 'Resposta de outra identidade' }, late === 'demo' ? 200 : Number(late));
    assert.ok(button(renderer, 'Gerenciar'));
    assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
    assert.equal(h.pathname, '/corvia-mail');
    assert.deepEqual(h.redirects, []);
    assert.equal(h.requests('/billing/status-email').length, 0);
  });
}

test('a previous account cannot finish loading or choose a tab for the current user', async t => {
  const h = harness(), { renderer, updateAuth } = await h.mount(t);
  const old = h.requests()[0];
  await updateAuth({ id: -2 });
  await h.reply(old, { ativa: false });
  assert.match(text(renderer), /Carregando/);
  assert.equal(h.requests('/billing/status-email').length, 0);
  await h.reply(h.requests()[1], { ativa: true });
  await act(async () => button(renderer, 'Esqueci a senha').props.onClick());
  await updateAuth({ id: -2, full_name: 'Mesmo usuário atualizado' });
  assert.ok(renderer.root.findByProps({ id: 'endereco-recuperar' }));
  assert.equal(h.requests().length, 2, 'refreshing the same identity must preserve the chosen tab');
});

test('logout renders the public gateway and cannot be reversed by a late mailbox response', async t => {
  const h = harness({ mailboxSession: true }), { renderer, updateAuth } = await h.mount(t);
  const old = h.requests()[0];
  await updateAuth(null);
  assert.equal(old.init.signal.aborted, true);
  await h.reply(old, { ativa: true });
  assert.match(text(renderer), /Entre primeiro no seu espaço profissional/);
  assert.equal(h.pathname, '/corvia-mail');
  assert.equal(h.requests().length, 1);
});

test('switching a loaded identity clears its selected tab and entered address immediately', async t => {
  const h = harness(), { renderer, updateAuth } = await h.mount(t);
  await h.reply(h.requests()[0], { ativa: true });
  await act(async () => button(renderer, 'Esqueci a senha').props.onClick());
  await act(async () => renderer.root.findByProps({ id: 'endereco-recuperar' }).props.onChange({ target: { value: 'anterior@example.test' } }));
  await updateAuth({ id: -2 });
  assert.equal(renderer.root.findAllByType('input').length, 0);
  assert.match(text(renderer), /Carregando/);
  await h.reply(h.requests()[1], { ativa: true });
  assert.equal(renderer.root.findByProps({ id: 'endereco-email' }).props.value, '');
  assert.equal(renderer.root.findAllByProps({ id: 'endereco-recuperar' }).length, 0);
  assert.doesNotMatch(text(renderer), /anterior@example/);
});

test('unmount aborts the transport and even an abort-ignoring demo result cannot navigate back', async t => {
  const h = harness(), { renderer } = await h.mount(t);
  const old = h.requests()[0];
  await h.go('/outra-pagina');
  assert.equal(old.init.signal.aborted, true);
  await h.reply(old, { ativa: false, modo_demonstracao: true });
  assert.equal(h.pathname, '/outra-pagina');
  assert.match(text(renderer), /Outra página/);
});

test('transport cancellation during a user switch does not expose an obsolete abort error', async t => {
  const h = harness({ respectAbort: true }), { renderer, updateAuth } = await h.mount(t);
  await updateAuth({ id: -2 });
  assert.equal(h.requests()[0].init.signal.aborted, true);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
  await h.reply(h.requests()[1], { ativa: true });
  assert.ok(button(renderer, 'Gerenciar'));
});

test('a pending account read has a bounded wait and a manual retry', async t => {
  const h = harness({ respectAbort: true }), { renderer } = await h.mount(t);
  await h.advance(15000);
  assert.equal(h.requests()[0].init.signal.aborted, true);
  assert.match(text(renderer), /A consulta demorou mais que o esperado/);
  assert.equal(renderer.root.findAllByType('input').length, 0);
  await act(async () => button(renderer, 'Tentar novamente').props.onClick());
  await h.reply(h.requests()[1], { ativa: true });
  assert.ok(button(renderer, 'Gerenciar'));
});

test('a current 401 presents a session recovery link and never pretends the account is inactive', async t => {
  const h = harness(), { renderer } = await h.mount(t);
  await h.reply(h.requests()[0], {}, 401);
  assert.match(text(renderer), /Sessão expirada/);
  assert.ok(renderer.root.findAllByType('a').some(node => node.props.href === '/entrar'));
  assert.deepEqual(h.redirects, []);
  assert.equal(h.requests('/billing/status-email').length, 0);
  assert.equal(renderer.root.findAllByType('input').length, 0);
});

for (const [name, options, account] of [
  ['demonstration', {}, { ativa: false, modo_demonstracao: true }],
  ['active mailbox session', { mailboxSession: true }, { ativa: true }],
]) {
  test(`confirmed ${name} preserves the existing direct mailbox navigation`, async t => {
    const h = harness(options);
    await h.mount(t);
    await h.reply(h.requests()[0], account);
    assert.equal(h.pathname, '/caixa-de-email');
    assert.equal(h.requests('/billing/status-email').length, 0);
  });
}

test('anonymous users and authentication still loading do not query private account status', async t => {
  const h = harness({ loading: true }), { renderer, updateAuth } = await h.mount(t);
  assert.equal(h.calls.length, 0);
  assert.match(text(renderer), /Carregando/);
  await updateAuth(null);
  assert.equal(h.calls.length, 0);
  assert.match(text(renderer), /Entre primeiro no seu espaço profissional/);
});
