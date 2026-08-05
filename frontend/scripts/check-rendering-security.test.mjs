import assert from "node:assert/strict";
import test from "node:test";

import { validateRenderingSource } from "./check-rendering-security.mjs";

const approvedPath = "pages/CaixaDeEmail.tsx";
const protectedRenderer = `
  const parser = new DOMParser();
  const document = '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'">';
  export const view = <iframe sandbox="allow-popups" srcDoc={document} />;
`;

test("aceita somente o renderer de e-mail com sandbox e CSP restritivos", () => {
  assert.deepEqual(validateRenderingSource(protectedRenderer, approvedPath), []);
});

test("falha se o sandbox do renderer aprovado for removido", () => {
  const unsafe = protectedRenderer.replace(' sandbox="allow-popups"', "");
  assert.match(validateRenderingSource(unsafe, approvedPath).join("\n"), /sandbox explícito/);
});

test("falha se allow-scripts for adicionado ao sandbox", () => {
  const unsafe = protectedRenderer.replace("allow-popups", "allow-popups allow-scripts");
  assert.match(validateRenderingSource(unsafe, approvedPath).join("\n"), /allow-scripts é proibido/);
});

test("falha se a CSP restritiva for removida", () => {
  const unsafe = protectedRenderer.replace("default-src 'none'", "img-src https:");
  assert.match(validateRenderingSource(unsafe, approvedPath).join("\n"), /CSP com default-src 'none'/);
});

test("DOMParser e srcDoc continuam proibidos fora do arquivo aprovado", () => {
  const failures = validateRenderingSource(protectedRenderer, "pages/OutroComponente.tsx");
  assert.equal(failures.length, 2);
  assert.match(failures.join("\n"), /parsing manual de HTML/);
  assert.match(failures.join("\n"), /iframe srcDoc/);
});
