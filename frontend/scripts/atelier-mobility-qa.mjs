import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';

// Local React rendering only. No production credentials, geolocation, Maps
// key, Google cartography, route service, clinical records or external writes.
const base = new URL(process.env.ATELIER_QA_URL || 'http://127.0.0.1:4322');
assert(['http:', 'https:'].includes(base.protocol) && ['127.0.0.1', 'localhost'].includes(base.hostname) && !base.username && !base.password, 'Credential-free loopback URL required');
const out = path.resolve(process.env.ATELIER_QA_OUT || '/tmp/corvia-mobility-qa');
assert(out.startsWith('/tmp/'), 'QA output must be inside /tmp');
fs.mkdirSync(out, { recursive: true });
assert(/^\/(?:private\/)?tmp\//.test(fs.realpathSync(out)), 'Output symlink must remain inside /tmp');
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const viewports = [
  { width: 1440, height: 900 }, { width: 1366, height: 540 },
  { width: 820, height: 900 }, { width: 390, height: 844 }, { width: 320, height: 640 },
].filter(v => !process.env.MOBILITY_QA_WIDTH || v.width === Number(process.env.MOBILITY_QA_WIDTH));
const scenarios = ['success', 'no-geometry', 'no-route', 'sdk-error-retry']
  .filter(s => !process.env.MOBILITY_QA_SCENARIO || s === process.env.MOBILITY_QA_SCENARIO);
const themes = (process.env.MOBILITY_QA_THEME || 'light,dark').split(',');
assert(viewports.length && scenarios.length && themes.every(t => ['light', 'dark'].includes(t)), 'Invalid QA selection');
const rows = [], failures = [], errors = [], blocked = [], requests = [];
let active = {};
const profile = { id: 990091, email: 'mobility-visual@example.invalid', full_name: 'Demonstração Visual', professional_title: 'Dr.', role: 'admin', profession: 'Medico', council_name: 'CRM', council_number: '000000', council_state: 'SP', product_access: true, investidor: false, profile_completion_required: false, kyc_required: false, onboarding_pendente: false, boas_vindas_pendente: false };
const origin = { id: 990101, name: 'Origem fictícia — teste local', latitude: -23.561, longitude: -46.658 };
const destination = { id: 990102, name: 'Destino fictício — teste de deslocamento', latitude: -23.579, longitude: -46.665 };
const target = { target_key: 'visual-local:990102', target_type: 'commitment', title: 'Compromisso fictício', starts_at: new Date(Date.now() + 7200000).toISOString(), arrival_buffer_minutes: 10, location: destination };
function encode(points) {
  let last = [0, 0], encoded = '';
  for (const point of points) point.forEach((coordinate, axis) => {
    const value = Math.round(coordinate * 1e5), delta = value - last[axis]; last[axis] = value;
    let number = delta < 0 ? ~(delta << 1) : delta << 1;
    while (number >= 32) { encoded += String.fromCharCode((32 | (number & 31)) + 63); number >>= 5; }
    encoded += String.fromCharCode(number + 63);
  });
  return encoded;
}
const geometry = points => ({ format: 'encoded_polyline', precision: 5, value: encode(points) });
const sampleRoutes = [
  { rank: 1, provider_rank: 1, recommended: true, duration_seconds: 1080, typical_duration_seconds: 900, traffic_delay_seconds: 180, distance_meters: 7200, congestion: 'moderado', summary: 'Percurso fictício A · Teste local', geometry_available: true, geometry: geometry([[-23.561, -46.658], [-23.565, -46.659], [-23.569, -46.656], [-23.574, -46.662], [-23.579, -46.665]]), traffic_segments: [{ start_index: 1, end_index: 2, speed: 'slow' }] },
  { rank: 2, provider_rank: 2, recommended: false, duration_seconds: 1320, typical_duration_seconds: 1260, traffic_delay_seconds: 60, extra_time_seconds: 240, distance_meters: 9100, congestion: 'normal', summary: 'Percurso fictício B · Alternativa local', geometry_available: true, geometry: geometry([[-23.561, -46.658], [-23.562, -46.652], [-23.569, -46.648], [-23.576, -46.654], [-23.579, -46.665]]) },
];

// This intercepted SDK projects ONLY the component's supplied polylines on a
// blank canvas. The watermark and attribution stand-in explicitly identify it
// as a fixture: it is not a Google tiles/terms/availability certification.
function installFixtureSdk() {
  const ns = 'http://www.w3.org/2000/svg';
  const node = (tag, attrs) => { const el = document.createElementNS(ns, tag); for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value); return el; };
  window.__mobilityFixture = { instances: [], fits: 0, externalNavigation: 0 };
  class MapFixture {
    constructor(el, options) {
      this.el = el; this.options = options; this.lines = new Set(); this.markers = new Set(); this.bounds = [];
      el.dataset.qaMapFixture = 'true'; el.style.position = 'relative';
      this.svg = node('svg', { viewBox: '0 0 800 340', 'aria-hidden': 'true', 'data-qa-map-canvas': 'true' });
      Object.assign(this.svg.style, { position: 'absolute', inset: '0', width: '100%', height: '100%', minHeight: '0', maxHeight: '100%' });
      el.appendChild(this.svg);
      const watermark = document.createElement('span'); watermark.dataset.qaFixtureNotice = 'true';
      watermark.textContent = 'FIXTURE VISUAL · SEM CARTOGRAFIA REAL';
      Object.assign(watermark.style, { position: 'absolute', top: '8px', left: '8px', right: '8px', color: '#263936', background: '#fffdf8', padding: '5px 8px', fontSize: '12px', lineHeight: '1.4', fontFamily: 'system-ui', textAlign: 'center', zIndex: '1' }); el.appendChild(watermark);
      const attribution = document.createElement('a'); attribution.dataset.qaAttribution = 'true';
      attribution.href = 'https://maps.google.com/'; attribution.textContent = 'Google Maps · fixture de atribuição';
      Object.assign(attribution.style, { position: 'absolute', bottom: '0', left: '0', maxWidth: '100%', color: '#263936', background: '#fffdf8', padding: '4px 8px', fontSize: '12px', lineHeight: '1.4', fontFamily: 'system-ui', zIndex: '2' });
      attribution.addEventListener('click', event => { event.preventDefault(); window.__mobilityFixture.externalNavigation++; }); el.appendChild(attribution);
      for (const [label, text, y] of [['Aumentar zoom — fixture', '+', '50px'], ['Diminuir zoom — fixture', '−', '96px']]) {
        const control = document.createElement('button'); control.type = 'button'; control.setAttribute('aria-label', label); control.dataset.qaNativeControl = 'true';
        // Intrinsic SVG dimensions, no CSS sizing escape hatch. This catches
        // legacy map/Home selectors accidentally resizing SDK-owned icons.
        const icon = node('svg', { width: 20, height: 20, viewBox: '0 0 20 20', 'aria-hidden': 'true', 'data-qa-native-icon': 'true' });
        icon.appendChild(node('path', { d: text === '+' ? 'M3 10H17M10 3V17' : 'M3 10H17', stroke: 'currentColor', 'stroke-width': 2, fill: 'none' })); control.appendChild(icon);
        Object.assign(control.style, { position: 'absolute', top: y, right: '10px', display: 'grid', placeItems: 'center', width: '44px', height: '44px', minHeight: '44px', color: '#263936', background: '#fffdf8', border: '1px solid #8c796b', fontSize: '22px', zIndex: '2', padding: '0' }); el.appendChild(control);
      }
      window.__mobilityFixture.instances.push(this); this.draw();
    }
    setOptions(options) { Object.assign(this.options, options); this.draw(); }
    fitBounds(bounds) { this.bounds = bounds.points; window.__mobilityFixture.fits++; this.draw(); }
    setCenter(center) { this.options.center = center; this.draw(); }
    setZoom() {}
    draw() {
      const points = this.bounds.length ? this.bounds : [{ lat: -23.561, lng: -46.665 }, { lat: -23.579, lng: -46.648 }];
      const xs = points.map(p => p.lng), ys = points.map(p => p.lat);
      const minX = Math.min(...xs), minY = Math.min(...ys), dx = Math.max(.0001, Math.max(...xs) - minX), dy = Math.max(.0001, Math.max(...ys) - minY);
      const project = p => [55 + (p.lng - minX) / dx * 675, 290 - (p.lat - minY) / dy * 215];
      this.svg.replaceChildren(node('rect', { width: 800, height: 340, fill: this.options.backgroundColor || '#f3f0e7' }));
      for (const line of [...this.lines].sort((a, b) => a.options.zIndex - b.options.zIndex)) {
        const p = node('path', { d: line.options.path.map((point, i) => `${i ? 'L' : 'M'}${project(point).join(' ')}`).join(' '), fill: 'none', stroke: line.options.strokeColor, 'stroke-width': line.options.strokeWeight, opacity: line.options.strokeOpacity ?? 1, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
        this.svg.appendChild(p);
      }
      for (const marker of this.markers) {
        const [cx, cy] = project(marker.options.position), icon = marker.options.icon || {};
        this.svg.appendChild(node('circle', { cx, cy, r: icon.scale || 8, fill: icon.fillColor || '#8c4d35', stroke: icon.strokeColor || '#fffdf8', 'stroke-width': icon.strokeWeight || 3 }));
      }
    }
  }
  class Overlay {
    constructor(options, kind) { this.options = options; this.kind = kind; this.setMap(options.map); }
    setMap(map) { if (this.map) { this.map[this.kind].delete(this); this.map.draw(); } this.map = map; if (map) { map[this.kind].add(this); map.draw(); } }
    addListener(_name, callback) { this.callback = callback; return { remove() {} }; }
  }
  window.google = { maps: {
    Map: MapFixture, Polyline: class extends Overlay { constructor(options) { super(options, 'lines'); } },
    Marker: class extends Overlay { constructor(options) { super(options, 'markers'); } },
    LatLngBounds: class { constructor() { this.points = []; } extend(point) { this.points.push(point); return this; } },
    SymbolPath: { CIRCLE: 'CIRCLE' }, event: { clearInstanceListeners() {}, trigger(map) { map.draw?.(); } },
  } };
  window.corviaMapsReady?.();
}
const sdkSource = `(${installFixtureSdk.toString()})();`;
const browser = await chromium.launch({ headless: true, channel: process.env.ATELIER_QA_BROWSER || 'chrome', args: ['--disable-gpu'] });
const settle = page => page.evaluate(async () => { await document.fonts.ready; await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))); });

