import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import ts from 'typescript';

const require = createRequire(import.meta.url);
// Optional isolated dependency location for installations missing dev packages.
const rendererRequire = process.env.CORVIA_TEST_RENDERER_ROOT
  ? createRequire(path.join(process.env.CORVIA_TEST_RENDERER_ROOT, 'package.json'))
  : require;
const TestRenderer = rendererRequire('react-test-renderer');
const { act } = TestRenderer;
const root = fileURLToPath(new URL('../', import.meta.url));
const temp = await mkdtemp(path.join(tmpdir(), 'corvia-search-flow-'));
await symlink(path.join(root, 'node_modules'), path.join(temp, 'node_modules'));
after(() => rm(temp, { recursive: true, force: true }));

function transpile(source, name) {
  return ts.transpileModule(source, {
    fileName: name,
    compilerOptions: {
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
      jsx: ts.JsxEmit.ReactJSX,
    },
  }).outputText;
}
const anchors = await readFile(path.join(root, 'src/lib/searchAnchors.ts'), 'utf8');
await writeFile(path.join(temp, 'searchAnchors.mjs'), transpile(anchors, 'searchAnchors.ts'));
const editorialSections = JSON.parse(await readFile(path.join(root, 'src/lib/documentEditorialTaxonomy.json'), 'utf8'));
let editorialHelper = await readFile(path.join(root, 'src/lib/documentEditorialTaxonomy.ts'), 'utf8');
editorialHelper = editorialHelper.replace('import sections from "./documentEditorialTaxonomy.json";', `const sections = ${JSON.stringify(editorialSections)};`);
await writeFile(path.join(temp, 'documentEditorialTaxonomy.mjs'), transpile(editorialHelper, 'documentEditorialTaxonomy.ts'));
let source = await readFile(path.join(root, 'src/pages/Busca.tsx'), 'utf8');
assert.ok(source.includes('import { api, ApiError, PaginaDe } from "../lib/api";'));
source = source.replace('import { api, ApiError, PaginaDe } from "../lib/api";', `
const api = { get: (...args) => globalThis.corviaSearchFixture.get(...args) };
class ApiError extends Error {}
`);
source = source.replace('import { Carregando, Erro, Vazio } from "../components/Estado";', `
const Carregando = () => <p role="status">Carregando</p>;
const Erro = ({ mensagem }) => <p role="alert">{mensagem}</p>;
const Vazio = ({ titulo }) => <p>{titulo}</p>;
`);
source = source.replace('import TctDiseaseOverview from "../components/TctDiseaseOverview";', `
const TctDiseaseOverview = ({ disease }) => <aside>{disease.name}</aside>;
`);
source = source.replace('"../lib/documentEditorialTaxonomy"', '"./documentEditorialTaxonomy.mjs"');
source = source.replace('"../lib/searchAnchors"' , '"./searchAnchors.mjs"');
await writeFile(path.join(temp, 'Busca.mjs'), transpile(source, 'Busca.tsx'));
const { default: Busca } = await import(pathToFileURL(path.join(temp, 'Busca.mjs')));

const tick = () => new Promise(resolve => setImmediate(resolve));
const nodeText = node => typeof node === 'string' ? node : (node.children ?? []).map(nodeText).join('');
const more = renderer => renderer.root.findAllByType('button')
  .find(button => /Carregar mais|Conectando mais/.test(nodeText(button)));
const item = (slug, title, frente = 'documento') => ({
  slug, title, frente, kind: 'protocolo', theme: 'Teste', snippet: '',
});
const page = (results, total = results.length, next_offset = null, extra = {}) => ({
  results, total, next_offset, por_frente: {}, ...extra,
});
function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
}
async function mount(t, query, get) {
  const calls = [];
  globalThis.corviaSearchFixture = {
    get: url => { calls.push(url); return get(url); },
  };
  let renderer;
  await act(async () => {
    renderer = TestRenderer.create(React.createElement(MemoryRouter, {
      initialEntries: [`/busca?q=${encodeURIComponent(query)}`],
      future: { v7_startTransition: true, v7_relativeSplatPath: true },
    }, React.createElement(Busca)));
    await tick();
  });
  t.after(async () => { await act(async () => renderer.unmount()); });
  return { renderer, calls };
}
async function submit(renderer, query) {
  await act(async () => renderer.root.findByType('input').props.onChange({ target: { value: query } }));
  await act(async () => {
    renderer.root.findByType('form').props.onSubmit({ preventDefault() {} });
    await tick();
  });
}

