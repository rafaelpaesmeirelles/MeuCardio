import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import TestRenderer from 'react-test-renderer';
import ts from 'typescript';
const { act } = TestRenderer;
const root = fileURLToPath(new URL('../', import.meta.url));
const temp = await mkdtemp(path.join(tmpdir(), 'corvia-universal-favorites-'));
await symlink(path.join(root, 'node_modules'), path.join(temp, 'node_modules'));
after(() => rm(temp, { recursive: true, force: true }));
const compile = source => ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX } }).outputText;
await writeFile(path.join(temp, 'favorites.mjs'), compile(await readFile(path.join(root, 'src/lib/favorites.ts'), 'utf8')));
for (const [name, file] of [['Button', 'src/components/BotaoFavorito.tsx'], ['Favorites', 'src/pages/Favoritos.tsx']]) {
  let source = await readFile(path.join(root, file), 'utf8');
  source = source.replace('import { api } from "../lib/api";', 'const api = { get: (...args) => globalThis.favoriteFixture.get(...args), post: (...args) => globalThis.favoriteFixture.post(...args), delete: (...args) => globalThis.favoriteFixture.delete(...args) };');
  source = source.replace('import { useAuth } from "../lib/auth";', 'const useAuth = () => ({ usuario: globalThis.favoriteFixture.user });');
  source = source.replace('"../lib/favorites"', '"./favorites.mjs"');
  source = source.replace(/import "\.\.\/styles\/[^\"]+";/g, '');
  source = source.replace('import { Carregando, Vazio } from "../components/Estado";', 'const Carregando = () => <p>Carregando…</p>; const Vazio = props => <p>{props.titulo} {props.acao}</p>;');
  source = source.replace('import("../components/ScientificReadingAccess")', 'Promise.resolve({ default: props => <span data-reading-type={props.entityType} data-reading-slug={props.slug} data-lazy={props.lazy} /> })');
  await writeFile(path.join(temp, `${name}.mjs`), compile(source));
}
const { default: Button } = await import(pathToFileURL(path.join(temp, 'Button.mjs')));
const { default: Favorites } = await import(pathToFileURL(path.join(temp, 'Favorites.mjs')));
const tree = (Component, props = {}) => React.createElement(MemoryRouter, { future: { v7_startTransition: true, v7_relativeSplatPath: true } }, React.createElement(Component, props));
const text = value => typeof value === 'string' ? value : (value?.children ?? []).map(text).join('');
const buttons = renderer => renderer.root.findAllByType('button');
const button = (renderer, label) => buttons(renderer).find(node => node.children.join('').includes(label));
const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return { promise, resolve, reject }; };
function setup(overrides = {}) {
  const calls = [];
  globalThis.window = new EventTarget();
  globalThis.favoriteFixture = { user: { id: 1 },
    get: (...args) => { calls.push(['get', ...args]); return Promise.resolve({ favorited: false, favorite_id: null, available: true }); },
    post: (...args) => { calls.push(['post', ...args]); return Promise.resolve({ id: 90 }); },
    delete: (...args) => { calls.push(['delete', ...args]); return Promise.resolve(); }, ...overrides };
  return calls;
}
async function mount(t, Component = Button, props = { itemType: 'doenca', itemSlug: 'fibrilacao-atrial' }) {
  let renderer; await act(async () => { renderer = TestRenderer.create(tree(Component, props)); });
  t.after(async () => { await act(async () => renderer.unmount()); }); return renderer;
}
const favorite = (id, type, overrides = {}) => ({ id, item_type: type, item_id: id, item_slug: `item-${id}`, title: `Item ${id}`, meta: '', url: `/biblioteca/item-${id}`, available: true, reading: null, ...overrides });

test('button checks one target, posts slug once under double click and deletes favorite identity', async t => {
  const saved = deferred();
  const calls = setup({ post: (...args) => { calls.push(['post', ...args]); return saved.promise; } });
  const renderer = await mount(t);
  assert.match(calls[0][1], /^\/favorites\/status\?/);
  assert.ok(calls[0][1].includes('item_slug=fibrilacao-atrial'));
  const handler = button(renderer, 'Favoritar').props.onClick;
  await act(async () => { handler(); handler(); });
  assert.equal(calls.filter(item => item[0] === 'post').length, 1);
  assert.deepEqual(calls.find(item => item[0] === 'post')[2], { item_type: 'doenca', item_slug: 'fibrilacao-atrial' });
  await act(async () => { saved.resolve({ id: 91 }); });
  assert.equal(button(renderer, 'Favoritado').props['aria-pressed'], true);
  await act(async () => { button(renderer, 'Favoritado').props.onClick(); });
  assert.ok(calls.some(item => item[0] === 'delete' && item[1] === '/favorites/by-id/91'));
});

test('failed status remains unknown and disabled until explicit retry succeeds', async t => {
  let count = 0; const calls = setup({ get: async () => { if (++count === 1) throw Error('offline'); return { favorited: true, favorite_id: 5, available: true }; } });
  const renderer = await mount(t);
  assert.equal(button(renderer, 'Consultando').props.disabled, true);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 1);
  assert.equal(calls.filter(item => item[0] === 'post').length, 0);
  await act(async () => { button(renderer, 'Tentar novamente').props.onClick(); });
  assert.equal(button(renderer, 'Favoritado').props['aria-pressed'], true);
});

