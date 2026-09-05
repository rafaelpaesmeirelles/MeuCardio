import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { runInNewContext } from "node:vm";
import test from "node:test";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const cleanup = readFileSync(resolve(root, "public/corvia-cache-cleanup.js"), "utf8");
const config = readFileSync(resolve(root, "vite.config.ts"), "utf8");

function worker(caches) {
  const listeners = new Map();
  runInNewContext(cleanup, {
    self: { addEventListener: (name, listener) => listeners.set(name, listener) },
    caches,
  });
  return listeners;
}

function activate(listeners) {
  let completion;
  listeners.get("activate")({ waitUntil: (promise) => { completion = promise; } });
  assert.equal(typeof completion?.then, "function");
  return completion;
}

test("removes legacy emergency caches, preserving visual and unrelated caches", async () => {
  const names = ["corvia-emergencia", "corvia-emergencia-v1", "corvia-emergencia-v2",
    "corvia-emergencia-v3", "corvia-assets-v2", "corvia-space-scenes-v1",
    "workbox-precache-v2", "corvia-emergencias-not-the-same-cache"];
  const removed = [];
  await activate(worker({ keys: async () => names, delete: async (name) => { removed.push(name); return true; } }));
  assert.deepEqual(removed, names.slice(0, 4));
});

test("activation awaits actual deletion completion", async () => {
  let finish;
  const pending = new Promise((resolve) => { finish = resolve; });
  let done = false;
  const completion = activate(worker({ keys: async () => ["corvia-emergencia-v2"], delete: () => pending }));
  completion.then(() => { done = true; });
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(done, false);
  finish(true);
  await completion;
  assert.equal(done, true);
});

test("cleanup is idempotent when no legacy cache remains", async () => {
  const names = new Set(["corvia-emergencia-v2", "corvia-assets-v2"]);
  const removed = [];
  const listeners = worker({ keys: async () => [...names], delete: async (name) => { removed.push(name); return names.delete(name); } });
  await activate(listeners);
  await activate(listeners);
  assert.deepEqual(removed, ["corvia-emergencia-v2"]);
  assert.deepEqual([...names], ["corvia-assets-v2"]);
});

test("Cache Storage errors are not silently reported as successful cleanup", async () => {
  const listeners = worker({ keys: async () => { throw new Error("storage unavailable"); } });
  await assert.rejects(activate(listeners), /storage unavailable/);
});

test("generated-worker configuration imports cleanup and keeps APIs network-only", () => {
  assert.match(config, /importScripts:\s*\["corvia-cache-cleanup\.js"\]/);
  assert.equal(config.includes('cacheName: "corvia-emergencia-v2"'), false);
  assert.equal(config.includes('urlPattern: /\\/api\\/emergencia/'), false);
  assert.ok(config.includes('urlPattern: /\\/api\\//,\n            handler: "NetworkOnly"'));
  assert.ok(config.includes('navigateFallbackDenylist: [/^\\/api\\//]'));
});

test("API requests, including navigation and logout-era calls, match NetworkOnly first", () => {
  // Evaluate the exact TS configuration after removing its import/export shell;
  // plugin dependencies are stubs, while all configured matchers are real.
  const executable = config.replace(/^import .*;\n/gm, "")
    .replace("export default defineConfig(", "globalThis.configuration = defineConfig(");
  const context = {
    defineConfig: (value) => value, react: () => ({}), VitePWA: (value) => value,
    self: { location: { origin: "https://corvia.example" } },
  };
  runInNewContext(executable, context);
  const rules = context.configuration.plugins[1].workbox.runtimeCaching;
  for (const mode of ["navigate", "cors", "same-origin"]) {
    for (const path of ["/api/emergencia", "/api/emergencia/protocolo", "/api/relacionados", "/api/auth/logout"]) {
      const url = new URL(path, "https://corvia.example");
      const rule = rules.find(({ urlPattern }) => typeof urlPattern === "function"
        ? urlPattern({ request: { mode }, url }) : urlPattern.test(url.href));
      assert.equal(rule?.handler, "NetworkOnly", `${mode} ${path}`);
    }
  }
});
