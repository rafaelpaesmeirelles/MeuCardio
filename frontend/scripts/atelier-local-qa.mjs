import fs from 'node:fs';
import path from 'node:path';
import { certifyAtelierReference } from './atelier-reference.mjs';

// Rendering/empty-error-state inspection only: no production authentication,
// clinical records, scientific results, mailbox, payment or AI service is used.
const baseUrl = new URL(process.env.ATELIER_QA_URL || 'http://127.0.0.1:4321');
if (!['http:', 'https:'].includes(baseUrl.protocol) || !['127.0.0.1', 'localhost'].includes(baseUrl.hostname) || baseUrl.username || baseUrl.password) {
  throw new Error('Local visual fixtures are restricted to credential-free loopback URLs.');
}
const base = baseUrl.origin;
const skipReference = process.env.ATELIER_QA_SKIP_REFERENCE === '1';
const isolationMessage = 'Serviço não conectado nesta revisão visual isolada.';
const homeReference = { status: skipReference ? 'skipped-by-request' : 'not-run', reason: skipReference ? 'ATELIER_QA_SKIP_REFERENCE=1; this run does not repeat or certify the Home reference.' : null };
const out = path.resolve(process.env.ATELIER_QA_OUT || '/tmp/corvia-atelier-qa');
if (!out.startsWith('/tmp/')) throw new Error('Visual QA artifacts must stay in a child directory of /tmp.');
fs.mkdirSync(out, { recursive: true });
const realOut = fs.realpathSync(out);
if (!realOut.startsWith('/tmp/') && !realOut.startsWith('/private/tmp/')) throw new Error('Visual QA output cannot follow a symlink outside /tmp.');

