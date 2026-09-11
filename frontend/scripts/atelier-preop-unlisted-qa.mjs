import fs from 'node:fs';
import assert from 'node:assert/strict';

// Focused real-browser UI check. Every API call is intercepted: no patient,
// document, account, email or calculator service is modified/executed remotely.
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs');
const base = new URL(process.env.ATELIER_QA_URL || 'http://127.0.0.1:4322');
assert(['localhost', '127.0.0.1'].includes(base.hostname) && !base.username && !base.password);
const output = process.env.ATELIER_QA_OUT || '/tmp/corvia-preop-unlisted-qa-20260911';
assert(output.startsWith('/tmp/'));
fs.mkdirSync(output, { recursive: true });
assert(/^\/(private\/)?tmp\//.test(fs.realpathSync(output)));
const profile = { id: -990091, email: 'demo@example.invalid', full_name: 'Demonstração — sem paciente real', role: 'admin', profession: 'Medica', product_access: true, investidor: false, profile_completion_required: false, kyc_required: false, onboarding_pendente: false, boas_vindas_pendente: false };
const report = [];
const browser = await chromium.launch({ headless: true, channel: 'chrome', args: ['--disable-gpu'] });
try {
  for (const [width, height, theme] of [[1440, 900, 'light'], [1440, 900, 'dark'], [390, 844, 'light'], [390, 844, 'dark']]) {
    const context = await browser.newContext({ viewport: { width, height }, locale: 'pt-BR', serviceWorkers: 'block', reducedMotion: 'reduce' });
    await context.addInitScript(theme => localStorage.setItem('corvia:cardiology-spaces:theme:v1', theme), theme);
    const calls = [], errors = [];
    await context.route('**/*', route => {
      const request = route.request(), url = new URL(request.url());
      if (url.origin !== base.origin) return route.abort('blockedbyclient');
      if (!url.pathname.startsWith('/api/')) return route.continue();
      const reply = (body, status = 200) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
      const p = url.pathname;
      if (p === '/api/auth/session-status') return reply({ authenticated: true });
      if (p === '/api/auth/me') return reply(profile);
      if (p === '/api/version') return reply({ commit: 'isolated-preop-qa' });
      if (p === '/api/billing/status') return reply({ status: 'inativo', acesso_administrativo: true, entitlements: { source: 'administrative', tudo_com_tudo: true } });
      if (request.method() === 'POST') {
        calls.push({ path: p, payload: request.postDataJSON() });
        if (p === '/api/auth/sessao') return reply({ ok: true });
        if (p === '/api/calculators/rcri/run') return reply({ result: { pontos: 0, classe: 'I', evento_pct: '0,4' }, interpretation: 'Fixture de interface, não avaliação clínica.' });
        if (p === '/api/calculators/dasi/run') return reply({ result: { score: 0, max: 58.2, capacidade_funcional: 'Fixture', ponto_decisao: 34 }, interpretation: 'Fixture de interface, não avaliação clínica.' });
        if (p === '/api/avaliacao-preoperatoria/gerar') return reply({ id: -990001 });
        return reply({ detail: 'Escrita não modelada bloqueada.' }, 403);
      }
      if (p === '/api/assinatura/provedores') return reply([]);
      return reply({ detail: 'Dependência não modelada nesta verificação isolada.' }, 503);
    });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(new URL('/avaliacao-preoperatoria', base).href, { waitUntil: 'domcontentloaded' });
    const select = page.getByLabel('Tipo de procedimento', { exact: true });
    await select.selectOption('outras_baixo_risco');
    const notice = page.locator('#gupta-limite-modelo');
    await notice.waitFor();
    await page.getByPlaceholder('Ex.: colecistectomia videolaparoscópica eletiva').fill('Procedimento fictício — sem validade clínica');
    await page.getByRole('button', { name: 'Calcular método(s)', exact: true }).click();
    await page.getByText('Resultado integrado', { exact: true }).waitFor();
    assert.equal(calls.some(call => call.path.includes('gupta-mica')), false);
    assert.equal(calls.filter(call => /calculators\/(rcri|dasi)\/run/.test(call.path)).length, 2);
    assert.match(await page.locator('.preop-page').innerText(), /Gupta MICA: não estimado/);
    const metrics = await notice.evaluate(element => {
      const style = getComputedStyle(element), b = element.getBoundingClientRect();
      const rgb = value => value.match(/[\d.]+/g).slice(0, 3).map(Number);
      const lum = rgb => rgb.map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4).reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
      const a = lum(rgb(style.color)), c = lum(rgb(style.backgroundColor));
      return { font: parseFloat(style.fontSize), contrast: (Math.max(a, c) + .05) / (Math.min(a, c) + .05), overflow: document.documentElement.scrollWidth > innerWidth + 2, left: b.left, right: b.right };
    });
    assert(metrics.font >= 16 && metrics.contrast >= 4.5 && !metrics.overflow && metrics.left >= 0 && metrics.right <= width);
    const size = await select.boundingBox();
    assert(size.height >= 44 && size.width >= 44);
    await notice.scrollIntoViewIfNeeded();
    await page.screenshot({ path: `${output}/${width}-${theme}.png` });
    await page.getByRole('button', { name: 'Gerar documento', exact: true }).click();
    await page.getByText('Documento gerado.', { exact: true }).waitFor();
    const generated = calls.find(call => call.path === '/api/avaliacao-preoperatoria/gerar');
    assert.equal(generated.payload.gupta, null);
    assert.equal(generated.payload.gupta_nao_estimado, true);
    assert(generated.payload.rcri && generated.payload.dasi);
    assert.deepEqual(errors, []);
    report.push({ width, height, theme, metrics, calls: calls.map(call => call.path), status: 'pass', limitations: 'APIs simuladas; nenhum cálculo clínico, documento ou envio real.' });
    await context.close();
  }
} finally {
  await browser.close();
  fs.writeFileSync(`${output}/report.json`, JSON.stringify(report, null, 2));
}
console.log(JSON.stringify(report));
