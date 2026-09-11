import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import ts from "typescript";

const source = readFileSync(new URL("../src/lib/atelierShelfPreferences.ts", import.meta.url), "utf8");
const home = readFileSync(new URL("../src/pages/CardiologySpacesHome.tsx", import.meta.url), "utf8");
const loaded = { exports: {} };
const { outputText, diagnostics } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 }, reportDiagnostics: true });
assert.deepEqual(diagnostics, []);
new Function("exports", "module", outputText)(loaded.exports, loaded);
const { emptyShelfPreferences, parseShelfPreferences, migrateShelfPreferences, previewShelfImport, saveShelfProfile, shelfReserveFor, shelfProfileItems, shelfOrganizationLabel, createShelfPreferenceStore, shelfHistoryKey, SHELF_PREFERENCES_PREFIX } = loaded.exports;
const ids = Array.from({ length: 14 }, (_, index) => `action-${index}`);
const allowed = new Set(ids);
const twoShelves = [{ id: "now", capacity: 4 }, { id: "references", capacity: 4 }];
const key = "scientific:pesquisa";
const storedKey = (userId) => `${SHELF_PREFERENCES_PREFIX}:${userId}`;
const base = (profiles = {}) => ({ ...emptyShelfPreferences(), updatedAt: "2026-09-01T12:00:00.000Z", profiles });
function storageFixture(initial = []) {
  const values = new Map(initial);
  const writes = [];
  return { values, writes, getItem: (key) => values.get(key) ?? null, setItem: (key, value) => { writes.push(key); values.set(key, value); } };
}

test("v1 roundtrip keeps full arrays, empty shelves and all five original science scopes", () => {
  const scopes = ["descobrir", "evidencias", "aprender", "ensinar", "produzir"];
  const original = base(Object.fromEntries(scopes.map((scope) => [`scientific:${scope}`, { now: ids.slice(0, 6), references: [] }])));
  original.profiles["essential:consultorio"] = { essential: ids.slice(0, 6) };
  const parsed = parseShelfPreferences(JSON.stringify(original));
  assert.deepEqual(parsed, original);
  const migrated = migrateShelfPreferences(parsed, {}, (path) => path);
  assert.deepEqual(migrated.profiles, original.profiles);
  for (const scope of scopes) assert.ok(migrated.archives.some((item) => item.profileKey === `scientific:${scope}` && item.profile.now.length === 6));
  assert.equal(migrated.profiles[key], undefined, "no arbitrary assignment to a new architectural space");
  assert.deepEqual(parseShelfPreferences(JSON.stringify(migrated)), migrated);
});

test("legacy essentials migrate without truncation or overriding an explicit empty choice", () => {
  const original = base({ "essential:hospital": { essential: [] } });
  const before = JSON.stringify(original);
  const migrated = migrateShelfPreferences(original, { consultorio: ids.slice(0, 6), hospital: ids.slice(0, 5) }, (path) => `mapped:${path}`);
  assert.equal(JSON.stringify(original), before);
  assert.equal(migrated.profiles["essential:consultorio"].essential.length, 6);
  assert.deepEqual(migrated.profiles["essential:hospital"].essential, []);
  assert.ok(migrated.archives.some((entry) => entry.profileKey === "essential:hospital" && entry.profile.essential.length === 5));
  assert.deepEqual(migrateShelfPreferences(migrated, { consultorio: ids.slice(0, 6), hospital: ids.slice(0, 5) }, (path) => `mapped:${path}`), migrated, "migration is idempotent");
});

test("history is user-scoped and written before primary; all legacy source keys stay intact", () => {
  const legacyKey = "corvia:cardiology-spaces:essentials:7:consultorio";
  const original = base({ [key]: { now: ids.slice(0, 6), references: ids.slice(6, 12) } });
  const storage = storageFixture([[storedKey(7), JSON.stringify(original)], [legacyKey, JSON.stringify(ids)]]);
  const store = createShelfPreferenceStore(() => storage);
  const saved = saveShelfProfile(store.read(7), key, { now: [ids[1]], references: [] }, twoShelves, allowed, []);
  assert.equal(store.write(7, saved), true);
  assert.deepEqual(storage.writes, [shelfHistoryKey(7), storedKey(7)]);
  assert.equal(storage.values.get(legacyKey), JSON.stringify(ids));
  const durableHistory = parseShelfPreferences(storage.values.get(shelfHistoryKey(7)));
  assert.deepEqual(durableHistory.archives[0].profile, original.profiles[key]);
  assert.deepEqual(store.read(8), emptyShelfPreferences());
  assert.deepEqual(store.read(7).reserves[key], [ids[0], ...ids.slice(2, 12)]);
});

