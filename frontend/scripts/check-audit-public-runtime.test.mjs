import test, { after } from "node:test";
import assert from "node:assert/strict";
import { readFile, mkdtemp, writeFile, rm } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import React from "react";
import TestRenderer, { act } from "react-test-renderer";
import { MemoryRouter, Routes, Route, useLocation } from "react-router-dom";
import { transform } from "esbuild";

const root = fileURLToPath(new URL("../", import.meta.url));
const dir = await mkdtemp(path.join(root, ".public-test-"));
after(async () => {
  assert.ok(path.resolve(dir).startsWith(path.resolve(root) + path.sep));
  await rm(dir, { recursive: true, force: true });
});
async function compile(name, source) {
  const result = await transform(source, { loader: "tsx", format: "esm", jsx: "automatic" });
  const file = path.join(dir, name + ".mjs");
  await writeFile(file, result.code);
  return import(pathToFileURL(file));
}
const helperSource = await readFile(path.join(root, "src/lib/loginReturn.ts"), "utf8");
const helper = await compile("loginReturn", helperSource);
const redirectSource = (await readFile(path.join(root, "src/components/LoginReturn.tsx"), "utf8"))
  .replace('"../lib/loginReturn"', '"./loginReturn.mjs"');
const { LoginRedirect, ResumeLogin } = await compile("redirect", redirectSource);
const validatorSource = (await readFile(path.join(root, "src/pages/ValidarDocumento.tsx"), "utf8"))
  .replace(/import PublicCardiologyFrame[^;]+;/, "const PublicCardiologyFrame = ({children}) => <main>{children}</main>;")
  .replace(/import "\.\.\/styles\/validar-documento.css";/, "");
const { default: Validator } = await compile("validator", validatorSource);
await compile("registry", (await readFile(path.join(root, "src/lib/clinicalRouteRegistry.ts"), "utf8"))
  .replace(/import \{ heartTeamEnabled, whatsappAssistantEnabled \}[^;]+;/, "const heartTeamEnabled=()=>false, whatsappAssistantEnabled=()=>false;"));
const { pageTitle } = await compile("pageTitle", (await readFile(path.join(root, "src/lib/pageTitle.ts"), "utf8"))
  .replace('"./clinicalRouteRegistry"', '"./registry.mjs"'));
const appSource = (await readFile(path.join(root, "src/App.tsx"), "utf8"))
  .replace(/^import .+;\r?\n/gm, "")
  .replace(/const (\w+) = lazy\(\(\) => import\("[^\"]+"\)\);/g, (_, name) => `const ${name}=()=> <div data-screen="${name}">${name}</div>;`);
const { default: App } = await compile("app", `
import { Suspense, useEffect } from "react";
import { Navigate, Route, Routes, useLocation, Outlet } from "react-router-dom";
import { LoginRedirect, ResumeLogin } from "./redirect.mjs";
import { readLoginReturn } from "./loginReturn.mjs";
import { pageTitle } from "./pageTitle.mjs";
const Shell=()=> <main id="conteudo-principal"><Outlet/></main>;
const CommercialFeatureGate=({children})=>children, OptionalFeatureBoundary=CommercialFeatureGate, AIInstallationGate=CommercialFeatureGate;
const HomeQuickActionsPersonalizer=()=>null, Carregando=()=> <p>Carregando</p>;
const cardiologySpacesEnabled=()=>true, heartTeamEnabled=()=>false, whatsappAssistantEnabled=()=>false;
const useAuth=()=>globalThis.publicFixtureAuth, useActivityHeartbeat=()=>{};
${appSource}`);
const legalSource = (await readFile(path.join(root, "src/components/LegalDocumentFrame.tsx"), "utf8"))
  .replace(/import \{ useAuth \}[^;]+;/, "const useAuth=()=>globalThis.publicFixtureAuth;")
  .replace(/import PublicCardiologyFrame[^;]+;/, "const PublicCardiologyFrame=({children})=> <main id='conteudo-principal'>{children}</main>;");
const { default: Legal } = await compile("legal", legalSource);

const storage = new Map();
globalThis.window = { sessionStorage: {
  getItem: key => storage.get(key) ?? null,
  setItem: (key, value) => storage.set(key, value),
  removeItem: key => storage.delete(key),
} };
globalThis.document = { title: "" };
const locationProbe = [];
function Probe() {
  const value = useLocation();
  React.useEffect(() => { locationProbe.push(value.pathname + value.search + value.hash); }, [value]);
  return null;
}
const frame = (path, children) => React.createElement(MemoryRouter, { initialEntries: [path], future: { v7_startTransition: true, v7_relativeSplatPath: true } }, React.createElement(Probe), children);

test("return URL rejects external destinations and authentication loops", () => {
  for (const value of ["https://other.invalid", "//other.invalid", "/\\other.invalid", "/entrar?a=1", "/redefinir-senha/token", "/", "/a\nb", null]) {
    assert.equal(helper.safeLoginReturn(value), null, String(value));
  }
  assert.equal(helper.safeLoginReturn("/trilhas/timeline?tema=teste#marco"), "/trilhas/timeline?tema=teste#marco");
});

