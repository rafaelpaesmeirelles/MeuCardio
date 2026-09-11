import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { stripTypeScriptTypes } from "node:module";
import test from "node:test";
import vm from "node:vm";

const home = readFileSync(new URL("../src/pages/CardiologySpacesHome.tsx", import.meta.url), "utf8");
const assistant = readFileSync(new URL("../src/components/PersonalAssistantPanel.tsx", import.meta.url), "utf8");
const geometry = readFileSync(new URL("../src/lib/mobilityGeometry.ts", import.meta.url), "utf8");
const adapter = await import(`data:text/javascript;base64,${Buffer.from(stripTypeScriptTypes(geometry)).toString("base64")}`);
const slice = (source, start, end) => {
  const from = source.indexOf(start);
  assert.notEqual(from, -1);
  const to = source.indexOf(end, from + start.length);
  assert.notEqual(to, -1);
  return source.slice(from, to);
};
const homeFunction = slice(home, "  async function startTravel()", "\n  function openExternalMap()");
const assistantFunction = slice(assistant, "  function atualizarDeslocamento()", "\n  if (!aberto)");
const closeHomeFunction = slice(home, "  function closeTravel()", "\n\n  useEffect");
const sanitize = slice(home, "function sanitizeMobilityResult", "\n\n\nexport default");
const settle = () => new Promise(resolve => setImmediate(resolve));
const target = { target_key: "appointment:demo-A", location: { latitude: 0, longitude: 0, name: "Local demonstrativo" } };
const result = (status = "live", destination = target) => ({ status, destination, routes: [{ geometry: { format: "encoded_polyline", value: "??AA", precision: 5 } }] });

function environment(kind, { saved = true, planned = target } = {}) {
  const requests = [];
  const states = { target: planned, result: null, error: null, busy: false, open: false };
  const generation = { current: 0 };
  const identity = { current: "context-A" };
  const routeContext = { current: { identity: "context-A", open: true } };
  let gps;
  const globals = {
    api: { post(path, payload) { return new Promise((resolve, reject) => requests.push({ path, payload, resolve, reject })); } },
    usuario: { id: "demonstration" }, plannedMobilityTarget: planned,
    mobilityPreference: { enabled: true, day_start_location_id: 1 }, mobilityDayContext: { stage: "before_first" },
    returnHomeActive: false, usesSavedOrigin: saved, travelIdentity: "context-A",
    currentTravelIdentity: identity, travelRequestGeneration: generation, travelResultIdentity: { current: null },
    travelIdentityFor: value => value?.target_key === target.target_key ? "context-A" : "context-B",
    withoutReservedSmokeTestRecord: value => value,
    mobilityRouteError: adapter.mobilityResultError, mobilityResultError: adapter.mobilityResultError,
    geolocationErrorMessage: () => "Erro demonstrativo",
    currentPosition: () => new Promise(resolve => { gps = resolve; }),
    setTravelOpen: value => { states.open = value; }, setTravelBusy: value => { states.busy = value; },
    setTravelError: value => { states.error = value; }, setTravelOrigin: value => { states.origin = value; },
    setMobilityTarget: value => { states.target = value; }, setMobilityResult: value => { states.result = value; },
    mobilidade: { enabled: true, day_start_location_id: 1 }, proximo: {}, proximoLocal: target,
    targetKey: target.target_key, retornoAtivo: false, usaOrigemSalva: saved,
    routeRequestGeneration: generation, routeResultIdentity: { current: null }, currentRouteContext: routeContext,
    routeIdentity: "context-A", setErroRota: value => { states.error = value; },
    setCarregandoRota: value => { states.busy = value; }, setOrigem: value => { states.origin = value; },
    setDeslocamento: value => { states.result = value; },
    setProximoAlvo: () => assert.fail("A calculation must not replace the canonical target"),
    navigator: { geolocation: { getCurrentPosition(success) { gps = success; } } },
  };
  const context = vm.createContext(globals);
  vm.runInContext(stripTypeScriptTypes(sanitize + (kind === "home" ? closeHomeFunction + homeFunction : assistantFunction)), context);
  const start = () => vm.runInContext(kind === "home" ? "startTravel()" : "atualizarDeslocamento()", context);
  return { context, states, requests, generation, identity, routeContext, start, gps: () => gps({ coords: { latitude: 0, longitude: 0 } }) };
}

