import assert from 'node:assert/strict';
import test, { after } from 'node:test';
import { mkdtemp, readFile, writeFile, symlink, rm } from 'node:fs/promises';
import path from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath, pathToFileURL } from 'node:url';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import TestRenderer from 'react-test-renderer';
import ts from 'typescript';

const { act } = TestRenderer;
const root = fileURLToPath(new URL('../', import.meta.url));
const temp = await mkdtemp(path.join(tmpdir(), 'corvia-intelligence-monitor-'));
await symlink(path.join(root, 'node_modules'), path.join(temp, 'node_modules'));
after(() => rm(temp, { recursive: true, force: true }));
const transpile = source => ts.transpileModule(source, { compilerOptions: {
  target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022, jsx: ts.JsxEmit.ReactJSX,
} }).outputText;
await writeFile(path.join(temp, 'scientificIntelligence.mjs'), transpile(await readFile(path.join(root, 'src/lib/scientificIntelligence.ts'), 'utf8')));
let source = await readFile(path.join(root, 'src/components/ScientificIntelligenceMonitor.tsx'), 'utf8');
source = source.replace('import { api } from "../lib/api";', 'const api = { get: (...args) => globalThis.corviaIntelligenceFixture.get(...args) };');
source = source.replace('import { useAuth } from "../lib/auth";', 'const useAuth = () => ({ usuario: globalThis.corviaIntelligenceFixture.user });');
source = source.replace('"../lib/scientificIntelligence"', '"./scientificIntelligence.mjs"');
source = source.replace('import Icone from "./Icone";', 'const Icone = () => null;');
source = source.replace('import ScientificReadingAccess from "./ScientificReadingAccess";', 'const ScientificReadingAccess = props => <span data-reading-type={props.entityType} data-reading-slug={props.slug} data-lazy={props.lazy} />;');
source = source.replace('import "../styles/scientific-intelligence-monitor.css";', '');
await writeFile(path.join(temp, 'monitor.mjs'), transpile(source));
const { default: Monitor } = await import(pathToFileURL(path.join(temp, 'monitor.mjs')));
const { intelligenceHealthLabel, scientificSourceUrl, scientificDate } = await import(pathToFileURL(path.join(temp, 'scientificIntelligence.mjs')));
const discovery = (id, title) => ({ id, title, org: 'Source', doi: '10.1234/article', url: null, discovered_at: '2026-09-10T08:00:00Z', published_at: null, status: 'new' });
const status = (overrides = {}) => ({
  health: 'active', enabled: true, cadence_hours: 4, normal_interval_hours: 4, surge_interval_hours: 1,
  schedule_reason: 'normal', high_frequency_window: null, last_heartbeat_at: null,
  last_started_at: null, last_completed_at: null, last_success_at: null, next_run_at: null,
  coverage: null, recent_discoveries: [], total_discovered: 0, pending_analysis: 0, ...overrides,
});
const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
const tree = props => React.createElement(MemoryRouter, { future: { v7_startTransition: true, v7_relativeSplatPath: true } }, React.createElement(Monitor, props));
const text = renderer => JSON.stringify(renderer.toJSON());
const fixture = get => { const calls = []; globalThis.corviaIntelligenceFixture = { user: { id: 1 }, get: (...args) => { calls.push(args); return get(...args); } }; return calls; };
async function mount(t, props) { let renderer; await act(async () => { renderer = TestRenderer.create(tree(props)); }); t.after(async () => { await act(async () => renderer.unmount()); }); return renderer; }
const click = async (renderer, label) => { await act(async () => renderer.root.findAllByType('button').find(node => node.children.join('') === label).props.onClick()); };

test('only an enabled and active status is announced as active', () => {
  for (const [health, enabled, expected] of [
    ['active', true, 'Monitoramento ativo'], ['active', false, 'Monitoramento desativado'],
    ['unknown', true, 'Aguardando confirmação do monitoramento'],
    ['unknown', false, 'Aguardando confirmação do monitoramento'],
    ['inactive', false, 'Monitoramento sem execução recente'],
    ['degraded', true, 'Monitoramento com pendências'], ['inactive', true, 'Monitoramento sem execução recente'],
  ]) assert.equal(intelligenceHealthLabel(status({ health, enabled })), expected);
});