const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const viewports = [
  { name: 'desktop', width: 1366, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
];
const publicRoutes = [
  { path: '/entrar', name: 'login', ready: '.login-gateway__form', screenshot: true },
  { path: '/solicitar-acesso', name: 'signup', ready: '.prehome-card--register', screenshot: true },
  { path: '/esqueci-senha', name: 'recovery', ready: '.prehome-card .login-formulario', screenshot: true },
  { path: '/redefinir-senha', name: 'reset-without-token', ready: '.prehome-confirmation' },
];
const authenticatedRoutes = [
  { path: '/exames', name: 'exames', ready: '.cc-exams-page', screenshot: true },
  { path: '/exames-ia', name: 'exames-ia', ready: '.ceai', gateFeature: 'ai', screenshot: true },
  { path: '/busca', name: 'busca', ready: '.tct-page' },
  { path: '/biblioteca', name: 'biblioteca', ready: '#analise-cientifica-ia-titulo', screenshot: true },
  { path: '/medicamentos', name: 'medicamentos', ready: '.cc-drugs-page' },
  { path: '/prontuario', name: 'prontuario', ready: '.pep' },
  { path: '/round', name: 'round', ready: '.ccc-patient-command__manager' },
  { path: '/estudos', name: 'estudos', ready: '.cc-studies-page' },
  // App.tsx intentionally keeps the legacy courses URL as a redirect.
  { path: '/cursos', resolvedPath: '/trilhas', name: 'cursos', ready: '.cv-learning-observatory' },
  { path: '/admin/usuarios', name: 'admin-usuarios', ready: '.admin-assinantes__filtros', screenshot: true },
  { path: '/minha-conta', name: 'minha-conta', ready: '.conta__grid', screenshot: true },
  { path: '/corvia-mail', name: 'corvia-mail', ready: '#endereco-email', gateFeature: 'mail', allowMissingH1: true },
  { path: '/tour', name: 'tour', ready: '.cst--atelier', screenshot: true },
];
const failures = [], errors = [], requests = [], blockedRequests = [], surfaces = [], warnings = [];
let activeInspection = { phase: 'setup', route: null, viewport: null };
let authenticated = false;
const profile = {
  id: 990091, email: 'atelier-visual@example.invalid', full_name: 'Alexandriana Visual',
  professional_title: 'Profa. Dra.', role: 'admin', profession: 'Medica', council_name: 'CRM',
  council_number: '000000', council_state: 'SP', product_access: true, investidor: false,
  profile_completion_required: false, kyc_required: false, onboarding_pendente: false,
  boas_vindas_pendente: false, created_at: '2026-09-01T00:00:00Z',
};

// Only empty collections with contracts found in the current frontend are
// modelled. Their provenance is included in the report; a zero here says
// nothing about the actual corpus, patients, subscribers or learning catalog.
const emptyCollections = new Map([
  ['/api/lab-tests/taxonomy', 'src/pages/Exames.tsx: Taxonomia[]'],
  ['/api/library/themes', 'src/pages/Biblioteca.tsx: { theme, count }[]'],
  ['/api/studies/types', 'src/pages/Estudos.tsx: Tipo[]'],
  ['/api/studies/themes', 'src/pages/Estudos.tsx: Tema[]'],
  ['/api/pacientes', 'src/pages/Prontuario.tsx: Paciente[]'],
  ['/api/agenda-clinica/hoje', 'src/pages/Prontuario.tsx: Fila[]'],
  ['/api/round/patients', 'src/pages/RoundGerenciavel.tsx: PacienteResumo[]'],
  ['/api/agenda/appointments', 'existing atelier-local-qa agenda fixture'],
  ['/api/agenda/commitments', 'existing atelier-local-qa agenda fixture'],
  ['/api/agenda/work-routines', 'existing atelier-local-qa agenda fixture'],
  ['/api/agenda/integrations', 'src/pages/MinhaConta.tsx: { provider }[]'],
]);
const emptyPages = new Map([
  ['/api/lab-tests', 'src/pages/Exames.tsx: PaginaExames'],
  ['/api/library/documents', 'src/pages/Biblioteca.tsx: DocumentPage'],
  ['/api/studies', 'src/pages/Estudos.tsx: paginated Item[]'],
  ['/api/drugs', 'src/pages/MedicamentosClinicalCommand.tsx + src/lib/api.ts: PaginaDe<Item>'],
  ['/api/trilhas', 'src/pages/Trilhas.tsx + src/lib/api.ts: PaginaDe<Trilha>'],
]);
const emptyPage = url => ({
  total: 0, limit: Math.max(1, Number(url.searchParams.get('limit')) || 50),
  offset: Math.max(0, Number(url.searchParams.get('offset')) || 0),
  next_offset: null, has_more: false, items: [],
});
const browser = await chromium.launch({
  headless: true, channel: process.env.ATELIER_QA_BROWSER || 'chrome', args: ['--disable-gpu'],
});
const context = await browser.newContext({
  viewport: { width: viewports[0].width, height: viewports[0].height }, locale: 'pt-BR', serviceWorkers: 'block',
});

await context.route('**/*', async route => {
  const request = route.request(), url = new URL(request.url());
  if (!url.pathname.startsWith('/api/')) {
    if (url.origin === base && ['GET', 'HEAD'].includes(request.method())) return route.continue();
    blockedRequests.push({ ...activeInspection, origin: url.origin, path: url.pathname, method: request.method() });
    return route.abort('blockedbyclient');
  }
  // Intercept API paths even when a local build points them at another host.
  // No request bodies, credentials, tokens or query values enter the report.
  const entry = { ...activeInspection, path: url.pathname, method: request.method() };
  requests.push(entry);
  const fulfill = (body, status = 200, fixture = 'empty-contract', provenance = null) => {
    Object.assign(entry, { status, fixture, provenance });
    return route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
  };
  if (request.method() === 'POST' && url.pathname === '/api/auth/sessao') {
    authenticated = true;
    return fulfill({ ok: true }, 200, 'isolated-auth-fixture');
  }
  if (request.method() === 'GET') {
    if (url.pathname === '/api/auth/session-status') return fulfill({ authenticated }, 200, 'isolated-auth-fixture');
    if (url.pathname === '/api/auth/me') return fulfill(authenticated ? profile : { detail: 'Sessão visual ausente.' }, authenticated ? 200 : 401, 'isolated-auth-fixture');
    if (url.pathname === '/api/version') return fulfill({ commit: 'atelier-isolated-visual-fixture' }, 200, 'isolated-version-fixture');
    if (emptyCollections.has(url.pathname)) return fulfill([], 200, 'empty-contract', emptyCollections.get(url.pathname));
    if (emptyPages.has(url.pathname)) return fulfill(emptyPage(url), 200, 'empty-contract', emptyPages.get(url.pathname));
    if (url.pathname === '/api/admin/usuarios') return fulfill({ items: [], page: Math.max(1, Number(url.searchParams.get('page')) || 1), page_size: Math.max(1, Number(url.searchParams.get('page_size')) || 25), total: 0, has_more: false }, 200, 'empty-contract', 'src/pages/AdminAssinantes.tsx: ListaResposta');
    if (url.pathname === '/api/library/catalog') return fulfill({ total: 0, fronts: [] }, 200, 'empty-contract', 'src/pages/Biblioteca.tsx: Catalog (no integrity/publication success flags)');
    if (url.pathname === '/api/library/area-counts') return fulfill({ areas: [] }, 200, 'empty-contract', 'src/pages/Biblioteca.tsx: AreaCountsResponse');
    if (url.pathname === '/api/agenda/mobility/day-context') return fulfill({ first_target: null, last_target: null });
    if (url.pathname.startsWith('/api/agenda/mobility/')) return fulfill(null);
    if (url.pathname === '/api/favorites/status') return fulfill({ favorited: false, available: true });
    if (url.pathname === '/api/clinical-change-approvals/count') return fulfill({ pending: 0 });
  }
  // Includes billing, mail, AI, external integrations and every business write.
  // HTTP 503 is expected isolation evidence, never a production outage verdict.
  return fulfill({ detail: isolationMessage }, 503, 'unmodelled-service-unavailable');
});

const page = await context.newPage();
page.setDefaultTimeout(30000);
page.setDefaultNavigationTimeout(60000);
page.on('pageerror', error => errors.push({ ...activeInspection, message: String(error) }));

async function settleSurface() {
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {
    warnings.push({ ...activeInspection, message: 'Network did not become idle; rendering metrics may reflect pending activity.' });
  });
  await page.evaluate(async () => {
    await document.fonts.ready;
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    window.scrollTo(0, 0);
  });
}

