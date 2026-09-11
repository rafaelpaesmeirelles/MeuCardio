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

function pwaConfig() {
  let pwa;
  const { default: vite } = load("vite.config.ts", {
    Buffer, self: { location: { origin: "https://corvia.test" } },
  }, (name) => {
    if (name === "vite") return { defineConfig: (config) => config };
    if (name === "@vitejs/plugin-react") return () => ({});
    if (name === "vite-plugin-pwa") return { VitePWA: (config) => { pwa = config; return {}; } };
    throw new Error(name);
  });
  return { pwa, graph: vite.plugins.find(({ name }) => name === "corvia-precache-dependencies") };
}

function diagramBundle(coreSize = 101 * 1024) {
  const chunk = (name, moduleId, imports = [], dynamicImports = [], options = {}) => ({
    type: "chunk", fileName: `assets/${name}-hash.js`, moduleIds: [moduleId],
    imports: imports.map((id) => `assets/${id}-hash.js`),
    dynamicImports: dynamicImports.map((id) => `assets/${id}-hash.js`),
    code: "x", isEntry: false, isDynamicEntry: false, ...options,
  });
  return Object.fromEntries([
    chunk("index", "/app/src/main.tsx", ["shell-shared"], ["Home", "core", "another-page"], { isEntry: true }),
    chunk("Home", "/app/src/pages/CardiologySpacesHome.tsx", ["shell-shared", "home-shared"]),
    chunk("AppFrame", "/app/src/components/CardiologySpacesAppFrame.tsx", ["frame-shared"]),
    chunk("another-page", "/app/src/pages/Documento.tsx", ["document-shared"]),
    chunk("shell-shared", "/app/node_modules/shared/index.js"),
    chunk("home-shared", "/app/node_modules/shared/home.js"),
    chunk("frame-shared", "/app/node_modules/shared/frame.js"),
    chunk("document-shared", "/app/node_modules/shared/document.js"),
    chunk("core", "/app/node_modules/mermaid/dist/mermaid.core.mjs", ["index"], ["diagram"], {
      isDynamicEntry: true, code: "x".repeat(coreSize),
    }),
    chunk("diagram", "/app/node_modules/mermaid/dist/chunks/diagram.mjs", ["core", "exclusive", "home-shared", "frame-shared", "document-shared"], ["nested"]),
    chunk("exclusive", "/app/node_modules/diagram-only/index.js", ["shell-shared"]),
    chunk("nested", "/app/node_modules/mermaid/dist/chunks/nested.mjs", ["diagram"]),
  ].map((item) => [item.fileName, item]));
}

test("installation/social PNGs and retired SVGs stay public without duplicate initial downloads", async () => {
  const { pwa } = pwaConfig();
  assert.equal(pwa.includeManifestIcons, false, "manifest icons bypass globIgnores unless disabled explicitly");
  assert.deepEqual(Array.from(pwa.manifest.icons, ({ src }) => src), [
    "/atelier/corvia-mark-atelier-192.png", "/atelier/corvia-mark-atelier-512.png",
  ]);
  const excluded = ["atelier/corvia-logo-atelier.png", "atelier/corvia-mark-atelier-192.png",
    "atelier/corvia-mark-atelier-512.png", "corvia-logo-canonical.svg", "corvia-logo-canonical-dark.svg",
    "corvia-logo-spaces.svg", "corvia-logo-spaces-dark.svg", "corvia-mark-canonical.svg"];
  for (const url of excluded) {
    assert.ok(readFileSync(new URL(`public/${url}`, root)).length > 0, `${url} remains available`);
    assert.ok(pwa.workbox.globIgnores.includes(url), url);
    assert.ok(!pwa.includeAssets.includes(url), url);
  }
  const visual = ["atelier/corvia-logo-atelier.svg", "atelier/corvia-mark-atelier.svg"];
  for (const url of visual) {
    assert.ok(pwa.includeAssets.includes(url), `${url} must remain in the offline shell`);
    assert.ok(!pwa.workbox.globIgnores.includes(url), url);
  }
  const { manifest } = await pwa.workbox.manifestTransforms[0]([...excluded, ...visual, "index.html"].map((url) => ({ url, size: 100 })));
  assert.deepEqual(Array.from(manifest, ({ url }) => url), [...visual, "index.html"]);
});

