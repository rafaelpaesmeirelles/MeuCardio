import assert from "node:assert/strict";
import test from "node:test";

import {
  hasReservedSmokeTestMarker,
  isReservedSmokeTestRecord,
  withoutReservedSmokeTestRecord,
  withoutReservedSmokeTestRecords,
} from "../src/lib/reservedSmokeAgenda.ts";

test("reconhece apenas o marcador reservado no início", () => {
  assert.equal(hasReservedSmokeTestMarker("[SMOKE-TEST] Bloco hospitalar"), true);
  assert.equal(hasReservedSmokeTestMarker("   [SMOKE-TEST] Consulta"), true);
  assert.equal(hasReservedSmokeTestMarker("[SMOKE-TEST]"), true);

  assert.equal(hasReservedSmokeTestMarker("Consulta [SMOKE-TEST] do paciente"), false);
  assert.equal(hasReservedSmokeTestMarker("[smoke-test] Consulta"), false);
  assert.equal(hasReservedSmokeTestMarker("[SMOKE] Consulta"), false);
  assert.equal(hasReservedSmokeTestMarker(null), false);
});

test("inspeciona somente campos de identidade do compromisso", () => {
  for (const field of ["title", "patient_name", "label", "service_name", "appointment_type"]) {
    assert.equal(isReservedSmokeTestRecord({ [field]: "[SMOKE-TEST] Item" }), true, field);
  }

  assert.equal(isReservedSmokeTestRecord({
    title: "Consulta legítima",
    notes: "Revisar execução [SMOKE-TEST] anterior",
    location: { name: "[SMOKE-TEST] laboratório" },
  }), false);
  assert.equal(isReservedSmokeTestRecord({ patient_name: "Maria Smoke-Teste" }), false);
  assert.equal(isReservedSmokeTestRecord([]), false);
});

test("remove exclusivamente registros reservados e preserva ordem e identidade", () => {
  const primeiro = { id: 1, title: "Consulta legítima" };
  const reservado = { id: 2, patient_name: "[SMOKE-TEST] Bloco 07:00" };
  const terceiro = { id: 3, title: "Debrief sobre [SMOKE-TEST]" };

  const resultado = withoutReservedSmokeTestRecords([primeiro, reservado, terceiro]);
  assert.deepEqual(resultado, [primeiro, terceiro]);
  assert.equal(resultado[0], primeiro);
  assert.equal(withoutReservedSmokeTestRecord(reservado), null);
  assert.equal(withoutReservedSmokeTestRecord(primeiro), primeiro);
  assert.equal(withoutReservedSmokeTestRecord(undefined), null);
});
