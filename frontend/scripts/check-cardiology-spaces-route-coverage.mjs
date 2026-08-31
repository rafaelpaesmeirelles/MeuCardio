import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");

const app = read("src/App.tsx");
const context = read("src/components/ClinicalRouteContext.tsx");

const shellStart = app.indexOf('<Route element={<Shell />}>');
if (shellStart < 0) throw new Error("Não foi possível localizar o bloco autenticado <Shell /> em App.tsx.");
const shellEnd = app.indexOf("</Route>", shellStart);
if (shellEnd < 0) throw new Error("Não foi possível localizar o fim do bloco autenticado <Shell /> em App.tsx.");
const shell = app.slice(shellStart, shellEnd);

const routePaths = [...shell.matchAll(/<Route\s+path="([^"]+)"/g)].map((match) => match[1]);
if (!routePaths.length) throw new Error("Nenhuma rota autenticada foi extraída de App.tsx.");

const prefixes = [...context.matchAll(/\{\s*prefix:\s*"([^"]+)"\s*,\s*group:\s*"([^"]+)"\s*,\s*space:\s*"([^"]+)"\s*\}/g)]
  .map(([, prefix, group, space]) => ({ prefix, group, space }));
if (!prefixes.length) throw new Error("ClinicalRouteContext não contém rotas canônicas.");

const validSpaces = new Set(["consultorio", "hospital", "ensino", "pesquisa", "gestao"]);
for (const item of prefixes) {
  if (!validSpaces.has(item.space)) throw new Error(`Espaço inválido em ${item.prefix}: ${item.space}`);
}

// Aliases deliberadamente removidos do produto: existem apenas para preservar deep-links.
const explicitAliases = new Set(["cursos", "cursos/:slug"]);

const absolutePath = (routePath) => `/${routePath.replace(/^\/+/, "")}`;
const isCovered = (pathname) => prefixes.some(({ prefix }) => pathname === prefix || pathname.startsWith(`${prefix}/`));

const uncovered = routePaths
  .filter((routePath) => !explicitAliases.has(routePath))
  .map((routePath) => ({ routePath, pathname: absolutePath(routePath) }))
  .filter(({ pathname }) => !isCovered(pathname));

if (uncovered.length) {
  throw new Error(
    `Rotas autenticadas sem espaço Cardiology Spaces explícito:\n${uncovered.map(({ routePath }) => ` - ${routePath}`).join("\n")}`,
  );
}

for (const alias of explicitAliases) {
  if (!routePaths.includes(alias)) throw new Error(`Alias esperado desapareceu de App.tsx: ${alias}`);
  const escaped = alias.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const redirectPattern = new RegExp(`<Route\\s+path="${escaped}"\\s+element=\\{<Navigate\\s+to="/trilhas"`);
  if (!redirectPattern.test(shell)) throw new Error(`${alias} deve continuar redirecionando para /trilhas e nunca reaparecer como função.`);
}

const layers = {
  consultorio: "../styles/cardiology-spaces-consultorio-pages.css",
  hospital: "../styles/cardiology-spaces-hospital-pages.css",
  ensino: "../styles/cardiology-spaces-ensino-pages.css",
  pesquisa: "../styles/cardiology-spaces-pesquisa-pages.css",
  gestao: "../styles/cardiology-spaces-gestao-pages.css",
};

for (const [space, importPath] of Object.entries(layers)) {
  const importStatement = `import "${importPath}";`;
  if (!context.includes(importStatement)) throw new Error(`ClinicalRouteContext não carrega a camada visual de ${space}: ${importPath}`);

  const cssPath = `src/styles/${path.basename(importPath)}`;
  if (!fs.existsSync(path.join(root, cssPath))) throw new Error(`Camada visual ausente: ${cssPath}`);
  const css = read(cssPath);
  if (!css.includes(`corvia-space--${space}`)) throw new Error(`${cssPath} não declara seletores explícitos para corvia-space--${space}.`);
}

const counts = Object.fromEntries([...validSpaces].map((space) => [space, prefixes.filter((item) => item.space === space).length]));
for (const [space, count] of Object.entries(counts)) {
  if (count === 0) throw new Error(`O espaço ${space} ficou sem nenhuma rota explícita.`);
}

console.log(`Cardiology Spaces route coverage OK: ${routePaths.length - explicitAliases.size} rotas autenticadas cobertas.`);
console.log(`Distribuição explícita: ${Object.entries(counts).map(([space, count]) => `${space}=${count}`).join(" · ")}`);
