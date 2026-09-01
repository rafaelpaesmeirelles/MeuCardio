import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");

const app = read("src/App.tsx");
const context = read("src/components/ClinicalRouteContext.tsx");
const registry = read("src/lib/clinicalRouteRegistry.ts");
const EXPECTED_AUTHENTICATED_PATTERNS = 75;

const shellStart = app.indexOf('<Route element={<Shell />}>');
if (shellStart < 0) throw new Error("Não foi possível localizar o bloco autenticado <Shell /> em App.tsx.");
const authenticatedRoutesEnd = app.indexOf("</Routes>", shellStart);
if (authenticatedRoutesEnd < 0) throw new Error("Não foi possível localizar o fim das rotas autenticadas em App.tsx.");
const authenticatedRoutes = app.slice(shellStart, authenticatedRoutesEnd);

const absolutePath = (routePath) => routePath === "/" ? "/" : `/${routePath.replace(/^\/+/, "")}`;
const indexRouteCount = [...authenticatedRoutes.matchAll(/<Route\s+index\b/g)].length;
const appDeclaredPaths = [...authenticatedRoutes.matchAll(/<Route\s+path="([^"]+)"/g)].map((match) => match[1]);
const appRoutePaths = [
  ...Array.from({ length: indexRouteCount }, () => "/"),
  ...appDeclaredPaths.filter((routePath) => routePath !== "*").map(absolutePath),
];

function duplicated(values) {
  const seen = new Set();
  const duplicates = new Set();
  for (const value of values) {
    if (seen.has(value)) duplicates.add(value);
    seen.add(value);
  }
  return [...duplicates].sort();
}

const appDuplicates = duplicated(appRoutePaths);
if (appDuplicates.length) throw new Error(`Padrões autenticados duplicados em App.tsx: ${appDuplicates.join(", ")}`);
if (appRoutePaths.length !== EXPECTED_AUTHENTICATED_PATTERNS) {
  throw new Error(`App.tsx declara ${appRoutePaths.length} padrões autenticados; esperado: ${EXPECTED_AUTHENTICATED_PATTERNS}.`);
}

const field = (body, name) => body.match(new RegExp(`(?:^|[,\\s])${name}:\\s*"([^"]*)"`))?.[1];
const registryRoutes = [...registry.matchAll(/route\(\{([\s\S]*?)\}\)/g)].map((match, index) => {
  const body = match[1];
  const definition = {
    path: field(body, "path"),
    space: field(body, "space"),
    group: field(body, "group"),
    kind: field(body, "kind") ?? "page",
    parent: field(body, "parent"),
    redirectTo: field(body, "redirectTo"),
  };
  if (!definition.path || !definition.space || !definition.group) {
    throw new Error(`Definição ${index + 1} do registro não possui path, space e group literais.`);
  }
  return definition;
});

if (registryRoutes.length !== EXPECTED_AUTHENTICATED_PATTERNS) {
  throw new Error(`clinicalRouteRegistry.ts declara ${registryRoutes.length} padrões; esperado: ${EXPECTED_AUTHENTICATED_PATTERNS}.`);
}

const registryRoutePaths = registryRoutes.map((definition) => definition.path);
const registryDuplicates = duplicated(registryRoutePaths);
if (registryDuplicates.length) throw new Error(`Padrões duplicados no registro: ${registryDuplicates.join(", ")}`);

const appPathSet = new Set(appRoutePaths);
const registryPathSet = new Set(registryRoutePaths);
const missingFromRegistry = appRoutePaths.filter((routePath) => !registryPathSet.has(routePath));
const missingFromApp = registryRoutePaths.filter((routePath) => !appPathSet.has(routePath));
if (missingFromRegistry.length || missingFromApp.length) {
  throw new Error([
    "App.tsx e clinicalRouteRegistry.ts divergiram.",
    missingFromRegistry.length ? `Ausentes no registro: ${missingFromRegistry.join(", ")}` : "",
    missingFromApp.length ? `Ausentes no App.tsx: ${missingFromApp.join(", ")}` : "",
  ].filter(Boolean).join("\n"));
}

for (const requiredPath of ["/", "/tour", "/tour/cardiology-spaces", "/em-breve"]) {
  if (!appPathSet.has(requiredPath) || !registryPathSet.has(requiredPath)) {
    throw new Error(`Padrão autenticado obrigatório ausente: ${requiredPath}`);
  }
}

