import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const root = process.cwd();
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");

test("a cascata global tem um único manifesto, sem importações duplicadas", () => {
  const main = read("src/main.tsx");
  const manifest = read("src/styles/app.css");
  const mainStyles = [...main.matchAll(/^import "\.\/styles\/([^\"]+\.css)";$/gm)].map((match) => match[1]);
  const imports = [...manifest.matchAll(/^@import "\.\/([^\"]+\.css)";$/gm)].map((match) => match[1]);

  assert.deepEqual(mainStyles, ["app.css"]);
  assert.equal(new Set(imports).size, imports.length, "o manifesto não pode importar uma folha duas vezes");
  for (const stylesheet of imports) {
    assert.equal(fs.existsSync(path.join(root, "src/styles", stylesheet)), true, `${stylesheet} precisa existir`);
  }
  assert.deepEqual(imports.slice(-2), [
    "clinical-form-control-contrast.css",
    "clinical-safety-legibility.css",
  ]);
});

test("emergência mantém viewport, texto clínico e alvos seguros", () => {
  const css = read("src/styles/clinical-safety-legibility.css");
  assert.match(css, /body\.corvia-route--emergencia[\s\S]*?\.emerg\s*\{[\s\S]*?right:\s*0\s*!important;[\s\S]*?width:\s*auto\s*!important;/);
  assert.match(css, /--corvia-clinical-copy:\s*1rem;/);
  assert.match(css, /--corvia-clinical-target:\s*44px;/);
  assert.match(css, /\.emerg-command__quick a\s*\{[\s\S]*?min-height:\s*48px;/);
  assert.match(css, /\.nodeLabel[\s\S]*?color:\s*#17313f\s*!important;[\s\S]*?font-size:\s*16px\s*!important;/);
});

test("medicamentos, agenda, evidências e trilhos da home usam o piso de legibilidade", () => {
  const css = read("src/styles/clinical-safety-legibility.css");
  for (const surface of [".mc-command__primary-block", "corvia-route--agenda", ".cc-evidence-page", ".ccc-reference-board"]) {
    assert.equal(css.includes(surface), true, `falta contrato para ${surface}`);
  }
  assert.match(css, /\.mc-command__tabs button[\s\S]*?min-height:\s*var\(--corvia-clinical-target\)/);
});

test("cadastro tem rolagem única e rotas públicas possuem títulos distintos", () => {
  const css = read("src/styles/clinical-safety-legibility.css");
  const app = read("src/App.tsx");
  assert.match(css, /\.prehome--register \.prehome-card--register\s*\{[\s\S]*?max-height:\s*none\s*!important;[\s\S]*?overflow:\s*visible\s*!important;/);
  for (const title of [
    "Entrar — CorVIA Clinical OS",
    "Solicitar acesso — CorVIA Clinical OS",
    "Validar documento clínico — CorVIA Clinical OS",
    "Termos de Uso — CorVIA Clinical OS",
  ]) assert.equal(app.includes(title), true, `falta título público: ${title}`);
  assert.match(app, /document\.title\s*=\s*tituloDaRota\(location\.pathname\)/);
});

test("Termos de Uso cobrem a plataforma e preservam o apêndice de mapas", () => {
  const terms = read("src/pages/TermosUso.tsx");
  for (const section of [
    "Apoio à decisão clínica",
    "Dados pessoais e dados de pacientes",
    "Prescrições, documentos e assinaturas",
    "Integrações e serviços de terceiros",
    "Apêndice — mapas e deslocamento",
  ]) assert.equal(terms.includes(section), true, `falta seção jurídica: ${section}`);
});