test("a denied backup never overwrites the last durable profile, while session changes survive remount", () => {
  const original = base({ [key]: { now: ids.slice(0, 6) } });
  const storage = storageFixture([[storedKey(7), JSON.stringify(original)]]);
  const store = createShelfPreferenceStore(() => ({ ...storage, setItem: () => { throw new Error("QuotaExceededError"); } }));
  const saved = saveShelfProfile(store.read(7), key, { now: [], references: [ids[7]] }, twoShelves, allowed, []);
  assert.equal(store.write(7, saved), false);
  assert.equal(storage.values.get(storedKey(7)), JSON.stringify(original));
  assert.deepEqual(store.read(7), saved);
  const changedCopy = store.read(7);
  changedCopy.profiles[key].now.push("must-not-leak");
  assert.deepEqual(store.read(7).profiles[key].now, []);
  assert.deepEqual(store.read(8), emptyShelfPreferences());
});

test("a primary quota failure leaves a recoverable full durable history and old primary", () => {
  const original = base({ [key]: { now: ids.slice(0, 6) } });
  const storage = storageFixture([[storedKey(7), JSON.stringify(original)]]);
  const store = createShelfPreferenceStore(() => ({ ...storage, setItem: (key, value) => { if (key === storedKey(7)) throw new Error("QuotaExceededError"); storage.setItem(key, value); } }));
  const saved = saveShelfProfile(store.read(7), key, { now: [], references: [ids[8]] }, twoShelves, allowed, []);
  assert.equal(store.write(7, saved), false);
  assert.equal(storage.values.get(storedKey(7)), JSON.stringify(original));
  assert.deepEqual(createShelfPreferenceStore(() => storage).read(7).archives[0].profile, original.profiles[key]);
  assert.deepEqual(store.read(7).profiles[key], saved.profiles[key]);
});

test("unavailable browser storage keeps saved and restored choices in user-isolated session memory", () => {
  const store = createShelfPreferenceStore(() => { throw new Error("SecurityError"); });
  const initial = saveShelfProfile(store.read(7), key, { now: [ids[9]], references: [] }, twoShelves, allowed, []);
  assert.equal(store.write(7, initial), false);
  const restoredDraft = { now: ids.slice(0, 4), references: [] };
  const restored = saveShelfProfile(store.read(7), key, restoredDraft, twoShelves, allowed, [ids[9]]);
  assert.equal(store.write(7, restored), false);
  assert.deepEqual(store.read(7).profiles[key], restoredDraft);
  assert.ok(store.read(7).reserves[key].includes(ids[9]));
  assert.ok(store.read(7).archives.some((archive) => archive.profile.now.includes(ids[9])));
  assert.deepEqual(store.read(8), emptyShelfPreferences());
});

test("import is a pure preview: eight visible items, excess and unavailable IDs recoverable, source unchanged", () => {
  const source = { now: ids.slice(0, 6), references: [...ids.slice(6, 12), "admin-only"] };
  const oldDraft = { now: [ids[13]], references: [] };
  const sourceBefore = JSON.stringify(source);
  const draftBefore = JSON.stringify(oldDraft);
  const preview = previewShelfImport(source, twoShelves, allowed, oldDraft, [ids[12]]);
  assert.deepEqual(preview.profile, { now: ids.slice(0, 4), references: ids.slice(4, 8) });
  assert.deepEqual(preview.reserve, [...ids.slice(8, 12), "admin-only", ids[12], ids[13]]);
  assert.equal(JSON.stringify(source), sourceBefore);
  assert.equal(JSON.stringify(oldDraft), draftBefore);
  assert.ok(!shelfProfileItems(preview.profile).includes("admin-only"));
});

