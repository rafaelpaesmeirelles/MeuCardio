import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import React from 'react';
import { MemoryRouter, useLocation, useNavigate } from 'react-router-dom';
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
const resultHelper = await readFile(path.join(root, 'src/lib/searchResults.ts'), 'utf8');
await writeFile(path.join(temp, 'searchResults.mjs'), transpile(resultHelper, 'searchResults.ts'));
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
source = source.replace('"../lib/searchResults"', '"./searchResults.mjs"');
await writeFile(path.join(temp, 'Busca.mjs'), transpile(source, 'Busca.tsx'));
const { default: Busca } = await import(pathToFileURL(path.join(temp, 'Busca.mjs')));

const tick = () => new Promise(resolve => setImmediate(resolve));
const nodeText = node => typeof node === 'string' ? node : (node.children ?? []).map(nodeText).join('');
const more = renderer => renderer.root.findAllByType('button')
  .find(button => /Carregar mais|Conectando mais|Tentar carregar mais/.test(nodeText(button)));
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
async function mount(t, query, get, initialEntries = [`/busca?q=${encodeURIComponent(query)}`]) {
  const calls = [], requests = [];
  const navigation = {};
  function NavigationProbe() {
    navigation.navigate = useNavigate();
    navigation.location = useLocation();
    return null;
  }
  globalThis.corviaSearchFixture = {
    get: (url, options) => { calls.push(url); requests.push({ url, options }); return get(url, options); },
  };
  let renderer;
  await act(async () => {
    renderer = TestRenderer.create(React.createElement(MemoryRouter, {
      initialEntries,
      future: { v7_startTransition: true, v7_relativeSplatPath: true },
    }, React.createElement(React.Fragment, null,
      React.createElement(NavigationProbe), React.createElement(Busca))));
    await tick();
  });
  t.after(async () => { await act(async () => renderer.unmount()); });
  return { renderer, calls, requests, location: () => navigation.location,
    go: async target => act(async () => { navigation.navigate(target); await tick(); }) };
}
async function submit(renderer, query) {
  await act(async () => renderer.root.findByType('input').props.onChange({ target: { value: query } }));
  await act(async () => {
    renderer.root.findByType('form').props.onSubmit({ preventDefault() {} });
    await tick();
  });
}

const searchCalls = (calls, query) => calls.filter(url => url.startsWith('/search?')
  && new URL(url, 'https://test.invalid').searchParams.get('q') === query
  && !new URL(url, 'https://test.invalid').searchParams.has('offset')
  && !new URL(url, 'https://test.invalid').searchParams.has('secao'));
const subjectPage = url => {
  const query = new URL(url, 'https://test.invalid').searchParams.get('q');
  return page([item(`resultado-${query}`, `Resultado ${query}`)]);
};

test('same-route URL navigation updates the subject once and preserves drafts for unrelated parameters', async t => {
  const { renderer, calls, go, location } = await mount(t, 'alfa', async url =>
    url.startsWith('/drugs?') ? { items: [] } : subjectPage(url));
  await go('/busca?q=beta&modo=tudo-com-tudo');
  assert.equal(renderer.root.findByType('input').props.value, 'beta');
  assert.match(nodeText(renderer.toJSON()), /Tudo sobre beta/);
  assert.match(nodeText(renderer.toJSON()), /Resultado beta/);
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Resultado alfa/);
  assert.equal(searchCalls(calls, 'beta').length, 1);
  await act(async () => renderer.root.findByType('input').props.onChange({ target: { value: 'rascunho' } }));
  await go('/busca?q=beta&modo=outro');
  assert.equal(renderer.root.findByType('input').props.value, 'rascunho');
  assert.match(nodeText(renderer.toJSON()), /Resultado beta/);
  assert.equal(searchCalls(calls, 'beta').length, 1);
  await submit(renderer, 'gama');
  assert.equal(new URLSearchParams(location().search).get('modo'), 'outro');
  assert.equal(new URLSearchParams(location().search).get('q'), 'gama');
  assert.equal(searchCalls(calls, 'gama').length, 1, 'form and URL effect must not both fetch');
});

