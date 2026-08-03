import { readFile } from "node:fs/promises";

const app = await readFile(new URL("../src/App.tsx", import.meta.url), "utf8");
const eagerPageImport = /^import\s+[^;]+\s+from\s+["']\.\/pages\//m;
const lazyPages = app.match(/lazy\s*\(\s*\(\)\s*=>\s*import\s*\(\s*["']\.\/pages\//g) || [];

if (eagerPageImport.test(app)) {
  console.error("App.tsx voltou a importar uma página de forma eager.");
  process.exit(1);
}

if (lazyPages.length < 45) {
  console.error(`Apenas ${lazyPages.length} páginas possuem divisão por rota; mínimo esperado: 45.`);
  process.exit(1);
}

if (!app.includes("<Suspense")) {
  console.error("Rotas lazy precisam permanecer protegidas por Suspense.");
  process.exit(1);
}

console.log(`Divisão por rota aprovada: ${lazyPages.length} páginas lazy.`);
