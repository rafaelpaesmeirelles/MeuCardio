// Shared by isolated Visual QA and focused regression tests. Hidden off-screen
// overflow must not conceal clipped names, architecture selectors or actions.
export function measureMobileSpaces() {
  const rect = (element) => {
    if (!element) return null;
    const r = element.getBoundingClientRect();
    const s = getComputedStyle(element);
    return { left:r.left, right:r.right, top:r.top, bottom:r.bottom, width:r.width, height:r.height,
      visible:s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0 };
  };
  const q = selector => document.querySelector(selector);
  const qa = selector => [...document.querySelectorAll(selector)];
  const textRects = element => {
    const range = document.createRange();
    range.selectNodeContents(element);
    return [...range.getClientRects()].filter(r => r.width && r.height)
      .map(r => ({left:r.left,right:r.right,top:r.top,bottom:r.bottom}));
  };
  const header = q('.atelier-header');
  const withinHeader = selector => rect(header?.querySelector(selector));
  const nameElement = header?.querySelector('.spaces-user__name');
  const identityName = nameElement ? {
    ...rect(nameElement), text:nameElement.textContent?.trim() || '',
    scrollWidth:nameElement.scrollWidth, clientWidth:nameElement.clientWidth,
    textRects:textRects(nameElement),
  } : null;
  const card = element => ({
    box:rect(element), text:[...element.querySelectorAll('strong, .atelier-portal__selected, .spaces-action > span')].flatMap(textRects),
    selected:element.getAttribute('aria-pressed') === 'true', label:element.textContent?.trim() || '',
    href:element.getAttribute('href'), image:element.querySelector('img') ? {
      loaded:element.querySelector('img').complete && element.querySelector('img').naturalWidth > 0,
      alt:element.querySelector('img').alt,
    } : null,
  });
  const mode = q('select[aria-label="Modo de trabalho"]');
  return {
    identityName, width:innerWidth, height:innerHeight, documentWidth:document.documentElement.scrollWidth,
    scrollX, scrollY, theme:document.documentElement.dataset.corviaTheme,
    arrival:!!q('.atelier-arrival'), activeSpace:q('.atelier-home')?.getAttribute('data-space'),
    header:rect(header), brand:withinHeader('.atelier-brand'), wordmark:withinHeader('.atelier-brand img'),
    brandAlt:header?.querySelector('.atelier-brand img')?.getAttribute('alt'),
    brandLoaded:!!header?.querySelector('.atelier-brand img')?.naturalWidth,
    identity:withinHeader('.atelier-account > summary'), avatar:withinHeader('.spaces-user__avatar'),
    catalog:withinHeader('.atelier-catalog-trigger'),
    search:withinHeader('.atelier-search'), input:withinHeader('.atelier-search input'),
    organization:rect(mode), modeValue:mode?.value,
    spaceButtons:qa('.atelier-mobile-spaces button').map(element => ({box:rect(element),text:textRects(element),label:element.textContent.trim(),selected:element.getAttribute('aria-pressed') === 'true'})),
    cards:qa('.atelier-portal').map(card),
    actions:qa('.atelier-shelf .spaces-action').map(card),
  };
}

export function validateMobileSpaces(m, expectedIdentityName) {
  const errors = [];
  const overlaps = (a,b) => a?.visible && b?.visible && a.left < b.right-1 && a.right > b.left+1 && a.top < b.bottom-1 && a.bottom > b.top+1;
  const outside = (r,box) => !box || r.left < box.left-1 || r.right > box.right+1 || r.top < box.top-1 || r.bottom > box.bottom+1;
  for (const key of ['header','brand','wordmark','identity','avatar','identityName','search','input','catalog','organization']) {
    const r=m[key];
    if (!r?.visible) errors.push(`${key}: not visible`);
    else if (r.left < -1 || r.right > m.width+1) errors.push(`${key}: outside viewport`);
    else if (key !== 'organization' && (r.top < -1 || r.bottom > m.height+1)) errors.push(`${key}: outside vertical viewport`);
  }
  if (m.documentWidth > m.width+1) errors.push('document: horizontal overflow');
  for (const [a,b] of [['brand','identity'],['brand','catalog'],['identity','catalog'],['search','brand'],['search','identity'],['search','catalog']]) {
    if (overlaps(m[a],m[b])) errors.push(`${a}/${b}: overlap`);
  }
  if (m.brandAlt !== 'CorVIA Cardiology Spaces' || !m.brandLoaded) errors.push('wordmark: missing accessible or loaded branding');
  if (expectedIdentityName && m.identityName?.text !== expectedIdentityName) errors.push('identity name: unexpected text');
  if (!m.identityName?.text) errors.push('identity name: empty text');
  if (m.identityName?.visible) {
    const name=m.identityName;
    if (!name.textRects?.length || name.scrollWidth > name.clientWidth+1 || name.textRects.some(r => outside(r,name) || outside(r,m.identity) || outside(r,m.header))) errors.push('identity name: clipped text');
    if (overlaps(name,m.avatar)) errors.push('identity name/avatar: overlap');
  }
  for (const key of ['brand','identity','catalog','input','organization']) {
    if (m[key]?.width < 44 || m[key]?.height < 44) errors.push(`${key}: touch target below 44px`);
  }
  if (m.input?.width < 120) errors.push('search: input too narrow');
  const checkCard = (item, label) => {
    if (!item.box?.visible || item.box.left < -1 || item.box.right > m.width+1) errors.push(`${label}: outside viewport`);
    if (item.box?.width < 44 || item.box?.height < 44) errors.push(`${label}: touch target below 44px`);
    if (item.text.some(r => outside(r,item.box))) errors.push(`${label}: clipped text`);
  };
  if (m.arrival) {
    if (m.cards.length !== 5) errors.push('arrival: expected five portals');
    if (m.cards.filter(card => card.selected).length !== 1) errors.push('arrival: expected one selected portal');
    if (m.spaceButtons.length !== 5) errors.push('arrival: expected five mobile spaces');
    if (m.spaceButtons.filter(button => button.selected).length !== 1) errors.push('arrival: expected one selected mobile space');
    for (const [index,button] of m.spaceButtons.entries()) checkCard(button,`space button ${index}`);
    for (const [index,card] of m.cards.entries()) {
      if (!card.selected && !card.box?.visible) continue;
      checkCard(card,`card ${index}`);
      if (!card.image?.loaded || !card.image?.alt) errors.push(`card ${index}: missing loaded accessible interior`);
    }
  } else {
    const count=m.modeValue === 'complete' ? 12 : 8;
    if (m.actions.length !== count) errors.push(`interior: expected ${count} actions`);
    for (const [index,action] of m.actions.entries()) {
      checkCard(action,`action ${index}`);
      if (!action.href?.startsWith('/') || action.href.startsWith('//')) errors.push(`action ${index}: missing same-origin route`);
    }
  }
  return errors;
}
