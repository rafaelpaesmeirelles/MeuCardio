import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { stripTypeScriptTypes } from "node:module";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../src/lib/googleMapsLoader.ts", import.meta.url), "utf8");
const executable = stripTypeScriptTypes(source, { mode: "strip" }).replace(/^export\s+/gm, "")
  + "\nglobalThis.loader = { loadGoogleMaps, MAPS_AUTH_ERROR };";

function environment({ existingScript = false, sdk, previousAuth, onAppend } = {}) {
  class Events {
    listeners = new Map();
    addEventListener(type, listener) {
      if (!this.listeners.has(type)) this.listeners.set(type, new Set());
      this.listeners.get(type).add(listener);
    }
    removeEventListener(type, listener) { this.listeners.get(type)?.delete(listener); }
    dispatchEvent(event) {
      for (const listener of [...(this.listeners.get(event.type) || [])]) listener.call(this, event);
      return true;
    }
    count(type) { return this.listeners.get(type)?.size || 0; }
  }
  class FakeEvent { constructor(type) { this.type = type; } }
  const scripts = [];
  const attached = [];
  class Script extends Events {
    dataset = {};
    src = "";
    async = false;
    removed = false;
    remove() {
      this.removed = true;
      const index = attached.indexOf(this);
      if (index >= 0) attached.splice(index, 1);
    }
    fire(type) { this.dispatchEvent(new FakeEvent(type)); }
  }
  const window = new Events();
  const timers = new Map();
  let nextTimer = 1;
  window.setTimeout = (callback, delay) => {
    const id = nextTimer++;
    timers.set(id, { callback, delay });
    return id;
  };
  window.clearTimeout = id => timers.delete(id);
  if (sdk) window.google = sdk;
  if (previousAuth) window.gm_authFailure = previousAuth;
  const document = {
    querySelector(selector) {
      assert.equal(selector, 'script[data-corvia-google-maps="true"]');
      return attached.find(script => script.dataset.corviaGoogleMaps === "true") || null;
    },
    createElement(tag) {
      assert.equal(tag, "script");
      const script = new Script();
      scripts.push(script);
      return script;
    },
    head: { appendChild(script) { attached.push(script); onAppend?.({ window, script }); return script; } },
  };
  if (existingScript) {
    const script = document.createElement("script");
    script.dataset.corviaGoogleMaps = "true";
    attached.push(script);
  }
  const context = vm.createContext({
    window, document, Event: FakeEvent,
    fetch() { assert.fail("Network access is forbidden in loader tests"); },
    XMLHttpRequest() { assert.fail("Network access is forbidden in loader tests"); },
  });
  vm.runInContext(executable, context, { filename: "googleMapsLoader.ts", timeout: 1000 });
  return {
    ...context.loader, window, scripts, attached, timers,
    sdkReady() { return window.google = { maps: { Map: function Map() {} } }; },
    expireTimers() {
      for (const [id, timer] of [...timers]) { timers.delete(id); timer.callback(); }
    },
    assertClean(script) {
      assert.equal(timers.size, 0);
      assert.equal(script.count("load"), 0);
      assert.equal(script.count("error"), 0);
      assert.equal(window.count(context.loader.MAPS_AUTH_ERROR), 0);
      assert.equal(window.corviaMapsReady, undefined);
    },
  };
}

test("concurrent consumers share one SDK insertion, timer and pending promise", async () => {
  const env = environment();
  const first = env.loadGoogleMaps("synthetic-browser-token");
  const second = env.loadGoogleMaps("synthetic-browser-token");
  const third = env.loadGoogleMaps("synthetic-browser-token");
  assert.strictEqual(first, second); assert.strictEqual(second, third);
  assert.equal(env.scripts.length, 1); assert.equal(env.attached.length, 1);
  assert.equal(env.timers.size, 1); assert.equal([...env.timers.values()][0].delay, 15000);
  const sdk = env.sdkReady(); env.window.corviaMapsReady();
  for (const result of await Promise.all([first, second, third])) assert.strictEqual(result, sdk);
  env.assertClean(env.scripts[0]);
});

test("network error removes the failed SDK and permits a clean retry", async () => {
  const env = environment();
  const first = env.loadGoogleMaps("synthetic-browser-token");
  const rejection = assert.rejects(first, /Verifique a conexão/);
  const failed = env.scripts[0]; failed.fire("error"); await rejection;
  assert.equal(failed.removed, true); env.assertClean(failed);
  const retry = env.loadGoogleMaps("synthetic-browser-token");
  assert.notStrictEqual(retry, first); assert.equal(env.scripts.length, 2); assert.equal(env.attached.length, 1);
  const sdk = env.sdkReady(); env.scripts[1].fire("load");
  assert.strictEqual(await retry, sdk); env.assertClean(env.scripts[1]);
});

