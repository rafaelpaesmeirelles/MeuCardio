import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { transform } from "esbuild";
import React from "react";
import TestRenderer, { act } from "react-test-renderer";

const require = createRequire(import.meta.url);
async function compile(path, dependencies = {}) {
  const source = await readFile(new URL(path, import.meta.url), "utf8");
  const output = await transform(source, { loader: path.endsWith("tsx") ? "tsx" : "ts", format: "cjs", jsx: "automatic" });
  const module = { exports: {} };
  new Function("require", "module", "exports", output.code)(name => dependencies[name] || require(name), module, module.exports);
  return module.exports;
}

test("departure keeps the appointment date, buffer, midnight boundary and return semantics", async () => {
  const { mobilitySchedule } = await compile("../src/lib/mobilitySchedule.ts");
  const appointment = { starts_at: "2026-09-10T00:10:00-03:00", arrival_buffer_minutes: 15 };
  const calculated = mobilitySchedule(appointment, 1800);
  assert.equal(calculated.start.toISOString(), "2026-09-10T03:10:00.000Z");
  assert.equal(calculated.departure.toISOString(), "2026-09-10T02:25:00.000Z");
  assert.equal(mobilitySchedule(appointment).departure, null, "do not invent departure without a route");
  assert.equal(mobilitySchedule(appointment, 0).departure, null);
  assert.equal(mobilitySchedule(null), null);
  assert.equal(mobilitySchedule({ starts_at: "invalid" }, 60), null);
  const returning = mobilitySchedule({ ...appointment, source: "return" }, 1800);
  assert.equal(returning.departure.getTime(), returning.start.getTime(), "return begins when the last commitment ends");
});

test("scientific sidebar shows actual milestones, remembers topic, cancels stale responses and handles failure", async () => {
  const stored = new Map();
  const originalStorage = globalThis.sessionStorage;
  globalThis.sessionStorage = { getItem: key => stored.get(key), setItem: (key, value) => stored.set(key, value) };
  const storage = await compile("../src/lib/scientificTimeline.ts");
  storage.rememberTimelineTopic(31, "B");
  const requests = [];
  const Card = (await compile("../src/components/ScientificTimelineCard.tsx", {
    "../lib/api": { api: { get: url => new Promise((resolve, reject) => requests.push({ url, resolve, reject })) } },
    "../lib/auth": { useAuth: () => ({ usuario: { id: 31 } }) },
    "../lib/scientificTimeline": storage,
    "react-router-dom": { Link: ({ to, children, ...props }) => React.createElement("a", { href: to, ...props }, children) },
    "./Icone": { default: () => null, __esModule: true },
  })).default;
  let renderer;
  const text = () => JSON.stringify(renderer.toJSON());
  const summary = tema => ({ tema, total: 2, primeiro_ano: 2020, ultimo_ano: 2026, marcos: [
    { ano: 2020, titulo: `Older ${tema}`, slug: `${tema}-old`, rota: `/estudos/${tema}-old` },
    { ano: 2026, titulo: `Latest ${tema}`, slug: `${tema}-new`, rota: `/estudos/${tema}-new` },
  ] });
  try {
    await act(async () => { renderer = TestRenderer.create(React.createElement(Card)); });
    await act(async () => requests[0].resolve([{ tema: "A", total_marcos: 2 }, { tema: "B", total_marcos: 2 }]));
    assert.match(requests[1].url, /tema=B/);
    await act(async () => renderer.root.findByType("select").props.onChange({ target: { value: "A" } }));
    await act(async () => requests[1].resolve(summary("B")));
    assert.doesNotMatch(text(), /Latest B/, "a late response cannot overwrite the selected theme");
    await act(async () => requests[2].resolve(summary("A")));
    assert.match(text(), /Latest A/);
    assert.doesNotMatch(text(), /Older A/);
    assert.match(text(), /2020–2026/);
    assert.ok(renderer.root.findAllByType("a").some(link => link.props.href === "/trilhas/timeline?tema=A"));
    assert.equal(storage.lastTimelineTopic(31), "A");
    assert.equal(storage.lastTimelineTopic(32), "", "topic memory is scoped to the user");
    await act(async () => renderer.root.findByType("select").props.onChange({ target: { value: "B" } }));
    await act(async () => requests.at(-1).reject(new Error("offline")));
    assert.match(text(), /Não foi possível carregar/);
    assert.doesNotMatch(text(), /Latest A/);
    await act(async () => renderer.root.findByType("button").props.onClick());
    await act(async () => requests.at(-1).resolve([]));
    assert.match(text(), /quando houver marcos científicos publicados/);
  } finally {
    if (renderer) await act(async () => renderer.unmount());
    globalThis.sessionStorage = originalStorage;
  }
});