test('late status cannot cross item or user changes', async t => {
  const old = deferred(); let count = 0;
  setup({ get: async () => ++count === 1 ? old.promise : { favorited: false, favorite_id: null, available: true } });
  const renderer = await mount(t);
  globalThis.favoriteFixture.user = { id: 2 };
  await act(async () => { renderer.update(tree(Button, { itemType: 'estudo', itemSlug: 'new' })); });
  await act(async () => { old.resolve({ favorited: true, favorite_id: 888, available: true }); });
  assert.equal(button(renderer, 'Favoritar').props['aria-pressed'], false);
});

test('saved unavailable target can still be removed without resaving it', async t => {
  const calls = setup({ get: async () => ({ favorited: true, favorite_id: 12, available: false }) });
  const renderer = await mount(t);
  assert.equal(button(renderer, 'Favoritado').props.disabled, false);
  await act(async () => { button(renderer, 'Favoritado').props.onClick(); });
  assert.ok(calls.some(item => item[1] === '/favorites/by-id/12'));
  assert.equal(button(renderer, 'Favoritar').props.disabled, true);
});

test('favorites keep real routes, source reading lazy, private links owner-specific and unavailable items removable', async t => {
  const items = [favorite(1, 'estudo', { title: 'Fibrilação atrial', url: '/estudos/fa', reading: { entity_type: 'estudo', slug: 'fa' } }), favorite(2, 'funcao', { title: 'Heart Team', url: '/heart-team' }), favorite(3, 'documento', { title: 'Conteúdo indisponível', available: false, url: '/hidden', reading: { entity_type: 'documento', slug: 'hidden' } }), favorite(4, 'documento_cientifico_privado', { url: '/documentos-cientificos-ia?document=4', private_reading: { document_id: 4 }, reading: { entity_type: 'documento', slug: 'must-not-read' } }), favorite(5, 'documento', { url: '//external.test/unsafe' })];
  const calls = setup({ get: async (...args) => { calls.push(['get', ...args]); return items; } });
  const renderer = await mount(t, Favorites);
  const links = renderer.root.findAllByType('a').map(node => node.props.href);
  assert.ok(links.includes('/estudos/fa')); assert.ok(links.includes('/heart-team'));
  assert.ok(links.includes('/documentos-cientificos-ia?document=4&leitura=original'));
  assert.ok(!links.includes('/hidden') && !links.includes('//external.test/unsafe'));
  const readers = renderer.root.findAllByType('span').filter(node => node.props['data-reading-type']);
  assert.equal(readers.length, 1); assert.equal(readers[0].props['data-lazy'], true);
  assert.equal(readers[0].props['data-reading-slug'], 'fa');
  assert.equal(calls.length, 1);
  assert.ok(buttons(renderer).some(node => node.props['aria-label'] === 'Remover dos favoritos: Conteúdo indisponível'));
});

test('favorites filter accents and type without querying or generating science', async t => {
  const items = [favorite(1, 'doenca', { title: 'Fibrilação atrial' }), favorite(2, 'estudo', { title: 'Fibrilação estudo' })];
  const calls = setup({ get: async (...args) => { calls.push(args); return items; } });
  const renderer = await mount(t, Favorites);
  await act(async () => { renderer.root.findByType('input').props.onChange({ target: { value: 'fibrilacao' } }); renderer.root.findByType('select').props.onChange({ target: { value: 'doenca' } }); });
  assert.match(text(renderer.toJSON()), /Fibrilação atrial/); assert.doesNotMatch(text(renderer.toJSON()), /Fibrilação estudo/);
  assert.equal(calls.length, 1);
});

test('failed favorite removal preserves the item with a recoverable error', async t => {
  setup({ get: async () => [favorite(5, 'exame')], delete: async () => { throw Error('offline'); } });
  const renderer = await mount(t, Favorites);
  await act(async () => { button(renderer, 'Remover').props.onClick(); });
  assert.match(text(renderer.toJSON()), /Item 5/); assert.match(text(renderer.toJSON()), /Ele continua salvo/);
  assert.equal(button(renderer, 'Remover').props.disabled, false);
});

test('favorites from a previous account never remain rendered while the next account loads', async t => {
  const second = deferred(); let count = 0;
  setup({ get: () => ++count === 1 ? Promise.resolve([favorite(1, 'documento', { title: 'FIRST ACCOUNT' })]) : second.promise });
  const renderer = await mount(t, Favorites);
  assert.match(text(renderer.toJSON()), /FIRST ACCOUNT/);
  globalThis.favoriteFixture.user = { id: 2 };
  await act(async () => { renderer.update(tree(Favorites)); });
  assert.doesNotMatch(text(renderer.toJSON()), /FIRST ACCOUNT/);
  await act(async () => { second.resolve([favorite(2, 'estudo', { title: 'SECOND ACCOUNT' })]); });
  assert.match(text(renderer.toJSON()), /SECOND ACCOUNT/);
});
