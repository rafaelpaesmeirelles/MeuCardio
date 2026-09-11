import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import ts from "typescript";
import { matchPath } from "react-router-dom";

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
function load(source, dependencies = {}) {
  const module = { exports: {} };
  const javascript = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const require = (name) => {
    assert.ok(name in dependencies, `dependência inesperada: ${name}`);
    return dependencies[name];
  };
  new Function("require", "exports", "module", javascript)(require, module.exports, module);
  return module.exports;
}
let featureEnabled = false;
const registry = load(read("src/lib/clinicalRouteRegistry.ts"), {
  "react-router-dom": { matchPath },
  "./aiFeatureFlags": { heartTeamEnabled: () => featureEnabled, whatsappAssistantEnabled: () => featureEnabled },
});
const navigation = load(read("src/lib/atelierNavigation.ts"), { "./clinicalRouteRegistry": registry });
const { createAtelierContextStore, atelierContextFromSearch, atelierHomeHref, atelierCatalogRoutesFor, atelierRecentContext } = navigation;
const spaces = Object.keys(registry.CLINICAL_SPACES);

test("storage inacessível não impede Home → tarefa → retorno com o mesmo espaço e modo", () => {
  const store = createAtelierContextStore(() => { throw new Error("SecurityError"); });
  assert.deepEqual(store.read(7, "hospital"), { space: "hospital", mode: "complete" });
  const chosen = { space: "pesquisa", mode: "scientific" };
  assert.equal(store.write(7, chosen), false);
  assert.deepEqual(store.read(7, "consultorio"), chosen);
  assert.equal(atelierHomeHref(store.read(7)), "/?espaco=pesquisa&modo=scientific");
});

test("falha de quota nunca repõe o espaço antigo sobre o estado de sessão", () => {
  const store = createAtelierContextStore(() => ({
    getItem: (key) => key.includes("context:v1") ? JSON.stringify({ space: "consultorio", mode: "complete" }) : null,
    setItem: () => { throw new Error("QuotaExceededError"); },
  }));
  assert.equal(store.read(8).space, "consultorio");
  assert.equal(store.write(8, { space: "hospital", mode: "essential" }), false);
  assert.deepEqual(store.read(8), { space: "hospital", mode: "essential" });
});

test("preferências são isoladas por usuário e leituras não expõem referências mutáveis", () => {
  const store = createAtelierContextStore(() => null);
  store.write(1, { space: "gestao", mode: "essential" });
  store.write(2, { space: "ensino", mode: "scientific" });
  const copy = store.read(1);
  copy.space = "hospital";
  assert.equal(store.read(1).space, "gestao");
  assert.equal(store.read(2).space, "ensino");
  assert.deepEqual(store.read(undefined), { space: "consultorio", mode: "complete" });
});

test("JSON válido restaura por usuário e valores inválidos não criam destinos", () => {
  const saved = new Map();
  const storage = () => ({ getItem: key => saved.get(key) || null, setItem: (key, value) => saved.set(key, value) });
  createAtelierContextStore(storage).write(5, { space: "hospital", mode: "scientific" });
  assert.deepEqual(createAtelierContextStore(storage).read(5), { space: "hospital", mode: "scientific" });
  saved.set("corvia:atelier:context:v1:5", '{"space":"//example.com","mode":"admin"}');
  assert.deepEqual(createAtelierContextStore(storage).read(5), { space: "consultorio", mode: "complete" });
  saved.set("corvia:atelier:context:v1:5", "{broken-json");
  assert.doesNotThrow(() => createAtelierContextStore(storage).read(5));
});