test('Back and Forward restore their URL subject; clearing or shortening it clears all previous results', async t => {
  const { renderer, calls, go } = await mount(t, 'alfa', async url =>
    url.startsWith('/drugs?') ? { items: [] } : subjectPage(url));
  await go('/busca?q=beta');
  await go(-1);
  assert.equal(renderer.root.findByType('input').props.value, 'alfa');
  assert.match(nodeText(renderer.toJSON()), /Resultado alfa/);
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Resultado beta/);
  await go(1);
  assert.equal(renderer.root.findByType('input').props.value, 'beta');
  assert.match(nodeText(renderer.toJSON()), /Resultado beta/);
  assert.equal(searchCalls(calls, 'alfa').length, 2);
  assert.equal(searchCalls(calls, 'beta').length, 2);
  const count = calls.length;
  await go('/busca?modo=tudo-com-tudo');
  assert.equal(renderer.root.findByType('input').props.value, '');
  assert.match(nodeText(renderer.toJSON()), /Um assunto, todas as conexões/);
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Resultado|Nada encontrado/);
  await go('/busca?q=x');
  assert.equal(renderer.root.findByType('input').props.value, 'x');
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Resultado/);
  assert.equal(calls.length, count, 'invalid/empty queries do not reach the API');
});

test('legacy tema URLs resolve on navigation and an explicit empty q does not revive their old subject', async t => {
  const { renderer, calls, go } = await mount(t, '', async url =>
    url.startsWith('/drugs?') ? { items: [] } : subjectPage(url), ['/busca?tema=fibrilacao-atrial']);
  assert.equal(renderer.root.findByType('input').props.value, 'fibrilacao atrial');
  assert.equal(searchCalls(calls, 'fibrilacao atrial').length, 1);
  await go('/busca?tema=hipertensao-arterial');
  assert.equal(renderer.root.findByType('input').props.value, 'hipertensao arterial');
  assert.equal(searchCalls(calls, 'hipertensao arterial').length, 1);
  const count = calls.length;
  await go('/busca?q=&tema=hipertensao-arterial');
  assert.equal(renderer.root.findByType('input').props.value, '');
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Resultado/);
  assert.equal(calls.length, count);
});

test('URL changes and clearing invalidate late base results before drug or graph requests can start', async t => {
  const old = deferred();
  const { renderer, calls, go } = await mount(t, 'alfa', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    return url.includes('q=alfa') ? old.promise : subjectPage(url);
  });
  await go('/busca?q=beta');
  await act(async () => { old.resolve(page([item('antigo', 'Resultado obsoleto')], 1, null,
    { primary_drug: { slug: 'farmaco-antigo', generic_name: 'Fármaco antigo' } })); await tick(); });
  assert.match(nodeText(renderer.toJSON()), /Resultado beta/);
  assert.doesNotMatch(nodeText(renderer.toJSON()), /obsoleto/);
  assert.equal(calls.filter(url => url.startsWith('/drug-insights/')).length, 0);
  const pending = deferred();
  globalThis.corviaSearchFixture.get = url => { calls.push(url); return url.startsWith('/drugs?') ? Promise.resolve({ items: [] }) : pending.promise; };
  await go('/busca?q=gama');
  await go('/busca');
  await act(async () => { pending.resolve(page([item('tardio', 'Resultado tardio')])); await tick(); });
  assert.match(nodeText(renderer.toJSON()), /Um assunto, todas as conexões/);
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Resultado|Carregando/);
});

