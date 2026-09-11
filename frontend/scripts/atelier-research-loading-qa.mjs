import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const base = new URL(process.env.ATELIER_QA_URL || 'http://127.0.0.1:4324');
if (!['127.0.0.1', 'localhost'].includes(base.hostname) || base.username || base.password) throw Error('Loopback only');
const out = process.env.ATELIER_LOADING_QA_OUT || '/tmp/corvia-research-loading-final-20260911';
if (!out.startsWith('/tmp/')) throw Error('Output must be in /tmp');
fs.mkdirSync(out, { recursive: true });
if (!/^\/(private\/)?tmp\//.test(fs.realpathSync(out))) throw Error('Unsafe output symlink');
const cases = JSON.parse(fs.readFileSync(path.join(root, 'casos-clinicos/metadados.json'), 'utf8')).slice(0, 2);
const raw = fs.readFileSync(path.join(root, 'content/Insuficiência_cardíaca/icfer-classificacao-diagnostico-quatro-pilares.md'), 'utf8');
const body_md = raw.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '');
const docSlug = 'icfer-classificacao-diagnostico-quatro-pilares';
const doc = { title: 'Documento canônico local — QA isolada', slug: docSlug, theme: 'Insuficiência cardíaca', kind: 'documento', summary: null, body_md, source_refs: [], review_status: 'revisado', version: 1 };
const profile = { id: 990092, email: 'loading-qa@example.invalid', full_name: 'Demonstração de carregamento', role: 'admin', professional_title: 'Dr.', profession: 'Medico', council_name: 'CRM', council_number: '000000', council_state: 'SP', product_access: true, investidor: false, profile_completion_required: false, kyc_required: false, onboarding_pendente: false, boas_vindas_pendente: false };
const rows = [], requests = [], pageErrors = [];
let scenario = '', blockedRead = '', failCase = false;
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs');
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--disable-gpu'] });
const context = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'pt-BR', serviceWorkers: 'block', reducedMotion: 'reduce' });
await context.addInitScript(() => {
  localStorage.setItem('corvia:cardiology-spaces:theme:v1:990092', 'dark');
  window.WebSocket = class extends EventTarget { readyState = 3; static OPEN = 1; static CLOSED = 3; send() {} close() {} };
  Object.defineProperty(navigator, 'geolocation', { value: { getCurrentPosition(_ok, error) { error?.({ code: 1 }); }, watchPosition() { return 0; }, clearWatch() {} } });
});
await context.route('**/*', async route => {
  const request = route.request(), url = new URL(request.url()), p = url.pathname;
  if (url.origin !== base.origin) return route.abort('blockedbyclient');
  if (!p.startsWith('/api/')) return ['GET', 'HEAD'].includes(request.method()) ? route.continue() : route.abort('blockedbyclient');
  requests.push({ scenario, method: request.method(), path: p });
  const json = (body, status = 200) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
  if (request.method() !== 'GET') return json({ detail: 'Mutation forbidden in local read-only QA' }, 403);
  if (p === blockedRead || (blockedRead === 'case-next-page' && p === '/api/casos-clinicos' && url.searchParams.get('offset') === '1')) return new Promise(() => {});
  if (p === '/api/auth/session-status') return json({ authenticated: true });
  if (p === '/api/auth/me') return json(profile);
  if (p === '/api/version') return json({ commit: 'local-isolated-loading-qa' });
  if (p === '/api/billing/status') return json({ entitlements: { ai: false, mail: false } });
  if (p === '/api/favorites/status') return json({ favorited: false, favorite_id: null, available: true });
  if (p === '/api/favorites') return json([]);
  if (p === '/api/clinical-change-approvals/count') return json({ pending: 0 });
  if (p === `/api/library/documents/${docSlug}`) return json(doc);
  if (p === '/api/casos-clinicos/themes') return json([...new Set(cases.map(item => item.tema))].map(theme => ({ theme, count: cases.filter(item => item.tema === theme).length })));
  if (p === '/api/casos-clinicos') {
    const offset = Number(url.searchParams.get('offset') || 0);
    return json({ items: cases.slice(offset, offset + 1).map(item => ({ slug: item.slug, titulo: item.titulo, tema: item.tema, nivel: item.nivel, tentativas: 0, acertou_na_ultima: null })), total: 2, limit: 1, offset, next_offset: offset ? null : 1, has_more: offset === 0 });
  }
  if (p.startsWith('/api/casos-clinicos/')) {
    const item = cases.find(item => p === `/api/casos-clinicos/${item.slug}`);
    if (item && !failCase) return json({ slug: item.slug, titulo: item.titulo, tema: item.tema, nivel: item.nivel, enunciado: item.enunciado, pergunta: item.pergunta, opcoes: item.opcoes, source_refs: item.source_refs || [] });
  }
  return json({ detail: 'Serviço não modelado na fixture local.' }, 503);
});
const page = await context.newPage();
page.on('pageerror', error => pageErrors.push({ scenario, message: error.message }));
async function run(name, route, width, check) {
  scenario = name;
  const row = { scenario: name, route, width, actions: [], issues: [], limitations: ['APIs locais interceptadas; sem sessão, acesso ou execução de serviço real.'] };
  rows.push(row);
  try {
    await page.setViewportSize({ width, height: 844 });
    await page.goto(new URL(route, base).href, { waitUntil: 'domcontentloaded' });
    await check(row);
    row.overflow = await page.evaluate(() => Math.max(0, document.documentElement.scrollWidth - innerWidth));
    assert.equal(row.overflow, 0);
    row.screenshot = path.join(out, `${name}.png`);
    await page.screenshot({ path: row.screenshot, fullPage: true });
  } catch (error) {
    row.issues.push(error.message);
    row.screenshot = path.join(out, `${name}-failed.png`);
    await page.screenshot({ path: row.screenshot, fullPage: true }).catch(() => {});
  }
}
try {
  blockedRead = '/api/billing/status';
  await run('gate-pending-mobile', '/documentos-cientificos-ia', 390, async row => {
    await page.getByRole('heading', { name: 'Não foi possível verificar o acesso' }).waitFor({ timeout: 22000 });
    assert.equal(await page.getByText('Verificando seu acesso…', { exact: true }).count(), 0);
    blockedRead = '';
    await page.getByRole('button', { name: 'Tentar novamente', exact: true }).focus();
    await page.keyboard.press('Enter');
    await page.getByRole('heading', { name: 'Conheça os planos que incluem este recurso' }).waitFor();
    row.actions.push('GET pendente → timeout; retry por teclado → acesso negado; funcionalidade protegida não liberada');
  });
  blockedRead = '/api/favorites/status';
  await run('favorite-pending-desktop', `/biblioteca/${docSlug}`, 1440, async row => {
    const control = page.locator('article .favorite-control').first();
    await control.getByRole('button', { name: 'Favorito não consultado', exact: true }).waitFor({ timeout: 22000 });
    assert.equal(await control.getByRole('button', { name: 'Favorito não consultado', exact: true }).isDisabled(), true);
    blockedRead = '';
    await control.getByRole('button', { name: 'Tentar novamente' }).click();
    await control.getByRole('button', { name: '☆ Favoritar', exact: true }).waitFor();
    row.actions.push('Leitura do documento preservada durante status pendente; timeout → erro → GET de repetição; nenhuma mutação');
  });
  blockedRead = 'case-next-page';
  await run('cases-partial-mobile', '/casos-clinicos', 390, async row => {
    await page.getByRole('link', { name: new RegExp(cases[0].titulo.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')) }).waitFor({ timeout: 8000 });
    await page.getByRole('button', { name: 'Tentar novamente', exact: true }).waitFor({ timeout: 22000 });
    assert.ok(await page.locator(`a[href="/casos-clinicos/${cases[0].slug}"]`).isVisible());
    blockedRead = '';
    await page.getByRole('button', { name: 'Tentar novamente', exact: true }).click();
    await page.locator(`a[href="/casos-clinicos/${cases[1].slug}"]`).waitFor();
    row.actions.push('Primeira página visível enquanto segunda aguarda; timeout preserva casos; retry recupera as duas páginas');
  });
  failCase = true;
  await run('case-detail-retry-mobile', `/casos-clinicos/${cases[0].slug}`, 390, async row => {
    await page.getByRole('button', { name: 'Tentar novamente', exact: true }).waitFor();
    failCase = false;
    await page.getByRole('button', { name: 'Tentar novamente', exact: true }).click();
    await page.getByRole('heading', { name: cases[0].titulo, exact: true }).waitFor();
    assert.ok(await page.getByRole('button', { name: 'Confirmar resposta', exact: true }).isDisabled());
    row.actions.push('GET503 → erro explícito → retry → enunciado/opções canônicos; nenhuma resposta enviada');
  });
} finally {
  await browser.close();
  fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify({ rows, requests, pageErrors }, null, 2));
}
console.log(JSON.stringify({ report: path.join(out, 'report.json'), rows: rows.map(({ scenario, issues, overflow }) => ({ scenario, issues, overflow })), pageErrors }, null, 2));
if (rows.some(row => row.issues.length) || pageErrors.length) process.exitCode = 1;