for (const kind of ["home", "assistant"]) {
  test(`${kind}: newer calculation wins; late result/error/finally cannot overwrite it`, async () => {
    const env = environment(kind);
    env.start(); env.start();
    env.requests[1].resolve(result());
    await settle();
    const current = env.states.result;
    env.requests[0].reject(new Error("obsolete"));
    await settle();
    assert.equal(env.states.result, current);
    assert.equal(env.states.error, kind === "home" ? null : "");
    assert.equal(env.states.busy, false);
    env.start(); env.start();
    env.requests[2].resolve(result("no_route"));
    await settle();
    assert.equal(env.states.result, current);
    assert.equal(env.states.busy, true, "obsolete finally must not stop newer request");
    env.requests[3].resolve(result());
    await settle();
  });

  test(`${kind}: a changed target or origin/preference identity rejects an in-flight result`, async () => {
    const env = environment(kind);
    env.start();
    env.identity.current = "context-B";
    env.routeContext.current = { identity: "context-B", open: true };
    env.requests[0].resolve(result());
    await settle();
    assert.equal(env.states.result, null);
  });

  test(`${kind}: close/reopen invalidates pending GPS before any route POST`, async () => {
    const env = environment(kind, { saved: false });
    env.start();
    if (kind === "home") vm.runInContext("closeTravel()", env.context);
    else {
      env.context.aberto = false;
      env.context.useEffect = callback => callback();
      vm.runInContext(stripTypeScriptTypes(slice(assistant, "  useEffect(() => {\n    routeRequestGeneration", "\n\n  function atualizarDeslocamento")), env.context);
      env.context.aberto = true;
    }
    const originAfterClose = env.states.origin;
    env.gps();
    await settle();
    assert.equal(env.requests.length, 0);
    assert.equal(env.states.origin, originAfterClose);
  });

  test(`${kind}: destination-null failure preserves the backend explanation`, async () => {
    const env = environment(kind);
    env.start();
    env.requests[0].resolve(result("destination_mismatch", null));
    await settle();
    assert.equal(env.states.result, null);
    assert.match(env.states.error, /não corresponde mais à Agenda/);
  });
}

test("Home: each automatic effect exposes destination-null statuses and opening does not cancel it", async () => {
  for (const [start, end, status, message] of [
    ["  useEffect(() => {\n    if (!usesSavedOrigin", "\n\n  useEffect", "destination_mismatch", /destino selecionado não corresponde/],
    ["  useEffect(() => {\n    if (!returnHomeActive", "\n\n  const chooseMode", "origin_mismatch", /compromisso de partida não corresponde/],
    ["  useEffect(() => {\n    if (!returnHomeActive", "\n\n  const chooseMode", "origin_without_location", /partida ainda não possui/],
  ]) {
    const env = environment("home");
    Object.assign(env.context, {
      useEffect: callback => callback(), resultMatchesTarget: false, returnHomeActive: true,
      mobilityDayContext: { last_target: { target_key: "appointment:demo-origin" } },
      mobilityPreference: { enabled: true, day_start_location_id: 1, day_end_destination_location_id: 2 },
    });
    vm.runInContext(stripTypeScriptTypes(slice(home, start, end)), env.context);
    env.context.setTravelOpen(true);
    env.requests[0].resolve(result(status, null));
    await settle();
    assert.match(env.states.error, message);
    assert.equal(env.states.result, null);
  }
});

test("completed routes survive lifecycle invalidation for the same context", async () => {
  for (const kind of ["home", "assistant"]) {
    const env = environment(kind);
    env.start();
    env.requests[0].resolve(result());
    await settle();
    const accepted = env.states.result;
    env.context.useEffect = callback => callback();
    if (kind === "home") {
      vm.runInContext("closeTravel()", env.context);
      vm.runInContext(stripTypeScriptTypes(slice(home, "  useEffect(() => {\n    travelRequestGeneration", "\n\n  useEffect")), env.context);
    } else {
      for (const open of [false, true]) {
        env.context.aberto = open;
        vm.runInContext(stripTypeScriptTypes(slice(assistant, "  useEffect(() => {\n    routeRequestGeneration", "\n\n  function atualizarDeslocamento")), env.context);
      }
    }
    assert.equal(env.states.result, accepted);
    assert.equal(env.states.busy, false);
  }
});

test("Home: canonical target prepared in this request is applied with its accepted route", async () => {
  const env = environment("home", { planned: null });
  env.start();
  assert.match(env.requests[0].path, /prepare-next-target/);
  env.requests[0].resolve(target);
  await settle();
  assert.equal(env.states.target, null, "prepare must not invalidate its own calculation mid-flight");
  env.requests[1].resolve(result());
  await settle();
  assert.equal(env.states.target, target);
  assert.equal(env.states.result.destination, target);
});

test("Home: minutes use finite nonnegative ceil, matching the map", () => {
  const expression = slice(home, "  const travelSeconds =", "\n  const travelDestination");
  for (const [seconds, expected] of [[61, 2], [60, 1], [0, 1], [NaN, null], [Infinity, null], [-1, null]]) {
    const value = vm.runInNewContext(stripTypeScriptTypes(expression) + "; travelMinutes", { bestRoute: { duration_seconds: seconds } });
    assert.equal(value, expected);
  }
});

test("Assistant: route, origin, provider and timestamp are gated by current result identity", () => {
  assert.match(assistant, /rotas=\{resultMatchesTarget \? deslocamento\?\.routes \|\| \[\] : \[\]\}/);
  assert.match(assistant, /updatedAt=\{resultMatchesTarget \? deslocamento\?\.updated_at : undefined\}/);
  assert.match(assistant, /const origemMapa = \(resultMatchesTarget \? origem : null\)/);
  assert.match(assistant, /const provedorMapa = \(resultMatchesTarget \? deslocamento\?\.provider : null\)/);
});