test("timeout removes the incomplete SDK and permits retry without poisoning the session", async () => {
  const env = environment({ sdk: { maps: {} } });
  const first = env.loadGoogleMaps("synthetic-browser-token");
  const rejection = assert.rejects(first, /demorou para responder/);
  env.expireTimers(); await rejection;
  assert.equal(env.attached.length, 0); env.assertClean(env.scripts[0]);
  const retry = env.loadGoogleMaps("synthetic-browser-token");
  const sdk = env.sdkReady(); env.window.corviaMapsReady();
  assert.strictEqual(await retry, sdk); assert.equal(env.scripts.length, 2);
});

test("an incomplete namespace cannot resolve on load or an early callback", async () => {
  const env = environment({ sdk: { maps: { Map: "not-a-constructor" } } });
  let resolved = false;
  const pending = env.loadGoogleMaps("synthetic-browser-token").then(value => { resolved = true; return value; });
  env.scripts[0].fire("load"); env.window.corviaMapsReady();
  await Promise.resolve();
  assert.equal(resolved, false); assert.equal(env.timers.size, 1);
  const sdk = env.sdkReady(); env.window.corviaMapsReady();
  assert.strictEqual(await pending, sdk); env.assertClean(env.scripts[0]);
});

test("SDK callback may complete before the script load event", async () => {
  const env = environment();
  const pending = env.loadGoogleMaps("synthetic-browser-token");
  const sdk = env.sdkReady(); env.window.corviaMapsReady();
  assert.strictEqual(await pending, sdk); env.assertClean(env.scripts[0]);
  env.scripts[0].fire("load"); env.scripts[0].fire("error");
  assert.strictEqual(await env.loadGoogleMaps("synthetic-browser-token"), sdk);
  assert.equal(env.scripts.length, 1);
});

test("synchronous cached SDK callback during insertion finds listeners already installed", async () => {
  const env = environment({ onAppend({ window, script }) {
    assert.equal(script.count("load"), 1); assert.equal(script.count("error"), 1);
    window.google = { maps: { Map: function Map() {} } };
    window.corviaMapsReady(); script.fire("load");
  } });
  assert.strictEqual(await env.loadGoogleMaps("synthetic-browser-token"), env.window.google);
  env.assertClean(env.scripts[0]);
});

test("a complete preloaded SDK requires no script or timer", async () => {
  const sdk = { maps: { Map: function Map() {} } };
  const env = environment({ sdk });
  assert.strictEqual(await env.loadGoogleMaps("synthetic-browser-token"), sdk);
  assert.equal(env.scripts.length, 0); assert.equal(env.timers.size, 0);
  assert.equal(typeof env.window.gm_authFailure, "function");
});

test("an existing in-flight tagged script is reused instead of duplicated", async () => {
  const env = environment({ existingScript: true });
  const pending = env.loadGoogleMaps("synthetic-browser-token");
  assert.equal(env.scripts.length, 1); assert.equal(env.attached.length, 1);
  const sdk = env.sdkReady(); env.scripts[0].fire("load");
  assert.strictEqual(await pending, sdk); env.assertClean(env.scripts[0]);
});

test("authentication failure rejects pending consumers, emits the shared event and chains the prior hook once", async () => {
  let previousCalls = 0;
  const env = environment({ previousAuth() { previousCalls += 1; } });
  let authEvents = 0;
  env.window.addEventListener(env.MAPS_AUTH_ERROR, () => { authEvents += 1; });
  const first = env.loadGoogleMaps("synthetic-browser-token");
  const second = env.loadGoogleMaps("synthetic-browser-token");
  const rejected = Promise.all([assert.rejects(first, /não autorizou/), assert.rejects(second, /não autorizou/)]);
  env.window.gm_authFailure(); await rejected;
  assert.equal(previousCalls, 1); assert.equal(authEvents, 1);
  assert.equal(env.attached.length, 0); assert.equal(env.timers.size, 0);
  assert.equal(env.window.corviaMapsReady, undefined);
  await assert.rejects(env.loadGoogleMaps("synthetic-browser-token"), /não autorizou/);
  assert.equal(env.scripts.length, 1);
});

test("late authentication failure remains visible even after SDK readiness", async () => {
  const env = environment({ sdk: { maps: { Map: function Map() {} } } });
  await env.loadGoogleMaps("synthetic-browser-token");
  let failure = 0;
  env.window.addEventListener(env.MAPS_AUTH_ERROR, () => { failure += 1; });
  env.window.gm_authFailure();
  assert.equal(failure, 1);
  await assert.rejects(env.loadGoogleMaps("synthetic-browser-token"), /não autorizou/);
  assert.equal(env.scripts.length, 0);
});

test("late events from a removed script cannot settle or clear a newer retry", async () => {
  const env = environment();
  const first = env.loadGoogleMaps("synthetic-browser-token");
  const rejected = assert.rejects(first, /demorou/);
  const stale = env.scripts[0]; env.expireTimers(); await rejected;
  const retry = env.loadGoogleMaps("synthetic-browser-token");
  const callback = env.window.corviaMapsReady;
  stale.fire("error"); stale.fire("load");
  assert.strictEqual(env.window.corviaMapsReady, callback); assert.equal(env.timers.size, 1);
  const sdk = env.sdkReady(); callback();
  assert.strictEqual(await retry, sdk); env.assertClean(env.scripts[1]);
});