test("only the on-demand Mermaid graph leaves precache; all app static dependencies remain", async () => {
  const { pwa, graph } = pwaConfig();
  const bundle = diagramBundle();
  graph.generateBundle({}, bundle);
  const entries = Object.values(bundle).map(({ fileName: url, code }) => ({ url, size: Buffer.byteLength(code) }));
  const { manifest } = await pwa.workbox.manifestTransforms[0](entries);
  const removed = entries.filter(({ url }) => !manifest.some((entry) => entry.url === url)).map(({ url }) => url);
  assert.deepEqual(removed, ["core", "diagram", "exclusive", "nested"].map((id) => `assets/${id}-hash.js`));
  for (const url of removed) {
    const rule = pwa.workbox.runtimeCaching.find(({ urlPattern }) => typeof urlPattern !== "function" && urlPattern.test(`https://corvia.test/${url}`));
    assert.equal(rule?.handler, "NetworkFirst", `${url} remains available after first use`);
  }
});

test("renderers remain precached if their Mermaid core fits the existing offline budget", async () => {
  const { pwa, graph } = pwaConfig();
  const bundle = diagramBundle(100 * 1024);
  graph.generateBundle({}, bundle);
  const entries = Object.values(bundle).map(({ fileName: url, code }) => ({ url, size: Buffer.byteLength(code) }));
  const { manifest } = await pwa.workbox.manifestTransforms[0](entries);
  assert.equal(manifest.length, entries.length);
});

test("a graph renderer required statically by Home is protected even when it exceeds the lazy graph", async () => {
  const { pwa, graph } = pwaConfig();
  const bundle = diagramBundle();
  bundle["assets/Home-hash.js"].imports.push("assets/diagram-hash.js");
  graph.generateBundle({}, bundle);
  const { manifest } = await pwa.workbox.manifestTransforms[0]([
    { url: "assets/diagram-hash.js", size: 1024 }, { url: "assets/exclusive-hash.js", size: 1024 },
  ]);
  assert.equal(manifest.length, 2);
});

test("repeated bundle generation does not retain removed graph decisions from a previous build", async () => {
  const { pwa, graph } = pwaConfig();
  graph.generateBundle({}, diagramBundle());
  graph.generateBundle({}, diagramBundle(100 * 1024));
  const { manifest } = await pwa.workbox.manifestTransforms[0]([{ url: "assets/diagram-hash.js", size: 1024 }]);
  assert.equal(manifest.length, 1);
});

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

test("public tour media bypasses SPA fallback and navigation caches even on direct download", () => {
  let pwa;
  load("vite.config.ts", { self: { location: { origin: "https://corvia.test" } } }, (name) => {
    if (name === "vite") return { defineConfig: (config) => config };
    if (name === "@vitejs/plugin-react") return () => ({});
    if (name === "vite-plugin-pwa") return { VitePWA: (config) => { pwa = config; return {}; } };
    throw new Error(name);
  });
  for (const extension of ["mp4", "jpg", "vtt"]) {
    const url = new URL(`/media/corvia-apresentacao-20260911.${extension}`, "https://corvia.test");
    assert.ok(pwa.workbox.navigateFallbackDenylist.some((pattern) => pattern.test(url.pathname)), url.pathname);
    for (const mode of ["navigate", "cors", "no-cors"]) {
      const rule = pwa.workbox.runtimeCaching.find(({ urlPattern }) => typeof urlPattern === "function"
        ? urlPattern({ url, request: { mode } }) : urlPattern.test(url.href));
      assert.equal(rule, undefined, `${mode}: ${url.pathname} should use ordinary HTTP range semantics`);
    }
  }
  assert.ok(pwa.workbox.globIgnores.includes("media/**"));
  const caddy = read("../infra/Caddyfile");
  assert.match(caddy, /handle \/media\/\*\s*\{\s*root \* \/site\s*file_server/);
  assert.doesNotMatch(caddy.match(/handle \/media\/\*\s*\{[^}]*\}/)?.[0] ?? "", /try_files|index\.html/);
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