test('a late drug insight or graph response cannot repopulate a different URL subject', async t => {
  const insight = deferred(), graph = deferred();
  const drug = { slug: 'farmaco', generic_name: 'Fármaco', drug_class: 'Teste',
    presentations: [], dosing: {}, indications: [], contraindications: [],
    interactions: [], monitoring: [], adverse_effects: [] };
  const { renderer, go } = await mount(t, 'farmaco', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url === '/drug-insights/farmaco') return insight.promise;
    if (url.startsWith('/relacionados/ecossistema?')) return graph.promise;
    if (url.includes('q=farmaco')) return page([], 0, null, { primary_drug: drug });
    if (url.includes('q=holter')) return page([item('holter', 'Holter', 'exame')]);
    return subjectPage(url);
  });
  await go('/busca?q=holter');
  await go('/busca?q=beta');
  await act(async () => {
    insight.resolve(drug);
    graph.resolve({ total: 1, grupos: [{ tipo: 'documento', itens: [{ slug: 'antigo', titulo: 'Conexão obsoleta', rota: '/biblioteca/antigo' }] }] });
    await tick();
  });
  assert.match(nodeText(renderer.toJSON()), /Resultado beta/);
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Medicamento identificado|Conexão obsoleta|Fármaco/);
});

test('repeated submit of the same pending subject dispatches once and a failed search can retry', async t => {
  let failures = 1;
  const pending = deferred();
  const { renderer, calls } = await mount(t, 'alfa', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (failures-- > 0) throw Error('temporary');
    return pending.promise;
  });
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 1);
  await act(async () => {
    const form = renderer.root.findByType('form');
    form.props.onSubmit({ preventDefault() {} });
    form.props.onSubmit({ preventDefault() {} });
    await tick();
  });
  assert.equal(searchCalls(calls, 'alfa').length, 2, 'one initial failure and one retry, no duplicate');
  await act(async () => { pending.resolve(page([item('recuperado', 'Resultado recuperado')])); await tick(); });
  assert.match(nodeText(renderer.toJSON()), /Resultado recuperado/);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 0);
});

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

const list = renderer => renderer.root.findByProps({ 'aria-label': 'Lista de conteúdos por relevância' });
const resultLinks = renderer => list(renderer).findAllByType('a');
const titles = renderer => resultLinks(renderer).map(nodeText);
const click = async button => act(async () => { void button.props.onClick(); await tick(); });
const filter = async (renderer, label, value) => act(async () => {
  renderer.root.findByProps({ 'aria-label': label }).props.onChange({ target: { value } });
  await tick();
});
const disease = { slug: 'estenose-mitral', name: 'Estenose mitral', summary: 'Resumo publicado', area: 'geral', category: 'valvopatia' };

test('one list retains backend relevance across fronts, without fixed disease sections or a duplicate timeline', async t => {
  const ordered = [
    { ...item('guideline', 'Diretriz mais relevante'), secao: 'diretriz', relevance_order: 0, ano: 2025 },
    { ...item('evidence', 'Recomendação específica', 'evidencia'), relevance_order: 1, ano: 2024 },
    { ...item(disease.slug, disease.name, 'doenca'), relevance_order: 2 },
    { ...item('image', 'Imagem complementar', 'galeria'), relevance_order: 3 },
  ];
  const { renderer, calls } = await mount(t, 'Estenose mitral', async url => url.startsWith('/drugs?')
    ? { items: [] } : page(ordered, 4, null, { primary_disease: disease, supplementary_groups: [] }));
  assert.deepEqual(titles(renderer), ordered.map(item => item.title));
  assert.equal(renderer.root.findAllByProps({ 'aria-label': 'Lista de conteúdos por relevância' }).length, 1);
  assert.match(nodeText(renderer.toJSON()), /Doença principal/);
  assert.doesNotMatch(nodeText(renderer.toJSON()), /Timeline|Sequência clínica/);
  assert.equal(calls.filter(url => url.startsWith('/relacionados/') || url.startsWith('/grafo/')).length, 0);
});