test('compact monitor uses internal discovery routes and only reads status on refresh', async t => {
  const calls = fixture(async () => status({ recent_discoveries: [discovery(42, 'Recent publication')] }));
  const renderer = await mount(t, { compact: true });
  const links = renderer.root.findAllByType('a').map(node => node.props.href);
  assert.ok(links.includes('/intelligence'));
  assert.ok(links.includes('/intelligence#descoberta-42'));
  assert.match(text(renderer), /Monitoramento ativo/);
  await click(renderer, 'Atualizar estado');
  assert.equal(calls.length, 2);
  assert.ok(calls.every(args => args.length === 1 && args[0] === '/guideline-updates/status'));
});

test('failed refresh removes old status and discoveries, and retry recovers', async t => {
  let attempt = 0;
  const calls = fixture(async () => {
    attempt += 1;
    if (attempt === 2) throw Error('offline');
    return status({ recent_discoveries: [discovery(attempt, attempt === 1 ? 'OLD DISCOVERY' : 'NEW DISCOVERY')] });
  });
  const renderer = await mount(t);
  assert.match(text(renderer), /OLD DISCOVERY/);
  await click(renderer, 'Atualizar estado');
  assert.doesNotMatch(text(renderer), /OLD DISCOVERY|Monitoramento ativo/);
  assert.match(text(renderer), /Tentar novamente/);
  await click(renderer, 'Tentar novamente');
  assert.match(text(renderer), /NEW DISCOVERY/);
  assert.equal(calls.length, 3);
});

test('pending responses cannot cross an account change or an unmount', async t => {
  const first = deferred(), second = deferred(), afterUnmount = deferred();
  const queue = [first, second, afterUnmount];
  let index = 0;
  fixture(() => queue[index++].promise);
  const renderer = await mount(t);
  globalThis.corviaIntelligenceFixture.user = { id: 2 };
  await act(async () => renderer.update(tree()));
  await act(async () => first.resolve(status({ recent_discoveries: [discovery(1, 'ACCOUNT ONE')] })));
  assert.doesNotMatch(text(renderer), /ACCOUNT ONE|Monitoramento ativo/);
  await act(async () => second.resolve(status({ health: 'degraded', recent_discoveries: [discovery(2, 'ACCOUNT TWO')] })));
  assert.match(text(renderer), /ACCOUNT TWO/);
  assert.match(text(renderer), /Monitoramento com pendências/);
  await click(renderer, 'Atualizar estado');
  await act(async () => renderer.unmount());
  await act(async () => afterUnmount.resolve(status({ recent_discoveries: [discovery(3, 'AFTER UNMOUNT')] })));
  assert.equal(renderer.toJSON(), null);
});

test('source links reject executable schemes and dates do not manufacture missing history', () => {
  assert.equal(scientificSourceUrl({ ...discovery(1, 'a'), url: 'javascript:alert(1)', doi: null }), null);
  assert.equal(scientificSourceUrl({ ...discovery(1, 'a'), url: 'https://publisher.example/article' }), 'https://publisher.example/article');
  assert.equal(scientificSourceUrl(discovery(1, 'a')), 'https://doi.org/10.1234/article');
  assert.equal(scientificDate(null), 'Ainda não registrada');
  assert.equal(scientificDate('invalid'), 'Data indisponível');
});


test('document availability is counted honestly and discovery reading is lazy', async t => {
  const calls = fixture(async () => status({
    recent_discoveries: [{ ...discovery(43, 'New source'), slug: 'new-source' }],
    document_processing: { health: 'inactive', enabled: false, last_heartbeat_at: null,
      total: 12, queued: 9, ready_full_pt: 0, ready_original: 2,
      blocked_license: 1, blocked_fulltext: 0, budget_wait: 1, failed: 1, by_status: {} },
  }));
  const renderer = await mount(t);
  const words = renderer.root.findAllByType('p').map(node => node.children.join('')).join(' ');
  assert.match(words, /0 traduções integrais do texto prontas/);
  assert.match(words, /sem atividade recente confirmada/);
  const reader = renderer.root.findAllByType('span').find(node => node.props['data-reading-type']);
  assert.equal(reader.props['data-reading-type'], 'descoberta');
  assert.equal(reader.props['data-reading-slug'], 'new-source');
  assert.equal(reader.props['data-lazy'], true);
  assert.equal(calls.length, 1);
});
