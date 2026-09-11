import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

// Local UI contract exercise only. Canonical text is reused verbatim, not
// re-reviewed, published, synthesized or sent to a clinical/AI service.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const base = new URL(process.env.ATELIER_QA_URL || 'http://127.0.0.1:4322');
if (!['127.0.0.1', 'localhost'].includes(base.hostname) || base.username || base.password) throw Error('Loopback only');
const out = path.resolve(process.env.ATELIER_SCIENCE_QA_OUT || '/tmp/corvia-science-functional-qa');
if (!out.startsWith('/tmp/')) throw Error('Output must be below /tmp');
fs.mkdirSync(out, { recursive: true });
if (!/^\/(private\/)?tmp\//.test(fs.realpathSync(out))) throw Error('Unsafe output symlink');
const provenance = [];
function read(relative) {
  const raw = fs.readFileSync(path.join(root, relative), 'utf8');
  provenance.push({ path: relative, sha256: crypto.createHash('sha256').update(raw).digest('hex') });
  return raw;
}
const metadata = dir => JSON.parse(read(`${dir}/metadados.json`));
const registry = read('frontend/src/lib/clinicalRouteRegistry.ts');
read('frontend/src/App.tsx');
const inventory = registry.split('\n').filter(line => /space: "(ensino|pesquisa)"/.test(line)).map(line => ({ route: line.match(/path: "([^"]+)"/)[1], space: line.match(/space: "([^"]+)"/)[1], alias: line.includes('kind: "alias"') }));
function document(relative) {
  const raw = read(relative), match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) throw Error('Expected canonical front matter');
  const data = { body_md: match[2], version: 1, source_refs: [], summary: null };
  for (const key of ['slug', 'title', 'theme', 'kind', 'summary', 'review_status', 'source_refs']) {
    const line = match[1].match(new RegExp(`^${key}: (.+)$`, 'm'))?.[1];
    if (line === undefined) continue;
    data[key] = /^["\[]/.test(line) ? JSON.parse(line) : line;
  }
  if (data.source_refs.length === 0) data.source_refs = [...match[1].matchAll(/^- (.+)$/gm)].map(item => item[1].replace(/^'|'$/g, ''));
  return data;
}
const doc = document('content/Insuficiência_cardíaca/icfer-classificacao-diagnostico-quatro-pilares.md');
const flux = document('content/Insuficiência_cardíaca/fluxograma-insuficiencia-cardiaca-cronica-por-fracao-de-ejecao-esc-2023.md');
const docs = [doc, flux];
const tracks = metadata('trilhas').slice(0, 2);
const track = tracks[0];
const cases = metadata('casos-clinicos').slice(0, 2), clinicalCase = cases[0];
const materials = metadata('material-paciente').slice(0, 2), material = materials[0];
const studiesAll = metadata('estudos');
const studies = [studiesAll.find(item => item.slug === 'dapa-hf-dapagliflozina-icfer'), studiesAll[0]].filter(Boolean);
const study = studies[0];
const evidences = metadata('evidencias').slice(0, 2).map((item, index) => ({ id: 990000 + index, summary: item.statement, source_url: null, doi: null, document_slug: null, tags: [], ...item }));
const evidence = evidences[0];
const gallery = metadata('galeria').slice(0, 2).map(item => ({ ...item, file_path: `/qa-canonical-gallery/${item.file_path}`, thumbnail_path: null }));
const galleryItem = gallery[0];
const profile = { id: 990091, email: 'science-functional@example.invalid', full_name: 'Demonstração CorVIA', professional_title: 'Dr.', role: 'admin', profession: 'Medico', council_name: 'CRM', council_number: '000000', council_state: 'SP', product_access: true, investidor: false, profile_completion_required: false, kyc_required: false, onboarding_pendente: false, boas_vindas_pendente: false };
const unavailable = 'Serviço indisponível na fixture local de Ensino e Pesquisa (503).';
const rows = [], requests = [], pageErrors = [], blocked = [];
let current = {}, failPath = null, paginationPath = null, failNextPage = false, favorites = [], nextFavorite = 990100, progress = new Set();
const norm = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
function filter(items, url) {
  const q = norm(url.searchParams.get('q'));
  return items.filter(item => (!q || norm([item.title, item.titulo, item.statement, item.summary, item.tema, item.theme].join(' ')).includes(q)) && (!url.searchParams.get('theme') || (item.theme || item.tema) === url.searchParams.get('theme')) && (!url.searchParams.get('kind') || item.kind === url.searchParams.get('kind')) && (!url.searchParams.get('modality') || item.modality === url.searchParams.get('modality')) && (!url.searchParams.get('study_type') || item.study_type === url.searchParams.get('study_type')));
}
const paginated = items => ({ items, total: items.length, limit: 500, offset: 0, next_offset: null, has_more: false });
const groups = (items, key, name = key) => [...new Set(items.map(item => item[key]))].map(value => ({ [name]: value, count: items.filter(item => item[key] === value).length }));
function trackDetail() {
  const steps = track.etapas.slice(0, 2).map((step, index) => ({ ...step, etapa_id: 990201 + index, titulo: docs[index].title, link: `/biblioteca/${docs[index].slug}`, concluida: progress.has(index), disponivel: true }));
  return { ...track, etapas: steps, total_etapas: steps.length, concluidas: progress.size, finalizada_em: null, concluida_atualmente: progress.size === steps.length, conclusao_historica_em: null, etapas_indisponiveis: 0 };
}
const privateDoc = { id: 990400, title: `Recorte local — ${doc.title}`, document_type: 'texto', language: 'pt', doi: null, source_url: null, media_type: 'text/plain', size_bytes: Buffer.byteLength(doc.body_md), analysis_status: 'pendente', incorporation_recommended: false, incorporation_status: 'nao_incorporado', incorporated_document_id: null, summary_pt: null, translation_available: false, created_at: '2026-09-11T12:00:00Z' };
const discovery = { id: 990500, slug: flux.slug, org: 'ESC', title: flux.title, title_original: flux.title, title_pt: null, summary_pt: null, theme: flux.theme, published_at: '2023-08-25T00:00:00Z', discovered_at: '2026-09-11T12:00:00Z', url: null, doi: null, status: 'detected', key_changes: [], limitations: [], impacts: [], summary_document_slug: flux.slug, clinical_content_changed: false, translation_mode: null, analyzed_at: null };
const monitor = { enabled: false, health: 'inactive', cadence_hours: 4, normal_interval_hours: 4, surge_interval_hours: 1, schedule_reason: 'Fixture local sem monitoramento externo.', high_frequency_window: null, last_heartbeat_at: null, last_started_at: null, last_completed_at: null, last_success_at: null, next_run_at: null, analysis_status: 'not_run', coverage: null, recent_discoveries: [discovery], total_discovered: 1, pending_analysis: 1 };
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs');
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--disable-gpu'] });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'pt-BR', serviceWorkers: 'block', reducedMotion: 'reduce' });
await context.addInitScript(() => {
  localStorage.setItem('corvia:cardiology-spaces:theme:v1:990091', 'light');
  localStorage.setItem('corvia:cardiology-spaces:tour:v3', 'true');
  Object.defineProperty(navigator, 'geolocation', { value: { getCurrentPosition() { throw Error('Real geolocation forbidden in QA'); }, watchPosition() { throw Error('Real geolocation forbidden in QA'); } } });
});
await context.route('**/*', async route => {
  const request = route.request(), url = new URL(request.url()), p = url.pathname, method = request.method();
  if (p.startsWith('/qa-canonical-gallery/')) {
    const relative = p.slice('/qa-canonical-gallery/'.length);
    const file = path.resolve(root, 'galeria', relative);
    if (!file.startsWith(path.join(root, 'galeria') + path.sep) || !fs.existsSync(file)) return route.fulfill({ status: 404 });
    return route.fulfill({ status: 200, contentType: 'image/jpeg', body: fs.readFileSync(file) });
  }
  if (!p.startsWith('/api/')) {
    if (url.origin === base.origin && ['GET', 'HEAD'].includes(method)) return route.continue();
    blocked.push({ ...current, origin: url.origin, path: p, method });
    return route.abort('blockedbyclient');
  }
  const entry = { ...current, path: p, method }; requests.push(entry);
  const json = (body, status = 200) => { entry.status = status; return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) }); };
  if (failPath && (typeof failPath === 'string' ? p === failPath : failPath.test(p))) return json({ detail: unavailable }, 503);
  if (paginationPath === p) {
    const items = p === '/api/studies' ? studies : docs, offset = Number(url.searchParams.get('offset') || 0);
    if (offset && failNextPage) return json({ detail: unavailable }, 503);
    return json({ items: items.slice(offset, offset + 1), total: items.length, limit: 1, offset, next_offset: offset === 0 ? 1 : null, has_more: offset === 0 });
  }
  if (p === '/api/auth/session-status') return json({ authenticated: true });
  if (p === '/api/auth/me') return json(profile);
  if (p === '/api/version') return json({ commit: 'local-science-contract-fixture' });
  if (p === '/api/billing/status') return json({ entitlements: { ai: true, mail: false } });
  if (p === '/api/clinical-change-approvals/count') return json({ pending: 0 });
  if (p === '/api/email/conta') return json({ ativa: false, status: 'inativa' });
  if (p === '/api/exportar/corvia-mail') return json({ disponivel: false, motivo: 'Fixture local: envio de e-mail não habilitado.', email_address: null });
  if (p === '/api/assinatura/certificado-a1') return json({ conectado: false });
  if (p === '/api/favorites/status') {
    const item = favorites.find(item => item.item_type === url.searchParams.get('item_type') && (item.item_slug === url.searchParams.get('item_slug') || String(item.item_id) === url.searchParams.get('item_id')));
    return json({ favorited: Boolean(item), favorite_id: item?.id ?? null, available: true });
  }
  if (p === '/api/favorites' && method === 'GET') return json(favorites);
  if (p === '/api/favorites' && method === 'POST') {
    const body = request.postDataJSON(), content = [...docs, ...studies, ...evidences, ...tracks, ...materials, ...gallery, ...cases].find(item => item.slug === body.item_slug);
    const item = { ...body, id: ++nextFavorite, title: content?.title || content?.titulo || content?.statement || privateDoc.title, url: body.item_type === 'documento' ? `/biblioteca/${body.item_slug}` : `/trilhas/${body.item_slug}`, meta: 'Recorte local para QA', available: true, reading: null, private_reading: null };
    favorites.push(item); return json({ id: item.id });
  }
  if (p.startsWith('/api/favorites/by-id/') && method === 'DELETE') { favorites = favorites.filter(item => item.id !== Number(p.split('/').at(-1))); return json({ ok: true }); }
  if (p === '/api/trilhas') return json(paginated(tracks.map(item => ({ ...item, total_etapas: item === track ? 2 : item.etapas.length, concluidas: item === track ? progress.size : 0, finalizada_em: null }))));
  if (p === '/api/trilhas/timeline/temas') return json(groups(studies, 'theme', 'tema').map(item => ({ ...item, total_marcos: item.count })));
  if (p === '/api/trilhas/timeline') {
    const selected = studies.filter(item => item.theme === url.searchParams.get('tema'));
    return json({ tema: url.searchParams.get('tema'), total: selected.length, primeiro_ano: Math.min(...selected.map(item => item.year)), ultimo_ano: Math.max(...selected.map(item => item.year)), eixos: [{ eixo: 'Estudos', total: selected.length }], marcos: selected.map(item => ({ ano: item.year, tipo: 'estudo', eixo: 'Estudos', subtipo: item.study_type, slug: item.slug, titulo: item.title, descricao: item.summary, fonte: item.journal, referencia: item.doi, rota: `/estudos/${item.slug}`, documento: null, tags: item.tags || [], doi: item.doi, pmid: item.pmid, source_url: item.url })) });
  }
  if (p === `/api/trilhas/${track.slug}/progresso` && method === 'POST') { const body = request.postDataJSON(), index = body.etapa_id - 990201; if (body.concluida) progress.add(index); else progress.delete(index); return json(trackDetail()); }
  if (p === `/api/trilhas/${track.slug}`) return json(trackDetail());
  if (p === '/api/material-paciente') return json(paginated(filter(materials, url)));
  if (p === `/api/material-paciente/${material.slug}`) return json(material);
  if (p === '/api/casos-clinicos/themes') return json(groups(cases, 'tema', 'theme'));
  if (p === '/api/casos-clinicos') return json(paginated(filter(cases, url).map(item => ({ ...item, tentativas: 0, acertou_na_ultima: null }))));
  if (p === `/api/casos-clinicos/${clinicalCase.slug}/responder` && method === 'POST') return json({ acertou: request.postDataJSON().opcao_escolhida === clinicalCase.resposta_correta, resposta_correta: clinicalCase.resposta_correta, explicacao: clinicalCase.explicacao });
  if (p === `/api/casos-clinicos/${clinicalCase.slug}`) return json(clinicalCase);
  if (p === '/api/gallery/modalities') return json(groups(gallery, 'modality'));
  if (p === '/api/gallery/images') return json(paginated(filter(gallery, url)));
  if (p === `/api/gallery/images/${galleryItem.slug}`) return json(galleryItem);
  if (p === '/api/library/catalog') return json({ total: docs.length, fronts: [{ key: 'documento', label: 'Recorte local de documentos', route: '/biblioteca#documentos', count: docs.length }] });
  if (p === '/api/library/themes') return json(groups(docs, 'theme'));
  if (p === '/api/library/area-counts') return json({ areas: [{ id: 'geral', label: 'Cardiologia Geral', count: docs.length, collections: 1 }] });
  if (p === '/api/library/presentation-options') return json(docs);
  if (p === '/api/library/documents') return json(paginated(filter(docs, url)));
  if (p.startsWith('/api/library/documents/')) { const item = docs.find(item => item.slug === decodeURIComponent(p.split('/').at(-1))); return json(item || { detail: unavailable }, item ? 200 : 503); }
  if (p === '/api/studies/types') return json(groups(studies, 'study_type'));
  if (p === '/api/studies/themes') return json(groups(studies, 'theme'));
  if (p === '/api/studies') return json(paginated(filter(studies, url)));
  if (p.startsWith('/api/studies/')) { const item = studies.find(item => item.slug === p.split('/').at(-1)); return json(item || { detail: unavailable }, item ? 200 : 503); }
  if (p === '/api/evidence/themes') return json(groups(evidences, 'theme'));
  if (p === '/api/evidence') return json(paginated(filter(evidences, url)));
  if (p === `/api/evidence/${evidence.slug}`) return json(evidence);
  if (p === '/api/guideline-updates/status') return json(monitor);
  if (p === '/api/guideline-updates/me') return json({ cutoff: '2023-01-01', items: [{ notification_id: 990501, read_at: null, message: 'Recorte local de notificação, sem atualização clínica aplicada.', guideline: discovery }] });
  if (p === '/api/guideline-updates') return json({ cutoff: '2023-01-01', items: [discovery] });
  if (p === `/api/guideline-updates/${discovery.id}/read`) return json({ notification_id: 990501, read_at: '2026-09-11T12:00:00Z' });
  if (p === '/api/documentos-cientificos-ia' && method === 'GET') return json([privateDoc]);
  if (p === `/api/documentos-cientificos-ia/${privateDoc.id}` && method === 'GET') return json(privateDoc);
  if (p === `/api/documentos-cientificos-ia/${privateDoc.id}/arquivo`) { entry.status = 200; return route.fulfill({ status: 200, contentType: 'text/plain', body: doc.body_md }); }
  if (p.startsWith('/api/scientific-reading/')) { const [, , , type, slug] = p.split('/'); const item = [...docs, ...studies, ...evidences, ...materials].find(item => item.slug === decodeURIComponent(slug || '')); const summary = item?.summary || item?.resumo; return json({ entity_type: type, slug: decodeURIComponent(slug || ''), summary_pt: summary ? { status: 'available', text: summary, origin: 'editorial' } : { status: 'unavailable' }, sources: [] }); }
  if (p === '/api/search') return json({ results: norm(url.searchParams.get('q')).includes('zzsem') ? [] : [{ ...doc, frente: 'documento', snippet: doc.summary }, { ...study, kind: study.study_type, frente: 'estudo', snippet: study.summary, ano: study.year }], total: 2, next_offset: null, por_frente: { documento: 1, estudo: 1 } });
  if (p === '/api/drugs') return json(paginated([]));
  if (p === '/api/exportar/catalogo') return json({ total: 2, tipos: ['documento', 'estudo'], itens: [{ tipo: 'documento', slug: doc.slug, titulo: doc.title, tema: doc.theme, detalhe: doc.summary, rotulo_tipo: 'Documento' }, { tipo: 'estudo', slug: study.slug, titulo: study.title, tema: study.theme, detalhe: study.journal, rotulo_tipo: 'Estudo' }].filter(item => !url.searchParams.get('tipo') || item.tipo === url.searchParams.get('tipo')) });
  // In particular: no inferred graph edges, no AI quote/analyze/incorporation,
  // no email, PDF/PPTX/DOCX generation and no non-fixture writes.
  return json({ detail: unavailable }, 503);
});
const page = await context.newPage();
page.setDefaultTimeout(10000); page.setDefaultNavigationTimeout(30000);
page.on('pageerror', error => pageErrors.push({ ...current, message: String(error) }));
async function settle() { await page.evaluate(async () => { await document.fonts.ready; await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))); }); }
const main = () => page.locator('#conteudo-principal');
async function visible(locator) { await locator.first().waitFor({ state: 'visible' }); }
async function check(condition, message) { if (!await condition) throw Error(message); }
async function screenshot(label) { await settle(); await page.screenshot({ path: path.join(out, `${current.width}-${label}.png`), fullPage: true }); return `${current.width}-${label}.png`; }
async function favorite() {
  const control = main().getByRole('button', { name: '☆ Favoritar', exact: true }).first();
  await control.click(); await visible(main().getByRole('button', { name: '★ Favoritado', exact: true }));
}
async function test(route, name, action) {
  if (process.env.ATELIER_SCIENCE_QA_ONLY && !process.env.ATELIER_SCIENCE_QA_ONLY.split(',').includes(name)) return;
  current = { route, width: page.viewportSize().width, name };
  const row = { ...current, actions: [], checks: [], issues: [], limitations: ['UI local com recorte canônico; não certifica publicação, corpus, backend ou serviço externo.'] };
  const errorStart = pageErrors.length, requestStart = requests.length;
  rows.push(row); failPath = null; paginationPath = null; failNextPage = false;
  try {
    await page.goto(new URL(route, base).href, { waitUntil: 'domcontentloaded' });
    await visible(main());
    await action(row);
    await settle();
    const layout = await main().evaluate(root => ({ overflow: Math.max(document.documentElement.scrollWidth - innerWidth, 0), headings: [...root.querySelectorAll('h1')].map(e => e.textContent), smallControls: [...root.querySelectorAll('button,input,select,textarea')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.height && !e.disabled && (r.height < 43.5 || r.width < 43.5); }).map(e => ({ text: e.getAttribute('aria-label') || e.textContent?.slice(0, 80), height: e.getBoundingClientRect().height, width: e.getBoundingClientRect().width })) }));
    row.layout = layout; row.resolvedPath = new URL(page.url()).pathname;
    if (layout.overflow > 2) row.issues.push(`Overflow horizontal ${layout.overflow}px`);
    row.screenshot = await screenshot(name);
  } catch (error) { row.issues.push(String(error)); row.screenshot = await screenshot(`${name}-failure`).catch(() => null); }
  row.pageErrors = pageErrors.slice(errorStart); row.requests = requests.slice(requestStart).map(({ path, method, status }) => ({ path, method, status }));
  console.log(JSON.stringify({ route, width: row.width, actions: row.actions, issues: row.issues, pageErrors: row.pageErrors }));
  fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify({ rows, provenance, blocked, pageErrors, limitations: ['All /api requests intercepted; all external requests blocked.', 'No backend/corpus/publication/AI certification.', 'No original external papers fetched; no clinical content generated.'] }, null, 2));
}
async function searchFilter(row, input, term, link) {
  await visible(link); await input.fill('zzsemresultado');
  await page.waitForTimeout(400); await check(link.count().then(n => n === 0), 'Filtro não removeu o resultado não correspondente');
  await input.fill(term); await visible(link); row.actions.push('buscar sem correspondência, restaurar busca com recorte e confirmar resultado');
}
async function openDetail(row, route, title) {
  await main().locator(`a[href="${route}"]`).first().click(); await page.waitForURL(url => url.pathname === route);
  await visible(main().getByRole('heading', { name: title, exact: true })); row.actions.push('abrir detalhe por link real da interface');
}
try {
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: width === 1440 ? 900 : 844 }); progress = new Set(); favorites = [];
    await test('/trilhas', 'trilhas', async row => { const link = main().locator(`a[href="/trilhas/${track.slug}"]`); await searchFilter(row, main().getByPlaceholder('Tema, objetivo, nível ou trilha…'), track.titulo, link); await openDetail(row, `/trilhas/${track.slug}`, track.titulo); });
    await test('/cursos', 'cursos-alias', async row => { await page.waitForURL(url => url.pathname === '/trilhas'); await visible(main().locator(`a[href="/trilhas/${track.slug}"]`)); row.actions.push('alias /cursos redireciona ao catálogo de Trilhas com conteúdo'); });
    await test(`/cursos/${track.slug}`, 'curso-alias', async row => { await page.waitForURL(url => url.pathname === '/trilhas'); await visible(main().locator(`a[href="/trilhas/${track.slug}"]`)); row.actions.push('alias legado /cursos/:slug redireciona ao catálogo /trilhas conforme registry'); row.limitations.push('Contrato atual redireciona ao catálogo, não ao detalhe do slug.'); });
    await test(`/trilhas/${track.slug}`, 'trilha-progresso', async row => {
      await visible(main().getByRole('heading', { name: track.titulo, exact: true })); await favorite(); row.actions.push('favoritar trilha em memória');
      const mark = main().getByRole('button', { name: 'Marcar etapa como concluída', exact: true }).first(); await mark.click(); await visible(main().getByRole('button', { name: 'Desmarcar etapa', exact: true })); row.actions.push('marcar progresso e confirmar estado concluído');
      failPath = `/api/trilhas/${track.slug}/progresso`; await main().getByRole('button', { name: 'Desmarcar etapa', exact: true }).click(); await visible(main().getByText(unavailable, { exact: true })); await check(progress.size === 1, '503 alterou progresso'); row.actions.push('503 preserva progresso');
      failPath = null; await main().getByRole('button', { name: 'Desmarcar etapa', exact: true }).click(); await check(progress.size === 0, 'Retry não reverteu progresso'); row.actions.push('repetir ação após 503');
    });
    await test('/trilhas/timeline', 'timeline', async row => { const selector = main().getByRole('combobox', { name: 'Escolha a doença/tema' }); await visible(selector); await selector.selectOption(study.theme); await visible(main().locator(`a[href="/estudos/${study.slug}"]`)); row.actions.push('selecionar tema e visualizar marco canônico com ano/fonte'); await openDetail(row, `/estudos/${study.slug}`, study.title); });
    await test('/material-paciente', 'material-paciente', async row => { const link = main().locator(`a[href="/material-paciente/${material.slug}"]`); await searchFilter(row, main().getByPlaceholder('Ex.: insuficiência cardíaca, hipertensão, anticoagulação…'), material.titulo, link); await openDetail(row, `/material-paciente/${material.slug}`, material.titulo); });
    await test(`/material-paciente/${material.slug}`, 'material-detalhe', async row => { await visible(main().getByRole('heading', { name: material.titulo, exact: true })); await main().getByRole('button', { name: /Baixar.*PDF/ }).click(); await visible(main().getByText(unavailable, { exact: true })); await visible(main().getByRole('heading', { name: material.titulo, exact: true })); row.actions.push('ler material; falha 503 no PDF mantém conteúdo e ação'); row.limitations.push('Não certifica geração de PDF nem envio ao paciente.'); });
    await test('/galeria', 'atlas', async row => { const link = main().locator(`a[href="/galeria/${galleryItem.slug}"]`); await searchFilter(row, main().getByRole('textbox', { name: 'Buscar imagem' }), galleryItem.title, link); await openDetail(row, `/galeria/${galleryItem.slug}`, galleryItem.title); });
    await test(`/galeria/${galleryItem.slug}`, 'atlas-detalhe', async row => { await visible(main().getByRole('heading', { name: galleryItem.title, exact: true })); const img = main().getByRole('img', { name: galleryItem.title }); await check(img.evaluate(e => e.complete && e.naturalWidth > 0), 'Imagem canônica não abriu'); await favorite(); row.actions.push('abrir imagem local canônica, achados/fonte/licença e favoritar'); });
    await test('/casos-clinicos', 'casos', async row => { const link = main().locator(`a[href="/casos-clinicos/${clinicalCase.slug}"]`); await searchFilter(row, main().getByRole('searchbox', { name: 'Buscar por tema específico' }), clinicalCase.titulo, link); await openDetail(row, `/casos-clinicos/${clinicalCase.slug}`, clinicalCase.titulo); });
    await test(`/casos-clinicos/${clinicalCase.slug}`, 'caso-resposta', async row => { const confirm = main().getByRole('button', { name: 'Confirmar resposta', exact: true }); await check(confirm.isDisabled(), 'Resposta deve exigir escolha'); await main().getByRole('button', { name: clinicalCase.opcoes[clinicalCase.resposta_correta], exact: true }).click(); failPath = `/api/casos-clinicos/${clinicalCase.slug}/responder`; await confirm.click(); await visible(main().getByText(unavailable, { exact: true })); row.actions.push('escolher resposta canônica; simular 503 de registro'); await check(confirm.isVisible(), '503 removeu caso e impossibilitou repetir a resposta'); failPath = null; await confirm.click(); await visible(main().getByText('Resposta correta.', { exact: true })); row.actions.push('repetir resposta após 503 e ler explicação canônica'); });
    await test('/apresentacao', 'apresentacao', async row => { await main().getByRole('button').filter({ hasText: doc.title }).first().click(); await main().getByLabel('Anotação do apresentador (opcional)').fill('Anotação demonstrativa para testar preservação após erro.'); await main().getByRole('radio', { name: /PowerPoint editável/ }).check(); await main().getByRole('button', { name: 'Gerar PowerPoint editável', exact: true }).click(); await visible(main().getByText(unavailable, { exact: true })); await check(main().getByLabel('Anotação do apresentador (opcional)').inputValue().then(v => v.startsWith('Anotação demonstrativa')), '503 apagou anotação'); row.actions.push('selecionar fonte, anotar, escolher PPTX, 503 preserva seleção/anotação'); row.limitations.push('Geração real de apresentações não exercitada.'); });
    await test('/busca', 'tudo-com-tudo', async row => { await main().getByRole('searchbox', { name: 'Assunto' }).fill('insuficiência cardíaca'); await main().getByRole('button', { name: 'Conectar', exact: true }).click(); await visible(main().locator(`a[href="/biblioteca/${doc.slug}"]`)); row.actions.push('Conectar assunto e abrir resultados canônicos em duas frentes'); await openDetail(row, `/biblioteca/${doc.slug}`, doc.title); row.limitations.push('Relações do grafo não inventadas: endpoints de relações retornam 503 explícito.'); });
    await test('/biblioteca', 'biblioteca', async row => { await visible(main().locator(`a[href="/biblioteca/${doc.slug}"]`)); await main().getByPlaceholder('Ex.: Cardiologia Geral, Pediátrica ou Cardio-Oncologia').fill('zzsemresultado'); await check(main().getByText('Cardiologia Geral', { exact: true }).count().then(n => n === 0), 'Busca de área não filtrou'); row.actions.push('abrir catálogo com documentos e filtrar área'); await openDetail(row, `/biblioteca/${doc.slug}`, doc.title); });
    await test(`/biblioteca/${doc.slug}`, 'documento', async row => { await visible(main().getByRole('heading', { name: doc.title, exact: true })); await favorite(); row.actions.push('ler Markdown canônico/referências; favoritar documento'); });
    await test('/fluxogramas', 'fluxogramas', async row => { const link = main().locator(`a[href="/biblioteca/${flux.slug}"]`); await searchFilter(row, main().locator('input').first(), flux.title, link); await openDetail(row, `/biblioteca/${flux.slug}`, flux.title); await visible(main().locator('.fluxograma svg')); await main().getByRole('combobox', { name: 'Zoom', exact: true }).selectOption('150'); await check(main().locator('.fluxograma svg').evaluate(e => e.style.width === '150%'), 'Zoom não aplicado'); await main().getByRole('combobox', { name: 'Zoom', exact: true }).selectOption('100'); const table = main().getByRole('region', { name: 'Tabela do documento — deslize para consultar todas as colunas' }); await table.focus(); await check(table.evaluate(e => document.activeElement === e), 'Tabela não alcançável pelo teclado'); await page.keyboard.press('ArrowRight'); row.actions.push('renderizar fluxograma Mermaid existente; zoom 150/100; tabela com foco/rolagem por teclado'); });
    await test('/estudos', 'estudos', async row => { const link = main().locator(`a[href="/estudos/${study.slug}"]`); await searchFilter(row, main().getByRole('textbox', { name: 'Buscar estudo', exact: true }), study.title, link); await openDetail(row, `/estudos/${study.slug}`, study.title); });
    await test(`/estudos/${study.slug}`, 'estudo-detalhe', async row => { await visible(main().getByRole('heading', { name: study.title, exact: true })); await favorite(); row.actions.push('ler resumo/limitações/referência canônica e favoritar estudo'); });
    await test('/evidencias', 'evidencias', async row => { const link = main().locator(`a[href="/evidencias/${evidence.slug}"]`); await searchFilter(row, main().getByPlaceholder('Ex.: anticoagulação, ICFER, hipertensão…'), evidence.statement, link); await openDetail(row, `/evidencias/${evidence.slug}`, evidence.statement); });
    await test(`/evidencias/${evidence.slug}`, 'evidencia-detalhe', async row => { await visible(main().getByRole('heading', { name: evidence.statement, exact: true })); await favorite(); row.actions.push('ler classe/nível da fonte existente e favoritar evidência'); });
    await test('/diretrizes', 'diretrizes', async row => { await visible(main().locator(`a[href="/biblioteca/${flux.slug}"]`)); const search = main().getByRole('searchbox').first(); await search.fill(flux.title); await visible(main().locator(`a[href="/biblioteca/${flux.slug}"]`)); row.actions.push('filtrar coleção editorial e abrir referência existente'); await openDetail(row, `/biblioteca/${flux.slug}`, flux.title); });
    await test('/intelligence', 'intelligence', async row => { await visible(main().getByText('Monitoramento sem execução recente', { exact: true })); failPath = '/api/guideline-updates/status'; await main().getByRole('button', { name: 'Atualizar estado', exact: true }).click(); await visible(main().getByText('Não foi possível confirmar o estado do monitoramento agora.', { exact: true })); failPath = null; await main().getByRole('button', { name: 'Tentar novamente', exact: true }).first().click(); await visible(main().getByText('Monitoramento sem execução recente', { exact: true })); row.actions.push('ler descoberta de fixture; estado inativo explícito; 503 e retry do monitor'); row.limitations.push('Sem execução de monitoramento/cobertura científica real.'); });
    await test('/documentos-cientificos-ia', 'cientifico-ia', async row => { await main().getByRole('button').filter({ hasText: privateDoc.title }).click(); await main().getByRole('button', { name: 'Abrir original', exact: true }).click(); await visible(main().locator('pre')); await main().getByRole('button', { name: 'Tradução em português', exact: true }).click(); await visible(main().getByText('O documento já está em português. Consulte o original.', { exact: true })); await main().getByRole('button', { name: 'Calcular orçamento de IA', exact: true }).click(); await visible(main().getByText(unavailable, { exact: true })); await main().locator('input[type=file]').setInputFiles({ name: 'recorte-canonico-qa.txt', mimeType: 'text/plain', buffer: Buffer.from(doc.body_md) }); await main().getByRole('button', { name: 'Salvar na biblioteca', exact: true }).click(); await visible(main().getByText(unavailable, { exact: true })); row.actions.push('abrir recorte TXT privado fixture, alternar leitura, 503 orçamento e upload'); row.limitations.push('Não chama analisar/incorporar; acesso AI concedido apenas na fixture.'); });
    await test('/favoritos', 'favoritos', async row => { await visible(main().getByText(doc.title, { exact: true })); const search = main().getByRole('searchbox', { name: 'Buscar nos favoritos', exact: true }); await search.fill(doc.title); await visible(main().getByText(doc.title, { exact: true })); failPath = /^\/api\/favorites\/by-id\//; await main().getByRole('button', { name: /Remover/ }).first().click(); await visible(main().getByText(/Ele continua salvo/)); failPath = null; await main().getByRole('button', { name: /Remover/ }).first().click(); await page.waitForTimeout(100); await check(main().getByText(doc.title, { exact: true }).count().then(n => n === 0), 'Favorito removido ainda visível'); row.actions.push('localizar favorito criado nesta sessão; 503 preserva item; repetir remoção'); });
    await test('/exportar', 'exportacao', async row => { await main().getByRole('button', { name: 'Adicionar', exact: true }).first().click(); await main().getByRole('button', { name: 'Adicionar', exact: true }).first().click(); await main().getByRole('button', { name: 'Mover para cima', exact: true }).nth(1).click(); const download = main().getByRole('button', { name: /Gerar e baixar/ }).first(); await download.click(); await visible(main().getByText(unavailable, { exact: true })); await check(main().getByRole('button', { name: 'Remover', exact: true }).count().then(n => n === 2), '503 apagou seleção exportação'); await main().getByRole('button', { name: 'Remover', exact: true }).first().click(); row.actions.push('adicionar dois conteúdos, ordenar, 503 exportação preserva composição, remover item'); row.limitations.push('Não gera arquivos nem envia e-mail; servidor exportador não certificado.'); });
    // Targeted failures of loaded collections, not a second empty-route sweep.
    for (const [route, endpoint, label] of [['/biblioteca', '/api/library/documents', 'biblioteca-503'], ['/estudos', '/api/studies', 'estudos-503']]) await test(route, label, async row => { failPath = endpoint; await page.reload({ waitUntil: 'domcontentloaded' }); await page.waitForTimeout(700); row.actions.push('interromper lista com 503 após dados disponíveis'); await visible(main().getByText(unavailable, { exact: true })); row.checks.push('erro explícito em vez de spinner sem fim'); failPath = null; await main().getByRole('button', { name: route === '/biblioteca' ? 'Tentar carregar documentos novamente' : 'Tentar carregar estudos novamente', exact: true }).click(); await visible(main().locator(`a[href="${route === '/biblioteca' ? `/biblioteca/${doc.slug}` : `/estudos/${study.slug}`}"]`)); row.actions.push('retry recupera lista canônica sem reload'); });
    for (const [route, endpoint, label, retry] of [['/biblioteca', '/api/library/catalog', 'biblioteca-colecoes-503', 'Tentar carregar as coleções novamente'], ['/estudos', '/api/studies/types', 'estudos-filtros-503', 'Tentar carregar filtros novamente']]) await test(route, label, async row => { failPath = endpoint; await page.reload({ waitUntil: 'domcontentloaded' }); await visible(main().getByText(unavailable, { exact: true })); failPath = null; await main().getByRole('button', { name: retry, exact: true }).click(); await main().getByText(unavailable, { exact: true }).waitFor({ state: 'hidden' }); row.actions.push('503 em metadados, erro explícito, retry sem apagar lista disponível'); });
    for (const [route, endpoint, label] of [['/biblioteca', '/api/library/documents', 'biblioteca-paginacao'], ['/estudos', '/api/studies', 'estudos-paginacao']]) await test(route, label, async row => {
      paginationPath = endpoint; failNextPage = true; await page.reload({ waitUntil: 'domcontentloaded' });
      const first = route === '/biblioteca' ? doc : study, second = route === '/biblioteca' ? flux : studies[1];
      await visible(main().locator(`a[href="${route}/${first.slug}"]`));
      await main().getByRole('button', { name: route === '/biblioteca' ? 'Carregar mais documentos' : /Carregar mais ·/, exact: route === '/biblioteca' }).click();
      await visible(main().getByText(unavailable, { exact: true })); await visible(main().locator(`a[href="${route}/${first.slug}"]`));
      failNextPage = false; await main().getByRole('button', { name: route === '/biblioteca' ? 'Tentar carregar documentos novamente' : 'Tentar carregar estudos novamente', exact: true }).click();
      await visible(main().locator(`a[href="${route}/${second.slug}"]`)); row.actions.push('primeira página real de fixture, 503 em próxima página preserva primeira, retry mantém cursor e acrescenta segunda sem duplicar');
    });
  }
} finally {
  await browser.close();
  fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify({ rows, provenance, blocked, pageErrors, limitations: ['Fixtures locais com conteúdo existente; não certificam backend, corpus ou publicação.', 'Nenhuma rede externa, autenticação real, análise IA, geração de arquivo ou envio.'] }, null, 2));
}
console.log(`Report: ${out}/report.json; ${rows.length} rows; ${rows.filter(row => row.issues.length).length} rows with issues.`);
const prior = (process.env.ATELIER_SCIENCE_QA_PRIOR || '').split(',').filter(Boolean).flatMap(file => JSON.parse(fs.readFileSync(file, 'utf8')).rows.map(row => ({ ...row, report: file })));
const consolidated = [...new Map([...prior, ...rows.map(row => ({ ...row, report: path.join(out, 'report.json') }))].map(row => [`${row.route}|${row.width}|${row.name}`, row])).values()];
const coverage = inventory.map(item => {
  const pattern = new RegExp(`^${item.route.replace(':slug', '[^/]+')}$`);
  const matches = consolidated.filter(row => pattern.test(row.route) && (!item.route.includes(':slug') || !inventory.some(staticRoute => !staticRoute.route.includes(':') && staticRoute.route === row.route)));
  return { ...item, status: matches.length ? matches.some(row => row.issues.length || row.pageErrors.length) ? 'issue-recorded' : 'fixture-ui-tested' : 'not-tested', widths: [...new Set(matches.map(row => row.width))], actions: [...new Set(matches.flatMap(row => row.actions))], limitations: [...new Set(matches.flatMap(row => row.limitations))], evidence: matches.map(row => ({ name: row.name, report: row.report, screenshot: row.screenshot, issues: row.issues })) };
});
fs.writeFileSync(path.join(out, 'consolidated.json'), JSON.stringify({ coverage, rows: consolidated, provenance, limitations: ['Não constitui full CI nem certificação backend/corpus/publicação.', 'Conteúdo clínico reutilizado sem alterar. Recorte de fixture não representa tamanho/disponibilidade do acervo.', 'PDF/PPTX/DOCX, e-mail, assinatura, grafo e análise IA não executados; falhas503 não são falhas de produção.'] }, null, 2));
process.exitCode = rows.some(row => row.issues.length || row.pageErrors.length) ? 1 : 0;