test('front and section filters request the full server set, preserve disease identity and travel with every page', async t => {
  const { renderer, calls, location } = await mount(t, 'Estenose mitral', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    const p = new URL(url, 'https://test.invalid').searchParams;
    const extra = { primary_disease: disease, supplementary_groups: [] };
    if (p.get('secao') === 'diretriz') return page([{ ...item('guidance', 'Consenso específico', 'estudo'), secao: 'diretriz' }], 1, null, extra);
    if (p.get('frente') === 'estudo') return p.has('offset')
      ? page([{ ...item('second-study', 'Segundo estudo', 'estudo'), relevance_order: 1 }], 2, null, extra)
      : page([{ ...item('unseen-study', 'Estudo fora do primeiro lote', 'estudo'), relevance_order: 0 }], 2, 1, extra);
    return page([item('doc', 'Documento inicial')], 120, 100, extra);
  });
  await filter(renderer, 'Frente de conhecimento', 'estudo');
  assert.deepEqual(titles(renderer), ['Estudo fora do primeiro lote']);
  assert.match(nodeText(renderer.toJSON()), /1 de 2 resultados carregados/);
  assert.equal(renderer.root.findByType('aside').children[0], disease.name);
  await click(more(renderer));
  assert.deepEqual(titles(renderer), ['Estudo fora do primeiro lote', 'Segundo estudo']);
  assert.ok(calls.some(url => url.includes('frente=estudo') && url.includes('offset=1')));
  await filter(renderer, 'Seção editorial', 'diretriz');
  assert.deepEqual(titles(renderer), ['Consenso específico']);
  const p = new URLSearchParams(location().search);
  assert.equal(p.get('q'), 'Estenose mitral');
  assert.equal(p.get('frente'), 'estudo');
  assert.equal(p.get('secao'), 'diretriz');
  assert.ok(calls.some(url => url.includes('frente=estudo') && url.includes('secao=diretriz') && !url.includes('offset=')));
});

test('filter navigation aborts pending pages, rejects stale results and Back/Forward restores filters', async t => {
  const old = deferred();
  const { renderer, requests, go } = await mount(t, 'tema', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    const p = new URL(url, 'https://test.invalid').searchParams;
    if (p.has('offset')) return old.promise;
    return p.get('frente') === 'exame' ? page([item('eco', 'Exame filtrado', 'exame')])
      : page([item('initial', 'Resultado inicial')], 2, 1);
  });
  await click(more(renderer));
  const pending = requests.find(({ url }) => url.includes('offset=1'));
  await filter(renderer, 'Frente de conhecimento', 'exame');
  assert.equal(pending.options.signal.aborted, true);
  await act(async () => { old.resolve(page([item('stale', 'Resultado obsoleto')], 2)); await tick(); });
  assert.deepEqual(titles(renderer), ['Exame filtrado']);
  await go(-1);
  assert.equal(renderer.root.findByProps({ 'aria-label': 'Frente de conhecimento' }).props.value, '');
  assert.deepEqual(titles(renderer), ['Resultado inicial']);
  await go(1);
  assert.equal(renderer.root.findByProps({ 'aria-label': 'Frente de conhecimento' }).props.value, 'exame');
  assert.deepEqual(titles(renderer), ['Exame filtrado']);
});

