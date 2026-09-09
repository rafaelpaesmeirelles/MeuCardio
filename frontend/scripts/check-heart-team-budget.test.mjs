import test, { after } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import React from "react";
import TestRenderer, { act } from "react-test-renderer";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { build } from "esbuild";

const root = fileURLToPath(new URL("../", import.meta.url));
const temp = await mkdtemp(path.join(root, "node_modules/.heart-team-budget-tests-"));
after(() => rm(temp, { recursive: true, force: true }));
const result = await build({
  entryPoints: [path.join(root, "src/pages/HeartTeamVirtual.tsx")], bundle: true, write: false, format: "esm", platform: "node",
  jsx: "automatic", external: ["react", "react/jsx-runtime", "react-router-dom"],
  plugins: [{ name: "fixture-api", setup(builder) {
    builder.onResolve({ filter: /\/lib\/api$/ }, () => ({ path: "api-stub", namespace: "fixture" }));
    builder.onLoad({ filter: /.*/, namespace: "fixture" }, () => ({ contents: `
      export class ApiError extends Error {}
      export const api = {
        get: (...args) => globalThis.heartTeamBudgetFixture.get(...args),
        post: (...args) => globalThis.heartTeamBudgetFixture.post(...args),
        uploadFormulario: (...args) => globalThis.heartTeamBudgetFixture.upload(...args),
      };`, loader: "js" }));
  } }],
});
const filename = path.join(temp, "HeartTeamVirtual.mjs");
await writeFile(filename, result.outputFiles[0].text);
const { default: HeartTeam, HeartTeamBudget: Budget } = await import(pathToFileURL(filename));
const text = (node) => node.children.map((child) => typeof child === "string" ? child : text(child)).join("");
const button = (renderer, label) => renderer.root.findAllByType("button").find((item) => text(item).includes(label));
const defaultQuote = { quote_id: 31, maximum_credit_centavos: 250, pricing_version: "test", currency: "BRL", expires_at: new Date(Date.now() + 900_000).toISOString(), case_fingerprint: "snapshot" };

async function mount(Component, { balance = 4000, quote = defaultQuote, props = {} } = {}) {
  const calls = [];
  const savedCase = { id: 9, status: "draft", question: "", selected_agents: [] };
  globalThis.heartTeamBudgetFixture = {
    get: async (url) => {
      calls.push(["get", url]);
      if (url === "/heart-team/cases" || url === "/heart-team/agents") return [];
      if (url === "/ai/wallet") return { enabled: true, billing_blocked: false, available_credit_centavos: balance };
      if (url === "/heart-team/cases/9") return savedCase;
      throw Error("Unexpected get " + url);
    },
    post: async (url, data) => {
      calls.push(["post", url, data]);
      if (url === "/heart-team/cases") return savedCase;
      if (url.endsWith("/estimate")) return quote;
      if (url.endsWith("/analyze")) return { status: "queued" };
      throw Error("Unexpected post " + url);
    },
    upload: async (...args) => { calls.push(["upload", ...args]); return {}; },
  };
  let renderer;
  await act(async () => {
    renderer = TestRenderer.create(React.createElement(MemoryRouter, { initialEntries: ["/heart-team"] },
      React.createElement(Routes, null, React.createElement(Route, { path: "/heart-team/:caseId?", element: React.createElement(Component, { caseId: 9, onStarted() {}, ...props }) })),
    ));
  });
  return { renderer, calls };
}

test("saving the case and attachments obtains a quote without starting paid analysis", async () => {
  const { renderer, calls } = await mount(HeartTeam);
  await act(async () => renderer.root.findAllByType("textarea")[0].props.onChange({ target: { value: "Caso clínico sintético sem identificadores" } }));
  for (let i = 1; i < 3; i++) await act(async () => renderer.root.findAllByType("input").filter((item) => item.props.type === "checkbox")[i].props.onChange({ target: { checked: true } }));
  await act(async () => renderer.root.findAllByType("input").find((item) => item.props.type === "file").props.onChange({ target: { files: [new File(["synthetic"], "case.txt")] } }));
  await act(async () => renderer.root.findByType("form").props.onSubmit({ preventDefault() {} }));
  const operations = calls.filter(([method]) => ["post", "upload"].includes(method)).map(([, url]) => url);
  assert.deepEqual(operations, ["/heart-team/cases", "/heart-team/cases/9/attachments", "/heart-team/cases/9/estimate"]);
  assert.equal(calls.some(([, url]) => url.endsWith("/analyze")), false);
  assert.match(JSON.stringify(renderer.toJSON()), /2,50/);
  assert.ok(button(renderer, "Executar por até"));
  await act(async () => renderer.unmount());
});

test("insufficient balance blocks execution and links to wallet without spending", async () => {
  const { renderer, calls } = await mount(Budget, { balance: 100, props: { initialDeidentified: true, initialMedicalReview: true } });
  assert.equal(button(renderer, "Executar por até").props.disabled, true);
  await act(async () => button(renderer, "Executar por até").props.onClick());
  assert.equal(calls.some(([, url]) => url.endsWith("/analyze")), false);
  assert.ok(renderer.root.findAllByType("a").some((item) => item.props.href === "/assinatura"));
  await act(async () => renderer.unmount());
});

test("execution sends the accepted quote and ceiling only after both medical confirmations", async () => {
  let started = 0;
  const { renderer, calls } = await mount(Budget, { props: { onStarted() { started++; } } });
  assert.equal(button(renderer, "Executar por até").props.disabled, true);
  for (let i = 0; i < 2; i++) await act(async () => renderer.root.findAllByType("input")[i].props.onChange({ target: { checked: true } }));
  await act(async () => button(renderer, "Executar por até").props.onClick());
  assert.deepEqual(calls.find(([, url]) => url.endsWith("/analyze")), ["post", "/heart-team/cases/9/analyze", {
    confirm_deidentified: true, confirm_medical_review: true, quote_id: 31, approved_max_credit_centavos: 250,
  }]);
  assert.equal(started, 1);
  await act(async () => renderer.unmount());
});

test("expired quotes require recalculation and cannot start a paid request", async () => {
  const { renderer, calls } = await mount(Budget, { quote: { ...defaultQuote, expires_at: "2000-01-01T00:00:00Z" }, props: { initialDeidentified: true, initialMedicalReview: true } });
  await act(async () => button(renderer, "Executar por até").props.onClick());
  assert.equal(calls.some(([, url]) => url.endsWith("/analyze")), false);
  assert.match(JSON.stringify(renderer.toJSON()), /expirou/);
  assert.equal(button(renderer, "Executar por até"), undefined);
  await act(async () => renderer.unmount());
});
