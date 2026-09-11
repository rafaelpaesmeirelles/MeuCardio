import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { stripTypeScriptTypes } from "node:module";
import test from "node:test";

const source = readFileSync(new URL("../src/lib/mobilityGeometry.ts", import.meta.url), "utf8");
const stripped = stripTypeScriptTypes(source, { mode: "strip" });
const { coordinateValid, decodeRoutePolyline, geometryAvailable, mobilityResultError } = await import(
  `data:text/javascript;base64,${Buffer.from(stripped).toString("base64")}`
);

// Synthetic geometry round-trip fixtures only; this encoder is never shipped.
function encode(points, precision = 5) {
  const factor = 10 ** precision;
  let previous = [0, 0];
  let output = "";
  for (const point of points) {
    const current = point.map(value => Math.round(value * factor));
    for (let dimension = 0; dimension < 2; dimension += 1) {
      const delta = current[dimension] - previous[dimension];
      let value = delta < 0 ? -2 * delta - 1 : 2 * delta;
      while (value >= 32) {
        output += String.fromCharCode((value % 32) + 32 + 63);
        value = Math.floor(value / 32);
      }
      output += String.fromCharCode(value + 63);
    }
    previous = current;
  }
  return output;
}

function route(points = [[1, 2], [1.001, 2.002]], precision = 5) {
  return { geometry: { format: "encoded_polyline", value: encode(points, precision), precision } };
}

test("decode preserves canonical polyline coordinates and order at precision 5", () => {
  assert.deepEqual(decodeRoutePolyline("_p~iF~ps|U_ulLnnqC_mqNvxq`@"), [[38.5, -120.2], [40.7, -120.95], [43.252, -126.453]]);
});

for (const precision of [5, 6]) {
  test(`precision ${precision}: negative deltas, geographical boundaries and antimeridian remain exact`, () => {
    const points = [[-90, -180], [90, 180], [0, -179.999], [-0.001, 179.999], [0, 0]];
    assert.deepEqual(decodeRoutePolyline(encode(points, precision), precision), points);
  });
}

test("coordinates require actual finite numbers in geographical bounds", () => {
  for (const point of [[0, 0], [-90, -180], [90, 180]]) assert.equal(coordinateValid(...point), true);
  for (const point of [[91, 0], [0, 181], [-91, 0], [0, -181], [NaN, 0], [0, Infinity], [null, 0], ["1", 2], [true, 2], [undefined, 0]]) {
    assert.equal(coordinateValid(...point), false);
  }
});

test("invalid types, characters, precision and truncated pairs are rejected completely", () => {
  for (const value of [null, undefined, 17, {}, [], "", "?", "??A", "??_", "??\u0000?", "??\u0080?", "??\n", "??!", "~~~~~~~", "_p~iF~ps|U_ulLnnq"]) {
    assert.doesNotThrow(() => decodeRoutePolyline(value));
    assert.deepEqual(decodeRoutePolyline(value), [], String(value));
  }
  for (const precision of [0, 4, 7, 5.5, NaN, Infinity, null, "5"]) assert.deepEqual(decodeRoutePolyline("??AA", precision), []);
});

test("a malformed suffix invalidates the whole geometry instead of drawing its valid prefix", () => {
  const valid = encode([[1, 2], [1.1, 2.2]]);
  assert.deepEqual(decodeRoutePolyline(valid + "_"), []);
  assert.deepEqual(decodeRoutePolyline(valid + "?"), []);
  assert.deepEqual(decodeRoutePolyline(encode([[1, 2], [91, 3]])), []);
  assert.deepEqual(decodeRoutePolyline(encode([[1, 2], [3, 181]])), []);
});

test("oversized encoded input and excessive point counts are rejected without truncation", () => {
  assert.deepEqual(decodeRoutePolyline("?".repeat(200_001)), []);
  assert.deepEqual(decodeRoutePolyline("??".repeat(50_001)), []);
});

test("drawable geometry requires two distinct points and honors the backend rejection flag", () => {
  assert.equal(geometryAvailable(route()), true);
  assert.equal(geometryAvailable(route([[0, 0], [0.000001, 0]], 6)), true);
  for (const candidate of [null, {}, { geometry: null }, route([[1, 2]]), route([[1, 2], [1, 2]]),
    { ...route(), geometry_available: false }, { geometry_available: true },
    { geometry: { ...route().geometry, value: "abc123" } },
    { geometry: { ...route().geometry, format: "geojson" } }]) {
    assert.equal(geometryAvailable(candidate), false);
  }
  const legacy = route(); delete legacy.geometry.precision;
  assert.equal(geometryAvailable(legacy), true);
});

test("results distinguish no route, unavailable geometry and a drawable alternative", () => {
  assert.match(mobilityResultError({ status: "no_route", routes: [] }), /não encontrou uma rota/);
  assert.match(mobilityResultError({ status: "geometry_unavailable", routes: [{ duration_seconds: 900, distance_meters: 5000 }] }), /tempo e distância/);
  assert.match(mobilityResultError({ status: "live", routes: [{}] }), /geometria utilizável/);
  assert.match(mobilityResultError({ status: "live", routes: [] }), /não retornou uma rota utilizável/);
  assert.equal(mobilityResultError({ status: "live", routes: [{ geometry_available: false }, route()] }), null);
  assert.equal(mobilityResultError({ status: "ok", routes: [route()] }), null);
});

test("explicit failures cannot be hidden by a stale drawable route", () => {
  for (const status of ["not_configured", "origin_not_geocoded", "destination_not_geocoded", "destination_without_location", "origin_without_location", "destination_mismatch", "origin_mismatch", "no_upcoming_location", "no_route", "geometry_unavailable"]) {
    assert.equal(typeof mobilityResultError({ status, routes: [route()] }), "string", status);
  }
  assert.equal(mobilityResultError({ status: "not_configured" }), "O destino está pronto, mas o provedor de trânsito ainda não está configurado.");
});

test("controlled provider failures never echo arbitrary upstream detail", () => {
  for (const code of ["traffic_provider_unavailable", "traffic_invalid_response", "traffic_provider_error", "unsupported_traffic_provider"]) {
    const result = mobilityResultError({ detail: { code, message: "fixture-private-address-and-key" } });
    assert.equal(typeof result, "string");
    assert.ok(!result.includes("fixture-private"));
  }
  for (const result of [null, undefined, [], "error", { status: "unknown", routes: [route()] }]) {
    assert.equal(typeof mobilityResultError(result), "string");
  }
});

test("helpers do not mutate route objects or result metrics", () => {
  const item = route();
  const result = { status: "live", routes: [{ ...item, duration_seconds: 900, distance_meters: 5000 }] };
  const before = structuredClone(result);
  geometryAvailable(result.routes[0]); mobilityResultError(result); decodeRoutePolyline(item.geometry.value);
  assert.deepEqual(result, before);
});
