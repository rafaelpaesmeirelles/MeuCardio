import assert from "node:assert/strict";
import test from "node:test";

import { validateLoginInputContrast } from "./check-login-input-contrast.mjs";

const TOKENS_CSS = `:root { --navy-900: #082637; --teal-600: #167d92; --white: #ffffff; }`;

const CSS_BOA = `
.login .login-formulario input {
  color: var(--navy-900);
  -webkit-text-fill-color: var(--navy-900);
  caret-color: var(--teal-600);
  background: var(--white);
}
.login .login-formulario input::placeholder {
  color: #6f858e;
  -webkit-text-fill-color: #6f858e;
  opacity: 1;
}
.login .login-formulario input:-webkit-autofill,
.login .login-formulario input:-webkit-autofill:hover,
.login .login-formulario input:-webkit-autofill:focus {
  -webkit-text-fill-color: var(--navy-900);
  caret-color: var(--teal-600);
  -webkit-box-shadow: 0 0 0 1000px var(--white) inset;
}
`;

test("CSS que segue o contrato não falha em nenhuma regra", () => {
  assert.deepEqual(validateLoginInputContrast(CSS_BOA, TOKENS_CSS), []);
});

test("falha se o texto voltar a ficar quase branco sobre fundo quase branco (o bug real)", () => {
  const comBug = CSS_BOA.replace("background: var(--white);", "background: #f5f7f8;").replace(
    "color: var(--navy-900);\n  -webkit-text-fill-color: var(--navy-900);",
    "color: #f1fbfc;\n  -webkit-text-fill-color: #f1fbfc;",
  );
  const falhas = validateLoginInputContrast(comBug, TOKENS_CSS);
  assert.match(falhas.join("\n"), /abaixo do mínimo WCAG AA de 4\.5:1/);
});

test("falha se a regra corrigida (.login .login-formulario input) deixar de existir", () => {
  const semRegraEspecifica = CSS_BOA.replace(/\.login \.login-formulario input \{[\s\S]*?\}\n/, "");
  const falhas = validateLoginInputContrast(semRegraEspecifica, TOKENS_CSS);
  assert.match(falhas.join("\n"), /não encontrei a regra/);
});

test("pega a ÚLTIMA declaração do seletor, não a primeira — o CSS real tem a versão escura antiga acima da correção", () => {
  const comVersaoAntigaAcima = `
.login .login-formulario input { color: #f1fbfc; background: rgba(2,14,21,.58); }
${CSS_BOA}`;
  assert.deepEqual(validateLoginInputContrast(comVersaoAntigaAcima, TOKENS_CSS), []);
});

test("falha se faltar -webkit-text-fill-color na regra base", () => {
  const semFillColor = CSS_BOA.replace("  -webkit-text-fill-color: var(--navy-900);\n", "");
  const falhas = validateLoginInputContrast(semFillColor, TOKENS_CSS);
  assert.match(falhas.join("\n"), /falta -webkit-text-fill-color na regra base/);
});

test("falha se faltar o tratamento de :-webkit-autofill", () => {
  const semAutofill = CSS_BOA.replace(
    /\.login \.login-formulario input:-webkit-autofill,[\s\S]*?\}\n/,
    "",
  );
  const falhas = validateLoginInputContrast(semAutofill, TOKENS_CSS);
  assert.match(falhas.join("\n"), /falta tratamento de :-webkit-autofill/);
});

test("falha se o -webkit-box-shadow do autofill perder o inset", () => {
  const semInset = CSS_BOA.replace("-webkit-box-shadow: 0 0 0 1000px var(--white) inset;", "-webkit-box-shadow: none;");
  const falhas = validateLoginInputContrast(semInset, TOKENS_CSS);
  assert.match(falhas.join("\n"), /precisa de -webkit-box-shadow \.\.\. inset/);
});

test("falha se faltar a regra de ::placeholder", () => {
  const semPlaceholder = CSS_BOA.replace(/\.login \.login-formulario input::placeholder \{[\s\S]*?\}\n/, "");
  const falhas = validateLoginInputContrast(semPlaceholder, TOKENS_CSS);
  assert.match(falhas.join("\n"), /falta a regra ::placeholder/);
});