async function measure(page, selector, name) {
  const data = await page.locator(selector).evaluate(root => {
    const isVisible = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden'; };
    const rgb = c => { const m = c.match(/[\d.]+/g); return m ? m.map(Number) : [0, 0, 0, 0]; };
    const lum = c => { const a = c.slice(0, 3).map(n => n / 255).map(n => n <= .04045 ? n / 12.92 : ((n + .055) / 1.055) ** 2.4); return .2126 * a[0] + .7152 * a[1] + .0722 * a[2]; };
    const ratio = (a, b) => { const x = lum(rgb(a)), y = lum(rgb(b)); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
    const rect = e => { const r = e.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height, right: r.right, bottom: r.bottom }; };
    const text = e => (e.innerText || e.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 160);
    const own = e => !e.closest('[data-qa-map-fixture]');
    const color = e => {
      const s = getComputedStyle(e); let p = e, background = 'rgb(255, 255, 255)', gradient = null;
      while (p) { const ps = getComputedStyle(p), c = rgb(ps.backgroundColor); if (!gradient && ps.backgroundImage !== 'none') gradient = ps.backgroundImage; if ((c[3] ?? 1) >= .99) { background = ps.backgroundColor; break; } p = p.parentElement; }
      const stops = gradient?.startsWith('linear-gradient(') ? gradient.match(/rgba?\([^)]+\)/g) : null;
      const contrasts = stops?.length ? stops.map(stop => ratio(s.color, stop)) : [ratio(s.color, background)];
      return { color: s.color, background, gradient, ratio: Math.min(...contrasts), fontSize: parseFloat(s.fontSize) };
    };
    const nodes = [root, ...root.querySelectorAll('*')].filter(e => own(e) && isVisible(e));
    const texts = nodes.filter(e => [...e.childNodes].some(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim())).map(e => ({ tag: e.tagName, class: e.className, text: text(e), ...color(e), rect: rect(e) }));
    const controls = nodes.filter(e => e.matches('button,a[href],input,select,summary')).map(e => ({ tag: e.tagName, class: e.className, text: text(e), disabled: e.disabled || false, ...color(e), rect: rect(e) }));
    const canvas = [...root.querySelectorAll('.deslocamento-mapa__google')].filter(isVisible).map(e => ({ rect: rect(e), children: e.childElementCount, routes: e.querySelectorAll('[data-qa-map-canvas] path').length }));
    const attribution = [...root.querySelectorAll('[data-qa-attribution]')].filter(isVisible).map(e => {
      const r = rect(e), map = rect(e.closest('.deslocamento-mapa__google')), figure = rect(e.closest('.deslocamento-mapa'));
      return { rect: r, canvas: map, figure, contained: r.x >= map.x - 1 && r.right <= map.right + 1 && r.y >= map.y - 1 && r.bottom <= map.bottom + 1 && map.bottom <= figure.bottom + 1 };
    });
    const nativeIcons = [...root.querySelectorAll('[data-qa-native-icon]')].filter(isVisible).map(e => ({ rect: rect(e), minHeight: getComputedStyle(e).minHeight }));
    return { theme: document.documentElement.dataset.corviaTheme, rect: rect(root), horizontalOverflow: root.scrollWidth - root.clientWidth, documentOverflow: document.documentElement.scrollWidth - innerWidth, texts, controls, canvas, attribution, nativeIcons, nestedInteractive: root.querySelectorAll('button button,button a').length, scrollHeight: root.scrollHeight, clientHeight: root.clientHeight };
  });
  const fail = message => failures.push({ ...active, name, message });
  if (data.theme !== active.theme) fail('Theme mismatch');
  if (data.horizontalOverflow > 2 || data.documentOverflow > 2) fail(`Horizontal overflow ${data.horizontalOverflow}/${data.documentOverflow}`);
  if (data.nestedInteractive) fail('Nested interactive element');
  for (const item of data.texts) {
    if (item.fontSize < 16) fail(`Text below16px: ${item.text} (${item.fontSize})`);
    if (item.ratio < 4.5) fail(`Contrast ${item.ratio.toFixed(2)}: ${item.text} ${item.color}/${item.background}`);
  }
  for (const item of data.controls) if (item.rect.width < 43.5 || item.rect.height < 43.5) fail(`Touch target ${item.rect.width.toFixed(1)}×${item.rect.height.toFixed(1)}: ${item.text}`);
  for (const item of data.controls) if (item.class.includes('atelier-commute__action') && !item.disabled && !item.gradient?.startsWith('linear-gradient(')) fail('Primary commute action lost its Atelier copper treatment');
  for (const attribution of data.attribution) if (!attribution.contained) fail('Attribution stand-in cropped or outside canvas');
  for (const canvas of data.canvas) if (canvas.rect.height < 200) fail(`Canvas collapsed to ${canvas.rect.height}`);
  for (const icon of data.nativeIcons) if (Math.abs(icon.rect.width - 20) > .5 || Math.abs(icon.rect.height - 20) > .5) fail(`SDK-owned20pxSVG contaminated: ${icon.rect.width}×${icon.rect.height}, minHeight=${icon.minHeight}`);
  rows.push({ ...active, name, ...data });
  return data;
}

