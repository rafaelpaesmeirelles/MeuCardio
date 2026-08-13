import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const base = process.env.QA_BASE_URL || 'http://127.0.0.1:8080';
const email = process.env.QA_EMAIL;
const password = process.env.QA_PASSWORD;
if (!email || !password) throw new Error('QA_EMAIL/QA_PASSWORD obrigatórios');
const out = process.env.QA_OUTPUT_DIR || 'rc4-acceptance/screenshots';
fs.mkdirSync(out, { recursive: true });
const report = { failures: [], pageErrors: [], mobility: {}, routes: [] };
const fail = (m) => report.failures.push(m);
const browser = await chromium.launch({ headless: true });

async function login(viewport, options = {}) {
  const context = await browser.newContext({ viewport, colorScheme: 'dark', locale: 'pt-BR', timezoneId: 'America/Sao_Paulo', ...options });
  const page = await context.newPage();
  page.on('pageerror', (e) => report.pageErrors.push(`${page.url()} :: ${String(e)}`));
  await page.goto(`${base}/entrar`, { waitUntil: 'networkidle' });
  await page.locator('#email').fill(email);
  await page.locator('#senha').fill(password);
  await page.locator('button[type="submit"]').click();
  await page.waitForURL((url) => !url.pathname.includes('/entrar'), { timeout: 20000 });
  return { context, page };
}

