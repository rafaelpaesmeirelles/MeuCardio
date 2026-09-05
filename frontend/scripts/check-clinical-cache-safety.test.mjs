import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import vm from "node:vm";
import test from "node:test";
import { transformSync } from "esbuild";

const root = new URL("../", import.meta.url);
const read = (path) => readFileSync(new URL(path, root), "utf8");
function load(path, globals = {}, require = () => { throw new Error("Unexpected import"); }) {
  const module = { exports: {} };
  const { code } = transformSync(read(path), {
    loader: path.endsWith(".tsx") ? "tsx" : "ts", format: "cjs", jsx: "automatic",
    define: { "import.meta.env.VITE_API_URL": '"/api"' },
  });
  vm.runInNewContext(code, { module, exports: module.exports, require, console, ...globals }, {
    filename: fileURLToPath(new URL(path, root)),
  });
  return module.exports;
}

function cacheStorage() {
  const deleted = [];
  return { deleted, caches: {
    keys: async () => ["corvia-emergencia", "corvia-emergencia-v1", "corvia-emergencia-v2",
      "corvia-assets-v2", "corvia-space-scenes-v1", "another-app-emergencia"],
    delete: async (name) => { deleted.push(name); return true; },
  } };
}
const legacy = ["corvia-emergencia", "corvia-emergencia-v1", "corvia-emergencia-v2"];

test("all clinical API routes use NetworkOnly, including emergency doses", () => {
  let pwa;
  const require = (name) => {
    if (name === "vite") return { defineConfig: (config) => config };
    if (name === "@vitejs/plugin-react") return () => ({});
    if (name === "vite-plugin-pwa") return { VitePWA: (config) => { pwa = config; return {}; } };
    throw new Error(name);
  };
  load("vite.config.ts", { self: { location: { origin: "https://corvia.test" } } }, require);
  for (const pathname of ["/api/emergencia", "/api/emergencia/abc", "/api/relacionados", "/api/auth/me"]) {
    const url = new URL(pathname, "https://corvia.test");
    const rule = pwa.workbox.runtimeCaching.find(({ urlPattern }) =>
      typeof urlPattern === "function"
        ? urlPattern({ url, request: { mode: "cors" } })
        : urlPattern.test(url.href));
    assert.equal(rule?.handler, "NetworkOnly", pathname);
  }
  assert.ok(pwa.workbox.importScripts.includes("/corvia-clinical-cache-cleanup-v1.js"));
});

test("service worker activation removes legacy clinical caches and preserves static assets", async () => {
  const { caches, deleted } = cacheStorage();
  let activate;
  let completion;
  vm.runInNewContext(read("public/corvia-clinical-cache-cleanup-v1.js"), {
    caches, self: { addEventListener: (name, callback) => { assert.equal(name, "activate"); activate = callback; } },
  });
  activate({ waitUntil: (promise) => { completion = promise; } });
  await completion;
  assert.deepEqual(deleted, legacy);
});

test("logout helper removes only legacy clinical caches", async () => {
  const { caches, deleted } = cacheStorage();
  await load("src/lib/clinicalCache.ts", { caches }).clearLegacyClinicalCaches();
  assert.deepEqual(deleted, legacy);
});

test("logout helper tolerates browsers without Cache Storage", async () => {
  await load("src/lib/clinicalCache.ts").clearLegacyClinicalCaches();
});

for (const failNetwork of [false, true]) {
  test(`API logout clears clinical caches even when network fails: ${failNetwork}`, async () => {
    let purged = 0;
    const removed = [];
    const { api } = load("src/lib/api.ts", {
      window: { localStorage: { removeItem: (key) => removed.push(key) } },
      fetch: async () => { if (failNetwork) throw new Error("offline"); return { ok: true }; },
    }, () => ({ clearLegacyClinicalCaches: async () => { purged += 1; } }));
    if (failNetwork) await assert.rejects(api.logout(), /offline/);
    else await api.logout();
    assert.equal(purged, 1);
    assert.ok(removed.includes("meucardio.token"));
  });
}

test("Cache Storage errors do not prevent local logout", async () => {
  const warnings = [];
  const { api } = load("src/lib/api.ts", {
    window: { localStorage: { removeItem() {} } },
    fetch: async () => ({ ok: true }),
    console: { warn: (message) => warnings.push(message) },
  }, () => ({ clearLegacyClinicalCaches: async () => { throw new Error("unavailable"); } }));
  await api.logout();
  assert.equal(warnings.length, 1);
});

test("failed server logout still clears the current user's React state", async () => {
  const changes = [];
  const removed = [];
  let stateIndex = 0;
  const react = {
    createContext: () => ({ Provider: "provider" }), useContext() {}, useEffect() {},
    useState: (value) => { const index = stateIndex++; return [value, (next) => changes.push([index, next])]; },
  };
  const require = (name) => {
    if (name === "react") return react;
    if (name === "react/jsx-runtime") return { jsx: (component, props) => props };
    if (name === "./api") return { api: { logout: async () => { throw new Error("offline"); } } };
    throw new Error(name);
  };
  const { AuthProvider } = load("src/lib/auth.tsx", {
    window: { sessionStorage: { removeItem: (key) => removed.push(key) } },
  }, require);
  const view = AuthProvider({ children: null });
  await assert.rejects(view.value.sair(), /offline/);
  assert.deepEqual(changes, [[0, null]]);
  assert.equal(removed.length, 1);
});