test('changing subject during pagination unlocks the new page and rejects stale results', async t => {
  const pending = deferred();
  const { renderer, calls } = await mount(t, 'alfa', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    const params = new URL(url, 'https://test.invalid').searchParams;
    if (params.get('q') === 'alfa') return params.has('offset')
      ? pending.promise : page([item('alfa-inicial', 'Conteúdo inicial alfa')], 2, 1);
    if (params.get('q') === 'beta') return params.has('offset')
      ? page([item('beta-final', 'Conteúdo final beta')], 2)
      : page([item('beta-inicial', 'Conteúdo inicial beta')], 2, 1);
    throw Error(`Unexpected request: ${url}`);
  });
  await act(async () => { void more(renderer).props.onClick(); await tick(); });
  assert.equal(more(renderer).props.disabled, true);
  await submit(renderer, 'beta');
  assert.equal(more(renderer).props.disabled, false);
  await act(async () => {
    pending.resolve(page([item('obsoleto', 'Resultado obsoleto alfa')], 2));
    await tick();
  });
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Resultado obsoleto/);
  assert.equal(more(renderer).props.disabled, false);
  await act(async () => more(renderer).props.onClick());
  assert.match(nodeText(renderer.toJSON()), /Conteúdo final beta/);
  assert.ok(calls.some(url => url.includes('q=beta') && url.includes('offset=1')));
});

test('a later lexical page removes the same item from connected groups', async t => {
  const document = item('monitorizacao-prolongada', 'Monitorização prolongada');
  const { renderer } = await mount(t, 'Holter 24h', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url.startsWith('/relacionados/ecossistema?')) return {
      total: 1,
      grupos: [{ tipo: 'documento', rotulo: 'Documentos', rota_lista: '/biblioteca', itens: [{
        slug: document.slug, titulo: document.title, rota: `/biblioteca/${document.slug}`,
      }] }],
    };
    if (url.startsWith('/search?')) return url.includes('offset=')
      ? page([document], 2)
      : page([item('holter-24h', 'Holter 24h', 'exame')], 2, 1);
    throw Error(`Unexpected request: ${url}`);
  });
  const links = () => renderer.root.findAllByType('a')
    .filter(link => link.props.href === `/biblioteca/${document.slug}`);
  assert.equal(links().length, 1);
  await act(async () => more(renderer).props.onClick());
  assert.equal(links().length, 1);
  assert.equal(more(renderer), undefined);
});

test('a primary drug uses the paginated search and does not request a second ecosystem', async t => {
  const drug = {
    slug: 'olmesartana', generic_name: 'Olmesartana', drug_class: 'BRA',
    presentations: [], dosing: {}, indications: [], contraindications: [],
    interactions: [], monitoring: [], adverse_effects: [],
  };
  const { renderer, calls } = await mount(t, 'olmesartana', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url === '/drug-insights/olmesartana') return drug;
    if (url.startsWith('/search?')) return page(
      [item(drug.slug, drug.generic_name, 'medicamento')], 1, null,
      { primary_drug: drug, supplementary_groups: [] },
    );
    throw Error(`Unexpected request: ${url}`);
  });
  assert.match(nodeText(renderer.toJSON()), /Medicamento identificado/);
  assert.equal(calls.filter(url => url === '/drug-insights/olmesartana').length, 1);
  assert.equal(calls.filter(url => url.startsWith('/relacionados/') || url.startsWith('/grafo/')).length, 0);
});

const section = (renderer, key) => renderer.root.findByProps({ id: `secao-${key}` });
const sectionMore = (renderer, key) => section(renderer, key).findByType('button');
const click = async button => act(async () => { void button.props.onClick(); await tick(); });

