import fs from 'node:fs';
import path from 'node:path';

// Runs with an isolated QA account, never supplies authentication or changes clinical data.
export async function certifyAtelierReference({ page, base, out, failures }) {
  const metrics = [];
  const spaces = ['consultorio','hospital','ensino','pesquisa','gestao'];
  const labels = ['Consultório','Hospital','Ensino','Pesquisa','Gestão'];
  const fail = message => failures.push(`atelier: ${message}`);
  const measure = async name => {
    await page.evaluate(() => document.fonts.ready);
    const item = await page.evaluate(() => ({
      width:innerWidth, scrollWidth:document.documentElement.scrollWidth,
      design:document.documentElement.dataset.corviaDesign,
      task:!!document.querySelector('.atelier-taskbar'),
      sceneryInTask:!!document.querySelector('.atelier-app .atelier-space__hero, .atelier-app .atelier-shelves'),
    }));
    if(item.scrollWidth > item.width + 2) fail(`${name}: horizontal overflow ${item.scrollWidth}/${item.width}`);
    if(item.design !== 'atelier') fail(`${name}: architectural design not active`);
    if(item.sceneryInTask) fail(`${name}: scenery consumes task space`);
    metrics.push({name,...item});
  };
  await page.goto(`${base}/`,{waitUntil:'networkidle'});
  await page.locator('.atelier-home').waitFor();
  const actual = await page.locator('.atelier-portal__label strong').allTextContents();
  if(JSON.stringify(actual) !== JSON.stringify(labels)) fail(`five real environments missing: ${actual}`);
  for(let i=0;i<spaces.length;i++) {
    await page.locator('.atelier-portal').nth(i).click();
    const selected = page.locator('.atelier-portal[aria-pressed="true"]');
    if(await selected.count() !== 1 || !(await selected.locator('img').getAttribute('src')).includes(`atelier-${spaces[i]}-small.webp`)) fail(`${spaces[i]}: incorrect selected architecture`);
    const before=await selected.getAttribute('aria-label');
    await page.locator('.atelier-portal').nth((i+1)%5).hover();
    if(await page.locator('.atelier-portal[aria-pressed="true"]').getAttribute('aria-label')!==before) fail(`${spaces[i]}: hover changes selected workspace`);
    await page.getByRole('combobox',{name:'Modo de trabalho',exact:true}).selectOption('complete');
    await page.locator('.atelier-primary').click();
    for(const [mode,count] of [['complete',12],['essential',8],['scientific',8]]) {
      await page.getByRole('combobox',{name:'Modo de trabalho',exact:true}).selectOption(mode);
      const links=page.locator('.atelier-shelves .spaces-action');
      if(await links.count()!==count) fail(`${spaces[i]}/${mode}: expected ${count} shortcuts, got ${await links.count()}`);
      if(['consultorio','hospital'].includes(spaces[i]) && mode==='complete' && !(await page.locator('.atelier-shelves a[href="/exames-ia"]').count())) fail(`${spaces[i]}: IA para Exames missing`);
      await measure(`${spaces[i]}/${mode}`);
    }
    await page.getByRole('button',{name:'Trocar de ambiente',exact:true}).click();
  }
  await page.locator('.atelier-portal').first().click();
  await page.getByRole('combobox',{name:'Modo de trabalho',exact:true}).selectOption('complete');
  await page.screenshot({path:path.join(out,'atelier-desktop-principal.png'),fullPage:true});
  await page.locator('.atelier-primary').click();
  await page.screenshot({path:path.join(out,'atelier-desktop-consultorio.png'),fullPage:true});
  const original=await page.locator('.atelier-shelf').first().locator('a').allTextContents();
  await page.getByRole('button',{name:'Personalizar',exact:true}).click();
  await page.locator('.spaces-personalizer').waitFor();
  await page.locator('.spaces-personalizer__selected article').first().getByRole('button',{name:/Remover/}).click();
  await page.getByRole('button',{name:'Cancelar',exact:true}).click();
  if(JSON.stringify(await page.locator('.atelier-shelf').first().locator('a').allTextContents())!==JSON.stringify(original)) fail('cancel changes preferences');
  await page.getByRole('button',{name:'Personalizar',exact:true}).click();
  await page.locator('.spaces-personalizer__selected article').first().getByRole('button',{name:/para depois/}).click();
  await page.getByRole('button',{name:'Salvar personalização',exact:true}).click();
  await page.reload({waitUntil:'networkidle'});
  // Network idleness can precede authenticated lazy-route mounting. The
  // preferences are then restored by an effect; wait for the actual saved
  // order instead of sampling an empty or not-yet-hydrated shelf once.
  await page.locator('.atelier-space').waitFor({state:'visible'});
  const expectedOrder=[original[1],original[0],...original.slice(2)];
  const persisted=await page.waitForFunction(expected => {
    const shelf=document.querySelector('.atelier-shelf');
    const actual=shelf ? [...shelf.querySelectorAll('a')].map(link=>link.textContent) : [];
    return JSON.stringify(actual)===JSON.stringify(expected);
  },expectedOrder,{timeout:10000}).then(()=>true).catch(()=>false);
  const reordered=await page.locator('.atelier-shelf').first().locator('a').allTextContents();
  if(!persisted || JSON.stringify(reordered)!==JSON.stringify(expectedOrder)) fail(`reorder not persisted after reload: expected ${JSON.stringify(expectedOrder)}, got ${JSON.stringify(reordered)}`);
  await page.getByRole('button',{name:'Personalizar',exact:true}).click();
  await page.getByRole('button',{name:'Restaurar esta prateleira',exact:true}).click();
  await page.getByRole('button',{name:'Salvar personalização',exact:true}).click();
  if(JSON.stringify(await page.locator('.atelier-shelf').first().locator('a').allTextContents())!==JSON.stringify(original)) fail('default restoration failed');
  await page.locator('.atelier-shelves a[href="/agenda"]').click();
  await page.locator('.atelier-taskbar').waitFor();
  await measure('agenda-task');
  await page.getByRole('button',{name:'Foco',exact:true}).click();
  if(await page.locator('.cv-topbar').isVisible()) fail('focus does not collapse navigation');
  await page.getByRole('button',{name:'Trocar função',exact:true}).click();
  await page.locator('.cv-drawer.is-open').waitFor();
  await page.keyboard.press('Escape');
  if(await page.locator('.cv-drawer.is-open').count()) fail('Escape does not close function catalog');
  await page.getByRole('button',{name:'Sair do foco',exact:true}).click();
  await page.locator('.atelier-taskbar__return').click();
  if(!(await page.locator('.atelier-shelves').isVisible())) fail('return does not restore workspace');
  for(const viewport of [{width:1366,height:650},{width:820,height:1024},{width:390,height:844},{width:320,height:740}]) {
    await page.setViewportSize(viewport);
    await page.goto(`${base}/`,{waitUntil:'networkidle'});
    // count() has no auto-wait: zero during authenticated route mounting is
    // not the responsive layout. Mount the arrival before checking its CSS.
    await page.locator('.atelier-arrival').waitFor({state:'visible'});
    await page.locator('.atelier-portal.is-selected').waitFor({state:'visible'});
    if(viewport.width<=700) {
      const portalCount=await page.locator('.atelier-portal:visible').count();
      const portalGeometry=await page.locator('.atelier-portal.is-selected').evaluate(element => {
        const parent=element.parentElement;
        const style=getComputedStyle(parent);
        const available=parent.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight);
        return {width:element.getBoundingClientRect().width,available};
      });
      if(portalCount!==1 || portalGeometry.width<portalGeometry.available-2) fail(`${viewport.width}: mobile must show one wide environment (visible=${portalCount}, width=${portalGeometry.width}, available=${portalGeometry.available})`);
    }
    await measure(`principal-${viewport.width}`);
    await page.locator('.atelier-primary').click();
    await measure(`consultorio-${viewport.width}`);
    await page.screenshot({path:path.join(out,`atelier-consultorio-${viewport.width}.png`),fullPage:true});
  }
  fs.writeFileSync(path.join(out,'atelier-reference.json'),JSON.stringify({metrics,failures},null,2));
  return metrics;
}
