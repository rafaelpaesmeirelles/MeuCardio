import test, { after } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import React from "react";
import TestRenderer, { act } from "react-test-renderer";
import { MemoryRouter } from "react-router-dom";
import { build } from "esbuild";

const root = fileURLToPath(new URL("../", import.meta.url));
const temp = await mkdtemp(path.join(root, "node_modules/.tct-disease-overview-tests-"));
after(() => rm(temp, { recursive: true, force: true }));
const built = await build({
  entryPoints: [path.join(root, "src/components/TctDiseaseOverview.tsx")],
  bundle: true, write: false, format: "esm", platform: "node", jsx: "automatic",
  external: ["react", "react/jsx-runtime", "react-router-dom"],
  plugins: [{ name: "fixture-api", setup(builder) {
    builder.onResolve({ filter: /\/lib\/api$/ }, () => ({ path: "api-stub", namespace: "fixture" }));
    builder.onLoad({ filter: /.*/, namespace: "fixture" }, () => ({
      contents: "export const api = { get: (...args) => globalThis.overviewAPI(...args) };", loader: "js",
    }));
  } }],
});
const filename = path.join(temp, "TctDiseaseOverview.mjs");
await writeFile(filename, built.outputFiles[0].text);
const { default: Overview } = await import(pathToFileURL(filename));
const disease = { slug: "doenca-a", name: "Doença A", summary: "Resumo do índice.", area: "geral", category: "hipertensao" };
const payload = { ...disease, summary: "Definição integral publicada.", epidemiology: "Contexto epidemiológico existente.",
  presentation: ["Sintoma primeiro", "Sintoma segundo", "Sintoma terceiro", "Sintoma quarto com ressalva integral."],
  diagnostic_approach: { confirmacao: ["Critério diagnóstico publicado."], avaliacao_inicial: ["Avaliação existente."] },
  source_refs: ["Diretriz publicada de referência"], source_urls: ["https://example.org/guideline", "javascript:alert(1)"],
  review_note: "INTERNAL REVIEW TOKEN", internal_metadata: { secret: "DO NOT EXPOSE" } };
const text = (node) => node.children.map((child) => typeof child === "string" ? child : text(child)).join("");
const allText = (renderer) => text(renderer.root);
const findButton = (renderer, prefix) => renderer.root.findAllByType("button").find((node) => text(node).startsWith(prefix));
const element = (value) => React.createElement(MemoryRouter, {}, React.createElement(Overview, { disease: value }));
const deferred = () => { let resolve; let reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return { promise, resolve, reject }; };

test("renders substantial published sections, human labels and safe sources without machine metadata", async () => {
  const calls = [];
  globalThis.overviewAPI = async (url) => { calls.push(url); return payload; };
  let renderer;
  await act(async () => { renderer = TestRenderer.create(element(disease)); });
  assert.deepEqual(calls, ["/specialty-guides/diseases/doenca-a"]);
  const output = allText(renderer);
  for (const value of ["Definição integral publicada.", "Contexto epidemiológico existente.", "Sintoma primeiro", "Confirmação diagnóstica", "Critério diagnóstico publicado.", "Avaliação inicial"]) assert.ok(output.includes(value), value);
  for (const value of ["confirmacao", "diagnostic_approach", "INTERNAL REVIEW TOKEN", "DO NOT EXPOSE", "[object Object]"]) assert.ok(!output.includes(value), value);
  assert.ok(renderer.root.findAllByType("a").some((a) => a.props.href === "/doencas/doenca-a"));
  assert.ok(renderer.root.findAllByType("a").some((a) => a.props.href === "https://example.org/guideline"));
  assert.ok(!renderer.root.findAllByType("a").some((a) => String(a.props.href).startsWith("javascript:")));
  assert.ok(!output.includes("Sintoma quarto"));
  await act(async () => findButton(renderer, "Ver restante: apresentação").props.onClick());
  assert.ok(allText(renderer).includes("Sintoma quarto com ressalva integral."));
  await act(async () => renderer.unmount());
});

test("long single fields expand intact and missing sections are not invented", async () => {
  const longText = "Texto clínico completo com ressalvas. ".repeat(50) + "CONDIÇÃO FINAL PRESERVADA.";
  globalThis.overviewAPI = async () => ({ ...disease, epidemiology: longText });
  let renderer;
  await act(async () => { renderer = TestRenderer.create(element(disease)); });
  assert.ok(!allText(renderer).includes("CONDIÇÃO FINAL"));
  assert.ok(!allText(renderer).includes("Fundamentos diagnósticos"));
  const button = findButton(renderer, "Ler conteúdo: epidemiologia");
  assert.equal(button.props["aria-expanded"], false);
  await act(async () => button.props.onClick());
  assert.ok(allText(renderer).includes(longText));
  assert.equal(findButton(renderer, "Recolher: epidemiologia").props["aria-expanded"], true);
  await act(async () => renderer.unmount());
});

test("subject changes clear old content and expansion and ignore stale replies", async () => {
  const first = deferred(), second = deferred();
  globalThis.overviewAPI = (url) => url.endsWith("doenca-a") ? first.promise : second.promise;
  let renderer;
  await act(async () => { renderer = TestRenderer.create(element(disease)); });
  assert.ok(allText(renderer).includes("Carregando"));
  const other = { slug: "doenca-b", name: "Doença B", summary: "Resumo B." };
  await act(async () => renderer.update(element(other)));
  assert.ok(!allText(renderer).includes("Resumo do índice."));
  await act(async () => second.resolve({ ...other, presentation: payload.presentation }));
  await act(async () => first.resolve(payload));
  assert.ok(allText(renderer).includes("Doença B"));
  assert.ok(!allText(renderer).includes("Definição integral publicada."));
  await act(async () => findButton(renderer, "Ver restante").props.onClick());
  assert.ok(allText(renderer).includes("Sintoma quarto"));
  globalThis.overviewAPI = async () => payload;
  await act(async () => renderer.update(element(disease)));
  assert.ok(!allText(renderer).includes("Sintoma quarto"));
  await act(async () => renderer.unmount());
});

test("detail failures show honest fallback and retry; late unmount responses have no effect", async () => {
  let attempts = 0;
  globalThis.overviewAPI = async () => { if (++attempts === 1) throw Error("raw server internal error"); return payload; };
  let renderer;
  await act(async () => { renderer = TestRenderer.create(element(disease)); });
  assert.ok(allText(renderer).includes("Não foi possível carregar os detalhes"));
  assert.ok(allText(renderer).includes("Resumo do índice."));
  assert.ok(!allText(renderer).includes("raw server"));
  await act(async () => findButton(renderer, "Tentar novamente").props.onClick());
  assert.equal(attempts, 2);
  assert.ok(allText(renderer).includes("Definição integral publicada."));
  const pending = deferred();
  globalThis.overviewAPI = () => pending.promise;
  await act(async () => renderer.update(element({ ...disease, slug: "pending" })));
  await act(async () => renderer.unmount());
  await act(async () => pending.resolve({ ...payload, slug: "pending" }));
  assert.equal(renderer.toJSON(), null);
});

test("a mismatched detail slug cannot display the wrong disease", async () => {
  globalThis.overviewAPI = async () => ({ ...payload, slug: "wrong-disease" });
  let renderer;
  await act(async () => { renderer = TestRenderer.create(element(disease)); });
  assert.ok(allText(renderer).includes("Não foi possível carregar os detalhes"));
  assert.ok(!allText(renderer).includes("Definição integral publicada."));
  await act(async () => renderer.unmount());
});
