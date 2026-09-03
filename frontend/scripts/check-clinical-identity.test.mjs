import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import ts from "typescript";

const source = readFileSync(new URL("../src/lib/clinicalIdentity.ts", import.meta.url), "utf8");
const javascript = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;
const module = { exports: {} };
new Function("exports", "module", javascript)(module.exports, module);
const { chamamentoComArtigo, nomeComTratamento } = module.exports;

test("treatment, article and first name form the clinical call name", () => {
  assert.equal(chamamentoComArtigo({ full_name: "Ana Souza", professional_title: "Dra." }, { curto: true }), "a Dra. Ana");
  assert.equal(chamamentoComArtigo({ full_name: "Carlos Lima", professional_title: "Prof. Dr." }, { curto: true }), "o Prof. Dr. Carlos");
  assert.equal(chamamentoComArtigo({ full_name: "Dra. Ana Souza", professional_title: "Dra." }, { curto: true }), "a Dra. Ana");
  assert.equal(nomeComTratamento({ full_name: "Dr. Rafael Paes", professional_title: "Dr." }, true), "Dr. Rafael");
});

test("neutral treatment uses an explicit gender marker but never infers from the name", () => {
  assert.equal(chamamentoComArtigo({ full_name: "Ana Souza", professional_title: "Esp.", sex: "F" }, { curto: true }), "a Esp. Ana");
  assert.equal(chamamentoComArtigo({ full_name: "João Lima", professional_title: "Esp.", genero: "masculino" }, { curto: true }), "o Esp. João");
  assert.equal(chamamentoComArtigo({ full_name: "Alex Silva", professional_title: "Esp.", gender: "não binário" }, { curto: true }), "Esp. Alex");
  assert.equal(chamamentoComArtigo({ full_name: "Maria Souza", professional_title: "Esp." }, { curto: true }), "Esp. Maria");
});

test("missing treatment or identity has a grammatical, non-invented fallback", () => {
  assert.equal(chamamentoComArtigo({ full_name: "Alex Silva", professional_title: null }, { curto: true }), "Alex");
  assert.equal(chamamentoComArtigo(null, { curto: true }), "você");
  assert.equal(chamamentoComArtigo(null, { curto: true, inicioDeFrase: true }), "Você");
  assert.equal(chamamentoComArtigo({ full_name: "Ana Souza", professional_title: "Dra." }, { curto: true, inicioDeFrase: true }), "A Dra. Ana");
});
