import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const home = read("src/pages/CardiologySpacesHome.tsx");
const scene = read("src/components/CardiologySpaceScene.tsx");
const tour = read("src/pages/CardiologySpacesTour.tsx");
const tourAlias = read("src/pages/Tour.tsx");
const app = read("src/App.tsx");
const view = read("src/components/AtelierHomeView.tsx");
const styles = read("src/styles/corvia-atelier.css");
const tourStyles = read("src/styles/corvia-atelier-tour.css");
const login = read("src/pages/Entrar.tsx");
const desktopNav = read("src/components/ClinicalDesktopNav.tsx");
const mobileNav = read("src/components/ClinicalMobileNav.tsx");
const timeline = read("src/pages/TimelineDoencas.tsx");

const scientificRoutes = [
  "/biblioteca",
  "/busca",
  "/busca?modo=tudo-com-tudo",
  "/documentos-cientificos-ia",
  "/diretrizes",
  "/evidencias",
  "/estudos",
  "/doencas",
  "/medicamentos",
  "/exames",
  "/calculadoras",
  "/fluxogramas",
  "/casos-clinicos",
  "/trilhas",
  "/trilhas/timeline",
  "/material-paciente",
  "/apresentacao",
  "/exportar",
  "/galeria",
  "/favoritos",
];