test('overlapping pages deduplicate by front and slug, restore backend order, and preserve every qualification', async t => {
  const first = { ...item('same', 'Conduta original'), relevance_order: 1,
    clinical_role: 'conditional', clinical_context: 'Somente quando há o critério clínico descrito.',
    match_reasons: [{ source: 'title', description: 'Assunto no título.' }] };
  const { renderer } = await mount(t, 'tema', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url.includes('offset=')) return page([
      { ...first, clinical_role: 'comparison', clinical_context: 'Não aplicar à população excluída.',
        match_reasons: [{ source: 'title', description: 'Assunto no título.' }, { source: 'body', description: 'População explicitamente qualificada.' }] },
      { ...item('same', 'Outro tipo, mesmo slug', 'exame'), relevance_order: 2 },
      { ...item('before', 'Anterior segundo a ordem do servidor'), relevance_order: 0 },
    ], 3);
    return page([first], 3, 1);
  });
  await click(more(renderer));
  assert.deepEqual(titles(renderer), ['Anterior segundo a ordem do servidor', 'Conduta original', 'Outro tipo, mesmo slug']);
  const text = nodeText(list(renderer));
  for (const qualification of ['Somente quando há o critério clínico descrito.', 'Não aplicar à população excluída.', 'Relação condicionada ao contexto', 'Comparação ou diagnóstico diferencial', 'População explicitamente qualificada.']) assert.ok(text.includes(qualification));
  assert.equal(text.split('Assunto no título.').length - 1, 1);
  assert.equal(more(renderer), undefined);
});

test('complete clinical exclusions precede a truncated title and remain visible with the match reason', async t => {
  // The production example had this geriatric recommendation in an EM query;
  // the fixture exercises rendering, without asking the client to reinterpret it.
  const title = 'Em idosos com fibrilação atrial, os anticoagulantes orais diretos são preferíveis…';
  const context = 'Exceto em pacientes com estenose mitral moderada a grave ou prótese valvar mecânica. Não extrapolar a preferência por DOAC a essa população.';
  const { renderer } = await mount(t, 'Estenose mitral', async url => url.startsWith('/drugs?') ? { items: [] }
    : page([{ ...item('doac-preferencial-sobre-varfarina-idoso', title, 'evidencia'),
      clinical_role: 'conditional', clinical_context: context, context_only: true,
      relation_type: 'contraindicated_in', match_reasons: [{ source: 'clinical_context', description: 'A população pesquisada é uma exceção explícita.' }],
    }], 1, null, { primary_disease: disease, supplementary_groups: [] }));
  const text = nodeText(list(renderer));
  assert.ok(text.indexOf(context) < text.indexOf(title));
  assert.match(text, /Contraindicação relacionada/);
  assert.match(text, /Mesmo tema clínico/);
  assert.match(text, /A população pesquisada é uma exceção explícita/);
  assert.equal(resultLinks(renderer).length, 1);
});

test('guide test suggestions are separate guided searches and never increase the published count', async t => {
  const { renderer, calls } = await mount(t, 'Estenose mitral', async url => url.startsWith('/drugs?') ? { items: [] }
    : page([item(disease.slug, disease.name, 'doenca')], 1, null, {
      primary_disease: disease, supplementary_groups: [{ tipo: 'exame', rotulo: 'Exames', rota_lista: '/exames', itens: [{
        slug: 'estenose-mitral--teste-estruturado-1', titulo: 'Ecocardiograma transtorácico com Doppler',
        rota: '/exames?q=Ecocardiograma', context_only: false, relation_method: 'SpecialtyDisease.tests',
      }] }],
    }));
  assert.equal(resultLinks(renderer).length, 1);
  const guided = renderer.root.findByProps({ 'aria-label': 'Pesquisas orientadas pelo guia' });
  assert.match(nodeText(guided), /não são verbetes adicionais/);
  assert.match(nodeText(guided), /Pesquisa orientada/);
  assert.equal(guided.findByType('a').props.href, '/exames?q=Ecocardiograma');
  assert.match(nodeText(renderer.toJSON()), /1 de 1 resultados carregados/);
  assert.equal(calls.filter(url => url.startsWith('/relacionados/')).length, 0);
});

