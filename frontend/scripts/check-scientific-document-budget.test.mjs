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
const temp = await mkdtemp(path.join(root, "node_modules/.document-budget-tests-"));
after(() => rm(temp, { recursive: true, force: true }));
const result = await build({
  entryPoints: [path.join(root, "src/pages/ScientificDocumentAI.tsx")], bundle: true, write: false, format: "esm", platform: "node",
  loader: { ".css": "empty" }, jsx: "automatic", external: ["react", "react/jsx-runtime", "react-router-dom"],
  plugins: [{ name: "fixture-api", setup(builder) {
    builder.onResolve({ filter: /\/lib\/api$/ }, () => ({ path: "api-stub", namespace: "fixture" }));
    builder.onLoad({ filter: /.*/, namespace: "fixture" }, () => ({ contents: `
      export class ApiError extends Error {}
      export const api = {
        get: (...args) => globalThis.documentBudgetFixture.get(...args),
        post: (...args) => globalThis.documentBudgetFixture.post(...args),
        upload: (...args) => globalThis.documentBudgetFixture.upload(...args),
      };`, loader: "js" }));
  } }],
});
const filename = path.join(temp, "ScientificDocumentAI.mjs");
await writeFile(filename, result.outputFiles[0].text);
const { default: Page } = await import(pathToFileURL(filename));
const text = (node) => node.children.map((child) => typeof child === "string" ? child : text(child)).join("");
const button = (renderer, label) => renderer.root.findAllByType("button").find((item) => text(item).includes(label));
const quoteDefault = { quote_id: 31, maximum_credit_centavos: 650, available_credit_centavos: 4000, currency: "BRL", includes_translation: true, expires_at: new Date(Date.now() + 900_000).toISOString() };

async function mount({ quote = quoteDefault, failAnalysis = false } = {}) {
  const calls = [];
  const doc = { id: 9, title: "Documento sintético", document_type: "artigo", analysis_status: "pendente" };
  globalThis.documentBudgetFixture = {
    get: async (url) => { calls.push(["get", url]); return url === "/documentos-cientificos-ia" ? [doc, { ...doc, id: 10, title: "Outro documento" }] : { ...doc, id: Number(url.split("/").at(-1)) }; },
    post: async (url, data) => {
      calls.push(["post", url, data]);
      if (url.endsWith("/orcamento")) return quote;
      if (url.endsWith("/analisar")) { if (failAnalysis) throw Error("stale quote"); return { ...doc, analysis_status: "concluido" }; }
      throw Error("Unexpected post " + url);
    },
    upload: async (...args) => { calls.push(["upload", ...args]); return doc; },
  };
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(MemoryRouter, null, React.createElement(Page))); });
  await act(async () => button(renderer, "Documento sintético").props.onClick());
  return { renderer, calls };
}
const analyses = (calls) => calls.filter(([method, url]) => method === "post" && url.endsWith("/analisar"));

test("quote calculation is free and only confirmation sends the exact approved ceiling", async () => {
  const { renderer, calls } = await mount();
  assert.equal(button(renderer, "Confirmar análise"), undefined);
  await act(async () => button(renderer, "Calcular orçamento").props.onClick());
  assert.equal(analyses(calls).length, 0);
  assert.match(JSON.stringify(renderer.toJSON()), /eventual tradução integral/);
  assert.match(text(button(renderer, "Confirmar análise")), /6,50/);
  await act(async () => button(renderer, "Confirmar análise").props.onClick());
  assert.deepEqual(analyses(calls), [["post", "/documentos-cientificos-ia/9/analisar", { quote_id: 31, approved_max_credit_centavos: 650 }]]);
  assert.equal(button(renderer, "Confirmar análise"), undefined);
  await act(async () => renderer.unmount());
});

test("insufficient credit blocks paid execution and links to wallet", async () => {
  const { renderer, calls } = await mount({ quote: { ...quoteDefault, available_credit_centavos: 100 } });
  await act(async () => button(renderer, "Calcular orçamento").props.onClick());
  assert.equal(button(renderer, "Confirmar análise").props.disabled, true);
  await act(async () => button(renderer, "Confirmar análise").props.onClick());
  assert.equal(analyses(calls).length, 0);
  assert.ok(renderer.root.findAllByType("a").some((item) => item.props.href === "/assinatura"));
  await act(async () => renderer.unmount());
});

test("expired quotes and selecting another document cannot reuse an approval", async () => {
  const { renderer, calls } = await mount({ quote: { ...quoteDefault, expires_at: "2000-01-01T00:00:00Z" } });
  await act(async () => button(renderer, "Calcular orçamento").props.onClick());
  await act(async () => button(renderer, "Confirmar análise").props.onClick());
  assert.equal(analyses(calls).length, 0);
  assert.match(JSON.stringify(renderer.toJSON()), /expirou/);
  await act(async () => button(renderer, "Calcular orçamento").props.onClick());
  await act(async () => button(renderer, "Outro documento").props.onClick());
  assert.equal(button(renderer, "Confirmar análise"), undefined);
  await act(async () => renderer.unmount());
});

test("failed paid requests consume the one-use quote in UI and require a fresh estimate", async () => {
  const { renderer, calls } = await mount({ failAnalysis: true });
  await act(async () => button(renderer, "Calcular orçamento").props.onClick());
  await act(async () => button(renderer, "Confirmar análise").props.onClick());
  assert.equal(analyses(calls).length, 1);
  assert.equal(button(renderer, "Confirmar análise"), undefined);
  assert.ok(button(renderer, "Calcular orçamento"));
  assert.match(JSON.stringify(renderer.toJSON()), /Não foi possível concluir/);
  await act(async () => renderer.unmount());
});
