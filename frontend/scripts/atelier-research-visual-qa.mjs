import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// UI regression only. All APIs use local, identified fixtures; no credentials,
// clinical edits, production requests or external services are used.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const base = new URL(process.env.ATELIER_QA_URL || 'http://127.0.0.1:4324');
if (!['127.0.0.1', 'localhost'].includes(base.hostname)) throw Error('Loopback only');
const out = process.env.ATELIER_RESEARCH_QA_OUT || '/tmp/corvia-research-mobile-qa';
if (!out.startsWith('/tmp/')) throw Error('Temporary output only');
fs.mkdirSync(out, { recursive: true });
if (!/^\/(private\/)?tmp\//.test(fs.realpathSync(out))) throw Error('Unsafe output symlink');
const metadata = dir => JSON.parse(fs.readFileSync(path.join(root, dir, 'metadados.json'), 'utf8'));
const studies = metadata('estudos').slice(0, 2);
const evidence = metadata('evidencias').slice(0, 2).map(e => ({ ...e, summary: e.statement, source_url: null }));
const cases = metadata('casos-clinicos').slice(0, 2);
const documentSlug = 'icfer-classificacao-diagnostico-quatro-pilares';
const documentBody = fs.readFileSync(path.join(root, 'content/Insuficiência_cardíaca', `${documentSlug}.md`), 'utf8').replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '');
const localDocument = { title: 'Documento canônico local — QA isolada', theme: 'Insuficiência cardíaca', kind: 'documento', summary: null, body_md: documentBody, source_refs: [], review_status: 'revisado', version: 1 };
const pageOf = items => ({ items, total: items.length, limit: 100, offset: 0, has_more: false, next_offset: null });
const areas = [
  ['geral', 'Cardiologia Geral'], ['pediatrica', 'Cardiologia Pediátrica'],
  ['neonatal', 'Cardiologia Neonatal'], ['congenita', 'Cardiopatias Congênitas'],
  ['geriatria', 'Cardio-Geriatria'], ['gestacao', 'Cardiologia na Gestação e Puerpério'],
  ['cardiooncologia', 'Cardio-Oncologia'], ['fetal', 'Cardiologia Fetal'],
].map(([id, label]) => ({ id, label, count: 2, collections: 1 }));
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/Users/rafaelpaesmeirelles/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs');
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const rows = [], errors = [], blocked = [];
try {
  for (const theme of (process.env.ATELIER_RESEARCH_THEMES || 'light,dark').split(',')) {
    const context = await browser.newContext({ locale: 'pt-BR', serviceWorkers: 'block', reducedMotion: 'reduce' });
    await context.addInitScript(theme => {
      localStorage.setItem('corvia:cardiology-spaces:theme:v1:990091', theme);
      localStorage.setItem('corvia:cardiology-spaces:tour:v3', 'true');
    }, theme);
    await context.route('**/*', async route => {
      const url = new URL(route.request().url()), p = url.pathname;
      if (url.origin !== base.origin) { blocked.push(url.origin); return route.abort('blockedbyclient'); }
      if (!p.startsWith('/api/')) return route.continue();
      const json = body => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) });
      if (p === '/api/auth/session-status') return json({ authenticated: true });
      if (p === '/api/auth/me') return json({ id: 990091, email: 'local-qa@example.invalid', full_name: 'Demonstração local', role: 'admin', product_access: true, profile_completion_required: false, kyc_required: false, onboarding_pendente: false, boas_vindas_pendente: false });
      if (p === '/api/version') return json({ commit: 'local-research-visual-fixture' });
      if (p === '/api/billing/status') return json({ entitlements: { ai: false, mail: false } });
      if (p === '/api/favorites/status') return json({ favorited: false, favorite_id: null, available: true });
      if (p === '/api/clinical-change-approvals/count') return json({ pending: 0 });
      if (p === '/api/studies') return json(pageOf(studies));
      const study = studies.find(item => p === `/api/studies/${item.slug}`);
      if (study) return json(study);
      if (p === '/api/studies/types') return json(studies.map(s => ({ study_type: s.study_type, count: 1 })));
      if (p === '/api/studies/themes') return json(studies.map(s => ({ theme: s.theme, count: 1 })));
      if (p === '/api/evidence') return json(pageOf(evidence));
      const recommendation = evidence.find(item => p === `/api/evidence/${item.slug}`);
      if (recommendation) return json(recommendation);
      if (p === '/api/evidence/themes') return json(evidence.map(e => ({ theme: e.theme, count: 1 })));
      if (p === '/api/casos-clinicos') return json(pageOf(cases));
      if (p === '/api/casos-clinicos/themes') return json(cases.map(c => ({ theme: c.tema, count: 1 })));
      if (p === '/api/library/catalog') return json({ total: 0, fronts: [] });
      if (p === '/api/library/themes') return json([]);
      if (p === '/api/library/area-counts') return json({ areas });
      if (p === '/api/library/documents') return json(pageOf([]));
      if (p === `/api/library/documents/${documentSlug}`) return json(localDocument);
      if (p === '/api/guideline-updates') return json({ cutoff: '2023-01-01', items: [] });
      if (p === '/api/guideline-updates/me') return json({ cutoff: '2023-01-01', items: [] });
      if (p === '/api/guideline-updates/status') return json({ enabled: false, health: 'inactive', analysis_status: 'not_run', recent_discoveries: [], total_discovered: 0, pending_analysis: 0 });
      return route.fulfill({ status: 503, contentType: 'application/json', body: '{"detail":"Recurso fora do recorte local de QA."}' });
    });
    const page = await context.newPage();
    page.on('pageerror', e => errors.push(String(e)));
    for (const width of (process.env.ATELIER_RESEARCH_WIDTHS || '320,390,768,1440').split(',').map(Number)) {
      await page.setViewportSize({ width, height: width < 768 ? 844 : 900 });
      for (const route of (process.env.ATELIER_RESEARCH_ROUTES || '/estudos,/diretrizes,/evidencias,/casos-clinicos,/biblioteca,/documentos-cientificos-ia').split(',')) {
        await page.goto(new URL(route, base).href, { waitUntil: 'networkidle' });
        await page.locator('#conteudo-principal').waitFor();
        await page.evaluate(() => document.fonts.ready);
        if (process.env.ATELIER_RESEARCH_TEXT_SPACING === '1') {
          // WCAG text-spacing stress, not a change to the shipped appearance.
          await page.addStyleTag({ content: '#root#root#root .cv-content * { line-height: 1.5 !important; letter-spacing: .12em !important; word-spacing: .16em !important; } #root#root#root .cv-content p { margin-bottom: 2em !important; }' });
        }
        const selectors = route === '/biblioteca'
          ? ['[aria-labelledby="acervo-especializado-titulo"]']
          : route === '/casos-clinicos' ? ['.filtros-conteudo'] : route === '/documentos-cientificos-ia' ? ['.commercial-feature-gate'] : ['.cv-page-hero'];
        const stats = await page.evaluate(() => {
          const main = document.querySelector('#conteudo-principal');
          const visible = e => e && e.getClientRects().length > 0;
          const rect = e => e ? ({ x: e.getBoundingClientRect().x, y: e.getBoundingClientRect().y, width: e.getBoundingClientRect().width, height: e.getBoundingClientRect().height, bottom: e.getBoundingClientRect().bottom }) : null;
          const style = e => e ? Object.fromEntries(['color', 'backgroundColor', 'backgroundImage', 'opacity', 'position', 'paddingTop', 'fontSize'].map(k => [k, getComputedStyle(e)[k]])) : null;
          const rgba = text => { const nums = text.match(/[\d.]+/g)?.map(Number); return nums?.length >= 3 ? [nums[0], nums[1], nums[2], nums[3] ?? 1] : null; };
          const blend = (front, back) => front.slice(0, 3).map((v, i) => v * front[3] + back[i] * (1 - front[3]));
          const luminance = rgb => rgb.map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4).reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
          const contrast = e => {
            let chain = [], gradient = false;
            for (let node = e; node; node = node.parentElement) {
              const s = getComputedStyle(node), bg = rgba(s.backgroundColor);
              gradient ||= s.backgroundImage !== 'none';
              if (bg) chain.unshift(bg);
              if (bg?.[3] === 1) break;
            }
            const bg = chain.reduce((back, front) => blend(front, back), [255, 255, 255]);
            const fg = rgba(getComputedStyle(e).webkitTextFillColor) || rgba(getComputedStyle(e).color);
            const a = luminance(blend(fg, bg)), b = luminance(bg);
            return { text: e.textContent, ratio: (Math.max(a, b) + .05) / (Math.min(a, b) + .05), gradient };
          };
          const space = main.querySelector('.cv-page-hero__space'), identity = main.querySelector('.cv-page-hero__identity');
          const controls = [...main.querySelectorAll('button,input,select,a')].filter(visible);
          return {
            actualTheme: document.documentElement.dataset.corviaTheme,
            overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
            hero: { space: rect(space), identity: rect(identity), spaceStyle: style(space), heroStyle: style(main.querySelector('.cv-page-hero')) },
            labels: [...main.querySelectorAll('label > strong,label > span,.hoje__temas a span,.hoje__temas a small')].filter(visible).map(e => ({ text: e.textContent, ...style(e), parentStyle: style(e.parentElement) })),
            smallControls: controls.filter(e => ['BUTTON','INPUT','SELECT'].includes(e.tagName)).map(e => ({ text: e.getAttribute('aria-label') || e.textContent?.slice(0, 60), ...rect(e) })).filter(r => r.width < 43.5 || r.height < 43.5),
            contrast: [...main.querySelectorAll('.filtros-conteudo label strong,.hoje__temas a span,.hoje__temas a small,.cv-page-hero__copy .eyebrow,.cv-page-hero__description,.colecao-conteudo > header > span,.commercial-feature-gate h1,.commercial-feature-gate .eyebrow')].filter(visible).map(contrast),
            docks: [...document.querySelectorAll('.cv-mobile-dock,.cv-utility-dock')].filter(visible).map(e => ({ name: e.className, ...rect(e), children: [...e.children].filter(visible).map(c => ({ name: c.className, ...rect(c) })) })),
          };
        });
        const failures = [];
        if (stats.overflow > 2) failures.push(`document overflow ${stats.overflow}`);
        if (stats.hero.space && stats.hero.identity && stats.hero.space.bottom > stats.hero.identity.y + 1) failures.push('hero space overlaps identity');
        if (stats.smallControls.length) failures.push(`${stats.smallControls.length} small controls`);
        for (const text of stats.contrast) {
          if (text.gradient || text.ratio < 4.5) failures.push(`unverified/low text contrast: ${text.text?.slice(0, 45)} (${text.ratio.toFixed(2)})`);
        }
        for (const dock of stats.docks) for (const box of [dock, ...dock.children]) {
          if (box.x < -1 || box.x + box.width > width + 1) failures.push(`dock clipped: ${box.name}`);
        }
        const name = `${theme}-${width}-${route.slice(1).replaceAll('/', '-')}`;
        for (const selector of selectors) {
          const target = page.locator(selector).first();
          if (await target.count()) { await target.screenshot({ path: path.join(out, `${name}.png`) }); break; }
        }
        await page.screenshot({ path: path.join(out, `${name}-viewport.png`) });
        rows.push({ route, width, theme, textSpacing: process.env.ATELIER_RESEARCH_TEXT_SPACING === '1', ...stats, failures });
        console.log(JSON.stringify({ route, width, theme, failures }));
      }
    }
    await context.close();
  }
} finally {
  await browser.close();
  fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify({ rows, errors, blocked, limitation: 'Local API fixtures; not production/API or clinical validation.' }, null, 2));
}
if (errors.length || rows.some(row => row.failures.length)) process.exitCode = 1;