test('an exact generic identity retains its complement and does not expand lexical neighbours', async t => {
  const { renderer, calls } = await mount(t, 'Holter 24h', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url.startsWith('/relacionados/ecossistema?')) return { total: 1, grupos: [{ tipo: 'documento', itens: [{
      slug: 'monitor', titulo: 'Monitorização complementar', rota: '/biblioteca/monitor',
      clinical_role: 'conditional', clinical_context: 'Interpretar conforme a apresentação clínica.',
    }] }] };
    return page([item('holter-24h', 'Holter 24h', 'exame'), item('sincope', 'Síncope investigada por Holter')]);
  });
  assert.equal(resultLinks(renderer).length, 2);
  const complement = renderer.root.findByProps({ 'aria-label': 'Conexões complementares do item' });
  assert.match(nodeText(complement), /Monitorização complementar/);
  assert.match(nodeText(complement), /Interpretar conforme a apresentação clínica/);
  assert.equal(calls.filter(url => url.startsWith('/relacionados/ecossistema?')).length, 1);
  assert.equal(calls.filter(url => url.startsWith('/grafo/')).length, 0);
});

test('a paginated duplicate keeps the clinical reason from an exact-identity complement', async t => {
  const { renderer } = await mount(t, 'Holter 24h', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url.startsWith('/relacionados/ecossistema?')) return { total: 1, grupos: [{ tipo: 'documento', itens: [{
      slug: 'monitor', titulo: 'Monitorização', rota: '/biblioteca/monitor',
      clinical_context: 'Conexão depende da apresentação clínica.', match_reasons: [{ source: 'graph', description: 'Relação editorial revisada.' }],
    }] }] };
    return url.includes('offset=') ? page([item('monitor', 'Monitorização')], 2)
      : page([item('holter-24h', 'Holter 24h', 'exame')], 2, 1);
  });
  await click(more(renderer));
  assert.equal(renderer.root.findAllByType('a').filter(a => a.props.href === '/biblioteca/monitor').length, 1);
  assert.match(nodeText(list(renderer)), /Conexão depende da apresentação clínica/);
  assert.match(nodeText(list(renderer)), /Relação editorial revisada/);
});

test('failed filtered pagination retains its cursor and retries without simultaneous duplicate calls', async t => {
  let attempts = 0;
  const { renderer, calls } = await mount(t, 'tema', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url.includes('offset=')) {
      if (++attempts === 1) throw Error('temporary');
      return page([{ ...item('end', 'Resultado recuperado'), relevance_order: 1 }], 2);
    }
    return page([{ ...item('initial', 'Resultado inicial'), relevance_order: 0 }], 2, 1);
  }, ['/busca?q=tema&frente=documento']);
  await act(async () => { more(renderer).props.onClick(); more(renderer).props.onClick(); await tick(); });
  assert.equal(attempts, 1);
  assert.equal(renderer.root.findAllByProps({ role: 'alert' }).length, 1);
  assert.deepEqual(titles(renderer), ['Resultado inicial']);
  await click(more(renderer));
  assert.deepEqual(titles(renderer), ['Resultado inicial', 'Resultado recuperado']);
  assert.equal(calls.filter(url => url.includes('frente=documento') && url.includes('offset=1')).length, 2);
});

test('zero-result filters remain changeable and clearing them restores the complete server list', async t => {
  const { renderer } = await mount(t, 'tema', async url => url.startsWith('/drugs?') ? { items: [] }
    : url.includes('secao=') ? page([]) : page([item('all', 'Resultado sem filtro')]));
  await filter(renderer, 'Seção editorial', 'diretriz');
  assert.match(nodeText(renderer.toJSON()), /Nenhum conteúdo com estes filtros/);
  const clear = renderer.root.findAllByType('button').find(button => nodeText(button) === 'Limpar filtros');
  await click(clear);
  assert.deepEqual(titles(renderer), ['Resultado sem filtro']);
});

