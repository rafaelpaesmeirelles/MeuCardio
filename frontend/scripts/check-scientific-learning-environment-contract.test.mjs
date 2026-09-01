import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const home = read("src/pages/CardiologySpacesHome.tsx");
const scene = read("src/components/CardiologySpaceScene.tsx");
const tour = read("src/pages/CardiologySpacesTour.tsx");
const tourAlias = read("src/pages/Tour.tsx");
const app = read("src/App.tsx");
const styles = read("src/styles/cardiology-spaces-home.css");
const tourStyles = read("src/styles/cardiology-spaces-tour.css");
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

test("offers the third experience at login and in the home selector", () => {
  assert.match(home, /type Mode = "complete" \| "essential" \| "scientific"/);
  assert.match(home, /chooseMode\("scientific"\)/);
  assert.match(home, />Ciência & Ensino</);
  assert.match(home, /setSelectedSpace\(nextMode === "scientific" \? "descobrir" : "consultorio"\)/);
  assert.match(login, /sessionStorage\.removeItem\("corvia:cardiology-spaces:mode"\)/);
});

test("keeps five scientific journeys and every scientific surface discoverable", () => {
  const approvedScenes = {
    descobrir: "consultorio",
    evidencias: "hospital",
    aprender: "ensino",
    ensinar: "pesquisa",
    produzir: "gestao",
  };
  for (const [id, sceneName] of Object.entries(approvedScenes)) {
    assert.match(home, new RegExp(`id: "${id}"`));
    assert.match(scene, new RegExp(`${id}:\\s*"/spaces/corvia-room-${sceneName}\\.jpg"`));
  }
  assert.match(scene, /src=\{SCENE_BY_SPACE\[space\]\}/);
  assert.doesNotMatch(scene, /<picture|srcSet=|\.webp|fetchPriority|priority/);
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

test("preserves canonical hover, keyboard focus and selected behavior", () => {
  assert.match(home, /onMouseEnter=\{\(\) => setPreviewSpace\(space\.id\)\}/);
  assert.match(home, /onFocus=\{\(\) => setPreviewSpace\(space\.id\)\}/);
  assert.match(home, /aria-pressed=\{selectedSpace === space\.id\}/);
  assert.match(styles, /\.spaces-door\.is-active/);
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

test("keeps the approved heart and compact six-action mobile dock", () => {
  assert.match(home, /spaces-choice__heart/);
  assert.match(home, /spaces-home__heart/);
  assert.match(styles, /@media\(max-width:900px\)/);
  assert.match(styles, /\.spaces-dock\{[^}]*repeat\(6,minmax\(0,1fr\)\)/);
  assert.match(styles, /\.spaces-home__heart\s*\{[^}]*width:min\(100vw,650px\)/);
  assert.match(tourStyles, /@media\s*\(max-width:\s*900px\)/);
  assert.match(tourStyles, /\.cst__dots\s*\{[^}]*max-width:\s*calc\(100vw - 190px\);[^}]*overflow-x:\s*auto/);
});