test("link direto sobrepõe o contexto antigo e o retorno preserva os dois parâmetros", () => {
  const store = createAtelierContextStore(() => null);
  store.write(4, { space: "consultorio", mode: "complete" });
  const direct = atelierContextFromSearch(new URLSearchParams("espaco=hospital&modo=scientific"), store.read(4));
  store.write(4, direct);
  assert.deepEqual(store.read(4, "consultorio"), { space: "hospital", mode: "scientific" });
  assert.deepEqual(atelierContextFromSearch(new URLSearchParams(atelierHomeHref(direct).split("?")[1]), { space: "gestao", mode: "essential" }), direct);
  assert.deepEqual(atelierContextFromSearch(new URLSearchParams("espaco=ensino"), direct), { space: "ensino", mode: "scientific" });
  assert.deepEqual(atelierContextFromSearch(new URLSearchParams("espaco=../../admin&modo=dark"), direct), direct);
});

test("chaves legadas válidas migram sem exigir escrita disponível", () => {
  const store = createAtelierContextStore(() => ({
    getItem: key => key === "corvia:atelier:space:9" ? "gestao" : key === "corvia:cardiology-spaces:mode" ? "essential" : null,
    setItem: () => { throw new Error("read-only"); },
  }));
  assert.deepEqual(store.read(9), { space: "gestao", mode: "essential" });
});

test("Retomar preserva paciente, busca e âncora sem confundir a URL com o padrão da rota", () => {
  const origin = "https://corvia.example";
  for (const path of ["/prontuario?paciente=42#evolucao", "/busca?modo=tudo-com-tudo&q=insuficiencia%20cardiaca", "/doencas/hipertensao#tratamento", "/caixa-de-email?folder=inbox"]) {
    assert.deepEqual(atelierRecentContext({ path, title: "Contexto" }, false, origin), { path, title: "Contexto" });
  }
});

test("Retomar rejeita destinos externos, protocolos, URLs ambíguas e rotas não registradas", () => {
  for (const path of ["https://external.example/agenda", "https://corvia.example/agenda", "//external.example/agenda", "///external.example/agenda", "/\\external.example/agenda", "/\t/external.example/agenda", "javascript:alert(1)", "agenda", "/nao-existe", "/?espaco=gestao", "/em-breve", "/tour"]) {
    assert.equal(atelierRecentContext({ path, title: "Contexto" }, false, "https://corvia.example"), null, path);
  }
  for (const value of [null, {}, { path: "/agenda" }, { path: 1, title: "Agenda" }, { path: "/agenda", title: [] }]) assert.equal(atelierRecentContext(value, false, "https://corvia.example"), null);
});

test("Retomar verifica o gate da rota exata e o papel atual", () => {
  const origin = "https://corvia.example";
  const admin = { path: "/admin/usuarios/42?aba=permissoes#conta", title: "Ficha" };
  assert.equal(atelierRecentContext(admin, false, origin), null);
  assert.deepEqual(atelierRecentContext(admin, true, origin), admin);
  const detail = { path: "/heart-team/caso-42?aba=revisao", title: "Caso" };
  featureEnabled = false;
  assert.equal(atelierRecentContext(detail, false, origin), null);
  featureEnabled = true;
  assert.deepEqual(atelierRecentContext(detail, false, origin), detail);
  featureEnabled = false;
});

