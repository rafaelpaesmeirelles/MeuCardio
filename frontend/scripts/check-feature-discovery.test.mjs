import assert from "node:assert/strict";
import { readFile, mkdtemp, writeFile, symlink, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";
import vm from "node:vm";
import test, { after } from "node:test";
import ts from "typescript";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";

const root = fileURLToPath(new URL("../", import.meta.url));
const read = name => readFile(path.join(root, "src", name), "utf8");
const transpile = source => ts.transpileModule(source, { compilerOptions: {
  target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022, jsx: ts.JsxEmit.ReactJSX,
} }).outputText;
function constant(source, name, next) {
  const block = source.slice(source.indexOf(`const ${name}`), source.indexOf(next, source.indexOf(`const ${name}`)));
  return vm.runInNewContext(`${transpile(block)}; JSON.stringify(${name})`, {
    heartTeamEnabled: () => false, whatsappAssistantEnabled: () => false,
  });
}
const home = await read("pages/CardiologySpacesHome.tsx");
const catalog = JSON.parse(constant(home, "CATALOG", "const ESSENTIAL_DEFAULTS"));
const panel = JSON.parse(constant(await read('pages/PainelClinicalOS.tsx'), 'MODULOS', 'const CONTEXTOS_INICIAIS'));

test('legacy panel retains one presentation and one telediagnosis access', () => {
  const items = panel.flatMap(group => group.items);
  for (const destination of ['/apresentacao', '/telediagnostico']) {
    assert.equal(items.filter(item => item.to === destination).length, 1, destination);
  }
});

test("requested functions stay discoverable in their categories when installation flags are off", () => {
  for (const [title, destination] of [["Clínica & Decisão", "/heart-team"], ["Assistência", "/whatsapp-assistant"], ["Ciência & Ensino", "/intelligence"]]) {
    const section = catalog.find(item => item.title === title);
    assert.ok(section, title);
    const action = section.actions.find(item => item.to === destination);
    assert.ok(action, destination);
    assert.equal(action.featured, true);
    assert.equal(section.actions[0].to, destination);
    assert.equal(catalog.flatMap(item => item.actions).filter(item => item.to === destination).length, 1);
    assert.notEqual(action.adminOnly, true);
  }
});

test("both navigation menus expose the same featured categories", async () => {
  for (const name of ["ClinicalMobileNav", "ClinicalDesktopNav"]) {
    const source = await read(`components/${name}.tsx`);
    for (const [constantName, next, destination] of [
      ["CLINICA_DECISAO", "const ESTUDO_EDUCACAO", "/heart-team"],
      ["ESTUDO_EDUCACAO", "const TRABALHO_ASSISTENCIA", "/intelligence"],
      ["TRABALHO_ASSISTENCIA", "const FERRAMENTAS", "/whatsapp-assistant"],
    ]) {
      const items = JSON.parse(constant(source, constantName, next));
      assert.equal(items.find(item => item.to === destination)?.featured, true, `${name}: ${destination}`);
    }
  }
});

const temp = await mkdtemp(path.join(tmpdir(), "corvia-discovery-"));
await symlink(path.join(root, "node_modules"), path.join(temp, "node_modules"));
after(() => rm(temp, { recursive: true, force: true }));
await writeFile(path.join(temp, "gate.mjs"), transpile(await read("components/AIInstallationGate.tsx")));
const { default: Gate } = await import(pathToFileURL(path.join(temp, "gate.mjs")));

test("disabled installation shows honest status without mounting operational children", () => {
  let mounted = false;
  const Operational = () => { mounted = true; return React.createElement("p", null, "operation"); };
  const html = renderToStaticMarkup(React.createElement(MemoryRouter, null,
    React.createElement(Gate, { enabled: false, label: "Assistente WhatsApp" }, React.createElement(Operational))));
  assert.equal(mounted, false);
  assert.match(html, /ainda não está ativo/);
  assert.match(html, /Assistente WhatsApp/);
  assert.doesNotMatch(html, /href="\/assinatura"/);
});

test("enabled installation renders existing module", () => {
  const html = renderToStaticMarkup(React.createElement(Gate, { enabled: true, label: "Heart Team" }, React.createElement("p", null, "existing module")));
  assert.match(html, /existing module/);
  assert.doesNotMatch(html, /ainda não está ativo/);
});
