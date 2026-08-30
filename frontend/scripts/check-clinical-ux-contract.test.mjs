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
  assert.match(css, /body\.corvia-route--emergencia[\s\S]*?\.cos-content\s*>\s*\.emerg\s*\{[\s\S]*?right:\s*0\s*!important;[\s\S]*?width:\s*calc\(100vw - var\(--ccc-nav-w\)\)\s*!important;/);
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

test("navegação usa contexto clínico e elimina rotas duplicadas do catálogo", () => {
  const context = read("src/lib/clinicalNavigationContext.ts");
  const desktop = read("src/components/ClinicalDesktopNav.tsx");
  const mobile = read("src/components/ClinicalMobileNav.tsx");
  const visualQa = read("../.github/workflows/visual-qa.yml");
  for (const token of ["Farmacologia clínica", "Contexto do paciente", "Produção clínica", "Tudo com Tudo", "commandDestination"]) {
    assert.equal(context.includes(token), true, `falta contexto: ${token}`);
  }
  assert.equal(desktop.includes("<details"), true, "seções desktop precisam de revelação progressiva");
  assert.equal(desktop.includes("No seu contexto"), true);
  assert.equal(mobile.includes("cc-mobile-more__context"), true);
  assert.equal(visualQa.includes("ancestor::details[1]"), true, "QA visual precisa abrir a seção antes de validar o link");
  assert.equal(visualQa.includes("scrollIntoViewIfNeeded"), true, "QA visual precisa rolar a navegação progressiva antes de validar o link");
  for (const [source, name] of [[desktop, "desktop"], [mobile, "mobile"]]) {
    assert.equal((source.match(/to: "\/calculadoras"/g) ?? []).length, 1, `calculadoras duplicada no ${name}`);
    assert.equal((source.match(/to: "\/telediagnostico"/g) ?? []).length, 1, `telediagnóstico duplicado no ${name}`);
    assert.equal(source.includes("Notas & Favoritos"), false, `o ${name} não pode prometer notas inexistentes`);
  }
});

test("busca tem refinamento progressivo e favoritos fecham o fluxo prometido", () => {
  const search = read("src/pages/Busca.tsx");
  const favorites = read("src/pages/Favoritos.tsx");
  const favoriteButton = read("src/components/BotaoFavorito.tsx");
  const drug = read("src/pages/MedicamentosClinicalCommand.tsx");
  const document = read("src/pages/Documento.tsx");
  const image = read("src/pages/ImagemGaleria.tsx");
  const drugApi = read("../backend/app/api/drug_insights.py");
  for (const token of ["Filtrar por área clínica", "Ver todos os", "aria-expanded", "tct-group__toggle"]) {
    assert.equal(search.includes(token), true, `busca sem contrato progressivo: ${token}`);
  }
  assert.equal(favorites.includes("Filtrar favoritos"), true);
  assert.equal(favorites.includes("Buscar conteúdo"), true);
  assert.equal(favoriteButton.includes("Atualizando…"), true);
  assert.equal(drug.includes('itemType="medicamento"'), true);
  assert.equal(document.includes('itemType="documento"'), true);
  assert.equal(image.includes('itemType="imagem"'), true);
  assert.match(drugApi, /"id": drug\.id/);
});
