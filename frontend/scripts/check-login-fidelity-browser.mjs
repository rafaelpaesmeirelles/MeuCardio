// Run against an isolated frontend preview; never submits real credentials.
// CORVIA_PLAYWRIGHT_MODULE may point to an existing Playwright installation.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
const { chromium } = await import(process.env.CORVIA_PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.CORVIA_QA_URL || 'http://127.0.0.1:18949';
const out = process.env.CORVIA_QA_OUTPUT || '/tmp/corvia-login-fidelity-qa';
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
const results = [];
const overlaps = (a, b) => Math.min(a.right,b.right)-Math.max(a.left,b.left)>1 && Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1;
try {
  for (const width of [320,360,390,412,768,1024,1440,1648]) {
    for (const theme of ['dark','light']) {
      const context = await browser.newContext({ viewport:{width,height:928}, serviceWorkers:'block' });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(`${base}/entrar`, { waitUntil:'networkidle' });
      await page.locator(`label:has(input[name="tema-publico"][value="${theme}"])`).click();
      await page.locator('.login-gateway__galaxy-canvas[data-ready="true"]').waitFor();
      const state = await page.evaluate(() => {
        const box = suffix => document.querySelector(`.login-gateway__${suffix}`).getBoundingClientRect().toJSON();
        const image = document.querySelector('.login-gateway__galaxy-image');
        return { width:innerWidth, scroll:document.documentElement.scrollWidth, theme:document.querySelector('main').dataset.loginTheme,
          fallback:getComputedStyle(image).opacity, core:box('core'), hero:box('hero'), head:box('console-head'), form:box('form'), join:box('join'),
          spaces:['ensino','hospital','pesquisa','consultorio','gestao'].map(id=>({id,...box(`space--${id}`)})) };
      });
      assert.equal(state.theme, theme);
      assert.ok(state.scroll<=width, `Horizontal overflow at ${width}/${theme}`);
      assert.equal(state.fallback,'0','Fallback must disappear after the first canvas frame');
      for (const card of state.spaces) {
        assert.ok(!overlaps(card,state.core), `${card.id} covers heart at ${width}/${theme}`);
        assert.ok(!overlaps(card,state.hero), `${card.id} covers title at ${width}/${theme}`);
        for (const other of state.spaces) if (card.id!==other.id) assert.ok(!overlaps(card,other), `${card.id} covers ${other.id}`);
      }
      assert.ok(state.head.bottom<=state.form.top+1, 'Identity header must stay above form');
      if (width>900) assert.ok(state.join.left>=state.form.right, 'Desktop join panel belongs on the right');
      else assert.ok(state.join.top>=state.form.bottom, 'Mobile join panel belongs below form');
      assert.deepEqual(errors,[]);
      if ([412,1648].includes(width)) await page.screenshot({path:path.join(out,`${width}-${theme}.png`),fullPage:true});
      results.push({width,theme,status:'passed'});
      console.log(`PASS ${width}px ${theme}: geometry, theme, single galaxy layer`);
      await context.close();
    }
  }
  const context = await browser.newContext({reducedMotion:'reduce',serviceWorkers:'block'});
  const page = await context.newPage();
  await page.goto(`${base}/entrar`,{waitUntil:'networkidle'});
  const canvas=page.locator('.login-gateway__galaxy-canvas[data-ready="true"]');
  await canvas.waitFor();
  const frame=()=>canvas.evaluate(el=>el.toDataURL());
  const stillA=await frame();
  await page.waitForTimeout(180);
  assert.equal(await frame(),stillA,'Reduced-motion preference must produce a still galaxy');
  await page.emulateMedia({reducedMotion:'no-preference'});
  const movingA=await frame();
  await page.waitForTimeout(180);
  assert.notEqual(await frame(),movingA,'Galaxy must animate without reduced-motion preference');
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.waitForTimeout(60);
  const stillB=await frame();
  await page.waitForTimeout(180);
  assert.equal(await frame(),stillB,'Runtime preference change must stop the animation');
  results.push({motion:'reduce / animate / reduce',status:'passed'});
  console.log('PASS reduced motion and runtime preference changes');
  await context.close();
  await writeFile(path.join(out,'report.json'),JSON.stringify(results,null,2));
} finally { await browser.close(); }