test("o produtor de contextos observa query/hash e o consumidor valida antes de oferecer Retomar", () => {
  const frame = read("src/components/CardiologySpacesAppFrame.tsx");
  const home = read("src/components/AtelierHomeView.tsx");
  assert.match(frame, /path: `\$\{location\.pathname\}\$\{location\.search\}\$\{location\.hash\}`/);
  assert.match(frame, /\[location\.pathname, location\.search, location\.hash, route\.name/);
  assert.match(home, /atelierRecentContext\(value, usuario\?\.role === "admin", window\.location\.origin\)/);
});

test("catálogo restaura entradas existentes e conserva todas as rotas principais sem duplicar", () => {
  for (const isAdmin of [false, true]) {
    const catalog = spaces.flatMap(space => atelierCatalogRoutesFor(space, isAdmin));
    const paths = catalog.map(route => route.path);
    for (const path of ["/caixa-de-email", "/tour", "/verificacao-identidade"]) assert.ok(paths.includes(path), path);
    for (const route of spaces.flatMap(space => registry.catalogRoutesFor(space, isAdmin))) assert.ok(paths.includes(route.path));
    assert.equal(new Set(paths).size, paths.length);
    assert.ok(paths.every(path => !path.includes(":")));
    assert.ok(!paths.includes("/cursos"));
  }
});

test("catálogo ampliado mantém os gates administrativos e de operações IA", () => {
  for (const enabled of [false, true]) {
    featureEnabled = enabled;
    const regular = spaces.flatMap(space => atelierCatalogRoutesFor(space, false));
    assert.ok(regular.every(route => !["admin", "admin-ai", "no-product-access"].includes(route.gate)));
    const admin = spaces.flatMap(space => atelierCatalogRoutesFor(space, true));
    assert.ok(admin.some(route => route.path === "/admin"));
    assert.equal(admin.some(route => route.path === "/admin/operacoes-ia"), enabled);
  }
});

test("Home e AppFrame consomem a mesma camada e retorno desktop/mobile leva espaço e modo", () => {
  const home = read("src/pages/CardiologySpacesHome.tsx");
  const frame = read("src/components/CardiologySpacesAppFrame.tsx");
  for (const source of [home, frame]) assert.match(source, /atelierCatalogRoutesFor as catalogRoutesFor/);
  assert.match(home, /permittedPaths\.has\(action\.to\.split\("\?"\)\[0\]\)/);
  assert.match(home, /if \(selected \|\| validMode\) writeAtelierContext\(usuario\?\.id, context\)/);
  assert.match(frame, /const context = readAtelierContext\(usuario\?\.id,/);
  assert.equal([...frame.matchAll(/to=\{atelierHomeHref\(context\)\}/g)].length, 2);
  assert.doesNotMatch(frame, /sessionStorage\.getItem\(`corvia:atelier:space:/);
});

test("cartões dark de catálogo/personalização e painel Contexto têm pares contrastantes locais", () => {
  const css = read("src/styles/corvia-atelier.css");
  const scope = 'html[data-corvia-design="atelier"][data-corvia-theme="dark"] ';
  const luminance = hex => {
    const [r,g,b] = hex.slice(1).match(/../g).map(v => parseInt(v,16)/255).map(v => v <= .04045 ? v/12.92 : ((v+.055)/1.055)**2.4);
    return .2126*r + .7152*g + .0722*b;
  };
  const ratio = (a,b) => (Math.max(luminance(a),luminance(b))+.05)/(Math.min(luminance(a),luminance(b))+.05);
  for (const component of [".atelier-home .spaces-catalog .spaces-action", ".atelier-home .spaces-personalizer__selected article", ".atelier-home .spaces-personalizer__grid > button", ".atelier-app .cv-drawer :is(.cv-nav-link,.cv-drawer__assistant)"]) {
    const start = css.lastIndexOf(scope + component + (component.includes("cv-drawer") ? " {" : ","));
    assert.ok(start >= 0, component + " precisa de correção dark escopada");
    const block = css.slice(start).match(/\{([^}]+)\}/)?.[1] || "";
    const foreground = block.match(/color:\s*(#[\da-f]{6})/i)?.[1];
    const background = block.match(/background:\s*(#[\da-f]{6})/i)?.[1];
    assert.ok(foreground && background);
    assert.ok(ratio(foreground, background) >= 4.5, component + " precisa de contraste AA");
  }
  assert.match(css, /\.atelier-app \.cv-intelligence\s*\{\s*background: #1d302f !important;/);
  assert.ok(ratio("#f4f1e7", "#1d302f") >= 4.5);
  assert.ok(ratio("#b8c3b8", "#1d302f") >= 4.5);
  assert.ok(ratio("#f4f1e7", "#334941") >= 4.5);
});
