// Computed colors, not antialiased screenshot pixels. Unknown paint stacks are
// explicitly left for screenshot review; they must never become false passes.
export function measureTextContrast(elements) {
  const rgba = value => {
    if (value === 'transparent') return [0, 0, 0, 0];
    const match = /^rgba?\(([^)]+)\)$/.exec(value);
    if (!match || match[1].includes('%')) return null;
    const parts = match[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    if (parts.length === 3) parts.push(1);
    return parts.length === 4 && parts.every(Number.isFinite) ? parts : null;
  };
  const over = (front, back) => {
    const alpha = front[3] + back[3] * (1 - front[3]);
    return [...front.slice(0, 3).map((channel, i) => alpha ? (channel * front[3] + back[i] * back[3] * (1 - front[3])) / alpha : 0), alpha];
  };
  const luminance = color => color.slice(0, 3).map(channel => {
    const value = channel / 255;
    return value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4;
  }).reduce((sum, channel, i) => sum + channel * [.2126, .7152, .0722][i], 0);
  return elements.map(element => {
    const style = getComputedStyle(element);
    const placeholder = element.matches('input, textarea') && !element.value && element.getAttribute('placeholder');
    const textStyle = placeholder ? getComputedStyle(element, '::placeholder') : style;
    const sample = { tag: element.tagName, className: element.className, text: (placeholder || element.textContent || element.value || element.getAttribute('aria-label') || '').trim().slice(0, 180), color: textStyle.color, minimum: parseFloat(textStyle.fontSize) >= 24 || parseFloat(textStyle.fontSize) >= 56 / 3 && Number(textStyle.fontWeight) >= 700 ? 3 : 4.5 };
    const unknown = reason => ({ ...sample, status: 'indeterminate', reason });
    if (!element.getClientRects().length || element.matches(':disabled')) return { ...sample, status: 'inactive' };
    if (placeholder && Number(textStyle.opacity) !== 1) return unknown('placeholder opacity needs screenshot review');
    let background = [0, 0, 0, 0];
    for (let current = element; current; current = current.parentElement) {
      const layer = getComputedStyle(current);
      if (Number(layer.opacity) !== 1 || layer.filter !== 'none' || layer.mixBlendMode !== 'normal') return unknown('group opacity/filter/blend needs screenshot review');
      if (background[3] < 1) {
        if (layer.backgroundImage !== 'none') return unknown('gradient/image behind text needs screenshot review');
        for (const pseudo of ['::before', '::after']) {
          const paint = getComputedStyle(current, pseudo);
          if (paint.content !== 'none' && paint.content !== 'normal' && paint.display !== 'none' && Number(paint.opacity) > 0 && (paint.backgroundImage !== 'none' || (rgba(paint.backgroundColor)?.[3] ?? 1) > 0)) return unknown('painted pseudo-element needs screenshot review');
        }
        const color = rgba(layer.backgroundColor);
        if (!color) return unknown('unsupported background color space');
        background = over(background, color);
      }
    }
    if (background[3] < 1) return unknown('no opaque backing color resolved');
    const foreground = rgba(textStyle.color);
    if (!foreground) return unknown('unsupported foreground color space');
    const a = luminance(over(foreground, background)), b = luminance(background);
    const ratio = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    return { ...sample, background, ratio, status: ratio >= sample.minimum ? 'pass' : 'fail' };
  });
}

