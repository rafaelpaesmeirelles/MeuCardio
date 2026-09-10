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
const temp = await mkdtemp(path.join(tmpdir(), 'corvia-original-entry-'));
await symlink(path.join(root, 'node_modules'), path.join(temp, 'node_modules'));
after(() => rm(temp, { recursive: true, force: true }));
let source = await readFile(path.join(root, 'src/pages/CorviaIntelligence.tsx'), 'utf8');
source = source.replace('import Diretrizes from "./Diretrizes";', 'const Diretrizes = props => <div data-monitor-only={props.intelligenceOnly} />;');
source = source.replace('import ScientificReadingAccess from "../components/ScientificReadingAccess";', 'const ScientificReadingAccess = props => <div data-reader-type={props.entityType} data-reader-slug={props.slug} />;');
source = source.replace('import BotaoFavorito from "../components/BotaoFavorito";', 'const BotaoFavorito = props => <button data-favorite-type={props.itemType} data-favorite-slug={props.itemSlug} />;');
await writeFile(path.join(temp, 'entry.mjs'), ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX } }).outputText);
const { default: Entry } = await import(pathToFileURL(path.join(temp, 'entry.mjs')));
async function mount(t, url) {
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(MemoryRouter, { initialEntries: [url], future: { v7_startTransition: true, v7_relativeSplatPath: true } }, React.createElement(Entry))); });
  t.after(async () => { await act(async () => renderer.unmount()); }); return renderer;
}

test('Intelligence keeps its monitor without a selected original', async t => {
  const renderer = await mount(t, '/intelligence');
  assert.equal(renderer.root.findAllByProps({ 'data-monitor-only': true }).length, 1);
  assert.equal(renderer.root.findAllByType('button').length, 0);
});

test('public source entry validates source key and shares the same identity with favorite and reader', async t => {
  const renderer = await mount(t, `/intelligence?fonte=${'A'.repeat(64)}`);
  assert.equal(renderer.root.findAllByProps({ 'data-reader-type': 'publicacao_original' })[0].props['data-reader-slug'], 'a'.repeat(64));
  assert.equal(renderer.root.findByType('button').props['data-favorite-slug'], 'a'.repeat(64));
  assert.equal(renderer.root.findByType('a').props.href, '/intelligence');
});

test('malformed private or traversal references never mount reader or favorite', async t => {
  for (const key of ['../../private', 'documento-privado-12', '', 'a'.repeat(63)]) {
    const renderer = await mount(t, `/intelligence?fonte=${encodeURIComponent(key)}`);
    assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 1);
    assert.equal(renderer.root.findAllByType('button').length, 0);
    assert.equal(renderer.root.findAllByProps({ 'data-reader-type': 'publicacao_original' }).length, 0);
  }
});
