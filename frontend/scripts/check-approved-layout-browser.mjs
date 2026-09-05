// Browser regression check with synthetic data; never sends API calls to production.
import fs from "node:fs/promises";
import path from "node:path";
const { chromium } = await import(process.env.CORVIA_PLAYWRIGHT_MODULE || "playwright");
const base = new URL(process.env.CORVIA_QA_URL || "http://127.0.0.1:18765");
if (!["127.0.0.1", "localhost"].includes(base.hostname)) throw new Error("QA requires a loopback URL");
const output = process.env.CORVIA_QA_OUTPUT || "/root/corvia-layout-qa-20260905";
await fs.mkdir(output, { recursive: true });
const replay = process.env.CORVIA_QA_REPLAY;
const browser = replay ? null : await chromium.launch({ headless: true, executablePath: process.env.CORVIA_CHROMIUM_PATH });
const records = replay ? JSON.parse(await fs.readFile(replay, "utf8")) : [];
const user = { id: 99999901, nome: "Médico QA", email: "qa@example.invalid", role: "medico", ativo: true,
  profile_completion_required: false, kyc_required: false, onboarding_pendente: false, investidor: false };
try {
  if (!replay) for (const width of [360, 390, 600, 768, 1024, 1600]) {
    for (const mode of ["choice", "home"]) for (const theme of ["light", "dark"]) {
      const page = await browser.newPage({ viewport: { width, height: width > 900 ? 900 : 844 }, serviceWorkers: "block" });
      const errors = [];
      page.on("pageerror", error => errors.push(error.message));
      await page.route("**/*", async route => {
        const url = new URL(route.request().url());
        if (url.origin !== base.origin) return route.abort();
        if (!url.pathname.startsWith("/api/")) return route.continue();
        let body = [];
        if (url.pathname.endsWith("/auth/session-status")) body = { authenticated: true };
        else if (url.pathname.endsWith("/auth/me")) body = user;
        else if (url.pathname.includes("/mobility/prepare-next-target")) body = null;
        else if (url.pathname.includes("/mobility/")) body = {};
        return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
      });
      await page.addInitScript(({ mode, theme, userId }) => {
        localStorage.setItem(`corvia:cardiology-spaces:theme:v1:${userId}`, theme);
        if (mode === "home") sessionStorage.setItem("corvia:cardiology-spaces:mode", "complete");
        window.__miniAngles = [];
        const originalRotate = CanvasRenderingContext2D.prototype.rotate;
        CanvasRenderingContext2D.prototype.rotate = function (angle) {
          if (this.canvas.classList.contains("galaxy-theme-toggle__canvas-live") && window.__miniAngles.length < 8) window.__miniAngles.push(angle);
          return originalRotate.call(this, angle);
        };
      }, { mode, theme, userId: user.id });
      await page.goto(base.href, { waitUntil: "networkidle", timeout: 45000 });
      await page.waitForSelector(".galaxy-theme-toggle__canvas-live[data-ready='true']", { timeout: 15000 });
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(200);
      const metrics = await page.evaluate(() => {
        const box = selector => {
          const e = document.querySelector(selector); if (!e) return null;
          const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
          return { x: r.x, y: r.y, w: r.width, h: r.height, right: r.right, bottom: r.bottom, display: s.display };
        };
        const content = document.querySelector(".spaces-choice__content");
        return { brand: box(".spaces-brand"), label: box(".spaces-brand > span"), toggle: box(".galaxy-theme-toggle"),
          canvas: box(".galaxy-theme-toggle__canvas-live"), search: box(".spaces-everything-search"),
          avatar: box(".spaces-user"), header: box(".spaces-home__topbar, .spaces-choice > header"),
          nav: box(".spaces-home__topbar > nav"), content: box(".spaces-choice__content"),
          contentPadding: content ? getComputedStyle(content).paddingTop : null,
          width: document.documentElement.scrollWidth, theme: document.documentElement.dataset.corviaTheme, angles: window.__miniAngles };
      });
      const name = `${mode}-${theme}-${width}`;
      records.push({ name, viewport: width, mode, errors, ...metrics });
      await page.screenshot({ path: path.join(output, `${name}.png`), fullPage: false });
      console.log(name, JSON.stringify({ brandGap: metrics.canvas.x - metrics.brand.right,
        searchGap: metrics.search ? metrics.search.x - metrics.canvas.right : null,
        padding: metrics.contentPadding, width: metrics.width, theme: metrics.theme, errors }));
      await page.close();
    }
  }
} finally { if (browser) await browser.close(); }
await fs.writeFile(path.join(output, "geometry.json"), JSON.stringify(records, null, 2));
const failures = [];
const overlap = (a, b) => a && b && a.right > b.x + 1 && b.right > a.x + 1 && a.bottom > b.y + 1 && b.bottom > a.y + 1;
for (const r of records) {
  if (r.errors.length) failures.push(`${r.name}: ${r.errors.join("; ")}`);
  if (r.label.display === "none") failures.push(`${r.name}: brand label hidden`);
  if (overlap(r.brand, r.canvas)) failures.push(`${r.name}: galaxy overlaps brand`);
  if (overlap(r.canvas, r.search)) failures.push(`${r.name}: galaxy overlaps search`);
  if (overlap(r.canvas, r.avatar)) failures.push(`${r.name}: galaxy overlaps avatar`);
  if (r.width > r.viewport + 1) failures.push(`${r.name}: horizontal overflow`);
  if (r.mode === "choice" && r.viewport <= 900 && r.contentPadding !== "34px") failures.push(`${r.name}: excess top spacing`);
  const deltas = r.angles.slice(1).map((angle, i) => Math.atan2(Math.sin(angle - r.angles[i]), Math.cos(angle - r.angles[i])));
  if (deltas.length < 2 || !deltas.every(delta => delta > 0)) failures.push(`${r.name}: rotation is not clockwise`);
}
await fs.writeFile(path.join(output, "result.json"), JSON.stringify({ cases: records.length, failures }, null, 2));
console.log(JSON.stringify({ cases: records.length, failures }, null, 2));
if (failures.length) process.exitCode = 1;