test("saving an import retains origin and reserve; re-adding is explicit and never refills an empty shelf", () => {
  const original = migrateShelfPreferences(base({ "scientific:ensinar": { now: ids.slice(0, 6), references: ids.slice(6, 12) } }), {}, (path) => path);
  const preview = previewShelfImport(original.profiles["scientific:ensinar"], twoShelves, allowed);
  const saved = saveShelfProfile(original, key, preview.profile, twoShelves, allowed, preview.reserve);
  assert.deepEqual(saved.profiles["scientific:ensinar"], original.profiles["scientific:ensinar"]);
  assert.deepEqual(saved.reserves[key], ids.slice(8, 12));
  const swapped = saveShelfProfile(saved, key, { now: [ids[8]], references: [] }, twoShelves, allowed, saved.reserves[key]);
  assert.deepEqual(swapped.profiles[key], { now: [ids[8]], references: [] });
  assert.ok(!swapped.reserves[key].includes(ids[8]));
  assert.ok(swapped.reserves[key].includes(ids[0]));
  assert.deepEqual(parseShelfPreferences(JSON.stringify(swapped)).profiles[key].references, []);
});

test("opening an over-capacity current profile exposes excess in reserve without modifying persisted choices", () => {
  const original = base({ [key]: { now: ids.slice(0, 6), references: ["admin-only"] } });
  const before = JSON.stringify(original);
  assert.deepEqual(shelfReserveFor(original, key, { now: ids.slice(0, 4), references: [] }), [ids[4], ids[5], "admin-only"]);
  assert.equal(JSON.stringify(original), before);
});

test("route remount reads a newer durable organization written by another tab", () => {
  const old = base({ [key]: { now: [ids[0]] } });
  const newer = base({ [key]: { now: [ids[1]] } });
  const storage = storageFixture([[storedKey(7), JSON.stringify(old)]]);
  const store = createShelfPreferenceStore(() => storage);
  store.read(7);
  storage.values.set(storedKey(7), JSON.stringify(newer));
  const remounted = store.read(7);
  assert.deepEqual(remounted.profiles[key], newer.profiles[key]);
  assert.ok(remounted.archives.some((archive) => archive.profile.now.includes(ids[0])));
});

test("storage events preserve a previous snapshot and cannot erase unsaved memory fallback", () => {
  const storage = storageFixture();
  const store = createShelfPreferenceStore(() => storage);
  const first = base({ [key]: { now: [ids[0]] } });
  const second = base({ [key]: { now: [ids[1]] } });
  store.write(7, first);
  assert.ok(store.sync(7, JSON.stringify(second)).archives.some((archive) => archive.profile.now.includes(ids[0])));
  const denied = createShelfPreferenceStore(() => null);
  denied.write(7, first);
  const synchronized = denied.sync(7, JSON.stringify(second));
  assert.deepEqual(synchronized.profiles[key], first.profiles[key]);
  assert.ok(synchronized.archives.some((archive) => archive.profile.now.includes(ids[1])));
});

test("previous labels distinguish all five scientific sources and invalid payloads fail closed", () => {
  for (const [scope, label] of Object.entries({ descobrir: "Descobrir", evidencias: "Evidências", aprender: "Aprender", ensinar: "Ensinar", produzir: "Produzir" })) assert.equal(shelfOrganizationLabel(`scientific:${scope}`), `Ciência & Ensino · ${label}`);
  for (const raw of [null, "broken", "[]", '{"schemaVersion":2,"profiles":{}}']) assert.deepEqual(parseShelfPreferences(raw), emptyShelfPreferences());
});

test("Home Cancelar and Restaurar are draft-only, while Salvar alone commits the edited profile", () => {
  const cancel = home.slice(home.indexOf("function cancelShelfPersonalizer"), home.indexOf("function toggleShelfAction"));
  const restore = home.slice(home.indexOf("function restoreShelfDefaults"), home.indexOf("function importPreviousOrganization"));
  const preview = home.slice(home.indexOf("function importPreviousOrganization"), home.indexOf("function saveShelfPreferences"));
  const save = home.slice(home.indexOf("function saveShelfPreferences"), home.indexOf("async function startTravel"));
  for (const draftOnly of [cancel, restore, preview]) assert.doesNotMatch(draftOnly, /shelfPreferenceStore\.write|setShelfPreferences|localStorage\.setItem/);
  assert.match(cancel, /setShelfDraft\(\{\}\)/);
  assert.match(restore, /setShelfReserve/);
  assert.match(restore, /shelfDraft\[definition\.id\]/);
  assert.match(save, /saveShelfProfile/);
  assert.match(save, /shelfPreferenceStore\.write/);
  assert.match(home, /<details className="atelier-previous-organizations"/);
  assert.doesNotMatch(home, /<details className="atelier-previous-organizations"[^>]*\sopen[\s=>]/);
  assert.match(home, /disabled=\{!allowed \|\| activeDraftIds\.length >= activePersonalizerDefinition\.capacity\}/);
});