test('editorial classification never changes a stored document, study or original source destination', async t => {
  const sourceKey = 'a'.repeat(64);
  const { renderer } = await mount(t, 'tema', async url => url.startsWith('/drugs?') ? { items: [] } : page([
    { ...item('trial', 'Ensaio clínico', 'documento'), kind: 'estudo' },
    { ...item('same-score', 'Documento de escore', 'documento'), kind: 'calculadora', secao: 'calculadora' },
    { ...item('same-score', 'Calculadora executável', 'calculadora'), kind: 'calculadora', secao: 'calculadora' },
    { ...item('sepsis', 'Sepsis-3', 'estudo'), kind: 'consenso', secao: 'diretriz' },
    item('case', 'Caso clínico', 'caso_clinico'), item('patient', 'Material para pacientes', 'material_paciente'),
    item('triage', 'Triagem', 'triagem_sintoma'),
    { ...item(sourceKey, 'Original armazenado', 'publicacao_original'), secao: 'publicacao_original' },
  ]));
  assert.deepEqual(resultLinks(renderer).map(a => a.props.href), [
    '/biblioteca/trial', '/biblioteca/same-score', '/calculadoras/same-score', '/estudos/sepsis',
    '/casos-clinicos/case', '/material-paciente/patient', '/triagem-sintomas?slug=triage', `/intelligence?fonte=${sourceKey}`,
  ]);
  assert.equal(titles(renderer).filter(title => title.includes('escore') || title.includes('executável')).length, 2);
});

test('a scientific original shared with a generic complement appears once and retains its reason', async t => {
  const original = item('a'.repeat(64), 'Original científico armazenado', 'publicacao_original');
  const { renderer } = await mount(t, 'Holter 24h', async url => {
    if (url.startsWith('/drugs?')) return { items: [] };
    if (url.startsWith('/relacionados/ecossistema?')) return { total: 1, grupos: [{ tipo: 'publicacao_original', itens: [{
      slug: original.slug, titulo: original.title, rota: `/intelligence?fonte=${original.slug}`,
      clinical_context: 'Original utilizado na fundamentação desta investigação.',
    }] }] };
    return page([item('holter-24h', 'Holter 24h', 'exame'), original]);
  });
  assert.equal(renderer.root.findAllByType('a').filter(a => a.props.href === `/intelligence?fonte=${original.slug}`).length, 1);
  assert.match(nodeText(list(renderer)), /Original utilizado na fundamentação desta investigação/);
});

for (const highlighted of [false, true]) {
  test(`integral evidence and its context appear once, preserving negation after character 180 (${highlighted ? 'marked' : 'plain'} snippet)`, async t => {
    const statement = 'Esta recomendação de anticoagulação considera o perfil clínico, a população do estudo, a segurança do tratamento e os critérios de elegibilidade descritos na publicação e deve ser interpretada com esses limites; não se aplica à estenose mitral moderada ou grave.';
    assert.ok(statement.indexOf('não se aplica') > 180);
    const context = 'A recomendação exclui pacientes com estenose mitral moderada ou grave.';
    const distinctReason = 'Tag revisada: estenose mitral.';
    const { renderer } = await mount(t, 'Estenose mitral', async url => url.startsWith('/drugs?') ? { items: [] }
      : page([{ ...item('comparacao-integral', statement, 'evidencia'),
        snippet: highlighted ? statement.replace('estenose mitral', '<mark>estenose mitral</mark>') : statement,
        clinical_role: 'comparison', clinical_context: context,
        match_reasons: [{ source: 'clinical_profile', description: context }, { source: 'reviewed_tag', description: distinctReason }],
      }], 1, null, { primary_disease: disease, supplementary_groups: [] }));
    assert.equal(nodeText(resultLinks(renderer)[0]), statement);
    const text = nodeText(list(renderer));
    assert.equal(text.split(statement).length - 1, 1, 'the complete statement is not repeated as a snippet');
    assert.equal(text.split(context).length - 1, 1, 'the exact context is not repeated as a match reason');
    assert.ok(text.includes(distinctReason), 'distinct match reasons remain visible');
    assert.ok(text.indexOf(context) < text.indexOf(statement));
  });
}