const functionalSpaces = ["consultorio", "hospital", "ensino", "pesquisa", "gestao"];
const functionalSpaceSet = new Set(functionalSpaces);
const allowedRouteSpaces = new Set([...functionalSpaces, "home"]);
const spacesStart = registry.indexOf("export const CLINICAL_SPACES");
const routesStart = registry.indexOf("export const CLINICAL_ROUTES");
if (spacesStart < 0 || routesStart < 0 || routesStart <= spacesStart) {
  throw new Error("Não foi possível localizar CLINICAL_SPACES e CLINICAL_ROUTES no registro.");
}
const declaredSpaces = [...registry.slice(spacesStart, routesStart).matchAll(/^  ([a-z][a-z0-9-]*):\s*\{/gm)].map((match) => match[1]);
const declaredSpaceDuplicates = duplicated(declaredSpaces);
if (declaredSpaceDuplicates.length) throw new Error(`Espaços funcionais duplicados: ${declaredSpaceDuplicates.join(", ")}`);
const undeclaredFunctionalSpaces = functionalSpaces.filter((space) => !declaredSpaces.includes(space));
const extraFunctionalSpaces = declaredSpaces.filter((space) => !functionalSpaceSet.has(space));
if (declaredSpaces.length !== functionalSpaces.length || undeclaredFunctionalSpaces.length || extraFunctionalSpaces.length) {
  throw new Error([
    "CLINICAL_SPACES deve declarar exatamente os cinco espaços funcionais.",
    undeclaredFunctionalSpaces.length ? `Ausentes: ${undeclaredFunctionalSpaces.join(", ")}` : "",
    extraFunctionalSpaces.length ? `Extras: ${extraFunctionalSpaces.join(", ")}` : "",
  ].filter(Boolean).join("\n"));
}

for (const definition of registryRoutes) {
  if (!allowedRouteSpaces.has(definition.space)) {
    throw new Error(`Espaço inválido em ${definition.path}: ${definition.space}`);
  }
  if (definition.parent && !registryPathSet.has(definition.parent)) {
    throw new Error(`Parent inexistente em ${definition.path}: ${definition.parent}`);
  }
  if (definition.redirectTo) {
    const redirectPath = definition.redirectTo.split(/[?#]/, 1)[0];
    if (!redirectPath.startsWith("/") || !registryPathSet.has(redirectPath)) {
      throw new Error(`redirectTo inexistente ou não canônico em ${definition.path}: ${definition.redirectTo}`);
    }
  }
}

const counts = Object.fromEntries(functionalSpaces.map((space) => [space, registryRoutes.filter((item) => item.space === space).length]));
for (const [space, count] of Object.entries(counts)) {
  if (count === 0) throw new Error(`O espaço ${space} ficou sem nenhuma rota explícita.`);
}

// Aliases deliberadamente removidos do produto: existem apenas para preservar deep-links.
const explicitAliases = new Set(["cursos", "cursos/:slug"]);

for (const alias of explicitAliases) {
  if (!appDeclaredPaths.includes(alias)) throw new Error(`Alias esperado desapareceu de App.tsx: ${alias}`);
  const escaped = alias.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const redirectPattern = new RegExp(`<Route\\s+path="${escaped}"\\s+element=\\{<Navigate\\s+to="/trilhas"`);
  if (!redirectPattern.test(authenticatedRoutes)) throw new Error(`${alias} deve continuar redirecionando para /trilhas e nunca reaparecer como função.`);
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

// Contrato de identidade visível: classes e nomes de arquivo legados podem existir
// como detalhes técnicos de compatibilidade, mas nenhuma superfície moderna pode
// voltar a exibir a nomenclatura antiga do produto.
const brandCss = read("src/styles/canonical-brand-standard.css");
if (!brandCss.includes('.cos-nav__home small::after')) {
  throw new Error("O shell legado não possui substituição visual explícita para o subtítulo antigo.");
}
if (!brandCss.includes('content:"Cardiology Spaces"')) {
  throw new Error("O shell legado deve exibir Cardiology Spaces no lugar da nomenclatura antiga.");
}
if (!brandCss.includes('a[href="/cursos"]') || !brandCss.includes('a[href^="/cursos/"]')) {
  throw new Error("Cursos deve permanecer invisível em qualquer shell legado.");
}

const modernSurfaces = [
  "src/components/ClinicalDesktopNav.tsx",
  "src/components/ClinicalMobileNav.tsx",
  "src/components/ClinicalCommandPrimitives.tsx",
  "src/pages/CardiologySpacesHome.tsx",
  "src/pages/CardiologySpacesTour.tsx",
];
for (const file of modernSurfaces) {
  const source = read(file);
  if (/Clinical Command Center|Clinical OS/.test(source)) {
    throw new Error(`${file} voltou a expor nomenclatura visual legada.`);
  }
  if (/to:\s*["']\/cursos(?:\/|["'])|href=["']\/cursos/.test(source)) {
    throw new Error(`${file} voltou a expor Cursos como opção navegável.`);
  }
}

const legacyShell = read("src/components/ShellClinicalOSLaunch.tsx");
if (!legacyShell.includes("<small>Clinical Command Center</small>")) {
  // Quando o shell for finalmente renomeado em código, a regra abaixo deixa de ser
  // necessária. Até lá, o texto residual só é aceitável porque canonical-brand-standard
  // o substitui de forma determinística por Cardiology Spaces.
  if (/Clinical Command Center/.test(legacyShell)) {
    throw new Error("Encontrada outra ocorrência não controlada de Clinical Command Center no shell legado.");
  }
}
if (!legacyShell.includes("Cardiology Spaces")) {
  throw new Error("O shell autenticado deve carregar branding Cardiology Spaces explícito.");
}

console.log(`Cardiology Spaces route registry OK: ${registryRoutes.length} padrões autenticados em paridade exata com App.tsx.`);
console.log(`Distribuição completa: ${Object.entries(counts).map(([space, count]) => `${space}=${count}`).join(" · ")} · home=${registryRoutes.filter((item) => item.space === "home").length}`);
console.log("Cardiology Spaces visible-brand contract OK: nomenclatura antiga não é exibida nas superfícies modernas.");
