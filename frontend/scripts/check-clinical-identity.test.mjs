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

test("registered sex chooses exactly one article and has priority over the title", () => {
  assert.equal(chamamentoComArtigo({ full_name: "Rafael Paes", professional_title: "Dr.", sex: "M" }, { curto: true }), "o Dr. Rafael");
  assert.equal(chamamentoComArtigo({ full_name: "Ana Souza", professional_title: "Dra.", sex: "F" }, { curto: true }), "a Dra. Ana");
  // Mesmo que o título escolhido seja flexionado de outro modo, o artigo
  // vem do sexo cadastrado — nunca mostramos "o/a" nem inferimos pelo nome.
  assert.equal(chamamentoComArtigo({ full_name: "Maria Souza", professional_title: "Dr.", sex: "F" }, { curto: true }), "a Dr. Maria");
  assert.equal(chamamentoComArtigo({ full_name: "João Lima", professional_title: "Dra.", sex: "M" }, { curto: true }), "o Dra. João");
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