async function inspectAttribution(page, selector) {
  for (const attribution of await page.locator(`${selector} [data-qa-attribution]`).all()) {
    await attribution.scrollIntoViewIfNeeded();
    const hit = await attribution.evaluate(e => { const r = e.getBoundingClientRect(); const top = document.elementFromPoint(r.x + Math.min(r.width / 2, 35), r.y + r.height / 2); return e === top || e.contains(top); });
    if (!hit) failures.push({ ...active, name: selector, message: 'Attribution stand-in is covered after scrollIntoView' });
  }
}

try {
  for (const theme of themes) for (const scenario of scenarios) {
    active = { theme, scenario };
    let sdkAttempts = 0, sdkFail = scenario === 'sdk-error-retry';
    const context = await browser.newContext({ viewport: viewports[0], locale: 'pt-BR', serviceWorkers: 'block', reducedMotion: 'reduce' });
    await context.addInitScript(({ theme }) => {
      localStorage.setItem('corvia:cardiology-spaces:theme:v1:990091', theme);
      localStorage.setItem('corvia:cardiology-spaces:tour:v3', 'true');
      Object.defineProperty(navigator, 'geolocation', { value: { getCurrentPosition() { throw new Error('Geolocation must not be used in the saved-origin visual fixture'); }, watchPosition() { throw new Error('Geolocation prohibited in visual fixture'); } } });
    }, { theme });
    await context.route('**/*', async route => {
      const req = route.request(), url = new URL(req.url());
      if (url.hostname === 'maps.googleapis.com' && url.pathname === '/maps/api/js') {
        sdkAttempts++;
        requests.push({ ...active, path: '/maps/api/js', method: req.method(), fixture: sdkFail ? 'intercepted-sdk-failure' : 'intercepted-svg-sdk' });
        return sdkFail ? route.abort('failed') : route.fulfill({ status: 200, contentType: 'application/javascript', body: sdkSource });
      }
      if (!url.pathname.startsWith('/api/')) {
        if (url.origin === base.origin && ['GET', 'HEAD'].includes(req.method())) return route.continue();
        blocked.push({ ...active, origin: url.origin, path: url.pathname, method: req.method() }); return route.abort('blockedbyclient');
      }
      requests.push({ ...active, path: url.pathname, method: req.method(), fixture: 'local-api' });
      const reply = (body, status = 200) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
      if (url.pathname === '/api/auth/session-status') return reply({ authenticated: true });
      if (url.pathname === '/api/auth/me') return reply(profile);
      if (url.pathname === '/api/version') return reply({ commit: 'isolated-mobility-visual-fixture' });
      if (url.pathname === '/api/agenda/mobility/prepare-next-target' || url.pathname === '/api/agenda/mobility/next-target') return reply(target);
      if (url.pathname === '/api/agenda/mobility/map-config') return reply({ provider: 'Google Maps', configured: true, api_key: 'fixture-intercepted-not-a-real-key' });
      if (url.pathname === '/api/agenda/mobility/preferences') return reply({ enabled: true, traffic_configured: true, day_start_origin_mode: 'saved_location', day_start_location_id: origin.id, day_start_location: origin, day_end_destination_location_id: null });
      if (url.pathname === '/api/agenda/mobility/day-context') return reply({ stage: 'before_first', first_target: target, last_target: target, start_location: origin, end_location: null });
      if (url.pathname.startsWith('/api/agenda/mobility/commute-')) return reply({ status: scenario === 'no-route' ? 'no_route' : 'ok', provider: 'Google Maps', updated_at: new Date().toISOString(), destination: target, origin_location: origin, routes: scenario === 'no-route' ? [] : scenario === 'no-geometry' ? sampleRoutes.map(({ geometry, ...r }) => ({ ...r, geometry_available: false })) : sampleRoutes, tips: ['Dados fictícios de teste local. Não utilizar para navegação.'] });
      if (['/api/agenda/appointments', '/api/agenda/commitments', '/api/agenda/work-routines', '/api/agenda/integrations'].includes(url.pathname)) return reply([]);
      if (url.pathname === '/api/clinical-change-approvals/count') return reply({ pending: 0 });
      if (url.pathname === '/api/favorites/status') return reply({ favorited: false, available: true });
      return reply({ detail: 'Serviço não conectado nesta revisão visual isolada.' }, 503);
    });
    const page = await context.newPage(); page.setDefaultTimeout(15000); page.setDefaultNavigationTimeout(30000);
    page.on('pageerror', error => errors.push({ ...active, message: String(error) }));
    try {
      for (const viewport of viewports) {
        active = { theme, scenario, viewport: `${viewport.width}x${viewport.height}` };
        sdkFail = scenario === 'sdk-error-retry';
        await page.setViewportSize(viewport);
        await page.goto(base.origin + '/?espaco=consultorio&modo=complete', { waitUntil: 'domcontentloaded' });
        await page.locator('.atelier-day > summary').click();
        await page.locator('.atelier-commute').waitFor({ state: 'visible' });
        await page.locator('.atelier-commute').scrollIntoViewIfNeeded();
        if (['success', 'sdk-error-retry'].includes(scenario)) await page.locator('.atelier-commute__map').waitFor({ state: 'visible' });
        if (scenario === 'sdk-error-retry') await page.locator('.atelier-commute .deslocamento-mapa__status button').waitFor();
        else if (scenario === 'success') await page.locator('.atelier-commute [data-qa-attribution]').waitFor();
        await settle(page);
        const stem = `${scenario}-${theme}-${viewport.width}x${viewport.height}`;
        await measure(page, '.atelier-commute', 'home-preview');
        await inspectAttribution(page, '.atelier-commute');
        await page.locator('.atelier-commute').screenshot({ path: path.join(out, `${stem}-preview.png`) });
        await page.locator('.atelier-commute__open').click();
        await page.locator('.spaces-travel').waitFor({ state: 'visible' });
        if (scenario === 'sdk-error-retry') await page.locator('.spaces-travel .deslocamento-mapa__status button').waitFor();
        else await page.locator('.spaces-travel [data-qa-attribution]').waitFor();
        await settle(page);
        const result = await measure(page, '.spaces-travel', 'expanded-map');
        assert.equal(await page.locator('.spaces-travel .deslocamento-rotas__lista > button').count(), scenario === 'no-route' ? 0 : 2, 'Unexpected route-choice count');
        if (scenario === 'success') assert(result.canvas.some(c => c.routes >= 3), 'Component did not draw the received route + halo + alternative');
        if (scenario === 'no-geometry' || scenario === 'no-route') assert(result.canvas.every(c => c.routes === 0), 'A route was invented without geometry');
        await inspectAttribution(page, '.spaces-travel');
        await page.locator('.spaces-travel').evaluate(e => { e.scrollTop = 0; });
        await page.screenshot({ path: path.join(out, `${stem}-dialog.png`) });
        if (scenario === 'success') {
          const alternative = page.locator('.spaces-travel .deslocamento-rotas__lista > button').nth(1);
          await alternative.click(); assert.equal(await alternative.getAttribute('aria-pressed'), 'true');
          // Enter keyboard modality: a click followed by programmatic focus()
          // correctly does not require :focus-visible in Chromium.
          await page.keyboard.press('Tab'); await page.keyboard.press('Shift+Tab');
          assert(await alternative.evaluate(e => e === document.activeElement), 'Keyboard did not return to selected route');
          const focus = await alternative.evaluate(e => ({ outline: getComputedStyle(e).outlineStyle, width: getComputedStyle(e).outlineWidth, color: getComputedStyle(e).outlineColor }));
          assert.notEqual(focus.outline, 'none', 'Route focus outline missing');
          rows.push({ ...active, name: 'alternative-selected-focus', ...focus });
          await page.screenshot({ path: path.join(out, `${stem}-alternative-focus.png`) });
        }
        if (scenario === 'sdk-error-retry') {
          sdkFail = false;
          await page.locator('.spaces-travel .deslocamento-mapa__status button').click();
          await page.locator('.spaces-travel [data-qa-attribution]').waitFor();
          await settle(page); await measure(page, '.spaces-travel', 'sdk-recovered');
          await inspectAttribution(page, '.spaces-travel');
          await page.locator('.spaces-travel').evaluate(e => { e.scrollTop = 0; });
          await page.screenshot({ path: path.join(out, `${stem}-recovered.png`) });
          assert(sdkAttempts >= 2, 'Retry did not issue another intercepted SDK load');
        }
        await page.keyboard.press('Escape');
        await page.locator('.spaces-travel').waitFor({ state: 'detached' });
        await settle(page); // The dialog hook restores focus in requestAnimationFrame.
        assert(await page.locator('.atelier-commute__open').evaluate(e => e === document.activeElement), 'Focus not restored to preview trigger');
        console.log(JSON.stringify({ ...active, checked: true, accumulatedFailures: failures.length }));
      }
    } catch (error) {
      failures.push({ ...active, name: 'runner-error', message: String(error.stack || error) });
      await page.screenshot({ path: path.join(out, `failure-${theme}-${scenario}.png`) }).catch(() => {});
    } finally { await context.close(); }
  }
} finally {
  await browser.close();
  fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify({ kind: 'isolated-mobility-fixture-visual-qa', limitation: 'React UI and intercepted Maps overlay geometry only; no real Google cartography, API availability, credentials, geolocation or production records. Attribution is a labelled stand-in. No screen-reader certification.', rows, failures, errors, requests, blocked }, null, 2));
}
console.log(JSON.stringify({ out, checks: rows.length, failures: failures.length, errors: errors.length }));
if (failures.length || errors.length) process.exitCode = 1;
