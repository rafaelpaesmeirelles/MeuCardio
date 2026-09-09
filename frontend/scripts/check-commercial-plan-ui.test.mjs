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
const temp = await mkdtemp(path.join(root, "node_modules/.commercial-ui-tests-"));
after(() => rm(temp, { recursive: true, force: true }));
async function component(relativePath) {
  const result = await build({
    entryPoints: [path.join(root, relativePath)], bundle: true, write: false, format: "esm", platform: "node",
    jsx: "automatic", external: ["react", "react/jsx-runtime", "react-router-dom"],
    plugins: [{ name: "fixture-api", setup(builder) {
      builder.onResolve({ filter: /\/lib\/api$/ }, () => ({ path: "api-stub", namespace: "fixture" }));
      builder.onLoad({ filter: /.*/, namespace: "fixture" }, () => ({ contents: `
        export class ApiError extends Error {}
        export const api = {
          get: (...args) => globalThis.commercialFixture.get(...args),
          post: (...args) => globalThis.commercialFixture.post(...args),
          put: (...args) => globalThis.commercialFixture.put(...args),
        };`, loader: "js" }));
    } }],
  });
  const filename = path.join(temp, path.basename(relativePath, ".tsx") + ".mjs");
  await writeFile(filename, result.outputFiles[0].text);
  return (await import(pathToFileURL(filename))).default;
}
const Subscription = await component("src/pages/Assinatura.tsx");
const Wallet = await component("src/components/AIWalletCard.tsx");
const Gate = await component("src/components/CommercialFeatureGate.tsx");
const body = (renderer) => JSON.stringify(renderer.toJSON());
const text = (node) => node.children.map((child) => typeof child === "string" ? child : text(child)).join("");
const button = (renderer, label) => renderer.root.findAllByType("button").find((item) => text(item).includes(label));
const plans = [
  ["basico", "CorVIA Básico", 9990, false, false], ["basico_mail", "CorVIA Básico + Mail", 11990, false, true],
  ["ia", "CorVIA IA", 14990, true, false], ["completo", "CorVIA Completo", 16990, true, true],
].map(([id, name, price_centavos, ai, mail]) => ({ id, name, price_centavos, features: { tudo_com_tudo: true, ai, mail }, periodicidade: "mensal", ai_monthly_credit_centavos: ai ? 4000 : 0, checkout_available: true }));
const wallet = { enabled: true, monthly_credit_centavos: 4000, available_credit_centavos: 3700, spent_credit_centavos: 100, reserved_credit_centavos: 200, paid_available_credit_centavos: 0, budget_credit_centavos: null, period_start: "2026-09-01", period_end: "2026-10-01", billing_blocked: false };

async function mount(Component, props, { enabled = false, ai = false, get, post, put } = {}) {
  const calls = [];
  globalThis.commercialFixture = {
    get: async (url) => {
      calls.push(["get", url]);
      if (get) return get(url);
      if (url === "/billing/plans") return { plans, subscriptions_enabled: enabled, checkout_available: true, commercial_version: "current" };
      if (url === "/billing/status") return { status: "ativo", plano: "basico", entitlements: { ai, mail: false, tudo_com_tudo: true, source: "subscription", commercial_version: "legacy" } };
      if (url === "/ai/wallet") return wallet;
      if (url === "/ai-credits/packages") return { enabled, packages: [{ amount_centavos: 2990, credit_centavos: 2990 }], automatic_topup: false };
      throw new Error("Unexpected read " + url);
    },
    post: async (...args) => { calls.push(["post", ...args]); if (post) return post(...args); throw Error("Unexpected purchase"); },
    put: async (...args) => { calls.push(["put", ...args]); if (put) return put(...args); return {}; },
  };
  let renderer;
  await act(async () => { renderer = TestRenderer.create(React.createElement(MemoryRouter, null, React.createElement(Component, props))); });
  return { renderer, calls };
}

test("prelaunch renders four plans and configurable credit without purchase actions", async () => {
  const { renderer, calls } = await mount(Subscription, {}, { ai: true });
  assert.equal(renderer.root.findAllByType("article").length, 4);
  assert.match(body(renderer), /Novas assinaturas ainda/);
  assert.match(body(renderer), /40,00/);
  assert.equal(button(renderer, "Assinar este plano"), undefined);
  assert.equal(button(renderer, "Mudar para este plano"), undefined);
  assert.equal(button(renderer, "de crédito por"), undefined);
  assert.equal(calls.some(([method]) => method !== "get"), false);
  assert.equal(calls.some(([, url]) => url === "/ai-credits/packages"), false);
  await act(async () => renderer.unmount());
});

test("feature denial keeps gated children unmounted and shows a useful upgrade path", async () => {
  let mounted = 0;
  function Child() { mounted++; return React.createElement("p", null, "paid functionality"); }
  const { renderer } = await mount(Gate, { feature: "ai", children: React.createElement(Child) });
  assert.equal(mounted, 0);
  assert.match(body(renderer), /Conheça os planos/);
  assert.ok(renderer.root.findAllByType("a").some((item) => item.props.href === "/assinatura"));
  await act(async () => renderer.unmount());
});

test("an empty budget means all prepaid balance and zero pauses new use", async () => {
  const { renderer, calls } = await mount(Wallet, { subscriptionsEnabled: false });
  assert.equal(renderer.root.findByType("input").props.value, "");
  await act(async () => renderer.root.findByType("form").props.onSubmit({ preventDefault() {} }));
  assert.deepEqual(calls.find(([method]) => method === "put"), ["put", "/ai/wallet/budget", { budget_credit_centavos: null }]);
  await act(async () => renderer.root.findByType("input").props.onChange({ target: { value: "0" } }));
  await act(async () => renderer.root.findByType("form").props.onSubmit({ preventDefault() {} }));
  assert.deepEqual(calls.filter(([method]) => method === "put").at(-1)[2], { budget_credit_centavos: 0 });
  assert.equal(renderer.root.findByType("input").props.max, undefined);
  await act(async () => renderer.unmount());
});

test("a transport retry reuses the checkout request key instead of creating a second purchase", async () => {
  const { renderer, calls } = await mount(Wallet, { subscriptionsEnabled: true }, { enabled: true, post: async () => { throw Error("Connection interrupted"); } });
  await act(async () => button(renderer, "de crédito por").props.onClick());
  await act(async () => button(renderer, "de crédito por").props.onClick());
  const purchases = calls.filter(([method]) => method === "post");
  assert.equal(purchases.length, 2);
  assert.equal(purchases[0][1], "/ai-credits/checkout");
  assert.equal(purchases[0][2].amount_centavos, 2990);
  assert.equal(purchases[0][2].request_key, purchases[1][2].request_key);
  assert.match(purchases[0][2].request_key, /^[a-f0-9-]{36}$/);
  await act(async () => renderer.unmount());
});
