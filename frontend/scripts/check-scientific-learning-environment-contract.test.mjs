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

test("offers the third environment at login and in the home selector", () => {
  assert.match(home, /type Mode = "complete" \| "essential" \| "scientific"/);
  assert.match(home, /chooseMode\("scientific"\)/);
  assert.match(home, />Ciência & Ensino</);
  assert.match(home, /setSelectedSpace\(nextMode === "scientific" \? "descobrir" : "consultorio"\)/);
  assert.match(login, /sessionStorage\.removeItem\("corvia:cardiology-spaces:mode"\)/);
});

test("keeps five scientific journeys and every existing scientific surface discoverable", () => {
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

test("preserves canonical hover, keyboard focus and selected behavior", () => {
  assert.match(home, /onMouseEnter=\{\(\) => setPreviewSpace\(space\.id\)\}/);
  assert.match(home, /onFocus=\{\(\) => setPreviewSpace\(space\.id\)\}/);
  assert.match(home, /aria-pressed=\{selectedSpace === space\.id\}/);
  assert.match(styles, /\.spaces-door\.is-active/);
});

test("ships the interactive Cardiology Spaces onboarding without a local repeat gate", () => {
  assert.doesNotMatch(tour, /corvia:cardiology-spaces:tour:v2/);
  assert.match(tour, /06 · CIÊNCIA & ENSINO/);
  assert.match(tour, /08 · INTELIGÊNCIA INTEGRADA/);
  assert.match(tour, /onboarding_pendente/);
  assert.match(app, /import\("\.\/pages\/CardiologySpacesTour"\)/);
  assert.match(app, /path="\/tour" element=\{<Tour \/>\}/);
  assert.match(app, /path="\/tour\/cardiology-spaces" element=\{<CardiologySpacesTour \/>\}/);
});

test("keeps 360px navigation legible instead of shrinking text to 9px", () => {
  assert.match(styles, /@media \(max-width:760px\)/);
  assert.match(styles, /font-size:max\(\.68rem,11px\)/);
  assert.doesNotMatch(styles, /(?:font-size|max-width):[^;]*(?:9px|72px)/);
  assert.match(styles, /\.spaces-dock \{ grid-template-columns:repeat\(6,minmax\(0,1fr\)\); max-width:calc\(100vw - 16px\); overflow-x:hidden; \}/);
  assert.match(styles, /\.spaces-dock a,\.spaces-dock button \{[^}]*font-size:max\(\.68rem,11px\);[^}]*white-space:normal;/);
  assert.doesNotMatch(styles, /\.spaces-dock \{[^}]*repeat\(7|minmax\(58px|overflow-x:auto/);
  assert.match(styles, /\.spaces-home \{ overflow-x:clip; \}/);
  assert.match(styles, /\.spaces-home__heart \{[^}]*width:min\(100vw,620px\)/);
  assert.doesNotMatch(styles, /width:min\(130vw,620px\)/);
  assert.match(tourStyles, /\.cst__controls>div\{max-width:calc\(100vw - 168px\);overflow-x:auto\}/);
});
