import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import React from "react";
import TestRenderer, { act } from "react-test-renderer";
import { transform } from "esbuild";

// Exercise the real component against a download that has dimensions but has
// not finished decoding: the progressive PNG shown in the reported video.
test("login shows only decoded frames, reuses downloads and cancels stale work", async () => {
  const source = (await readFile(new URL("../src/components/LoginGalaxy.tsx", import.meta.url), "utf8"))
    .replace(/import lightSource[^;]+;/, 'const lightSource = "/assets/light.webp";')
    .replace(/import darkSource[^;]+;/, 'const darkSource = "/assets/dark.webp";')
    .replace(/import \{ darkGalaxyPoster, lightGalaxyPoster \}[^;]+;/, 'const darkGalaxyPoster = "data:image/webp;base64,dark"; const lightGalaxyPoster = "data:image/webp;base64,light";');
  const transformed = await transform(source, { loader: "tsx", format: "cjs", jsx: "automatic" });
  const module = { exports: {} };
  const { createRequire } = await import("node:module");
  const require = createRequire(import.meta.url);
  new Function("require", "module", "exports", transformed.code)(require, module, module.exports);
  const Galaxy = module.exports.default;
  const originals = Object.fromEntries(["Image", "window", "document", "requestAnimationFrame", "cancelAnimationFrame"].map(key => [key, globalThis[key]]));
  const images = [];
  const visibleCanvases = [];
  const posters = [];
  const frames = new Map();
  const visibilityListeners = new Set();
  const motionListeners = new Set();
  let nextFrame = 1;
  const makeCanvas = () => {
    const calls = [];
    const writes = [];
    const context = Object.fromEntries(["translate", "scale", "rotate", "drawImage", "clearRect", "save", "restore"].map(name => [name, (...args) => calls.push([name, ...args])]));
    return { calls, writes, dataset: new Proxy({}, { set(target, key, value) { writes.push([key, value]); target[key] = value; return true; } }), getContext: () => context };
  };
  const motion = { matches: false, addEventListener: (_, fn) => motionListeners.add(fn), removeEventListener: (_, fn) => motionListeners.delete(fn) };
  globalThis.Image = class {
    naturalWidth = 1366;
    naturalHeight = 462;
    constructor() { images.push(this); }
    decode() { return new Promise((resolve, reject) => { this.finish = resolve; this.fail = reject; }); }
  };
  globalThis.window = { matchMedia: () => motion };
  globalThis.document = { hidden: false, createElement: makeCanvas, addEventListener: (_, fn) => visibilityListeners.add(fn), removeEventListener: (_, fn) => visibilityListeners.delete(fn) };
  globalThis.requestAnimationFrame = fn => { const id = nextFrame++; frames.set(id, fn); return id; };
  globalThis.cancelAnimationFrame = id => frames.delete(id);
  let renderer;
  try {
    await act(async () => {
      renderer = TestRenderer.create(React.createElement(Galaxy, { theme: "light" }), {
        createNodeMock: (node) => {
          if (node.type === "img") { const poster = { dataset: {} }; posters.push(poster); return poster; }
          const canvas = makeCanvas(); visibleCanvases.push(canvas); return canvas;
        },
      });
    });
    assert.equal(images.length, 1);
    assert.match(renderer.root.findByType("img").props.src, /^data:image\/webp;base64,/, "the initial complete frame needs no network request");
    assert.equal(posters[0].dataset.replaced, undefined, "the galaxy is present while downloading");
    assert.equal(visibleCanvases[0].dataset.ready, undefined);
    assert.equal(visibleCanvases[0].calls.length, 0, "partial dimensions do not count as decoded pixels");

    await act(async () => renderer.update(React.createElement(Galaxy, { theme: "dark" })));
    assert.equal(images.length, 2);
    await act(async () => images[0].finish());
    assert.equal(visibleCanvases[0].calls.length, 0, "late light download must not paint after switching to dark");
    await act(async () => images[1].finish());
    const darkCanvas = visibleCanvases.at(-1);
    assert.equal(darkCanvas.dataset.ready, "true");
    assert.equal(posters.at(-1).dataset.replaced, "true", "replace the poster only after a complete animated frame");
    assert.ok(darkCanvas.calls.some(([name]) => name === "drawImage"));
    for (let i = 0; i < 6; i++) {
      const scheduled = [...frames.values()]; frames.clear();
      scheduled.forEach(fn => fn(performance.now() + (i + 1) * 40));
    }
    assert.equal(darkCanvas.writes.length, 1, "animation must not invalidate styles on every frame");

    document.hidden = true;
    visibilityListeners.forEach(fn => fn());
    assert.equal(frames.size, 0);
    document.hidden = false;
    visibilityListeners.forEach(fn => fn());
    assert.equal(frames.size, 1);
    motion.matches = true;
    motionListeners.forEach(fn => fn());
    assert.equal(frames.size, 0, "reduced motion keeps a complete static frame");

    await act(async () => renderer.update(React.createElement(Galaxy, { theme: "light" })));
    assert.equal(images.length, 2, "returning to a theme reuses its decoded image");
    assert.equal(visibleCanvases.at(-1).dataset.ready, "true");
    await act(async () => renderer.unmount());
    assert.equal(frames.size, 0);
    assert.equal(visibilityListeners.size, 0);
    assert.equal(motionListeners.size, 0);

    // A fresh URL models a failed asset in the reported dark first load.
    const failedModule = { exports: {} };
    new Function("require", "module", "exports", transformed.code)(require, failedModule, failedModule.exports);
    await act(async () => {
      renderer = TestRenderer.create(React.createElement(failedModule.exports.default, { theme: "dark" }), {
        createNodeMock: node => {
          if (node.type === "img") { const poster = { dataset: {} }; posters.push(poster); return poster; }
          const canvas = makeCanvas(); visibleCanvases.push(canvas); return canvas;
        },
      });
    });
    const beforeFailure = images.length;
    await act(async () => images.at(-1).fail(new Error("network failure")));
    assert.equal(images.length, beforeFailure + 1, "retry the failed download once");
    await act(async () => images.at(-1).fail(new Error("still offline")));
    assert.equal(images.length, beforeFailure + 1, "do not retry indefinitely");
    assert.equal(visibleCanvases.at(-1).dataset.ready, undefined);
    assert.equal(posters.at(-1).dataset.replaced, undefined, "dark galaxy remains visible even when animation cannot load");
    assert.match(renderer.root.findByType("img").props.src, /^data:image\/webp;base64,dark$/);
  } finally {
    if (renderer) await act(async () => renderer.unmount());
    for (const [key, value] of Object.entries(originals)) {
      if (value === undefined) delete globalThis[key]; else globalThis[key] = value;
    }
  }
});
