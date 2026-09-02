import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync(new URL("../src/pages/HeartTeamVirtual.tsx", import.meta.url), "utf8");
const schema = readFileSync(new URL("../../backend/app/schemas/heart_team.py", import.meta.url), "utf8");
const compose = readFileSync(new URL("../../docker-compose.prod.yml", import.meta.url), "utf8");
const registry = readFileSync(new URL("../src/lib/clinicalRouteRegistry.ts", import.meta.url), "utf8");

test("Heart Team uses the registered agent and case contract", () => {
  for (const key of ["coordinator", "heart_failure", "electrophysiology", "imaging", "critical_care", "pharmacology", "evidence", "red_team"]) {
    assert.match(page, new RegExp(`key: "${key}"`));
  }
  for (const field of ["case_text", "laboratory_tests", "source_patient_id", "source_patient_authorized", "selected_agents"]) {
    assert.match(page, new RegExp(`${field}:`));
    assert.match(schema, new RegExp(`${field}:`));
  }
  assert.match(page, /confirm_deidentified: confirmDeidentified/);
  assert.match(page, /confirm_medical_review: confirmMedicalReview/);
});

test("suggestions and final medical review cannot bypass human confirmation", () => {
  assert.match(page, /decision, final_text:/);
  assert.match(page, /medical_responsibility_confirmed: responsibility/);
  assert.match(page, /human_decisions_confirmed: sourcesReviewed/);
  assert.match(page, /filter\(\(suggestion\) => !suggestion\.review\)/);
  assert.match(page, /\["unusable", "failed"\]/);
  assert.match(schema, /decision: Literal\["accepted", "rejected"\]/);
});

test("durable queue is polled safely and never exposes partial results", () => {
  assert.match(page, /ACTIVE_ANALYSIS_STATES = new Set\(\["queued", "analyzing"\]\)/);
  assert.match(page, /attempts >= 120/);
  assert.match(page, /consecutiveFailures >= 5/);
  assert.match(page, /window\.setTimeout/);
  assert.match(page, /window\.clearTimeout/);
  assert.match(page, /cancelled = true/);
  assert.match(page, /Conteúdo parcial não é apresentado como parecer clínico/);
  assert.match(page, /Atualizar agora/);
});

test("Tudo com Tudo related content is rendered as validated links", () => {
  for (const field of ["href", "title", "type"]) assert.match(page, new RegExp(`item\\.${field}`));
  assert.match(page, /item\.href\.startsWith\("https:\/\/"\)/);
  assert.match(page, /<RelatedContent value=\{consensus\.related_content\}/);
});

test("verified sources use internal routes and never render empty anchors", () => {
  assert.match(page, /source\.route \|\| source\.url/);
  assert.match(page, /if \(!href\) return <article className="cai-source"/);
  assert.match(page, /href=\{href\}/);
  assert.doesNotMatch(page, /href=\{source\.url \|\|/);
});

test("Heart Team is enabled end to end in the production release", () => {
  assert.match(compose, /backend:[\s\S]*HEART_TEAM_ENABLED: "true"/);
  assert.match(compose, /whatsapp-heart-team-worker:[\s\S]*HEART_TEAM_ENABLED: "true"/);
  assert.match(compose, /frontend-build:[\s\S]*VITE_HEART_TEAM_ENABLED: "true"/);
  assert.match(registry, /path: "\/heart-team"[\s\S]*intelligence: true[\s\S]*gate: "heart-team"/);
});
