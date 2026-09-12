// Local function checks; no browser, API, database or external messages.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

const path = new URL('../src/pages/WhatsAppAssistant.tsx', import.meta.url);
const text = fs.readFileSync(path, 'utf8');
const source = ts.createSourceFile(path.pathname, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const snippets = [];
function collect(node) {
  if (ts.isFunctionDeclaration(node) && ['act', 'commandStatus', 'commandGuidance'].includes(node.name?.text)) snippets.push(node.getText(source));
  ts.forEachChild(node, collect);
}
collect(source);
assert.equal(snippets.length, 3);
const js = ts.transpileModule(snippets.join('\n'), { compilerOptions: { jsx: ts.JsxEmit.React, target: ts.ScriptTarget.ES2022 } }).outputText;
const state = {};
let response;
let fail;
const env = {
  Error, React: { createElement: (_, props) => props }, ClinicalAIStatusBadge: {},
  api: { post: async () => { if (fail) throw fail; return response; } },
  setWorking: value => state.working = value,
  setError: value => state.error = value,
  setMessage: value => state.message = value,
  setConfirmPin: value => state.pin = value,
  confirmPin: 'local-fake-pin',
  load: async () => { state.loads = (state.loads ?? 0) + 1; state.error = ''; },
};
vm.createContext(env); vm.runInContext(js, env);
for (const status of ['executing', 'execution_uncertain', 'undoing', 'undo_uncertain', 'undo_conflict']) {
  assert.ok(env.commandGuidance({ status }));
  assert.notEqual(env.commandStatus({ status }).label, 'Em processamento');
}
console.log('PASS: all claimed/uncertain/conflict states have explicit labels and guidance');

for (const status of ['completed', 'execution_uncertain', 'failed', 'undo_conflict']) {
  response = { status };
  await env.act({ id: 7, confirmation_token: 'fake' }, 'confirm');
  assert.equal(state.working, '');
  assert.equal(Boolean(state.message), status === 'completed');
  assert.equal(Boolean(state.error), status !== 'completed');
}
console.log('PASS: HTTP success with uncertain/failed result never displays execution success');

response = { status: 'undone' };
await env.act({ id: 7, undo_token: 'fake' }, 'undo');
assert.equal(state.message, 'Ação desfeita e registrada.');
fail = new Error('A ação foi alterada depois do comando.');
const previousLoads = state.loads;
await env.act({ id: 7, undo_token: 'fake' }, 'undo');
assert.equal(state.loads, previousLoads + 1);
assert.equal(state.message, '');
assert.match(state.error, /Confira o histórico/);
console.log('PASS: compensation conflict refreshes history and preserves actionable error guidance');
