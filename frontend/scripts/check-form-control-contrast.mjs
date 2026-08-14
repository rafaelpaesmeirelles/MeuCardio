import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const raiz = process.cwd();
const cssPath = path.join(raiz, "src/styles/clinical-form-control-contrast.css");
const mainPath = path.join(raiz, "src/main.tsx");
const css = fs.readFileSync(cssPath, "utf8");
const main = fs.readFileSync(mainPath, "utf8");

function exigir(condicao, mensagem) {
  if (!condicao) {
    console.error(`ERRO: ${mensagem}`);
    process.exitCode = 1;
  }
}

const importContrato = 'import "./styles/clinical-form-control-contrast.css";';
const indiceContrato = main.indexOf(importContrato);
const ultimoImportCss = [...main.matchAll(/^import "\.\/styles\/[^\"]+\.css";$/gm)].at(-1)?.index ?? -1;

exigir(fs.existsSync(cssPath), "clinical-form-control-contrast.css precisa existir.");
exigir(indiceContrato >= 0, "main.tsx precisa importar o contrato global de contraste.");
exigir(indiceContrato === ultimoImportCss, "o contrato de contraste precisa ser a última folha CSS importada.");

for (const trecho of [
  ".clinical-os input:not([type=\"checkbox\"])",
  ".clinical-os select",
  ".clinical-os textarea",
  "-webkit-text-fill-color: #eef8fa",
  "background-color: #0b1f2b",
  ".clinical-os input:-webkit-autofill",
  ".login input:not([type=\"checkbox\"])",
  "-webkit-text-fill-color: #082637",
  "background-color: #ffffff",
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

if (!process.exitCode) {
  console.log("OK: contrato global de contraste dos campos está ativo e importado por último.");
}
