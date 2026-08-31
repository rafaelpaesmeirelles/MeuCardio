import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
const home = read("src/pages/CardiologySpacesHome.tsx");
const scene = read("src/components/CardiologySpaceScene.tsx");
const tour = read("src/pages/CardiologySpacesTour.tsx");
const app = read("src/App.tsx");
const styles = read("src/styles/cardiology-spaces-v2.css");
const tourStyles = read("src/styles/cardiology-spaces-tour.css");
const login = read("src/pages/Entrar.tsx");
const desktopNav = read("src/components/ClinicalDesktopNav.tsx");
const mobileNav = read("src/components/ClinicalMobileNav.tsx");

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
  for (const id of ["descobrir", "evidencias", "aprender", "ensinar", "produzir"]) {
    assert.match(home, new RegExp(`id: "${id}"`));
    assert.match(scene, new RegExp(`space === "${id}"`));
  }
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

test("preserves canonical hover, keyboard focus and selected behavior", () => {
  assert.match(home, /onMouseEnter=\{\(\) => setPreviewSpace\(space\.id\)\}/);
  assert.match(home, /onFocus=\{\(\) => setPreviewSpace\(space\.id\)\}/);
  assert.match(home, /aria-pressed=\{selectedSpace === space\.id\}/);
  assert.match(styles, /\.spaces-door\.is-active/);
});

test("ships the expanded Cardiology Spaces tour with investor and onboarding gates", () => {
  assert.match(tour, /corvia:cardiology-spaces:tour:v3/);
  for (const marker of ["01 · ESCOLHA A EXPERIÊNCIA", "02 · CARDIOLOGY SPACES", "05 · DESLOCAMENTO", "06 · TUDO COM TUDO", "07 · CIÊNCIA & ENSINO", "08 · SEU CORVIA"]) {
    assert.ok(tour.includes(marker), `tour missing ${marker}`);
  }
  assert.match(tour, /usuario\?\.investidor/);
  assert.match(app, /usuario\.onboarding_pendente/);
  assert.match(app, /usuario\.investidor/);
  assert.match(app, /path="\/tour" element=\{<Tour \/>\}/);
  assert.match(app, /path="\/tour\/cardiology-spaces" element=\{<CardiologySpacesTour \/>\}/);
});

test("keeps the approved heart and compact six-action mobile dock", () => {
  assert.match(home, /spaces-choice__heart/);
  assert.match(home, /spaces-home__heart/);
  assert.match(styles, /@media\(max-width:900px\)/);
  assert.match(styles, /\.spaces-dock\{[^}]*repeat\(6,minmax\(0,1fr\)\)/);
  assert.match(styles, /\.spaces-home__heart\{[^}]*width:min\(100vw,650px\)/);
  assert.match(tourStyles, /@media\(max-width:950px\)/);
  assert.match(tourStyles, /\.cst__controls>div\{max-width:calc\(100vw - 140px\);overflow-x:auto\}/);
});