test('principal disease stays in its section and absent initial sections expose their exact totals', async t => {
  const disease = { slug: 'fibrilacao-atrial', name: 'Fibrilação atrial', summary: 'Resumo', area: 'Arritmias', category: 'Arritmia' };
  const { renderer, calls } = await mount(t, 'fibrilação atrial', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    const p = new URL(url, 'https://test.invalid').searchParams;
    if (p.has('secao')) return page([
      { ...item('sbc-2025', 'Diretriz brasileira 2025'), secao: 'diretriz' },
      { ...item('esc-2024', 'ESC 2024'), secao: 'diretriz' },
    ], 2, null, { por_secao: { diretriz: 2 } });
    return page([item(disease.slug, disease.name, 'doenca'), item('fa-idoso', 'FA no idoso', 'doenca')], 4, 2,
      { primary_disease: disease, supplementary_groups: [], por_secao: { doenca: 2, diretriz: 2 } });
  });
  assert.equal(section(renderer, 'doenca').findAllByType('a').length, 2);
  assert.match(nodeText(section(renderer, 'doenca')), /Doença principal/);
  assert.match(nodeText(section(renderer, 'diretriz')), /0 de 2 resultados carregados/);
  assert.equal(calls.filter(url => url.includes('secao=')).length, 0, 'sections load only when requested');
  await click(sectionMore(renderer, 'diretriz'));
  assert.match(nodeText(section(renderer, 'diretriz')), /2 de 2 resultados carregados/);
  assert.match(nodeText(section(renderer, 'diretriz')), /ESC 2024/);
  assert.match(nodeText(section(renderer, 'doenca')), /2 de 2 resultados carregados/);
  assert.equal(section(renderer, 'diretriz').findAllByType('button').length, 0);
  assert.ok(calls.some(url => /secao=diretriz/.test(url) && /offset=0/.test(url)));
});

test('section and global pagination merge concurrently without duplicates and keep independent cursors', async t => {
  const globalPage = deferred(), sectionPage = deferred();
  const initial = { ...item('a', 'Diretriz inicial'), secao: 'diretriz' };
  const shared = { ...item('b', 'Diretriz compartilhada'), secao: 'diretriz' };
  const { renderer, calls } = await mount(t, 'tema', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    const p = new URL(url, 'https://test.invalid').searchParams;
    if (p.has('secao')) return p.get('offset') === '0' ? sectionPage.promise
      : page([{ ...item('c', 'Diretriz final'), secao: 'diretriz' }], 3);
    if (p.has('offset')) return globalPage.promise;
    return page([initial], 4, 1, { por_secao: { diretriz: 3, exame: 1 } });
  });
  await click(sectionMore(renderer, 'diretriz'));
  await click(more(renderer));
  await act(async () => {
    globalPage.resolve(page([shared, item('eco', 'Eco', 'exame')], 4, 3));
    sectionPage.resolve(page([initial, shared], 3, 2, { por_secao: { diretriz: 3 } }));
    await tick();
  });
  assert.equal(section(renderer, 'diretriz').findAllByType('a').length, 2);
  assert.match(nodeText(section(renderer, 'exame')), /1 de 1 resultados carregados/);
  assert.match(nodeText(section(renderer, 'diretriz')), /2 de 3 resultados carregados/);
  await click(sectionMore(renderer, 'diretriz'));
  assert.equal(section(renderer, 'diretriz').findAllByType('a').length, 3);
  assert.ok(calls.some(url => url.includes('secao=diretriz') && url.includes('offset=2')));
  assert.ok(calls.some(url => !url.includes('secao=') && url.includes('offset=1')));
  assert.equal(more(renderer), undefined, 'all unique results already loaded through either path');
});

test('a stale section response cannot enter a new subject or unlock its pending section', async t => {
  const old = deferred(), current = deferred();
  const { renderer } = await mount(t, 'alfa', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    const p = new URL(url, 'https://test.invalid').searchParams;
    if (p.has('secao')) return p.get('q') === 'alfa' ? old.promise : current.promise;
    return page([item(`${p.get('q')}-eco`, 'Ecocardiografia', 'exame')], 2, 1,
      { por_secao: { exame: 1, diretriz: 1 } });
  });
  await click(sectionMore(renderer, 'diretriz'));
  await submit(renderer, 'beta');
  assert.equal(Boolean(sectionMore(renderer, 'diretriz').props.disabled), false);
  await click(sectionMore(renderer, 'diretriz'));
  await act(async () => { old.resolve(page([{ ...item('old', 'Diretriz obsoleta'), secao: 'diretriz' }])); await tick(); });
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Diretriz obsoleta/);
  assert.equal(sectionMore(renderer, 'diretriz').props.disabled, true);
  await act(async () => { current.resolve(page([{ ...item('new', 'Diretriz beta'), secao: 'diretriz' }])); await tick(); });
  assert.match(nodeText(section(renderer, 'diretriz')), /Diretriz beta/);
});