test("real redirect persists the deep link and resume consumes it exactly once", async () => {
  storage.clear();
  let renderer;
  await act(async () => { renderer = TestRenderer.create(frame("/trilhas/timeline?tema=teste#marco", React.createElement(Routes, null,
    React.createElement(Route, { path: "/entrar", element: React.createElement("p", null, "Entrar") }),
    React.createElement(Route, { path: "*", element: React.createElement(LoginRedirect) })))); });
  assert.equal(locationProbe.at(-1), "/entrar");
  const destination = helper.readLoginReturn();
  assert.equal(destination, "/trilhas/timeline?tema=teste#marco");
  await act(async () => renderer.unmount());
  await act(async () => { renderer = TestRenderer.create(frame("/entrar", React.createElement(Routes, null,
    React.createElement(Route, { path: "/entrar", element: React.createElement(ResumeLogin, { destination }) }),
    React.createElement(Route, { path: "*", element: React.createElement("p", null, "Destino") })))); });
  assert.equal(locationProbe.at(-1), destination);
  assert.equal(helper.readLoginReturn(), null);
  await act(async () => renderer.unmount());
});

async function validator(path = "/validar") {
  let renderer;
  await act(async () => { renderer = TestRenderer.create(frame(path, React.createElement(Routes, null,
    React.createElement(Route, { path: "/validar/:codigo?", element: React.createElement(Validator) })))); });
  return renderer;
}
const success = code => ({ ok: true, json: async () => ({ codigo: code, valido: true, tipo: "documento", aviso: "fixture", validacao_independente_url: "https://validar.iti.gov.br" }) });
test("manual validation makes one request; same-code retry makes exactly one more", async () => {
  const calls = [];
  globalThis.fetch = async url => { calls.push(url); return success("ABC"); };
  const renderer = await validator();
  await act(async () => renderer.root.findByType("input").props.onChange({ target: { value: " a bc " } }));
  await act(async () => renderer.root.findByType("form").props.onSubmit({ preventDefault() {} }));
  assert.deepEqual(calls, ["/api/documentos-publicos/validar/ABC"]);
  assert.equal(locationProbe.at(-1), "/validar/ABC");
  await act(async () => renderer.root.findByType("form").props.onSubmit({ preventDefault() {} }));
  assert.equal(calls.length, 2);
  await act(async () => renderer.unmount());
});

test("editing a pending validation aborts it and ignores its late response", async () => {
  let finish, signal;
  globalThis.fetch = (url, options) => { signal = options.signal; return new Promise(resolve => { finish = resolve; }); };
  const renderer = await validator("/validar/OLD");
  await act(async () => renderer.root.findByType("input").props.onChange({ target: { value: "NEW" } }));
  assert.equal(signal.aborted, true);
  await act(async () => finish(success("OLD")));
  assert.equal(renderer.root.findByType("input").props.value, "NEW");
  assert.equal(renderer.root.findAll(node => typeof node.props.className === "string" && node.props.className.startsWith("corvia-validator__result")).length, 0);
  await act(async () => renderer.unmount());
});

test("service failure is shown and permits a deliberate retry", async () => {
  let calls = 0;
  globalThis.fetch = async () => { calls++; return { ok: false, status: 503, json: async () => ({}) }; };
  const renderer = await validator("/validar/ABC");
  assert.equal(calls, 1);
  assert.ok(renderer.root.findByProps({ role: "alert" }));
  assert.equal(renderer.root.findByType("button").props.disabled, false);
  await act(async () => renderer.unmount());
});

test("actual App routes keep product public in both session states and recover malformed validation URL", async () => {
  storage.clear();
  for (const usuario of [null, { id: 1, role: "admin" }]) {
    globalThis.publicFixtureAuth = { usuario, carregando: false };
    let renderer;
    await act(async () => { renderer = TestRenderer.create(frame("/produto", React.createElement(App))); });
    assert.ok(renderer.root.findByProps({ "data-screen": "Produto" }));
    assert.equal(document.title, "Conheça o CorVIA · CorVIA");
    await act(async () => renderer.unmount());
    await act(async () => { renderer = TestRenderer.create(frame("/validar/ABC/extra", React.createElement(App))); });
    assert.ok(renderer.root.findByProps({ "data-screen": "ValidarDocumento" }));
    assert.equal(locationProbe.at(-1), "/validar");
    await act(async () => renderer.unmount());
  }
});

test("legal content has one main landmark publicly and when nested in the authenticated shell", async () => {
  for (const usuario of [null, { id: 1 }]) {
    globalThis.publicFixtureAuth = { usuario, carregando: false };
    const legal = React.createElement(Legal, { title: "Termos", eyebrow: "Legal", updated: "12/09/2026", description: "Teste", features: [], footer: "Rodapé" }, "Conteúdo");
    let renderer;
    await act(async () => { renderer = TestRenderer.create(frame("/termos", usuario ? React.createElement("main", { id: "conteudo-principal" }, legal) : legal)); });
    assert.equal(renderer.root.findAllByType("main").length, 1);
    assert.equal(renderer.root.findAllByProps({ id: "conteudo-principal" }).length, 1);
    await act(async () => renderer.unmount());
  }
});

test("titles describe each route and omit record identities", () => {
  assert.notEqual(pageTitle("/biblioteca"), pageTitle("/apresentacao"));
  assert.equal(pageTitle("/validar/CONFIDENTIAL"), "Validar documento · CorVIA");
  assert.ok(!pageTitle("/admin/usuarios/998899").includes("998899"));
});
