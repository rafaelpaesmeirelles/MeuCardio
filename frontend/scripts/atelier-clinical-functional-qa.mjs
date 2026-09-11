import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';

// Isolated UI behavior, NOT backend/clinical/AI certification. No real account,
// patient, writes, paid service or external network is ever contacted.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const base = new URL(process.env.ATELIER_QA_URL || 'http://127.0.0.1:4322');
assert(['http:', 'https:'].includes(base.protocol) && ['localhost', '127.0.0.1'].includes(base.hostname) && !base.username && !base.password);
const output = path.resolve(process.env.ATELIER_QA_OUT || '/tmp/corvia-clinical-functional-qa');
assert(output.startsWith('/tmp/'));
fs.mkdirSync(output, { recursive: true });
assert(/^\/(private\/)?tmp\//.test(fs.realpathSync(output)));
const sources = [];
function source(relative) {
  const text = fs.readFileSync(path.join(root, relative), 'utf8');
  sources.push({ path: relative, sha256: createHash('sha256').update(text).digest('hex') });
  return text;
}
function reviewed(relative, count) {
  const values = JSON.parse(source(relative));
  assert(Array.isArray(values));
  return values.filter(item => item.review_status === 'revisado').slice(0, count);
}
const diseases = reviewed('doencas/metadados.json', 12);
const fa = JSON.parse(source('doencas/metadados.json')).find(item => item.slug === 'fibrilacao-atrial' && item.review_status === 'revisado');
assert(fa); if (!diseases.some(item => item.slug === fa.slug)) diseases.unshift(fa);
const drugs = reviewed('medicamentos/metadados.json', 28);
const kairosSnapshot = JSON.parse(source('backend/app/data/pricing/kairos-453-2026-08.json'));
const kairosRecord = kairosSnapshot.records.find(record => record.product === 'ALDACTONE');
assert(kairosRecord);
const kairosOptions = kairosRecord.presentations.map(item => {
  const prices = Object.fromEntries(Object.entries(item).filter(([key]) => key.startsWith('pmc')).map(([key, value]) => [key.slice(3), Number(value.replace(',', '.'))]));
  return { produto: kairosRecord.product, laboratorio: kairosRecord.laboratory, apresentacao: item.presentation,
    preco_minimo: Math.min(...Object.values(prices)), preco_maximo: Math.max(...Object.values(prices)), precos_por_icms: prices, pagina_fonte: kairosRecord.page };
});
const kairosFixture = { fonte: 'K@iros', tipo_fonte: 'inteligencia_de_mercado', edicao: kairosSnapshot.issue, competencia: kairosSnapshot.competence, opcoes: kairosOptions };
const brl = value => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
const kairosMinimum = brl(kairosOptions[0].preco_minimo);
const exams = reviewed('exames/metadados.json', 20);
const checklists = reviewed('checklists/metadados.json', 28);
const triages = reviewed('triagem-sintomas/metadados.json', 8);
const protocols = reviewed('emergencia/metadados.json', 2);
const contentPaths = fs.readdirSync(path.join(root, 'content'), { recursive: true }).filter(name => name.endsWith('.md'));
const documents = protocols.map(item => {
  const relative = contentPaths.find(name => name.endsWith(`/${item.documento_slug}.md`) || name === `${item.documento_slug}.md`);
  assert(relative, `Canonical emergency document missing: ${item.documento_slug}`);
  const raw = source(`content/${relative}`);
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  assert(match && /^review_status:\s*["']?revisado["']?\s*$/m.test(match[1]));
  const scalar = key => { const value = match[1].match(new RegExp(`^${key}: (.+)$`, 'm'))?.[1]; return value?.startsWith('"') ? JSON.parse(value) : value; };
  const refs = match[1].match(/^source_refs: (\[.*\])$/m)?.[1];
  return { slug: item.documento_slug, title: scalar('title'), theme: scalar('theme'), kind: scalar('kind'), body_md: match[2], review_status: 'revisado', source_tier: scalar('source_tier') || '', gaps: [], source_refs: refs ? JSON.parse(refs) : [] };
});

// Execute only the pure established demo function and the calculator registry
// before its first application import. No app package/settings/DB are imported.
source('backend/app/services/investidor_demo.py');
source('backend/app/services/calculators.py');
source('backend/app/services/ia/cardiovascular_exam_assist.py');
source('backend/app/api/cardiovascular_exam_ai.py');
source('backend/app/api/checklists.py');
source('backend/tests/test_checklist_application_response.py');
const pure = String.raw`
import ast, json, pathlib, runpy, sys, types
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dataclasses import asdict
root = pathlib.Path(sys.argv[1])
tree = ast.parse((root/'backend/app/services/investidor_demo.py').read_text())
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_agenda_demo')
assert not any(isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.Name) and n.id in {'open','eval','exec','__import__'} for n in ast.walk(fn))
ns = dict(datetime=datetime,timedelta=timedelta,ZoneInfo=ZoneInfo)
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<pure-demo>','exec'),ns)
endpoints = ['appointments','locations','services','integrations','capabilities','mobility/preferences','work-routines','work-routines/occurrences','commitment-series','commitments','google-teste/status']
agenda = {'/api/agenda/'+p:ns['_agenda_demo']('/api/agenda/'+p) for p in endpoints}
calc_tree = ast.parse((root/'backend/app/services/calculators.py').read_text())
nodes=[]
for n in calc_tree.body:
    if isinstance(n,ast.ImportFrom) and n.level: break
    if isinstance(n,ast.ImportFrom): assert n.module in {'dataclasses','typing'}
    assert not isinstance(n,ast.Import)
    nodes.append(n)
module=types.ModuleType('isolated_calculator_catalog');sys.modules[module.__name__]=module
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<pure-calculator-catalog>','exec'),module.__dict__)
catalog=[]
for c in module.REGISTRY.values():
    item=asdict(c);item.pop('compute',None);item.pop('interpret',None);catalog.append(item)
def literal(n):
    if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Mult):return literal(n.left)*literal(n.right)
    return ast.literal_eval(n)
constants={}
for relative in ['backend/app/services/ia/cardiovascular_exam_assist.py','backend/app/api/cardiovascular_exam_ai.py']:
    for n in ast.parse((root/relative).read_text()).body:
        if isinstance(n,ast.Assign):
            for t in n.targets:
                if isinstance(t,ast.Name) and t.id in {'EXAM_TYPES','SUPPORTED_MEDIA_TYPES','MAX_FILES','MAX_FILE_BYTES','MAX_TOTAL_BYTES','CONSENT_VERSION'}:constants[t.id]=literal(n.value)
# Exercise the actual endpoint response, not a hand-corrected frontend shape.
# This helper imports stdlib only; no DB, app settings, conftest or pytest.
contract = runpy.run_path(str(root/'backend/tests/test_checklist_application_response.py'))
model = next(item for item in json.loads((root/'checklists/metadados.json').read_text())
             if item['slug']=='alta-pos-fibrilacao-atrial' and item['review_status']=='revisado')
applications = []
for count in (0,1):
    checklist = types.SimpleNamespace(**{'scope_type':'doenca',**model,'id':-942})
    run = types.SimpleNamespace(id=-940-count,user_id=-990091,checklist_id=checklist.id,
        identificacao_livre='APLICAÇÃO FICTÍCIA — QA local; não representa uma alta real',
        itens_no_momento=model['itens'],marcados=[item['id'] for item in model['itens'][:count]],
        observacoes='DEMONSTRAÇÃO DE INTERFACE — sem dados clínicos',finalizado_em=None)
    response, _, _ = contract['application_response'](run,checklist,run.user_id)
    applications.append(response)
print(json.dumps(dict(agenda=agenda,calculators=catalog,constants=constants,applications=applications),ensure_ascii=False))
`;
const canonical = JSON.parse(execFileSync(process.env.PYTHON_BIN || 'python3', ['-B', '-c', pure, root], { encoding: 'utf8' }));
const profile = { id: -990091, email: 'demonstracao@corvia.example.invalid', full_name: 'Demonstração CorVIA — QA fictícia', role: 'admin', profession: 'Medica', professional_title: '', council_name: null, council_number: null, council_state: null, photo_url: null, product_access: true, investidor: false, profile_completion_required: false, kyc_required: false, onboarding_pendente: false, boas_vindas_pendente: false };
const patients = [1, 2].map(index => ({ id: -900 - index, full_name: `Paciente demonstrativo ${index}`, birth_date: null, sex: null, phone: null, cpf: null, email: null }));
const appointment = canonical.agenda['/api/agenda/appointments'].find(item => item.patient_name === 'Paciente demonstrativo');
assert(appointment);
const flow = { appointment_id: appointment.id, scheduled_at: appointment.starts_at, patient_name: appointment.patient_name, patient_profile_id: patients[0].id, state: 'scheduled', arrived_at: null, encounter_id: null };
const roundPatient = { id: -910, record_number: 'DEMONSTRACAO-001', initials: 'DEMO', bed: 'DEMO', unit: 'Unidade demonstrativa', archived: false, archived_at: null, archive_reason: null, plan: null, pending: [], medications: [], problems: [], labs: {}, diagnostic_hypothesis: [], chief_complaint: null, anamnesis: null, physical_exam: null, cardiac_exam: {}, vital_signs: {}, imaging: null };
const entitlement = { status: 'inativo', current_period_end: null, plano: null, periodicidade: null, acesso_administrativo: true, portal_available: false, change_plan_available: false, entitlements: { tudo_com_tudo: true, ai: true, mail: true, source: 'administrative', commercial_version: null } };
const aiStatus = { enabled: false, unavailable_reason: 'ai_disabled', exam_types: canonical.constants.EXAM_TYPES, supported_media_types: canonical.constants.SUPPORTED_MEDIA_TYPES, max_files: canonical.constants.MAX_FILES, max_file_bytes: canonical.constants.MAX_FILE_BYTES, max_total_bytes: canonical.constants.MAX_TOTAL_BYTES, consent_version: canonical.constants.CONSENT_VERSION, persists_files_in_corvia: false, provider_response_storage_requested: false, external_processor: 'openai', searches_current_guidelines: true, raw_dicom_supported: false, video_supported: false };
const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
function pageOf(items, url) {
  const q = normalize(url.searchParams.get('q'));
  const filtered = items.filter(item => (!q || normalize(JSON.stringify(item)).includes(q)) && ['theme', 'category', 'area'].every(key => !url.searchParams.get(key) || item[key] === url.searchParams.get(key)));
  const limit = Number(url.searchParams.get('limit') || url.searchParams.get('page_size')) || 200;
  const page = Number(url.searchParams.get('page')) || 1;
  const offset = Number(url.searchParams.get('offset')) || (page - 1) * limit;
  return { items: filtered.slice(offset, offset + limit), total: filtered.length, limit, page, page_size: limit, offset, has_more: offset + limit < filtered.length, next_offset: offset + limit < filtered.length ? offset + limit : null };
}
const report = { kind: 'isolated-real-React-UI-functional', sourceRoot: root, base: base.origin, startedAt: new Date().toISOString(), sources, cases: [], requests: [], externalBlocked: [], pageErrors: [], residual: [], noRealServices: true };
let active = null;
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs');
const browser = await chromium.launch({ headless: true, channel: 'chrome', args: ['--disable-gpu'] });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'pt-BR', timezoneId: 'America/Sao_Paulo', serviceWorkers: 'block', reducedMotion: 'reduce' });
await context.route('**/*', async route => {
  const request = route.request(), url = new URL(request.url()), method = request.method();
  if (!url.pathname.startsWith('/api/')) {
    if (url.origin === base.origin && ['GET', 'HEAD'].includes(method)) return route.continue();
    report.externalBlocked.push({ case: active?.name, path: url.pathname, method }); return route.abort('blockedbyclient');
  }
  const record = { case: active?.name, path: url.pathname, method }; report.requests.push(record);
  const fulfill = (value, status = 200, provenance = 'isolated-contract-fixture') => { Object.assign(record, { status, provenance }); return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(value) }); };
  if (active?.fault && active.fault === url.pathname) return fulfill({ detail: 'Indisponibilidade 503 controlada pela QA fictícia.' }, 503, 'injected-error-recovery-test');
  if (active?.pricing && url.pathname === '/api/receituario/classificar' && method === 'POST') return fulfill({ versao_listas: 'QA-sem-validade-clinica', exige_revisao: true, documentos: [{ tipo: 'QA', tipo_nome: 'Classificação demonstrativa — conferência de legibilidade sem validade clínica', tipo_ativo: false, itens: [], pendencias: [] }], recusados: [] }, 200, 'UI-state-only-NOT-clinical-classification');
  if (method === 'POST' && url.pathname === '/api/auth/sessao') return fulfill({ ok: true });
  if (method !== 'GET') return fulfill({ detail: 'Escrita bloqueada na QA fictícia isolada; nada foi enviado.' }, 403, 'blocked-write');
  const p = url.pathname;
  if (active?.pricing && p === '/api/drugs/sugestoes') {
    if (normalize(url.searchParams.get('q')).includes('amiodarona')) return fulfill([{ slug: 'amiodarona', generic_name: 'Amiodarona', brand_name: null, manufacturer: null, source: 'corvia', tem_conteudo_clinico: true }]);
    if (!normalize(url.searchParams.get('q')).includes('aldactone')) return fulfill([]);
    const generic = { slug: 'espironolactona', generic_name: 'Espironolactona', brand_name: 'Aldactone', manufacturer: kairosRecord.laboratory, source: 'corvia', tem_conteudo_clinico: true };
    return fulfill([generic, { ...generic, brand_name: kairosRecord.product, apresentacao: kairosOptions[0].apresentacao, source: 'K@iros', price_source: 'kairos', preco: { valor: null, rotulo: kairosMinimum }, price_min: kairosOptions[0].preco_minimo, price_max: kairosOptions[0].preco_maximo, price_reference: `edição ${kairosSnapshot.issue} · competência ${kairosSnapshot.competence}`, source_page: kairosRecord.page }], 200, 'literal-licensed-local-Kairos-snapshot-UI-fixture');
  }
  if (active?.pricing && p === '/api/drugs/espironolactona/apresentacoes') {
    if (active.priceLookupFault) return fulfill({ detail: 'Falha controlada de consulta de preços.' }, 503);
    if (active.holdPriceLookup) return new Promise(resolve => {
      active.releasePriceLookup = async () => { await fulfill({ uf: null, cmed_publicado_em: null, apresentacoes: [], aviso: null, kairos: kairosFixture }, 200, 'deliberately-delayed-old-presentation'); resolve(); };
    });
    return fulfill({ uf: null, cmed_publicado_em: null, apresentacoes: [], aviso: null, kairos: kairosFixture }, 200, 'literal-licensed-local-Kairos-snapshot-UI-fixture');
  }
  if (active?.pricing && p === '/api/drugs/amiodarona/apresentacoes') return fulfill({ uf: null, cmed_publicado_em: null, apresentacoes: [], aviso: 'SEM PREÇO NESTA FIXTURE DE CORRIDA — não representa cobertura real', kairos: { ...kairosFixture, opcoes: [] } });
  if (p === '/api/auth/session-status') return fulfill({ authenticated: true });
  if (p === '/api/auth/me') return fulfill(profile);
  if (p === '/api/version') return fulfill({ commit: 'isolated-functional-qa' });
  if (p === '/api/billing/status') return fulfill(entitlement);
  if (p === '/api/ai/status') return fulfill({ ativo: true, provedor: 'offline-qa-fixture', modelo: 'none', modelos_disponiveis: [], limite_diario: 0, usado_hoje: 0, restante_hoje: 0, ferramentas_disponiveis_instalacao: false, ferramentas_consentidas: false }, 200, 'consent-UI-state-only-no-AI-service');
  if (p === '/api/ai/conversas') return fulfill([]);
  if (p === '/api/heart-team/cases' || p === '/api/heart-team/cases/-930') {
    const draft = { id: -930, status: 'draft', question: 'DEMONSTRAÇÃO DE INTERFACE — sem resultados de IA', case_data: {}, created_at: '2026-09-11T12:00:00Z', result: null, consensus: null };
    return fulfill(p.endsWith('/-930') ? draft : [draft], 200, 'synthetic-unsent-draft-no-AI-result');
  }
  if (p === '/api/heart-team/agents') return fulfill([], 200, 'use-existing-frontend-canonical-agent-labels');
  if (p === '/api/prescricao-especial/capacidades') return fulfill({ enabled: true, allows_self: true, rafael_signer: false });
  if (p === '/api/prescricao-especial/minhas') return fulfill([]);
  if (p === '/api/exames-ia/status') return fulfill(aiStatus);
  if (Object.hasOwn(canonical.agenda, p)) return fulfill(canonical.agenda[p], 200, 'canonical-pure-investidor-demo');
  if (p === '/api/pacientes') return fulfill(patients.filter(item => normalize(item.full_name).includes(normalize(url.searchParams.get('busca')))));
  if (p === '/api/agenda-clinica/hoje') return fulfill([flow]);
  if (/^\/api\/pacientes\/-90[12]$/.test(p)) return fulfill(patients.find(item => p.endsWith(String(item.id))));
  if (/^\/api\/pacientes\/-90[12]\/(atendimentos|resumo-clinico|ecgs|exames-multimodais|resultados|linha-do-tempo)$/.test(p)) return fulfill([]);
  if (/^\/api\/pacientes\/-90[12]\/ecgs\/ia-status$/.test(p)) return fulfill({ enabled: false, supported_media_types: [] });
  if (/^\/api\/pacientes\/-90[12]\/exames-multimodais\/status$/.test(p)) return fulfill({ enabled: false, exam_types: aiStatus.exam_types, supported_media_types: [] });
  if (p === '/api/round/patients') return fulfill(url.searchParams.get('archived') ? [] : [roundPatient]);
  if (/^\/api\/round\/patients\/-910\/(ai-assist|prescriptions|documents|timeline)$/.test(p)) return fulfill([]);
  if (p === '/api/specialty-guides/diseases') return fulfill(pageOf(diseases, url), 200, 'reviewed-canonical-subset');
  if (p === '/api/specialty-guides/disease-facets') return fulfill({ areas: [...new Set(diseases.map(item => item.area))].map(id => ({ id, count: diseases.filter(item => item.area === id).length })), clinical_domains: [], categories: [] });
  if (p.startsWith('/api/specialty-guides/diseases/')) { const item = diseases.find(item => item.slug === p.split('/').at(-1)); if (item) return fulfill(item, 200, 'reviewed-canonical-item'); }
  if (p === '/api/specialty-guides/triage') return fulfill(triages, 200, 'reviewed-canonical-subset');
  if (p.startsWith('/api/specialty-guides/triage/')) { const item = triages.find(item => item.slug === p.split('/').at(-1)); if (item) return fulfill(item, 200, 'reviewed-canonical-item'); }
  if (p === '/api/drugs') return fulfill(pageOf(drugs, url), 200, 'reviewed-canonical-subset');
  if (p === '/api/drugs/sugestoes') return fulfill(pageOf(drugs, url).items.map(item => ({ slug: item.slug, generic_name: item.generic_name, brand_name: null, manufacturer: null, source: 'corvia', tem_conteudo_clinico: true })), 200, 'canonical-generics-only-no-commercial-price');
  if (p === '/api/lab-tests') return fulfill(pageOf(exams, url), 200, 'reviewed-canonical-subset');
  if (p === '/api/lab-tests/taxonomy') return fulfill([...new Set(exams.map(item => item.category))].map(category => ({ category, count: exams.filter(item => item.category === category).length, subtypes: [...new Set(exams.filter(item => item.category === category).map(item => item.theme))].map(theme => ({ theme, count: exams.filter(item => item.category === category && item.theme === theme).length })) })));
  if (p.startsWith('/api/lab-tests/')) { const item = exams.find(item => item.slug === p.split('/').at(-1)); if (item) return fulfill(item, 200, 'reviewed-canonical-item'); }
  if (p === '/api/calculators') return fulfill(canonical.calculators, 200, 'canonical-pure-calculator-catalog-subset');
  if (p.startsWith('/api/calculators/')) { const item = canonical.calculators.find(item => item.slug === p.split('/').at(-1)); if (item) return fulfill(item, 200, 'canonical-pure-calculator-definition'); }
  if (p === '/api/checklists') return fulfill(pageOf(checklists, url), 200, 'reviewed-canonical-subset');
  if (p === '/api/checklists/aplicacoes/minhas') return fulfill([]);
  if (/^\/api\/checklists\/aplicacoes\/-94[01]$/.test(p)) return fulfill(canonical.applications.find(item => p.endsWith(String(item.id))), 200, 'real-endpoint-response-over-synthetic-application-reviewed-canonical-snapshot');
  if (p.startsWith('/api/checklists/')) { const item = checklists.find(item => item.slug === p.split('/').at(-1)); if (item) return fulfill(item, 200, 'reviewed-canonical-item'); }
  if (p === '/api/emergencia') return fulfill({ protocolos: protocols, documentos: Object.fromEntries(documents.map(item => [item.slug, item])) }, 200, 'reviewed-canonical-protocols-and-full-documents');
  if (p === '/api/library/documents') return fulfill(pageOf(documents, url), 200, 'reviewed-canonical-subset');
  if (p === '/api/assinatura/provedores' || p === '/api/receituario/tipos') return fulfill([]);
  if (p === '/api/receituario' || p === '/api/document-templates/gerados') return fulfill(pageOf([], url));
  if (p === '/api/document-templates') return fulfill([{ id: -920, title: 'Modelo demonstrativo — sem validade clínica', doc_type: 'outro', body: 'DEMONSTRAÇÃO DE INTERFACE. Documento sem validade clínica. Paciente: {{nome}}.' }]);
  if (p === '/api/document-templates/exames-sugeridos') return fulfill({ 'Recorte canônico': exams.slice(0, 3).map(item => item.name) });
  if (p === '/api/favorites/status') return fulfill({ favorited: false, available: true });
  if (p === '/api/clinical-change-approvals/count') return fulfill({ pending: 0 });
  return fulfill({ detail: 'Dependência não modelada nesta QA isolada.' }, 503, 'unmodelled-dependency');
});
const page = await context.newPage();
page.setDefaultTimeout(9000); page.setDefaultNavigationTimeout(45000);
page.on('pageerror', error => report.pageErrors.push({ case: active?.name, message: String(error) }));
page.on('dialog', dialog => { active?.actions.push({ name: `dismiss native ${dialog.type()}`, status: 'pass' }); void dialog.dismiss(); });
async function settle() { await page.waitForLoadState('networkidle', { timeout: 12000 }).catch(() => {}); await page.evaluate(() => document.fonts.ready); }
async function action(name, fn) { await fn(); active.actions.push({ name, status: 'pass' }); }
async function fill(locator, value) { await locator.click(); await locator.fill(value); assert.equal(await locator.inputValue(), value); }
async function metrics() {
  return page.evaluate(() => {
    const visible = element => { const b = element.getBoundingClientRect(), s = getComputedStyle(element); return b.width > 0 && b.height > 0 && s.display !== 'none' && s.visibility !== 'hidden'; };
    const main = document.querySelector('#conteudo-principal') || document.body;
    return { width: innerWidth, scrollWidth: document.documentElement.scrollWidth, overflow: document.documentElement.scrollWidth > innerWidth + 2,
      headings: [...main.querySelectorAll('h1,h2,h3')].filter(visible).slice(0, 14).map(e => e.textContent.trim()),
      smallControls: [...main.querySelectorAll('input:not([type=checkbox]):not([type=radio]),select,textarea,button')].filter(visible).map(e => { const b = e.getBoundingClientRect(), s = getComputedStyle(e); return { text: (e.getAttribute('aria-label') || e.textContent || e.getAttribute('placeholder') || '').trim().slice(0, 80), font: parseFloat(s.fontSize), height: b.height, width: b.width }; }).filter(e => e.font < 14 || e.height < 40).slice(0, 25),
      overflowElements: [...main.querySelectorAll('*')].filter(visible).filter(e => { const b = e.getBoundingClientRect(); return b.right > innerWidth + 2 && b.width > 0; }).slice(0, 8).map(e => ({ tag: e.tagName, class: typeof e.className === 'string' ? e.className : '', text: e.textContent.trim().slice(0, 60) })) };
  });
}
async function textContrast(locator, pseudo = null) {
  return locator.evaluateAll((elements, pseudo) => elements.filter(element => {
    const box = element.getBoundingClientRect(), style = getComputedStyle(element);
    return box.width > 0 && box.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
  }).map(element => {
    const rgba = value => { const numbers = value.match(/[\d.]+/g)?.map(Number) || []; return [numbers[0], numbers[1], numbers[2], numbers[3] ?? 1]; };
    const layers = [];
    for (let ancestor = element; ancestor; ancestor = ancestor.parentElement) {
      const s = getComputedStyle(ancestor), color = rgba(s.backgroundColor);
      layers.push({ class: ancestor.className, color: s.backgroundColor, image: s.backgroundImage });
      if (color[3] === 1) break;
    }
    const blend = (top, bottom) => top.slice(0, 3).map((value, index) => value * top[3] + bottom[index] * (1 - top[3]));
    const background = [...layers].reverse().reduce((acc, layer) => blend(rgba(layer.color), acc), [255, 255, 255]);
    const style = getComputedStyle(element, pseudo), textFillColor = style.webkitTextFillColor || style.color;
    const effectiveFill = rgba(textFillColor); effectiveFill[3] *= Number(style.opacity);
    const foreground = blend(effectiveFill, background);
    const luminance = rgb => rgb.map(value => value / 255).map(value => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4).reduce((sum, value, index) => sum + value * [0.2126, 0.7152, 0.0722][index], 0);
    const a = luminance(foreground), b = luminance(background);
    const box = element.getBoundingClientRect();
    return { class: element.className, tag: element.tagName, text: (pseudo ? element.getAttribute('placeholder') || '' : element.textContent).trim().slice(0, 90), placeholder: element.getAttribute('placeholder'), fontSize: parseFloat(style.fontSize), height: box.height, color: style.color, textFillColor, textShadow: style.textShadow, caretColor: style.caretColor, background, contrast: (Math.max(a,b)+0.05)/(Math.min(a,b)+0.05), layers, measurable: layers.every(layer => layer.image === 'none') };
  }), pseudo);
}
const cases = [
  { route: '/agenda', ready: '.agenda-calendario', async run() {
    await action('Read real demo appointment and open/cancel scheduling', async () => {
      await page.getByRole('button', { name: 'Novo atendimento', exact: true }).click();
      const dialog = page.getByRole('dialog', { name: 'Agendar paciente' }); await dialog.waitFor();
      assert(await dialog.getByRole('button', { name: 'Confirmar agendamento' }).isDisabled());
      await fill(dialog.locator('input').first(), 'Paciente demonstrativo — não salvar');
      await dialog.getByRole('button', { name: 'Cancelar', exact: true }).click(); assert.equal(await page.getByRole('dialog').count(), 0);
    });
    await action('Open personal commitment, fill title and cancel', async () => {
      await page.getByRole('button', { name: 'Compromisso pessoal', exact: true }).click(); const dialog = page.getByRole('dialog', { name: 'Novo compromisso' });
      assert(await dialog.getByRole('button', { name: 'Criar compromisso', exact: true }).isDisabled());
      await fill(dialog.locator('input').first(), 'Compromisso demonstrativo — não salvar'); await dialog.getByRole('button', { name: 'Cancelar', exact: true }).click();
    });
    await action('Open settings, inspect saved fictitious locations and close', async () => { await page.getByRole('button', { name: 'Configurar', exact: true }).click(); const dialog = page.getByRole('dialog', { name: 'Configurar agenda' }); await dialog.getByPlaceholder('Nome do local (ex.: Hotel)').fill('Local demonstrativo — não salvar'); await dialog.getByRole('button', { name: 'Concluir configuração' }).click(); });
  } },
  { route: '/prontuario', ready: '.pep-patient', async run() {
    await action('Filter synthetic patients, select second and open/close unsaved encounter', async () => {
      await fill(page.getByRole('textbox', { name: 'Buscar paciente', exact: true }), 'demonstrativo 2');
      await page.locator('.pep-list button').filter({ hasText: 'Paciente demonstrativo 2' }).click();
      assert(new URL(page.url()).searchParams.get('paciente') === '-902');
      await page.getByRole('button', { name: '+ Iniciar atendimento', exact: true }).click();
      await fill(page.getByLabel('Motivo / queixa principal'), 'DEMONSTRAÇÃO: campo de teste, sem informação clínica.');
      await page.locator('.pep-editor').getByRole('button', { name: 'Fechar', exact: true }).click();
    });
  } },
  { route: '/receituario', ready: '.prescricao__abas', async run() {
    await action('Switch prescription tabs and type/filter canonical medication', async () => {
      await page.getByRole('tab', { name: 'Histórico', exact: true }).click(); await fill(page.getByPlaceholder('Nome completo ou parte do nome'), 'Paciente demonstrativo');
      await page.getByRole('tab', { name: 'Nova receita', exact: true }).click(); await fill(page.getByPlaceholder('Digite o nome genérico ou comercial'), 'AAS');
      await page.getByRole('listbox', { name: 'Sugestões de medicamentos' }).waitFor();
    });
  } },
  { route: '/documentos', ready: 'h1', async run() {
    await action('Open blank document, type demonstration title and cancel without generating', async () => {
      await page.getByRole('button').filter({ hasText: 'Documento em branco' }).first().click();
      await fill(page.getByPlaceholder('Ex.: Declaração de comparecimento'), 'DEMONSTRAÇÃO — sem validade clínica');
      await page.getByRole('button', { name: 'Cancelar', exact: true }).last().click();
    });
  } },
  { route: '/avaliacao-preoperatoria', ready: 'h1', async run() { await action('Fill synthetic identifier/procedure; no calculation or document generated', async () => { await fill(page.getByPlaceholder('Usado só para organizar o histórico'), 'Paciente demonstrativo'); await fill(page.getByPlaceholder('Ex.: colecistectomia videolaparoscópica eletiva'), 'DEMONSTRAÇÃO — procedimento não definido'); }); } },
  { route: '/exames', ready: '.cc-exams-page', async run() { await action('Filter canonical exams and open first matching detail', async () => { await fill(page.getByRole('textbox', { name: 'Buscar exame' }), exams[0].name); await settle(); await page.locator(`a[href="/exames/${exams[0].slug}"]`).first().click(); await page.getByRole('heading', { name: exams[0].name, exact: true }).waitFor(); }); } },
  { route: '/doencas', ready: 'h1', async run() { await action('Filter FA and open reviewed canonical disease', async () => { const input = page.getByPlaceholder('Nome, sigla, sinônimo, sintoma ou tema…'); await fill(input, 'fibrilação atrial'); await settle(); await page.locator('a[href="/doencas/fibrilacao-atrial"]').first().click(); await page.getByRole('heading', { name: fa.name, exact: true }).first().waitFor(); }); } },
  { route: '/medicamentos', ready: '.cc-drugs-page', async run() { await action('Filter canonical drug name and clear filter', async () => { const input = page.locator('.cc-drugs-page input').first(); await fill(input, drugs[0].generic_name); await page.getByText(drugs[0].generic_name, { exact: true }).first().waitFor(); await input.fill(''); }); } },
  { route: '/interacoes', ready: '#cc-interaction-search', async run() { await action('Select/remove two canonical drugs and verify minimum-two control', async () => { const verify = page.getByRole('button', { name: 'Verificar combinação', exact: true }); assert(await verify.isDisabled()); await page.locator('.cc-drug-picker button').nth(0).click(); assert(await verify.isDisabled()); await page.locator('.cc-drug-picker button').nth(1).click(); assert(await verify.isEnabled()); await page.locator('.cc-selected-drugs button').first().click(); assert(await verify.isDisabled()); }); } },
  { route: '/calculadoras', ready: '.cv-calculators-page', async run() { await action('Filter canonical RCRI and open its actual definition', async () => { await fill(page.locator('input[type=search]').first(), 'RCRI'); await page.locator('a[href="/calculadoras/rcri"]').first().click(); await page.getByRole('heading').filter({ hasText: 'RCRI' }).first().waitFor(); const checkbox = page.locator('input[type=checkbox]').first(); await checkbox.check(); assert(await checkbox.isChecked()); await checkbox.uncheck(); }); } },
  { route: '/condicoes', ready: 'h1', async run() { await action('Filter canonical drugs and select/deselect clinical condition UI', async () => { await fill(page.getByPlaceholder('Filtrar pelo nome…'), 'AAS'); const button = page.locator('button.painel__tema').first(); await button.click(); await button.click(); }); } },
  { route: '/exames-ia', ready: '.ceai', async run() { await action('Fill offline IA form and add/remove local synthetic text without analysis', async () => { await fill(page.getByPlaceholder('Ex.: correlacionar achados com dispneia e definir próximos passos diagnósticos.'), 'DEMONSTRAÇÃO DE INTERFACE — não analisar.'); await page.locator('input[type=file]').first().setInputFiles({ name: 'demonstracao-sem-dados.txt', mimeType: 'text/plain', buffer: Buffer.from('DEMONSTRAÇÃO DE INTERFACE. Sem dados clínicos ou identificadores.') }); await page.getByRole('button', { name: /Remover arquivo 1/ }).click(); assert.equal(await page.locator('.ceai__file-list').count(), 0); assert((await page.locator('.ceai').innerText()).includes('desligada')); }); } },
  { route: '/round', ready: '.ccc-patient-command__manager', async run() { await action('Read synthetic Round record and dismiss archive confirmation', async () => { await page.getByText('DEMONSTRACAO-001', { exact: false }).first().waitFor(); await page.getByRole('button', { name: 'Arquivar', exact: true }).click(); assert(active.actions.some(item => item.name === 'dismiss native confirm')); await fill(page.locator('#pront'), 'DEMO-NÃO-SALVAR'); await fill(page.locator('#ini'), 'QA'); }); } },
  { route: '/emergencia', ready: '.emerg', async run() { await action('Open reviewed emergency protocol and inspect text', async () => { const choice = page.getByRole('button').filter({ hasText: protocols[0].titulo }).first(); await choice.click(); await page.getByRole('heading').filter({ hasText: protocols[0].titulo }).first().waitFor(); }); } },
  { route: '/checklists', ready: 'h1', async run() { await action('Open canonical checklist model without applying to a patient', async () => { await page.locator(`a[href="/checklists/${checklists[0].slug}"]`).first().click(); await page.getByRole('heading').filter({ hasText: checklists[0].condicao }).first().waitFor(); }); } },
  ...canonical.applications.map(application => ({ route: `/checklists/alta/${application.id}`, variant: 'applied-checklist', ready: '.checklist__contador', async run() {
    await action('Read actual endpoint response; preserve marked IDs and toggle only local state', async () => {
      assert(Array.isArray(application.marcados));
      await page.getByRole('heading', { name: application.condicao, exact: true }).waitFor();
      await page.getByText(application.identificacao, { exact: true }).waitFor();
      const boxes = page.locator('.checklist__item input[type=checkbox]');
      assert.equal(await boxes.count(), application.itens.length);
      assert.equal(await page.locator('.checklist__contador strong').innerText(), `${application.marcados.length}/${application.itens.length}`);
      const first = boxes.first(), wasChecked = application.marcados.includes(application.itens[0].id);
      assert.equal(await first.isChecked(), wasChecked);
      await first.setChecked(!wasChecked);
      assert.equal(await page.locator('.checklist__contador strong').innerText(), `${application.marcados.length + (wasChecked ? -1 : 1)}/${application.itens.length}`);
      await first.setChecked(wasChecked);
      await fill(page.locator('.checklist__obs'), 'DEMONSTRAÇÃO — observação local não enviada.');
      assert(await page.getByRole('button', { name: 'Salvar', exact: true }).isEnabled());
      assert(await page.getByRole('button', { name: 'Finalizar alta', exact: true }).isEnabled());
      assert.equal(await page.getByRole('link', { name: 'Ver o protocolo de origem' }).getAttribute('href'), `/biblioteca/${application.documento_origem}`);
      for (const item of await page.locator('.checklist__item').all()) await item.scrollIntoViewIfNeeded();
      await page.getByRole('heading', { name: application.condicao, exact: true }).scrollIntoViewIfNeeded();
    });
    if (application.marcados.length) await action('GET 503 is visible; existing reload recovery restores the saved snapshot', async () => {
      active.fault = `/api/checklists/aplicacoes/${application.id}`;
      await page.reload(); await settle();
      await page.locator('p.erro').filter({ hasText: 'Indisponibilidade 503 controlada' }).waitFor();
      assert.equal(await page.locator('.checklist__contador').count(), 0);
      active.failureRecovery = { mode: 'normal-page-reload', inlineRetryAvailable: (await page.getByRole('button', { name: /Tentar novamente/i }).count()) > 0 };
      active.errorScreenshot = path.join(output, `${active.name.replaceAll('/', '-')}-503.png`);
      await page.screenshot({ path: active.errorScreenshot, fullPage: false });
      active.fault = null; await page.reload(); await settle();
      await page.locator('.checklist__contador').waitFor();
      assert(await page.locator('.checklist__item input[type=checkbox]').first().isChecked());
      assert.equal(await page.locator('.checklist__obs').inputValue(), application.observacoes);
    });
    assert.equal(report.requests.filter(request => request.case === active.name && request.path.startsWith('/api/checklists/') && request.method !== 'GET').length, 0);
  } })),
  { route: '/receituario', variant: 'prescription-item-label', ready: '.prescricao-item__topo > span', async run() {
    await action('Measure ITEM 01 computed font and composite surface contrast', async () => {
      const label = page.locator('.prescricao-item__topo > span').first(); await label.scrollIntoViewIfNeeded();
      active.itemLabel = await label.evaluate(element => {
        const rgba = value => { const numbers = value.match(/[\d.]+/g)?.map(Number) || []; return [numbers[0], numbers[1], numbers[2], numbers[3] ?? 1]; };
        const layers = [];
        for (let ancestor = element; ancestor; ancestor = ancestor.parentElement) {
          const s = getComputedStyle(ancestor), color = rgba(s.backgroundColor);
          layers.push({ class: ancestor.className, color: s.backgroundColor, image: s.backgroundImage });
          if (color[3] === 1) break;
        }
        const blend = (top, bottom) => top.slice(0, 3).map((value, index) => value * top[3] + bottom[index] * (1 - top[3]));
        const background = [...layers].reverse().reduce((acc, layer) => blend(rgba(layer.color), acc), [255, 255, 255]);
        const style = getComputedStyle(element);
        // WebKit text fill can override color even when color is !important.
        const textFillColor = style.webkitTextFillColor || style.color;
        const foreground = blend(rgba(textFillColor), background);
        const luminance = rgb => rgb.map(value => value / 255).map(value => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4).reduce((sum, value, index) => sum + value * [0.2126, 0.7152, 0.0722][index], 0);
        const a = luminance(foreground), b = luminance(background);
        return { text: element.textContent, fontSize: parseFloat(style.fontSize), color: style.color, textFillColor, background, contrast: (Math.max(a,b)+0.05)/(Math.min(a,b)+0.05), layers, measurable: layers.every(layer => layer.image === 'none') };
      });
      assert.equal(active.itemLabel.fontSize, 14); assert(active.itemLabel.measurable); assert(active.itemLabel.contrast >= 4.5);
    });
  } },
  ...['light', 'dark'].flatMap(theme => [
    { route: '/checklists/alta/-941', variant: 'applied-checklist-visual', theme, ready: '.checklist__contador', async run() {
      await action('Read effective clinical text contrast only; no form interaction', async () => {
        active.textContrast = await textContrast(page.locator('.checklist__contador, .checklist__contador > strong, .checklist__pendente, .checklist__grupo h3, .checklist__texto, .checklist__origem-item, .checklist__obrig, .checklist__nota'));
        assert(active.textContrast.length > 10);
        for (const item of active.textContrast) { assert(item.measurable, item.class); assert(item.contrast >= 4.5, `${item.class}: ${item.contrast}`); }
        const text = active.textContrast.filter(item => item.class === 'checklist__texto');
        assert(text.every(item => item.fontSize >= 16));
        await page.getByRole('heading', { name: canonical.applications[1].condicao, exact: true }).scrollIntoViewIfNeeded();
      });
    } },
    { route: '/receituario', variant: 'prescription-label-visual', theme, ready: '.prescricao-item__topo > span', async run() {
      await action('Inspect all rendered prescription fields, placeholders, nested labels and C5; scroll only', async () => {
        active.textContrast = await textContrast(page.locator('.prescricao-item__topo > span, .prescricao label, .prescricao label small, .prescricao label strong, .prescricao__nota-legal'));
        active.itemLabel = active.textContrast.find(item => item.text === 'Item 01');
        assert.equal(active.itemLabel.text, 'Item 01'); assert.equal(active.itemLabel.fontSize, 14); assert.equal(active.itemLabel.textShadow, 'none');
        for (const item of active.textContrast) { assert(item.measurable, item.class); assert(item.contrast >= 4.5, `${item.text}: ${item.contrast}`); }
        active.quantityLabel = active.textContrast.find(item => item.text === 'Quantidade em algarismos');
        active.legalNote = active.textContrast.find(item => item.class === 'prescricao__nota-legal');
        assert.equal(active.quantityLabel.fontSize, 14); assert.equal(active.legalNote.fontSize, 16);
        const fields = page.locator('.prescricao input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=file]), .prescricao select, .prescricao textarea');
        active.fields = await textContrast(fields);
        active.placeholders = await textContrast(fields.locator('xpath=self::*[@placeholder]'), '::placeholder');
        assert(active.fields.length > 10); assert(active.placeholders.length > 3);
        for (const item of [...active.fields, ...active.placeholders]) {
          assert(item.measurable); assert(item.contrast >= 4.5, `${item.tag} ${item.placeholder}: ${item.contrast}`);
          assert(item.background.every(channel => channel >= 240), `Non-light field: ${item.placeholder}`);
          assert(item.fontSize >= 14); assert(item.height >= 44);
        }
        assert(active.fields.every(item => item.caretColor === 'rgb(38, 57, 54)'));
        active.visualScreenshots = [];
        const capture = async (label, locator) => {
          await locator.scrollIntoViewIfNeeded();
          const screenshot = path.join(output, `${active.name}-${label}.png`);
          await page.screenshot({ path: screenshot, fullPage: false }); active.visualScreenshots.push(screenshot);
        };
        await capture('nota-c5', page.locator('.prescricao__nota-legal'));
        for (const field of await fields.all()) await field.scrollIntoViewIfNeeded();
        await capture('final-formulario', page.locator('.prescricao__acoes'));
        await capture('item-quantidade', page.locator('.prescricao-item').getByText('Quantidade em algarismos', { exact: true }));
        assert.equal(report.requests.filter(request => request.case === active.name && /\/api\/(receituario|prescricao-especial)/.test(request.path) && request.method !== 'GET').length, 0);
      });
    } },
    { route: '/receituario', variant: 'prescription-summary-visual', theme, ready: '.prescricao-resumo', async run() {
      await action('Inspect continuous-use label and summary text/control geometry; scroll only', async () => {
        active.textContrast = await textContrast(page.locator('.prescricao-continuo strong, .prescricao-resumo p, .prescricao-resumo h2, .prescricao-resumo strong, .prescricao-resumo small, .prescricao-resumo dt, .prescricao-resumo dd, .prescricao-resumo li, .prescricao-resumo__status'));
        assert(active.textContrast.length >= 10);
        for (const item of active.textContrast) { assert(item.measurable); assert(item.contrast >= 4.5, `${item.text}: ${item.contrast}`); }
        const metadata = active.textContrast.filter(item => ['SMALL', 'DT', 'DD', 'LI'].includes(item.tag) || item.class.includes('prescricao-resumo__status'));
        assert(metadata.every(item => item.fontSize >= 14));
        active.summaryGeometry = await page.locator('.prescricao-resumo').evaluate(panel => {
          const boundary = panel.getBoundingClientRect(), overflow = [], textRects = [];
          const walk = document.createTreeWalker(panel, NodeFilter.SHOW_TEXT);
          let node;
          while ((node = walk.nextNode())) {
            if (!node.textContent.trim()) continue;
            const range = document.createRange(); range.selectNodeContents(node);
            for (const rect of range.getClientRects()) {
              if (rect.width <= 0 || rect.height <= 0) continue;
              textRects.push({ text: node.textContent.trim().slice(0, 70), left: rect.left, right: rect.right });
              if (rect.left < boundary.left - 1 || rect.right > boundary.right + 1) overflow.push(node.textContent.trim().slice(0, 70));
            }
          }
          return { width: boundary.width, scrollWidth: panel.scrollWidth, clientWidth: panel.clientWidth, overflow, textRects };
        });
        assert.equal(active.summaryGeometry.overflow.length, 0);
        assert(active.summaryGeometry.scrollWidth <= active.summaryGeometry.clientWidth + 1);
        active.visualScreenshots = [];
        const capture = async (label, locator) => {
          await locator.scrollIntoViewIfNeeded();
          const screenshot = path.join(output, `${active.name}-${label}.png`);
          await page.screenshot({ path: screenshot, fullPage: false }); active.visualScreenshots.push(screenshot);
        };
        await capture('uso-continuo', page.locator('.prescricao-continuo'));
        await capture('resumo-inicio', page.locator('.prescricao-resumo__topo'));
        active.summaryControls = [];
        for (const control of await page.locator('.prescricao-resumo button').all()) {
          await control.scrollIntoViewIfNeeded();
          const geometry = await control.evaluate(element => {
            const box = element.getBoundingClientRect(), text = element.textContent.trim(), style = getComputedStyle(element);
            const centerX = box.left + box.width / 2, centerY = box.top + box.height / 2;
            const top = document.elementFromPoint(centerX, centerY);
            return { text, fontSize: parseFloat(style.fontSize), width: box.width, height: box.height, scrollWidth: element.scrollWidth, clientWidth: element.clientWidth, reachable: !!top && (top === element || element.contains(top)), disabled: element.disabled };
          });
          active.summaryControls.push(geometry);
          assert(geometry.reachable, geometry.text); assert(geometry.height >= 44); assert(geometry.fontSize >= 14); assert(geometry.scrollWidth <= geometry.clientWidth + 1);
        }
        await capture('resumo-acoes', page.locator('.prescricao-resumo__acoes'));
      });
    } },
  ]),
  { route: '/cardiologia-intensiva', ready: 'h1', async run() { await action('Filter intensive-care reference interface', async () => { const search = page.getByPlaceholder('Ex.: choque, ECMO, ventilação, delirium, pós-parada'); await fill(search, 'parada'); await search.fill(''); }); } },
  { route: '/triagem-sintomas', ready: 'h1', async run() { await action('Open a reviewed triage question set without requesting assessment', async () => { const link = page.getByRole('button', { name: triages[0].name, exact: true }); await link.click(); await page.getByRole('heading', { name: triages[0].name, exact: true }).waitFor(); const choice = page.locator('input[type=checkbox]').first(); if (await choice.count()) { await choice.check(); await choice.uncheck(); } else { const select = page.locator('select').first(); assert(await select.count()); const option = await select.locator('option').nth(1).getAttribute('value'); await select.selectOption(option); } }); } },
  { route: '/heart-team', ready: '.cai-heart-team', optionalGate: true, async run() {
    await action('Fill unsent draft and verify required review/agents; no analysis', async () => {
      const submit = page.getByRole('button', { name: 'Salvar caso e ver orçamento' }); assert(await submit.isDisabled());
      await fill(page.getByLabel('Relato clínico livre'), 'DEMONSTRAÇÃO DE INTERFACE — sem caso clínico real ou resultado de análise.');
      const required = page.locator('.cai-agent-grid button').first(); const selected = await required.getAttribute('aria-pressed'); await required.click(); assert.equal(await required.getAttribute('aria-pressed'), selected);
      const optional = page.locator('.cai-agent-grid button').nth(1); await optional.click(); assert.equal(await optional.getAttribute('aria-pressed'), 'false'); await optional.click();
      assert(await submit.isDisabled());
      await page.getByLabel('Toda conclusão terá revisão médica').check(); await page.getByLabel('Toda conclusão terá revisão médica').uncheck();
    });
    await action('Open explicit draft history and retain safe unavailable-budget state', async () => {
      await page.getByRole('button', { name: /Histórico/ }).click(); await page.getByRole('button').filter({ hasText: 'DEMONSTRAÇÃO DE INTERFACE — sem resultados de IA' }).click();
      await page.getByRole('heading', { name: 'Orçamento do conselho' }).waitFor(); await page.getByRole('alert').filter({ hasText: 'Escrita bloqueada' }).waitFor();
      assert.equal(await page.getByRole('button', { name: /^Executar por/ }).count(), 0);
    });
  } },
  { route: '/ecg-ia', ready: '.ceai', async run() { await action('Legacy ECG URL renders the same Exames IA component, as registered in App.tsx', async () => { assert.equal(new URL(page.url()).pathname, '/ecg-ia'); assert(await page.locator('.ceai input[type=file]').count()); assert((await page.locator('.ceai').innerText()).includes('desligada')); }); } },
  ...[
    { route: '/exames', fault: '/api/lab-tests', retry: 'Tentar consultar exames novamente', recovered: '.cc-exam-groups' },
    { route: '/calculadoras', fault: '/api/calculators', retry: 'Tentar novamente', recovered: '.cv-calculators-page' },
    { route: '/documentos', fault: '/api/document-templates', retry: 'Tentar carregar modelos novamente', recovered: '#modelos-salvos' },
    { route: '/receituario', fault: '/api/prescricao-especial/capacidades', retry: 'Tentar carregar prescrição especial novamente', recovered: '.prescricao__abas' },
    { route: '/assistente', fault: '/api/ai/status', retry: 'Tentar novamente', recovered: '.ia-escolha' },
  ].map(definition => ({ ...definition, variant: 'error-recovery', ready: '[role=alert]', async run() {
    await action('Injected 503 shows explicit error and recovers on retry without pageerror', async () => {
      assert(await page.getByRole('alert').count()); active.fault = null;
      await page.getByRole('button', { name: definition.retry, exact: true }).click(); await settle();
      await page.locator(definition.recovered).waitFor();
      assert.equal(await page.getByRole('button', { name: definition.retry, exact: true }).count(), 0);
    });
    if (definition.route === '/assistente') await action('Consent write failure does not advance or enable tools', async () => {
      await page.locator('.ia-escolha__cartao').nth(1).click();
      await page.getByRole('button', { name: 'Ativar acesso à agenda e ao e-mail' }).click();
      await page.getByRole('alert').filter({ hasText: 'Nenhuma nova autorização foi confirmada' }).waitFor();
      assert(await page.getByRole('button', { name: 'Ativar acesso à agenda e ao e-mail' }).isEnabled());
    });
  } })),
];
for (const theme of ['light', 'dark']) {
  cases.push({ route: '/receituario', variant: 'prescription-pricing-recovery', pricing: true, theme, ready: '.prescricao-resumo', async run() {
    await action('Failed presentation lookup stays explicit and can recover through its own retry', async () => {
      active.priceLookupFault = true;
      await fill(page.getByPlaceholder('Digite o nome genérico ou comercial'), 'Aldactone');
      await page.getByRole('listbox', { name: 'Sugestões de medicamentos' }).locator('button').first().click();
      await page.locator('.prescricao-preco-aviso[role=alert]').waitFor();
      active.priceLookupFault = false;
      await page.getByRole('button', { name: 'Tentar consultar preços novamente', exact: true }).click();
      await page.locator('.prescricao-apresentacoes__fonte--kairos').waitFor();
      assert.equal(await page.locator('.prescricao-preco-aviso[role=alert]').count(), 0);
    });
    await action('Late prices for one drug cannot populate the next selected drug', async () => {
      active.holdPriceLookup = true;
      await page.getByPlaceholder('Digite o nome genérico ou comercial').fill('');
      await fill(page.getByPlaceholder('Digite o nome genérico ou comercial'), 'Aldactone');
      await page.getByRole('listbox', { name: 'Sugestões de medicamentos' }).locator('button').first().click();
      await page.getByText('Buscando marcas e preços…', { exact: true }).waitFor();
      await fill(page.getByPlaceholder('Digite o nome genérico ou comercial'), 'Amiodarona');
      await page.getByRole('listbox', { name: 'Sugestões de medicamentos' }).locator('button').first().click();
      await page.getByText('SEM PREÇO NESTA FIXTURE DE CORRIDA — não representa cobertura real', { exact: true }).waitFor();
      assert.equal(typeof active.releasePriceLookup, 'function');
      await active.releasePriceLookup(); delete active.releasePriceLookup; active.holdPriceLookup = false;
      await settle();
      assert.equal(await page.locator('.prescricao-apresentacoes__fonte--kairos').count(), 0);
      assert((await page.locator('.prescricao-resumo').innerText()).includes('Amiodarona'));
      assert(!(await page.locator('.prescricao-resumo').innerText()).includes('ALDACTONE'));
    });
  } });
  cases.push({ route: '/receituario', variant: 'prescription-pricing-catalogue', pricing: true, theme, ready: '.prescricao-resumo', async run() {
    await action('A brand-only result must still expose explicit priced presentations; no automatic commercial choice', async () => {
      await fill(page.getByPlaceholder('Digite o nome genérico ou comercial'), 'Aldactone');
      await page.getByRole('listbox', { name: 'Sugestões de medicamentos' }).locator('button').first().click();
      const options = page.locator('.prescricao-apresentacoes__fonte--kairos');
      await options.waitFor();
      assert.equal(await options.locator('button').count(), kairosOptions.length);
      await options.locator('button').first().click();
      assert.equal(await page.locator('.prescricao-resumo__preco').innerText(), kairosMinimum);
    });
  } });
  cases.push({ route: '/receituario', variant: 'prescription-pricing-filled', pricing: true, theme, ready: '.prescricao-resumo', async run() {
    await action('Exact Kairos result shows its minimum published PMC and source; populate summary and inspect all labels', async () => {
      await fill(page.getByPlaceholder('Digite o nome genérico ou comercial'), 'Aldactone');
      await page.getByRole('listbox', { name: 'Sugestões de medicamentos' }).locator('button').nth(1).click();
      assert.equal(await page.locator('.prescricao-resumo__preco').innerText(), kairosMinimum);
      assert.equal(await page.locator('.prescricao-resumo__total > span > strong').innerText(), kairosMinimum);
      await page.locator('.prescricao-paciente__grade input[autocomplete="name"]').fill('PACIENTE FICTÍCIO — QA SEM VALIDADE CLÍNICA');
      await page.locator('.prescricao-resumo').getByRole('button', { name: 'Ver prévia', exact: true }).click();
      await page.getByText('Classificação demonstrativa — conferência de legibilidade sem validade clínica', { exact: true }).last().waitFor();
      const targets = page.locator('.prescricao-resumo :is(p,h2,span,strong,small,dt,dd,li), .prescricao-selecao :is(p,span,strong,small)');
      active.textContrast = await textContrast(targets);
      for (const item of active.textContrast) { assert(item.measurable); assert(item.contrast >= 4.5, `${item.text}: ${item.contrast}`); }
      assert.equal(await page.locator('.prescricao-resumo').evaluate(element => getComputedStyle(element).position), 'static');
      await page.locator('.prescricao-resumo__topo').scrollIntoViewIfNeeded();
      active.summaryScreenshot = path.join(output, `${active.name}-populated.png`); await page.screenshot({ path: active.summaryScreenshot });
      await page.locator('.prescricao-resumo__acoes').scrollIntoViewIfNeeded();
      const summary = await page.locator('.prescricao-resumo').evaluate(element => ({ width: element.clientWidth, scrollWidth: element.scrollWidth }));
      assert(summary.scrollWidth <= summary.width + 1);
    });
    await action('Editing the presentation invalidates the price instead of retaining another pack reference', async () => {
      const presentation = page.locator('.prescricao-item input').nth(1);
      await presentation.fill('APRESENTAÇÃO MANUAL DE TESTE, SEM PREÇO VINCULADO');
      assert(!(await page.locator('.prescricao-resumo__total').innerText()).includes(brl(kairosOptions[0].preco_minimo)));
    });
    await action('Typing a different medication clears the previous brand and commercial reference', async () => {
      await fill(page.getByPlaceholder('Digite o nome genérico ou comercial'), 'Aldactone');
      await page.getByRole('listbox', { name: 'Sugestões de medicamentos' }).locator('button').nth(1).click();
      await fill(page.getByPlaceholder('Digite o nome genérico ou comercial'), 'PRODUTO FICTÍCIO SEM PREÇO');
      assert(!(await page.locator('.prescricao-resumo').innerText()).includes('ALDACTONE'));
      assert(!(await page.locator('.prescricao-resumo__total').innerText()).includes(brl(kairosOptions[0].preco_minimo)));
    });
  } });
}
for (const theme of ['light', 'dark']) {
  cases.push({ route: '/prontuario', variant: 'prontuario-context-visual', theme, ready: '.pep-patient', async run() {
    await action('Inspect the changed encounter fieldset without saving or finalizing', async () => {
      await page.getByRole('button', { name: '+ Iniciar atendimento', exact: true }).click();
      await page.getByLabel('Motivo / queixa principal').fill('DEMONSTRAÇÃO — texto extenso para verificar o editor, sem validade clínica.');
      await page.getByLabel('Anamnese', { exact: true }).fill('Anotação fictícia para verificar o espaço de leitura e os controles. '.repeat(6));
      const fields = page.getByRole('group', { name: 'Dados do atendimento' });
      assert(!(await fields.isDisabled()));
      active.fieldsetGeometry = await fields.evaluate(element => {
        const box = element.getBoundingClientRect();
        return { width: box.width, scrollWidth: element.scrollWidth, gap: getComputedStyle(element).gap,
          labels: Array.from(element.querySelectorAll('label')).map(label => ({ text: label.firstChild.textContent, display: getComputedStyle(label).display, font: getComputedStyle(label).fontSize })) };
      });
      assert(active.fieldsetGeometry.scrollWidth <= active.fieldsetGeometry.width + 1);
      assert(active.fieldsetGeometry.labels.every(label => label.display === 'grid'));
      active.textContrast = await textContrast(fields.locator('label'));
      for (const label of active.textContrast) { assert(label.fontSize >= 14); assert(label.measurable && label.contrast >= 4.5, `${label.text}: ${label.contrast}`); }
      await page.getByLabel('Tipo', { exact: true }).scrollIntoViewIfNeeded();
      active.editorScreenshot = path.join(output, `${active.name}-editor.png`);
      await page.screenshot({ path: active.editorScreenshot });
      const save = page.getByRole('button', { name: 'Salvar rascunho', exact: true });
      await save.scrollIntoViewIfNeeded(); await save.focus(); assert(await save.evaluate(e => e === document.activeElement));
      const final = page.getByRole('button', { name: 'Finalizar', exact: true });
      assert(await final.isVisible());
    });
  } });
}
const chosen = process.env.ATELIER_QA_ROUTES?.split(',');
const variants = process.env.ATELIER_QA_VARIANTS?.split(',');
const desktopWidth = Number(process.env.ATELIER_QA_DESKTOP_WIDTH || 1440);
assert(Number.isInteger(desktopWidth) && desktopWidth >= 1024 && desktopWidth <= 1920);
try {
  for (const viewport of [{ name: 'desktop', width: desktopWidth, height: 900 }, { name: 'mobile', width: 390, height: 844 }]) {
    await page.setViewportSize(viewport);
    for (const item of cases.filter(item => (!chosen || chosen.includes(item.route)) && (!variants || variants.includes(item.variant)))) {
      active = { name: `${viewport.name}-${item.route.slice(1)}${item.variant ? `-${item.variant}` : ''}${item.theme ? `-${item.theme}` : ''}`, route: item.route, theme: item.theme, pricing: item.pricing, viewport, actions: [], status: 'running', fault: item.fault || null }; report.cases.push(active);
      const requestStart = report.requests.length, errorStart = report.pageErrors.length;
      try {
        if (item.theme && page.url().startsWith(base.origin)) await page.evaluate(({ theme, userId }) => localStorage.setItem(`corvia:cardiology-spaces:theme:v1:${userId}`, theme), { theme: item.theme, userId: profile.id });
        await page.goto(new URL(item.route, base).href); await settle();
        if (item.theme) assert.equal(await page.locator('html').getAttribute('data-corvia-theme'), item.theme);
        if (item.optionalGate && !(await page.locator(item.ready).count())) { active.status = 'not-testable-feature-gate'; active.reason = 'Current preview flag does not expose Heart Team; not a functional PASS.'; continue; }
        await page.locator(item.ready).first().waitFor();
        active.before = await metrics();
        await item.run(); await settle();
        active.after = await metrics(); active.status = 'pass';
        if (active.before.overflow || active.after.overflow) active.status = 'layout-failure';
        if (report.pageErrors.length > errorStart) active.status = 'javascript-error';
      } catch (error) { active.status = 'needs-investigation'; active.error = String(error.message).slice(0, 1800); active.after = await metrics().catch(() => null); }
      finally {
        active.finalPath = new URL(page.url()).pathname;
        active.unmodelled = report.requests.slice(requestStart).filter(record => record.provenance === 'unmodelled-dependency').map(record => record.path);
        active.writesBlocked = report.requests.slice(requestStart).filter(record => record.method !== 'GET');
        active.screenshot = path.join(output, `${active.name.replaceAll('/', '-')}.png`); await page.screenshot({ path: active.screenshot, fullPage: false }).catch(() => {});
        fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify(report, null, 2));
        console.log(JSON.stringify({ name: active.name, status: active.status, actions: active.actions.length, error: active.error?.slice(0, 240), unmodelled: active.unmodelled }));
      }
    }
  }
} finally {
  await context.close(); await browser.close(); report.browserClosed = true;
  report.finishedAt = new Date().toISOString();
  report.residual = ['No backend persistence, document generation/signature/email, external integrations, AI analysis or clinical algorithm correctness certified.', 'Calculator catalog is the pure base registry, not dynamically merged dose/perioperative plugins.', 'Canonical content is an explicit reviewed local subset; counts do not represent the complete corpus.', 'Detail-route patient IDs/checklist applications/Heart Team cases beyond the explicit synthetic fixtures remain untested.'];
  fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ report: path.join(output, 'report.json'), browserClosed: true, statuses: report.cases.reduce((counts, item) => ({ ...counts, [item.status]: (counts[item.status] || 0) + 1 }), {}) }));
}