// Runs only inside the existing isolated Visual QA workflow, using synthetic API fixtures.
// No decisions are submitted: every clinical-approval mutation is intercepted and fails the gate.
export async function inspectFavoritesAndApprovals({ page: sourcePage, base, out, report, approvalTitle }) {
  // Earlier real-stack surfaces deliberately exercise the PWA. Isolate only
  // synthetic API fixtures: a controlling service worker can bypass route().
  const context = await sourcePage.context().browser().newContext({
    storageState: await sourcePage.context().storageState(),
    viewport: sourcePage.viewportSize(),
    locale: 'pt-BR', colorScheme: 'dark', serviceWorkers: 'block',
  });
  const page = await context.newPage();
  page.on('pageerror', error => report.pageErrors.push(String(error)));
  let role = 'admin';
  let owner = true;
  let approvalMutationRequests = 0;
  let physicianNoticeRequests = 0;
  const cases = [];
  const proposal = {
    id: 99001, version: 3, status: 'pending', created_at: '2026-09-10T12:00:00Z',
    guideline: { id: 99002, slug: 'visual-qa-proposal', title: 'Proposta visual de revisão de conteúdo científico com comparação detalhada antes e depois', doi: '10.0000/visual-qa-fixture', url: 'https://example.org/visual-qa-source' },
    proposed_changes: [{ item_type: 'disease', item_id: 99003, label: 'Conteúdo de demonstração para revisão administrativa', before: { treatment_summary: 'Texto atual de demonstração. Nenhuma conduta clínica real.' }, after: { treatment_summary: 'Texto proposto de demonstração, aguardando análise e consentimento.' }, changed_fields: ['treatment_summary'], change_summary_pt: 'Comparação fictícia para verificar a leitura e os controles de aprovação.', effect_kind: 'clinical_content', impact_scope: { fluxograma: true, emergency_protocols: [] }, source_url: 'https://example.org/visual-qa-source' }],
    audit_events: [{ action: 'clinical_change_proposed', at: '2026-09-10T12:00:00Z' }],
  };
  const favorites = [
    { id: 99101, item_type: 'estudo', item_id: 99111, item_slug: 'visual-qa-study', title: 'Fibrilação atrial: publicação científica de demonstração para leitura e favoritos', url: '/estudos/visual-qa-study', meta: 'Exemplo visual · Cardiologia', available: true, reading: { entity_type: 'estudo', slug: 'visual-qa-study' }, private_reading: null },
    { id: 99102, item_type: 'documento_cientifico_privado', item_id: 99112, item_slug: '99112', title: 'Meu documento científico privado de demonstração', url: '/documentos-cientificos-ia?document=99112', meta: 'Biblioteca privada', available: true, reading: null, private_reading: { document_id: 99112 } },
    { id: 99103, item_type: 'documento', item_id: 99113, item_slug: 'visual-qa-unavailable', title: 'Conteúdo indisponível', url: null, meta: null, available: false, unavailable_reason: 'Este conteúdo não está disponível atualmente. Você pode remover o favorito.', reading: null, private_reading: null },
  ];
  const fulfill = (route, body, status = 200) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });
  const handler = async route => {
    const url = new URL(route.request().url());
    const method = route.request().method();
    if (url.pathname === '/api/auth/me') {
      const response = await route.fetch();
      const profile = await response.json();
      return fulfill(route, { ...profile, role });
    }
    if (url.pathname.startsWith('/api/clinical-change-approvals')) {
      if (method !== 'GET') { approvalMutationRequests++; return fulfill(route, { detail: 'Visual QA blocks every approval mutation.' }, 403); }
      if (url.pathname === '/api/clinical-change-approvals/count') {
        if (role === 'medico') physicianNoticeRequests++;
        return owner && role === 'admin' ? fulfill(route, { pending: 1 }) : fulfill(route, { detail: 'Owner-only notice.' }, 403);
      }
      if (!owner || role !== 'admin') return fulfill(route, { detail: 'Somente o administrador responsável pode consultar propostas clínicas.' }, 403);
      return fulfill(route, url.pathname === '/api/clinical-change-approvals' ? { items: [proposal], total: 1 } : proposal);
    }
    if (url.pathname === '/api/favorites' && method === 'GET') return fulfill(route, favorites);
    if (url.pathname === '/api/favorites/status') return fulfill(route, { favorited: false, favorite_id: null, available: true, item_type: url.searchParams.get('item_type'), item_id: null, item_slug: url.searchParams.get('item_slug') });
    if (url.pathname.startsWith('/api/favorites') && method !== 'GET') return fulfill(route, { detail: 'Visual QA does not change favorites.' }, 403);
    return route.continue();
  };
  await context.route('**/api/**', handler);
  const fail = message => report.failures.push(`favorites-approvals: ${message}`);
  async function setTheme(theme) {
    if (await page.locator('html').getAttribute('data-corvia-theme') !== theme) {
      // Internal pages expose the theme selector in the account menu. The
      // galaxy control belongs to Home/choice and is not present in AppFrame.
      const account = page.locator('.cv-account__trigger');
      if (await account.getAttribute('aria-expanded') !== 'true') await account.click();
      await page.locator('.cv-account-menu').getByRole('radio', { name: theme === 'light' ? /Modo claro/ : /Modo escuro/ }).click();
      if (await account.getAttribute('aria-expanded') === 'true') await account.click();
      await page.locator('.cv-account-menu').waitFor({ state: 'hidden' });
    }
    await page.waitForFunction(value => document.documentElement.getAttribute('data-corvia-theme') === value, theme);
  }
  async function contrast(selector, name) {
    const metrics = await page.locator(selector).evaluateAll(measureTextContrast);
    if (!metrics.length) fail(`${name}: no text selected for contrast measurement`);
    for (const item of metrics) if (item.status === 'fail') fail(`${name}: contrast ${item.ratio.toFixed(3)} < ${item.minimum} for ${item.tag} ${item.text}`);
    return metrics;
  }
  async function geometry(selector, name) {
    const metrics = await page.locator(selector).evaluate(element => {
      const box = element.getBoundingClientRect();
      const range = document.createRange(); range.selectNodeContents(element);
      const lines = [...range.getClientRects()].filter(rect => rect.width > 0 && rect.height > 0);
      return { text: element.textContent.trim(), left: box.left, right: box.right, width: box.width, scrollWidth: element.scrollWidth, clientWidth: element.clientWidth, viewport: innerWidth, documentWidth: document.documentElement.scrollWidth, textRects: lines.map(rect => ({ left: rect.left, right: rect.right, top: rect.top })) };
    });
    if (metrics.left < -1 || metrics.right > metrics.viewport + 1 || metrics.scrollWidth > metrics.clientWidth + 1 || metrics.documentWidth > metrics.viewport + 12 || metrics.textRects.some(rect => rect.left < -1 || rect.right > metrics.viewport + 1)) fail(`${name}: horizontal overflow in ${selector}`);
    return metrics;
  }
  try {
    for (const width of [360, 1440]) {
      await page.setViewportSize({ width, height: width === 360 ? 900 : 1000 });
      for (const theme of ['light', 'dark']) {
        role = 'admin'; owner = true;
        const name = `${width}-${theme}`;
        await page.goto(`${base}/admin/mudancas-clinicas`, { waitUntil: 'networkidle' });
        await setTheme(theme);
        const heading = page.locator('.admin-clinical-changes > header h1');
        await heading.waitFor({ state: 'visible' });
        if ((await heading.innerText()).trim() !== approvalTitle) fail(`${name}: administrative title differs from the approved wording`);
        await page.locator('.clinical-change-notice').waitFor({ state: 'visible' });
        const ownerNotice = await page.locator('.clinical-change-notice').innerText();
        if (!/1 mudança.*aprova/i.test(ownerNotice)) fail(`${name}: owner pending-change notice missing count or approval access`);
        const headingMetrics = await geometry('.admin-clinical-changes > header h1', `${name}/approval-title`);
        await page.locator('.admin-clinical-changes__list button').first().click();
        const approve = page.getByRole('button', { name: 'Aprovar e aplicar alterações', exact: true });
        await approve.waitFor({ state: 'visible' });
        const approvalDisabled = await approve.isDisabled();
        const consentChecked = await page.locator('.admin-clinical-changes__decision input[type="checkbox"]').isChecked();
        if (!approvalDisabled || consentChecked) fail(`${name}: approval enabled before explicit review consent`);
        await geometry('.admin-clinical-changes', `${name}/approval-comparison`);
        const approvalContrast = await contrast('.clinical-change-notice a strong, .clinical-change-notice p, .admin-clinical-changes > header h1, .admin-clinical-changes__decision label, .admin-clinical-changes__decision legend, .admin-clinical-changes__decision button:enabled', `${name}/approval-text`);
        await heading.scrollIntoViewIfNeeded();
        await page.screenshot({ path: `${out}/approval-owner-${name}.png`, fullPage: false });
        await page.locator('.admin-clinical-changes__comparison').scrollIntoViewIfNeeded();
        await page.screenshot({ path: `${out}/approval-comparison-${name}.png`, fullPage: false });
        cases.push({ name, surface: 'approval-owner', heading: headingMetrics, ownerNotice, approvalDisabled, consentChecked, contrast: approvalContrast, fixtureOnly: true });

        await page.goto(`${base}/favoritos`, { waitUntil: 'networkidle' });
        await setTheme(theme);
        await page.locator('.favorites-page__item').nth(2).waitFor({ state: 'visible' });
        const favoriteMetrics = await geometry('.favorites-page', `${name}/favorites`);
        const favoriteContrast = await contrast('.favorites-page h1, .favorites-page h2, .favorites-page h2 a, .favorites-page p, .favorites-page label, .favorites-page input:enabled, .favorites-page select:enabled, .favorites-page button:enabled, .favorites-page__private-reading a', `${name}/favorite-text`);
        const publicReaderCount = await page.locator('.favorites-page__item').nth(0).locator('.scientific-reading-access').count();
        const privateCard = page.locator('.favorites-page__item').nth(1);
        const privateLinks = await privateCard.locator('.favorites-page__private-reading a').evaluateAll(links => links.map(link => link.getAttribute('href')));
        const unavailableCard = page.locator('.favorites-page__item').nth(2);
        const unavailableRemovable = await unavailableCard.getByRole('button', { name: 'Remover dos favoritos: Conteúdo indisponível', exact: true }).isEnabled();
        if (publicReaderCount !== 1 || await privateCard.locator('.scientific-reading-access').count() !== 0 || privateLinks.length !== 3 || privateLinks.some(link => !/^\/documentos-cientificos-ia\?document=99112&leitura=(original|resumo|traduzido)$/.test(link))) fail(`${name}: public/private scientific reading boundaries incorrect`);
        if (!unavailableRemovable || await unavailableCard.locator('a').count()) fail(`${name}: unavailable favorite must remain removable without source links`);
        for (let index = 0; index < 3; index++) {
          await page.locator('.favorites-page__item').nth(index).scrollIntoViewIfNeeded();
          await page.screenshot({ path: `${out}/favorites-${name}-${['public', 'private', 'unavailable'][index]}.png`, fullPage: false });
        }
        cases.push({ name, surface: 'favorites', geometry: favoriteMetrics, publicReaderCount, privateLinks, unavailableRemovable, contrast: favoriteContrast, fixtureOnly: true });

        owner = false;
        await page.goto(`${base}/admin/mudancas-clinicas`, { waitUntil: 'networkidle' });
        await page.getByText('A revisão e a decisão destas mudanças estão restritas ao administrador responsável pelo CorVIA.', { exact: true }).waitFor({ state: 'visible' });
        if (await page.locator('.admin-clinical-changes__list button').count() || await page.getByRole('button', { name: 'Aprovar e aplicar alterações', exact: true }).count() || await page.getByText(proposal.guideline.title, { exact: true }).count()) fail(`${name}: another administrator received owner proposal data`);
        if (await page.locator('.clinical-change-notice').count()) fail(`${name}: owner notice leaked to another administrator`);
        await page.screenshot({ path: `${out}/approval-other-admin-${name}.png`, fullPage: false });
        cases.push({ name, surface: 'approval-other-admin', proposalVisible: false, noticeVisible: false, fixtureOnly: true });
        role = 'medico';
        const physicianRequestsBefore = physicianNoticeRequests;
        await page.goto(`${base}/favoritos`, { waitUntil: 'networkidle' });
        if (await page.locator('.clinical-change-notice').count() || physicianNoticeRequests !== physicianRequestsBefore || await page.getByText(proposal.guideline.title, { exact: true }).count()) fail(`${name}: owner notice was requested or shown to a physician`);
        cases.push({ name, surface: 'physician-notice-isolation', noticeVisible: false, noticeRequests: physicianNoticeRequests - physicianRequestsBefore, fixtureOnly: true });
      }
    }
    if (cases.length !== 16) fail(`matrix incomplete: ${cases.length}/16`);
    if (approvalMutationRequests) fail(`${approvalMutationRequests} approval mutations attempted without consent`);
    report.favoritesAndApprovals = { cases, approvalMutationRequests, fixtureOnly: true };
  } finally {
    await context.close();
  }
}