async function measureSurface() {
  return page.evaluate(() => {
    const visible = element => {
      const box = element.getBoundingClientRect(), style = getComputedStyle(element);
      return box.width > 0 && box.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    };
    const summary = element => {
      const rect = element.getBoundingClientRect(), style = getComputedStyle(element);
      return {
        tag: element.tagName.toLowerCase(), id: element.id || null,
        text: (element.innerText || element.getAttribute('aria-label') || element.getAttribute('placeholder') || '').trim().replace(/\s+/g, ' ').slice(0, 180),
        fontSize: parseFloat(style.fontSize), lineHeight: style.lineHeight, fontFamily: style.fontFamily,
        color: style.color, background: style.backgroundColor,
        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        clippedHorizontally: element.scrollWidth > element.clientWidth + 2,
      };
    };
    const root = document.querySelector('#conteudo-principal, .cst--atelier, .corvia-atelier-public, .login-gateway') || document.body;
    const sample = selector => [...root.querySelectorAll(selector)].filter(visible).slice(0, 16).map(summary);
    const h1 = [...root.querySelectorAll('h1')].filter(visible);
    const width = document.documentElement.clientWidth;
    const overflow = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - width;
    const offenders = [...document.body.querySelectorAll('*')].filter(element => {
      if (!visible(element) || element.closest('[aria-hidden="true"]')) return false;
      const rect = element.getBoundingClientRect();
      return rect.right > width + 2 || rect.left < -2;
    }).slice(0, 20).map(summary);
    return {
      width, height: innerHeight, documentHeight: document.documentElement.scrollHeight,
      horizontalOverflow: Math.max(0, overflow), overflowCandidates: offenders,
      design: document.documentElement.dataset.corviaDesign || null,
      theme: document.documentElement.dataset.corviaTheme || document.documentElement.dataset.theme || null,
      stylesheets: [...document.styleSheets].map(sheet => sheet.href ? new URL(sheet.href, location.href).pathname : 'inline'),
      title: document.title, h1Count: h1.length, firstLevelText: h1.map(summary),
      headings: sample('h2'), primaryText: sample('p, label, legend'), controls: sample('button, input, select, textarea'),
      stateText: [...root.querySelectorAll('[role="alert"], [role="status"], .cc-empty, .pep-empty, .learning-state')].filter(visible).map(element => element.textContent.trim().replace(/\s+/g, ' ').slice(0, 300)),
      brokenImages: [...document.images].filter(image => visible(image) && image.complete && image.naturalWidth === 0).map(image => ({ src: new URL(image.currentSrc || image.src, location.href).pathname, alt: image.alt })),
      nestedMainCount: document.querySelectorAll('main main').length,
    };
  });
}

