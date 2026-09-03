import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const raiz = process.cwd();
const cssPath = path.join(raiz, "src/styles/clinical-form-control-contrast.css");
const lightCssPath = path.join(raiz, "src/styles/cardiology-spaces-light-mode.css");
const assistantCssPath = path.join(raiz, "src/styles/clinical-assistant-command.css");
const assistantPagePath = path.join(raiz, "src/pages/Assistente.tsx");
const mainPath = path.join(raiz, "src/main.tsx");
const css = fs.readFileSync(cssPath, "utf8");
const assistantCss = fs.readFileSync(assistantCssPath, "utf8");
const assistantPage = fs.readFileSync(assistantPagePath, "utf8");
const main = fs.readFileSync(mainPath, "utf8");

function exigir(condicao, mensagem) {
  if (!condicao) {
    console.error(`ERRO: ${mensagem}`);
    process.exitCode = 1;
  }
}

const importContrato = 'import "./styles/clinical-form-control-contrast.css";';
const importTemaClaro = 'import "./styles/cardiology-spaces-light-mode.css";';
const importsCss = [...main.matchAll(/^import "\.\/styles\/[^\"]+\.css";$/gm)].map((match) => match[0]);

exigir(fs.existsSync(cssPath), "clinical-form-control-contrast.css precisa existir.");
exigir(fs.existsSync(lightCssPath), "cardiology-spaces-light-mode.css precisa existir.");
exigir(fs.existsSync(assistantCssPath), "clinical-assistant-command.css precisa existir.");
exigir(fs.existsSync(assistantPagePath), "Assistente.tsx precisa existir.");
exigir(main.includes(importContrato), "main.tsx precisa importar o contrato global de contraste.");
exigir(importsCss.at(-2) === importContrato,
  "o contrato escuro de contraste precisa permanecer imediatamente antes do tema claro.");
exigir(importsCss.at(-1) === importTemaClaro,
  "o tema claro isolado precisa ser a última folha CSS para sobrepor controles escuros com segurança.");

for (const trecho of [
  ".clinical-os input:not([type=\"checkbox\"])",
  ".clinical-os select",
  ".clinical-os textarea",
  "-webkit-text-fill-color: #eef8fa",
  "background-color: #0b1f2b",
  ".clinical-os input:-webkit-autofill",
  ".login input:not([type=\"checkbox\"])",
  // A prancha canônica aprovada usa navy/teal também antes do login. Estes
  // valores fixos garantem contraste alto sem reabrir a antiga exceção branca.
  "-webkit-text-fill-color: #eaf5f7",
  "background-color: #0b1f2b",
  ".login input:-webkit-autofill",
]) {
  exigir(css.includes(trecho), `contrato incompleto: falta ${trecho}`);
}

// A origem do bug foi usar tokens semânticos que mudam dentro de .clinical-os
// em uma superfície de fundo literal. O contrato final precisa usar tokens
// brutos/hex explícitos, para não voltar a depender de --texto/--superficie.
exigir(!/\.clinical-os[\s\S]*?\{[^}]*color:\s*var\(--texto\)/m.test(css),
  "o contrato final não pode usar var(--texto) para campos do Clinical OS.");
exigir(!/\.clinical-os[\s\S]*?\{[^}]*background(?:-color)?:\s*var\(--superficie\)/m.test(css),
  "o contrato final não pode usar var(--superficie) para campos do Clinical OS.");

// O composer do Assistente é uma superfície estrutural do Command Center,
// não uma barra flutuante de vidro. Protege o bug fotografado em produção:
// sticky + rgba/backdrop-filter deixavam o campo transparente e fora do painel.
const blocoEnvio = assistantCss.match(/body\.corvia-route--assistente \.ia__envio\s*\{([^}]*)\}/m)?.[1] ?? "";
const blocoTextarea = assistantCss.match(/body\.corvia-route--assistente \.ia__envio textarea\s*\{([^}]*)\}/m)?.[1] ?? "";
exigir(blocoEnvio.includes("position:relative"), "composer do Assistente precisa permanecer integrado ao fluxo do painel.");
exigir(blocoEnvio.includes("bottom:auto"), "composer do Assistente não pode voltar a ficar ancorado à viewport.");
exigir(blocoEnvio.includes("background:#071a25"), "composer do Assistente precisa usar superfície navy sólida canônica.");
exigir(blocoEnvio.includes("backdrop-filter:none"), "composer do Assistente não pode voltar ao efeito translúcido de vidro.");
exigir(blocoTextarea.includes("background:#0b2230!important"), "textarea do Assistente precisa manter superfície escura legível.");
exigir(blocoTextarea.includes("color:#eef9fa!important"), "textarea do Assistente precisa manter texto claro legível.");

// Clínica e Pessoal usam o MESMO workspace/composer. Se alguém voltar a
// renderizar um composer específico por modo, uma das duas variantes pode
// regredir visualmente sem o checker perceber.
const ocorrenciasComposer = assistantPage.match(/className="ia__envio"/g) ?? [];
exigir(ocorrenciasComposer.length === 1,
  "Assistente Clínica e Pessoal devem compartilhar um único composer canônico.");
exigir(assistantPage.includes('modo === "clinica" ? "Clínica" : "Pessoal"'),
  "Assistente.tsx precisa continuar atendendo os dois modos no mesmo workspace.");
exigir(assistantPage.includes('placeholder={modo === "clinica"'),
  "o composer compartilhado precisa continuar contextualizando Clínica e Pessoal.");

if (!process.exitCode) {
  console.log("OK: contrato global de contraste e composer canônico do Assistente estão protegidos.");
}
