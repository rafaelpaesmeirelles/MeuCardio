// Shared by the existing isolated visual QA and its focused regression tests.
export function measureMobileSpaces() {
  const rect = (element) => {
    if (!element) return null;
    const r = element.getBoundingClientRect();
    const s = getComputedStyle(element);
    return { left:r.left, right:r.right, top:r.top, bottom:r.bottom, width:r.width, height:r.height,
      visible:s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0 };
  };
  const q = (selector) => document.querySelector(selector);
  const choice = !!q('.spaces-choice');
  const header = q(choice ? '.spaces-choice > header' : '.spaces-home__topbar');
  const withinHeader = (selector) => rect(header?.querySelector(selector));
  return {
    width:innerWidth, theme:document.documentElement.dataset.corviaTheme, choice,
    header:rect(header), brand:withinHeader('.spaces-brand'), wordmark:withinHeader('.spaces-brand strong'),
    galaxy:withinHeader('.galaxy-theme-toggle'), galaxyImage:withinHeader('.galaxy-theme-toggle__image'), identity:withinHeader('.spaces-user'), avatar:withinHeader('.spaces-user__avatar'),
    search:withinHeader('.spaces-everything-search'), input:withinHeader('.spaces-everything-search input'),
    cards:[...document.querySelectorAll('.spaces-choice__cards > button')].map((card) => ({
      box:rect(card), text:[...card.querySelectorAll('strong, small, em')].map((element) => {
        const range = document.createRange();
        range.selectNodeContents(element);
        return [...range.getClientRects()].filter((r) => r.width && r.height).map((r) => ({left:r.left,right:r.right}));
      }).flat(),
    })),
  };
}

export function validateMobileSpaces(m) {
  const errors = [];
  for (const key of ['header','brand','wordmark','galaxy','identity','avatar',...(m.choice ? [] : ['search','input'])]) {
    const r=m[key];
    if (!r?.visible) errors.push(`${key}: not visible`);
    else if (r.left < -1 || r.right > m.width + 1) errors.push(`${key}: outside viewport`);
  }
  const overlaps=(a,b) => a?.visible && b?.visible && a.left < b.right-1 && a.right > b.left+1 && a.top < b.bottom-1 && a.bottom > b.top+1;
  for (const [a,b] of [['brand','galaxy'],['galaxy','identity'],['brand','identity'],['search','brand'],['search','identity']]) {
    if(overlaps(m[a],m[b])) errors.push(`${a}/${b}: overlap`);
  }
  if(m.galaxyImage?.visible && (m.galaxyImage.left < -1 || m.galaxyImage.right > m.width+1 || overlaps(m.galaxyImage,m.brand) || overlaps(m.galaxyImage,m.identity))) errors.push('galaxy image: overflow or overlap');
  if(m.galaxy?.width < 44 || m.galaxy?.height < 44) errors.push('galaxy: touch target below 44px');
  if(!m.choice && m.input?.width < 120) errors.push('search: input too narrow');
  if(m.choice && m.cards.length !== 3) errors.push('choice: expected three cards');
  for(const [index,card] of m.cards.entries()) {
    if(!card.box?.visible || card.box.left < -1 || card.box.right > m.width+1) errors.push(`card ${index}: outside viewport`);
    if(card.text.some((r) => r.left < card.box.left-1 || r.right > card.box.right+1)) errors.push(`card ${index}: clipped text`);
  }
  return errors;
}