async function inspectRoute(target, phase) {
  const firstRequest = requests.length, firstError = errors.length;
  activeInspection = { phase, route: target.path, viewport: 'desktop' };
  try {
    await page.setViewportSize({ width: viewports[0].width, height: viewports[0].height });
    await page.goto(base + target.path, { waitUntil: 'domcontentloaded' });
    const content = page.locator(target.ready).first();
    // App.tsx gates only the declared commercial targets. This exact card is
    // CommercialFeatureGate's error branch, not its denied-plan branch or an
    // arbitrary alert. Accept it only alongside our recorded billing 503 below.
    const gate = target.gateFeature ? page.locator('#conteudo-principal .pagina > .cartao')
      .filter({ has: page.getByRole('heading', { level: 1, name: 'Não foi possível verificar o acesso', exact: true }) })
      .filter({ has: page.getByText(isolationMessage, { exact: true }) })
      .filter({ has: page.getByText(target.gateFeature === 'ai' ? 'Recursos de IA' : 'CorVIA Mail', { exact: true }) })
      .filter({ has: page.getByRole('alert') }) : null;
    await (gate ? content.or(gate).first() : content).waitFor({ state: 'visible' });
    // The same mounted route is resized for mobile, avoiding a second cold
    // lazy-module load. No guessed build-chunk URLs or synthetic content imports.
    for (const viewport of viewports) {
      activeInspection = { phase, route: target.path, viewport: viewport.name };
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await settleSurface();
      const productContentRendered = await content.isVisible();
      const gateRendered = gate ? await gate.isVisible() : false;
      const billingUnavailable = requests.slice(firstRequest).some(request =>
        request.phase === phase && request.route === target.path && request.path === '/api/billing/status'
        && request.method === 'GET' && request.status === 503 && request.fixture === 'unmodelled-service-unavailable');
      if (gateRendered && (!billingUnavailable || productContentRendered)) {
        throw new Error('Commercial gate does not match the isolated billing-unavailable state.');
      }
      if (!productContentRendered && !gateRendered) throw new Error('Neither route content nor the expected isolated commercial gate is visible.');
      const metrics = await measureSurface();
      const resolvedPath = new URL(page.url()).pathname;
      const row = {
        ...activeInspection, name: target.name, status: 'rendering/empty-error-state',
        renderedComponent: gateRendered ? 'commercial-feature-gate' : 'route-content',
        authorizationState: gateRendered ? 'unavailable-isolated-fixture' : target.gateFeature ? 'content-rendered' : 'not-applicable',
        gateFeature: target.gateFeature || null, productContentRendered,
        resolvedPath, expectedPath: target.resolvedPath || target.path, metrics,
        pageerrors: errors.slice(firstError),
        isolatedApi: requests.slice(firstRequest).map(({ path: apiPath, method, status, fixture }) => ({ path: apiPath, method, status, fixture })),
        screenshot: null,
      };
      surfaces.push(row);
      const fail = message => failures.push(phase + ' ' + target.path + ' ' + viewport.name + ': ' + message);
      if (resolvedPath !== row.expectedPath) fail('unexpected redirect to ' + resolvedPath);
      if (metrics.design !== 'atelier') fail('architectural design is not active');
      if (metrics.horizontalOverflow > 2) fail('horizontal overflow: ' + metrics.horizontalOverflow + 'px');
      if (!metrics.h1Count && !target.allowMissingH1) fail('no visible first-level heading');
      if (metrics.brokenImages.length) fail('broken visible images: ' + metrics.brokenImages.map(item => item.src).join(', '));
      if (!metrics.h1Count || metrics.nestedMainCount) warnings.push({ ...activeInspection, message: 'Heading/landmark structure needs human review.', h1Count: metrics.h1Count, nestedMainCount: metrics.nestedMainCount });
      if (target.screenshot) {
        const screenshot = target.name + '-' + viewport.name + '.png';
        await page.screenshot({ path: path.join(out, screenshot), fullPage: true });
        row.screenshot = screenshot;
      }
    }
  } catch (error) {
    const message = String(error?.stack || error);
    failures.push(phase + ' ' + target.path + ': ' + message);
    surfaces.push({ ...activeInspection, name: target.name, status: 'rendering-failed', message, pageerrors: errors.slice(firstError) });
    await page.screenshot({ path: path.join(out, target.name + '-failure.png'), fullPage: true }).catch(() => {});
  }
}