test("science organizes the selected workspace after login without changing login appearance or access", () => {
  assert.match(home, /type Mode = "complete" \| "essential" \| "scientific"/);
  assert.match(view, /<option value="scientific">Ciência & Ensino<\/option>/);
  assert.match(view, /aria-label="Modo de trabalho" value=\{props\.mode\} onChange=\{\(event\) => props\.onMode/);
  assert.match(home, /onMode=\{chooseMode\}/);
  const chooseMode = home.slice(home.indexOf("const chooseMode ="), home.indexOf("function resetMode"));
  assert.match(chooseMode, /setMode\(nextMode\)/);
  assert.match(chooseMode, /writeAtelierContext\(usuario\?\.id, \{ space: selectedSpace as FunctionalSpace, mode: nextMode \}\)/);
  assert.match(chooseMode, /setSearchParams\(\{ espaco: selectedSpace, modo: nextMode \}/);
  assert.doesNotMatch(chooseMode, /setSelectedSpace\(/, "organization must not switch the selected environment");
  assert.match(home, /const availableSpaces = SPACES;/);
  assert.match(home, /mode === "scientific" \? ATELIER_SCIENCE\[id\] : ATELIER_DEFAULTS\[id\]/);
  assert.match(login, /sessionStorage\.removeItem\("corvia:cardiology-spaces:mode"\)/);
  assert.match(login, /id: "light"/);
  assert.match(login, /id: "dark"/);
  assert.doesNotMatch(login, /id: "scientific"/);
  assert.match(login, /Cinco espaços de trabalho\.<br \/><em>Uma só cardiologia\./);
  assert.match(login, /Novo no CorVIA/);
  assert.match(login, /to="\/solicitar-acesso">Solicitar acesso profissional/);
});

test("preserves legacy science journey assets and keeps every scientific surface discoverable", () => {
  const scientificJourneys = ["descobrir", "evidencias", "aprender", "ensinar", "produzir"];
  for (const id of scientificJourneys) {
    assert.match(home, new RegExp(`id: "${id}"`));
    for (const theme of ["dark", "light"]) {
      const asset = `/spaces/corvia-science-${id}-${theme}-768.webp`;
      assert.ok(scene.includes(`${id}: "${asset}"`), `missing approved ${id}/${theme} scene`);
      assert.ok(existsSync(new URL(`../public${asset}`, import.meta.url)), `missing scene asset ${asset}`);
    }
  }
  assert.equal(scientificJourneys.length, 5);
  assert.match(scene, /theme\s*===\s*"light"\s*\?\s*LIGHT_SCENE_BY_SPACE\[space\]\s*:\s*SCENE_BY_SPACE\[space\]/);
  assert.match(scene, /src=\{scene\}/);
  assert.match(scene, /decoding="async"/);
  assert.doesNotMatch(home, /<CardiologySpaceScene[^>]*priority=/);
  for (const route of scientificRoutes) {
    assert.ok(home.includes(`"${route}"`), `missing ${route}`);
    const routePath = route.split("?")[0].replace(/^\//, "");
    assert.ok(app.includes(`path="${routePath}"`) || app.includes(`path="/${routePath}"`), `route is not registered: ${route}`);
  }
  assert.equal(scientificRoutes.length, 20);
});

test("courses are no longer exposed but old URLs fail safe into Trilhas", () => {
  for (const source of [home, desktopNav, mobileNav]) assert.doesNotMatch(source, /to:\s*"\/cursos"|\["\/cursos"/);
  assert.doesNotMatch(home, />Cursos</);
  assert.match(app, /path="cursos" element=\{<Navigate to="\/trilhas" replace \/>\}/);
  assert.match(app, /path="cursos\/:slug" element=\{<Navigate to="\/trilhas" replace \/>\}/);
});

test("timeline keeps URL, selected tab, response and related content in the same request context", () => {
  assert.match(timeline, /const requisicaoTimeline = useRef\(0\)/);
  assert.match(timeline, /requisicaoTimeline\.current !== idRequisicao/);
  assert.match(timeline, /setTimeline\(null\)/);
  assert.match(timeline, /if \(dados\.tema && dados\.tema !== temaAtivo\)/);
  assert.match(timeline, /if \(\(atuais\.get\("tema"\) \?\? ""\) !== temaAtivo\) return atuais/);
  assert.match(timeline, /const timelineExibida = timeline\?\.tema === temaAtivo \? timeline : null/);
  assert.match(timeline, /!carregandoTimeline && !erroTimeline && timelineExibida && \(/);
  assert.match(timeline, /key=\{timelineExibida\.tema\}/);
  assert.match(timeline, /tema=\{timelineExibida\.tema\}/);
  assert.doesNotMatch(timeline, /tema=\{timeline\?\.tema \|\| temaAtivo\}/);
});

test("portal selection is keyboard-native and hover cannot select a different workspace", () => {
  assert.match(view, /<button type="button" className=\{`atelier-portal/);
  assert.match(view, /onClick=\{\(\) => props\.onSelect\(space\.id\)\} aria-pressed=\{space\.id === props\.active\.id\}/);
  assert.doesNotMatch(view, /onMouseEnter=|onFocus=/, "hover/focus must not change the chosen architecture");
  assert.match(styles, /\.atelier-portal:hover img/);
  assert.match(styles, /\.atelier-portal\.is-selected img/);
  assert.match(styles, /:focus-visible\{outline:3px solid/);
  assert.match(styles, /\.atelier-portal\{[^}]*overflow:hidden/);
});

test("ships the expanded Cardiology Spaces tour with investor and onboarding gates", () => {
  assert.match(tour, /corvia:cardiology-spaces:tour:v4/);
  for (const marker of ["01 · ESCOLHA A EXPERIÊNCIA", "02 · CINCO AMBIENTES", "04 · MEU DIA ENTRE ESPAÇOS", "05 · TUDO COM TUDO", "06 · CIÊNCIA & ENSINO", "07 · O SEU CORVIA"]) {
    assert.ok(tour.includes(marker), `tour missing ${marker}`);
  }
  assert.match(tour, /usuario\?\.investidor/);
  assert.match(app, /usuario\.onboarding_pendente/);
  assert.match(app, /usuario\.investidor/);
  assert.match(app, /path="\/tour" element=\{<CardiologySpacesTour \/>\}/);
  assert.match(app, /path="\/tour\/cardiology-spaces" element=\{<Tour \/>\}/);
  assert.match(tourAlias, /pathname: "\/tour", search: location\.search, hash: location\.hash/);
});

test("mobile keeps one broad architecture, readable shelves and reachable tour controls", () => {
  // The approved Atelier replaces the cosmic heart/dock, not its functions.
  assert.doesNotMatch(home, /spaces-choice__heart|spaces-home__heart|className="spaces-dock"/);
  assert.match(view, /aria-label="Escolher ambiente"/);
  assert.match(styles, /\.atelier-portal\.is-selected\{display:block!important;aspect-ratio:1\.22/);
  assert.match(styles, /\.atelier-shelf\{grid-template-columns:repeat\(2,minmax\(0,1fr\)\)/);
  assert.match(styles, /\.atelier-shelf \.spaces-action>span\{font-size:16px\}/);
  assert.match(styles, /\.atelier-mobile-spaces button\{[^}]*min-height:44px/);
  assert.match(view, /onClick=\{props\.onCatalog\}>Todas as funções/);
  assert.match(view, /onClick=\{props\.onPersonalize\}/);
  assert.match(tourStyles, /\.cst--atelier button \{[^}]*min-height: 44px/);
  assert.match(tourStyles, /\.cst-at__stage \{[^}]*overflow: auto/);
  assert.match(tourStyles, /\.cst-at__controls \{ grid-template-columns: minmax\(0, 1fr\) minmax\(0, 1fr\)/);
});
