// Local-only geometry regression test. All API responses are synthetic.
// Build first; provide CORVIA_PLAYWRIGHT_MODULE when Playwright is not installed locally.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const { chromium } = await import(process.env.CORVIA_PLAYWRIGHT_MODULE || 'playwright');
const dist = path.resolve(fileURLToPath(new URL('../dist/', import.meta.url)));
const out = process.env.CORVIA_QA_OUTPUT || '/tmp/corvia-layout-geometry-qa';
fs.mkdirSync(out, { recursive: true });
if (!fs.existsSync(path.join(dist, 'index.html'))) throw new Error('Build frontend first.');
const mime = { '.html':'text/html', '.js':'text/javascript', '.css':'text/css', '.svg':'image/svg+xml', '.webp':'image/webp', '.png':'image/png', '.woff2':'font/woff2' };
const server = http.createServer((req, res) => {
  const requested = path.resolve(dist, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
  if (requested !== dist && !requested.startsWith(dist + path.sep)) { res.writeHead(403); res.end(); return; }
  const file = fs.existsSync(requested) && fs.statSync(requested).isFile() ? requested : path.join(dist, 'index.html');
  res.writeHead(200, { 'Content-Type':mime[path.extname(file)] || 'application/octet-stream', 'Cache-Control':'no-store' });
  fs.createReadStream(file).pipe(res);
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch({ headless:true });
const results = [], failures = [];
const user = { id:999999, nome:'Usuário QA', email:'geometry@example.invalid', role:'medico', ativo:true, onboarding_pendente:false, profile_completion_required:false, kyc_required:false, investidor:false };
try {
  for (const width of [360, 390, 412, 768, 1024, 1440]) for (const theme of ['dark', 'light']) {
    const context = await browser.newContext({ viewport:{width,height:900}, colorScheme:theme, serviceWorkers:'block' });
    await context.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.pathname.startsWith('/api/')) {
        let data = [];
        if (url.pathname.endsWith('/auth/session-status')) data = {authenticated:true};
        else if (url.pathname.endsWith('/auth/me')) data = user;
        else if (url.pathname.endsWith('/version')) data = {commit:'layout-geometry-qa'};
        else if (url.pathname.includes('/mobility/')) data = url.pathname.endsWith('prepare-next-target') ? null : {enabled:false,first_target:null,last_target:null};
        return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(data)});
      }
      if (url.origin !== origin) return route.abort();
      return route.continue();
    });
    await context.addInitScript(() => {
      const rotate = CanvasRenderingContext2D.prototype.rotate;
      CanvasRenderingContext2D.prototype.rotate = function(angle) {
        if (this.canvas.classList.contains('galaxy-theme-toggle__canvas-live')) window.__miniAngle = angle;
        return rotate.call(this, angle);
      };
    });
    const page = await context.newPage();
    page.on('pageerror', e => failures.push(`${width}/${theme}: ${e.message}`));
    await page.goto(origin, {waitUntil:'networkidle'});
    await page.locator('.spaces-choice').waitFor({timeout:15000});
    if (await page.locator('html').getAttribute('data-corvia-theme') !== theme) await page.locator('.galaxy-theme-toggle').click();
    await page.waitForFunction(t => document.documentElement.dataset.corviaTheme === t, theme);
    for (const scene of ['choice', 'home']) {
      if (scene === 'home') {
        await page.locator('.spaces-choice__cards button').first().click();
        await page.locator('.spaces-home').waitFor();
      }
      await page.waitForTimeout(350);
      const metrics = await page.evaluate(() => {
        const rect = selector => {
          const e = document.querySelector(selector); if (!e) return null;
          const r = e.getBoundingClientRect();
          return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};
        };
        return {brand:rect('.spaces-brand'), galaxy:rect('.galaxy-theme-toggle__canvas-live'), toggle:rect('.galaxy-theme-toggle'), user:rect('.spaces-user'), header:rect('main > header'), eyebrow:rect('.spaces-eyebrow'), search:rect('.spaces-everything-search'), input:rect('.spaces-everything-search input'), brandTextVisible:getComputedStyle(document.querySelector('.spaces-brand > span')).display !== 'none', direction:document.querySelector('.galaxy-theme-toggle__canvas-live')?.dataset.rotationDirection, angle:window.__miniAngle ?? null};
      });
      const overlap = (a,b) => a && b && Math.min(a.right,b.right)-Math.max(a.x,b.x)>1 && Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y)>1;
      const key = `${width}/${theme}/${scene}`;
      if (!metrics.brandTextVisible) failures.push(`${key}: brand text hidden`);
      if (overlap(metrics.brand, metrics.galaxy)) failures.push(`${key}: brand/galaxy overlap`);
      if (overlap(metrics.galaxy, metrics.search)) failures.push(`${key}: galaxy/search overlap`);
      if (overlap(metrics.galaxy, metrics.user)) failures.push(`${key}: galaxy/avatar overlap`);
      if (metrics.user.right > width + 1) failures.push(`${key}: avatar outside viewport`);
      if (width <= 900 && scene === 'choice' && metrics.eyebrow.y - metrics.header.bottom > 36) failures.push(`${key}: excessive top gap`);
      if (scene === 'home' && metrics.input.width < 20) failures.push(`${key}: search input too narrow`);
      const expectedDirection = scene === 'choice' && theme === 'dark' ? 'clockwise' : 'counterclockwise';
      if (metrics.direction !== expectedDirection || metrics.angle === null || metrics.angle * (expectedDirection === 'clockwise' ? 1 : -1) <= 0) failures.push(`${key}: rotation context mismatch`);
      results.push({width, theme, scene, ...metrics});
      console.log(key, JSON.stringify(metrics));
      if ([390,768].includes(width)) await page.screenshot({path:path.join(out, `${width}-${theme}-${scene}.png`)});
    }
    await context.close();
  }
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
fs.writeFileSync(path.join(out,'results.json'), JSON.stringify({results,failures},null,2));
console.log(JSON.stringify({cases:results.length,failures},null,2));
if (failures.length) process.exitCode = 1;