test('server sections take precedence and legacy underscore fronts retain their destinations', async t => {
  const { renderer } = await mount(t, 'tema', async url => url.startsWith('/drugs?') ? { items: [] } : page([
    { ...item('classificado', 'Título sem palavras de classificação'), secao: 'diretriz' },
    item('caso', 'Tratamento em caso clínico', 'caso_clinico'),
    item('paciente', 'Tratamento para pacientes', 'material_paciente'),
    item('triagem', 'Protocolo de triagem', 'triagem_sintoma'),
  ]));
  assert.equal(section(renderer, 'diretriz').findByType('a').props.href, '/biblioteca/classificado');
  assert.equal(section(renderer, 'caso_clinico').findByType('a').props.href, '/casos-clinicos/caso');
  assert.equal(section(renderer, 'material_paciente').findByType('a').props.href, '/material-paciente/paciente');
  assert.equal(section(renderer, 'triagem_sintoma').findByType('a').props.href, '/triagem-sintomas?slug=triagem');
});

test('a failed section request keeps its cursor and can retry without duplicate in-flight calls', async t => {
  let requests = 0;
  const { renderer, calls } = await mount(t, 'tema', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url.includes('secao=')) {
      if (++requests === 1) throw Error('temporary');
      return page([{ ...item('d', 'Diretriz recuperada'), secao: 'diretriz' }]);
    }
    return page([], 1, 0, { por_secao: { diretriz: 1 } });
  });
  const first = sectionMore(renderer, 'diretriz');
  await act(async () => { first.props.onClick(); first.props.onClick(); await tick(); });
  assert.equal(requests, 1);
  assert.equal(section(renderer, 'diretriz').findAllByProps({ role: 'alert' }).length, 1);
  await click(sectionMore(renderer, 'diretriz'));
  assert.match(nodeText(section(renderer, 'diretriz')), /Diretriz recuperada/);
  assert.equal(calls.filter(url => url.includes('secao=') && url.includes('offset=0')).length, 2);
});


test('editorial study and calculator documents retain Library routes and neutral titles stay neutral', async t => {
  const { renderer } = await mount(t, 'tema', async url => url.startsWith('/drugs?') ? { items: [] } : page([
    { ...item('trial', 'Ensaio clínico', 'documento'), kind: 'estudo' },
    { ...item('neutral', 'Miopatia: comentário sobre consenso', 'documento'), kind: 'documento' },
    { ...item('same-score', 'Documento de escore', 'documento'), kind: 'calculadora', secao: 'calculadora' },
    { ...item('same-score', 'Calculadora executável', 'calculadora'), kind: 'calculadora', secao: 'calculadora' },
  ]));
  assert.equal(section(renderer, 'estudo').findByType('a').props.href, '/biblioteca/trial');
  assert.equal(section(renderer, 'geral').findByType('a').props.href, '/biblioteca/neutral');
  assert.deepEqual(section(renderer, 'calculadora').findAllByType('a').map(a => a.props.href).sort(), ['/biblioteca/same-score', '/calculadoras/same-score']);
});


test('formal ScientificStudy in guidance retains its studies URL and trial names do not promote it', async t => {
  const { renderer } = await mount(t, 'tema', async url => url.startsWith('/drugs?') ? { items: [] } : page([
    { ...item('sepsis', 'Sepsis-3', 'estudo'), kind: 'consenso' },
    { ...item('consensus', 'CONSENSUS trial', 'estudo'), kind: 'ensaio_clinico' },
  ]));
  assert.equal(section(renderer, 'diretriz').findByType('a').props.href, '/estudos/sepsis');
  assert.equal(section(renderer, 'estudo').findByType('a').props.href, '/estudos/consensus');
});
