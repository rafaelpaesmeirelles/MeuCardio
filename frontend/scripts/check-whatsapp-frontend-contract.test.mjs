import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync(new URL("../src/pages/WhatsAppAssistant.tsx", import.meta.url), "utf8");
const schema = readFileSync(new URL("../../backend/app/schemas/whatsapp.py", import.meta.url), "utf8");
const api = readFileSync(new URL("../../backend/app/api/whatsapp.py", import.meta.url), "utf8");

test("WhatsApp exposes only the eight canonical permissions", () => {
  const keys = ["read_agenda", "read_tasks", "search_science", "create_reminder", "create_appointment", "create_draft", "external_communication", "heart_team_draft"];
  for (const key of keys) {
    assert.match(page, new RegExp(`key: "${key}"`));
    assert.match(schema, new RegExp(key));
  }
  assert.match(schema, /PERMISSION_KEYS = frozenset/);
});

test("pairing, review, confirmation, undo and destructive controls match backend routes", () => {
  for (const path of ["/pairings", "/pairings/complete", "/commands", "/history", "/messages/pending", "/metrics", "/data"]) assert.match(page, new RegExp(path.replaceAll("/", "\\/")));
  for (const action of ["transcript", "pii-review", "media-review", "confirm", "undo"]) assert.match(page, new RegExp(action));
  assert.match(api, /@router\.post\("\/messages\/\{mid\}\/media-review"\)/);
  assert.match(page, /contains_no_identifiers/);
  assert.match(page, /requires_in_app/);
  assert.match(page, /Confirmar desconexão/);
  assert.match(page, /Confirmar exclusão/);
});

test("review feedback reflects the nested command and its authorization state", () => {
  assert.match(page, /result\.command/);
  assert.match(page, /reviewOutcome/);
  assert.match(page, /Ação reversível concluída e registrada/);
  assert.match(page, /aguardando sua confirmação explícita/);
  assert.doesNotMatch(page, /processamento solicitado ainda não foi executado automaticamente/);
});

test("pending review renders the canonical authenticated review payload", () => {
  for (const field of ["review_text", "mime_type", "filename"]) {
    assert.match(api, new RegExp(field));
    assert.match(page, new RegExp(field));
  }
  assert.match(page, /Conteúdo sensível visível apenas nesta área autenticada/);
  assert.doesNotMatch(page, /item\.transcript|item\.redacted_preview/);
});

test("N3 confirmation tokens are obtained only inside the authenticated CorVIA UI", () => {
  assert.match(api, /@router\.post\("\/commands\/\{cid\}\/confirmation-token"/);
  assert.match(page, /\/confirmation-token/);
  assert.match(page, /can_confirm/);
  assert.match(page, /Liberar confirmação/);
  assert.match(page, /needs_clarification/);
});