try {
  for (const target of publicRoutes) await inspectRoute(target, 'public');
  activeInspection = { phase: 'isolated-login', route: '/entrar', viewport: 'desktop' };
  await page.setViewportSize({ width: viewports[0].width, height: viewports[0].height });
  await page.goto(base + '/entrar', { waitUntil: 'domcontentloaded' });
  await page.locator('#email').fill(profile.email);
  await page.locator('#senha').fill('local-fixture-not-a-credential');
  await page.locator('.login-gateway__form button[type="submit"]').click();
  await page.locator('.atelier-home').waitFor();
  if (!skipReference) {
    activeInspection = { phase: 'home-reference', route: '/', viewport: 'mixed' };
    const firstReferenceFailure = failures.length, firstReferenceError = errors.length;
    try {
      await certifyAtelierReference({ page, base, out, failures });
      homeReference.status = failures.length === firstReferenceFailure && errors.length === firstReferenceError ? 'passed' : 'failed';
    } catch (error) {
      homeReference.status = 'failed';
      failures.push('home-reference: ' + String(error?.stack || error));
      // A reference failure must not erase evidence for the remaining pages.
      await page.screenshot({ path: path.join(out, 'home-reference-failure.png'), fullPage: true }).catch(() => {});
    }
  }
  for (const target of authenticatedRoutes) await inspectRoute(target, 'authenticated');
} catch (error) {
  failures.push(String(error?.stack || error));
  await page.screenshot({ path: path.join(out, 'failure.png'), fullPage: true }).catch(() => {});
} finally {
  const expectedSurfaces = (publicRoutes.length + authenticatedRoutes.length) * viewports.length;
  const renderedSurfaces = surfaces.filter(item => item.status === 'rendering/empty-error-state').length;
  const expectedScreenshots = [...publicRoutes, ...authenticatedRoutes].filter(item => item.screenshot).length * viewports.length;
  const screenshots = surfaces.filter(item => item.screenshot).map(item => item.screenshot);
  if (renderedSurfaces !== expectedSurfaces) failures.push('Incomplete rendering coverage: ' + renderedSurfaces + '/' + expectedSurfaces + ' surfaces.');
  if (screenshots.length !== expectedScreenshots) failures.push('Incomplete screenshot coverage: ' + screenshots.length + '/' + expectedScreenshots + ' captures.');
  fs.writeFileSync(path.join(out, 'local-report.json'), JSON.stringify({
    kind: 'isolated-visual-fixtures-not-production', status: 'rendering/empty-error-state',
    limitations: [
      'This is not CI, production evidence, a clinical validation, or an authentication/authorization certification.',
      'All API traffic is intercepted. Known collection contracts are empty; unmodelled services and business writes return 503.',
      'Only a synthetic local UI session is used. No patient data, science records, mailbox messages or service success is fabricated.',
      'Screenshots and typography/overflow metrics require human review; they are not a complete accessibility audit.',
      'The missing-token reset page is inspected without submitting recovery, signup, billing, upload or clinical forms.',
      'A commercial-feature-gate capture proves only rendering of the expected isolated billing failure, never IA/Mail product rendering or production denial.',
    ],
    base, viewports, homeReference, expectedSurfaces, renderedSurfaces, expectedScreenshots, screenshots,
    failures, errors, warnings, surfaces, requests, blockedRequests,
  }, null, 2));
  await browser.close();
}
console.log(JSON.stringify({ out, surfaces: surfaces.length, failures, errors }, null, 2));
if (failures.length || errors.length) process.exitCode = 1;