async function requestJson(page, url, options = {}) {
  return await page.evaluate(async ({ url, options }) => {
    const response = await fetch(url, { credentials: 'include', headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
    const text = await response.text();
    let body = null;
    try { body = text ? JSON.parse(text) : null; } catch { body = text; }
    return { ok: response.ok, status: response.status, body };
  }, { url, options });
}

async function assertPage(page, route) {
  await page.goto(`${base}${route}`, { waitUntil: 'networkidle', timeout: 25000 });
  await page.waitForTimeout(350);
  const state = await page.evaluate(() => ({ path: location.pathname, width: innerWidth, scrollWidth: document.documentElement.scrollWidth, text: document.body?.innerText || '', shell: !!document.querySelector('.clinical-os') }));
  report.routes.push({ route, path: state.path, width: state.width, scrollWidth: state.scrollWidth });
  if (state.path === '/entrar') fail(`${route}: perdeu sessão`);
  if (/carregando a tela/i.test(state.text)) fail(`${route}: loading infinito`);
  if (/internal server error|application error|erro 500/i.test(state.text)) fail(`${route}: erro de servidor visível`);
  if (!state.shell && route !== '/tour') fail(`${route}: fora do shell canônico`);
  if (state.scrollWidth > state.width + 16 && route !== '/agenda') fail(`${route}: overflow horizontal ${state.scrollWidth} > ${state.width}`);
}

try {
  const desktop = await login({ width: 1440, height: 1000 });
  const page = desktop.page;
  const location = await requestJson(page, '/api/agenda/locations', { method: 'POST', body: JSON.stringify({ name: 'Hospital QA CorVIA', timezone: 'America/Sao_Paulo', address: { city: 'Ambiente QA', state: 'SP' }, latitude: 0.10, longitude: 0.10, default_arrival_buffer_minutes: 20 }) });
  if (!location.ok) fail(`seed location: HTTP ${location.status}`);
  const service = await requestJson(page, '/api/agenda/services', { method: 'POST', body: JSON.stringify({ location_id: location.body?.id, code: 'qa-consulta', name: 'Consulta QA', duration_minutes: 30 }) });
  if (!service.ok) fail(`seed service: HTTP ${service.status}`);
  const startsAt = new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString();
  const appointment = await requestJson(page, '/api/agenda/appointments', { method: 'POST', body: JSON.stringify({ patient_name: 'Paciente QA', starts_at: startsAt, service_id: service.body?.id, location_id: location.body?.id, appointment_type: 'consulta', visit_mode: 'presencial' }) });
  if (!appointment.ok) fail(`seed appointment: HTTP ${appointment.status}`);
  const mobility = await requestJson(page, '/api/agenda/mobility/preferences', { method: 'PUT', body: JSON.stringify({ enabled: true, consent_accepted: true, automatic_foreground_refresh: true, refresh_interval_minutes: 5, travel_mode: 'driving' }) });
  if (!mobility.ok) fail(`seed mobility: HTTP ${mobility.status}`);

  await page.goto(`${base}/`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(out, 'home-desktop.png'), fullPage: false });
  await page.goto(`${base}/agenda`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(out, 'agenda.png'), fullPage: false });
  await page.goto(`${base}/`, { waitUntil: 'networkidle' });
  await page.evaluate(() => window.dispatchEvent(new Event('corvia:abrir-assistente-pessoal')));
  await page.locator('.cos-assistant-panel.is-open').waitFor({ state: 'visible', timeout: 10000 });
  await page.screenshot({ path: path.join(out, 'assistente-pessoal.png'), fullPage: false });
  await page.goto(`${base}/medicamentos`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(out, 'medicamentos.png'), fullPage: false });
  await page.goto(`${base}/biblioteca/acc-2026-expert-consensus-icfep-diagnostico-fenotipos-e-tratamento`, { waitUntil: 'networkidle' });
  await page.getByText(/ICFEp/i).first().waitFor({ state: 'visible', timeout: 15000 });
  await page.screenshot({ path: path.join(out, 'conteudo-novo-icfep.png'), fullPage: false });

  const mobile = await login({ width: 390, height: 844 }, { geolocation: { latitude: 0.11, longitude: 0.11 }, permissions: ['geolocation'] });
  let commuteCalls = 0;
  let postedAppointmentId = null;
  await mobile.page.route('**/api/agenda/mobility/commute-appointment', async (route) => {
    commuteCalls += 1;
    postedAppointmentId = route.request().postDataJSON().appointment_id;
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'live', provider: 'QA route', updated_at: new Date().toISOString(), destination: { appointment_id: appointment.body.id, routine_id: null, starts_at: appointment.body.starts_at, ends_at: appointment.body.ends_at, service_name: 'Consulta QA', source: 'appointment', arrival_buffer_minutes: 20, location: location.body }, routes: [{ rank: 1, provider_rank: 1, recommended: true, duration_seconds: 1440, typical_duration_seconds: 1080, traffic_delay_seconds: 360, extra_time_seconds: 0, distance_meters: 11400, congestion: 'moderado', summary: 'Rota QA', labels: [], geometry: { format: 'encoded_polyline', value: '_p~iF~ps|U_ulLnnqC_mqNvxq`@', precision: 5 }, traffic_segments: [], incidents: [] }], tips: [] }) });
  });
  await mobile.page.goto(`${base}/`, { waitUntil: 'networkidle' });
  await mobile.page.getByText('11.4 km').waitFor({ state: 'visible', timeout: 15000 });
  await mobile.page.getByText('24 min').waitFor({ state: 'visible', timeout: 15000 });
  const mobileState = await mobile.page.evaluate(() => { const summary = document.querySelector('.ccc-mobile-summary'); const text = summary?.textContent || ''; const labels = Array.from(document.querySelectorAll('.cc-mobile-nav span')).map((x) => x.textContent?.trim()); return { text, labels, width: innerWidth, scrollWidth: document.documentElement.scrollWidth }; });
  if (!(mobileState.text.indexOf('Seu dia') < mobileState.text.indexOf('Deslocamento') && mobileState.text.indexOf('Deslocamento') < mobileState.text.indexOf('Assistente') && mobileState.text.indexOf('Assistente') < mobileState.text.indexOf('Atualizações'))) fail('home mobile: ordem canônica inválida');
  if (JSON.stringify(mobileState.labels) !== JSON.stringify(['Início','Buscar','Pacientes','Agenda','Mais'])) fail(`bottom nav alterado: ${JSON.stringify(mobileState.labels)}`);
  if (mobileState.scrollWidth > mobileState.width + 8) fail(`home mobile: overflow ${mobileState.scrollWidth} > ${mobileState.width}`);
  if (postedAppointmentId !== appointment.body.id) fail(`appointment mismatch: enviado=${postedAppointmentId} exibido=${appointment.body.id}`);
  report.mobility = { commuteCalls, postedAppointmentId, appointmentId: appointment.body.id, destinationName: location.body.name, durationSeconds: 1440, distanceMeters: 11400, trafficDelaySeconds: 360 };
  await mobile.page.screenshot({ path: path.join(out, 'home-mobile-deslocamento.png'), fullPage: false });

  const noPermission = await login({ width: 390, height: 844 });
  let noPermissionCalls = 0;
  await noPermission.page.route('**/api/agenda/mobility/commute-appointment', async (route) => { noPermissionCalls += 1; await route.abort(); });
  await noPermission.page.goto(`${base}/`, { waitUntil: 'networkidle' });
  await noPermission.page.waitForTimeout(1000);
  if (noPermissionCalls !== 0) fail(`sem permissão: commute chamado ${noPermissionCalls}x`);
  await noPermission.page.screenshot({ path: path.join(out, 'home-mobile-sem-permissao.png'), fullPage: false });

  for (const route of ['/', '/agenda', '/medicamentos', '/estudos', '/evidencias', '/diretrizes', '/trilhas/timeline', '/triagem-sintomas', '/checklists', '/material-paciente']) await assertPage(page, route);
  await desktop.context.close(); await mobile.context.close(); await noPermission.context.close();
} finally { await browser.close(); }
if (report.pageErrors.length) fail(`pageerrors: ${report.pageErrors.join(' | ')}`);
fs.writeFileSync(path.join(path.dirname(out), 'report.json'), JSON.stringify(report, null, 2));
if (report.failures.length) { console.error(report); process.exit(1); }
console.log(JSON.stringify(report, null, 2));
