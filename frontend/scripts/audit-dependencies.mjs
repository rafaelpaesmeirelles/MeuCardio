import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const root = new URL("../", import.meta.url);
const sourceRoot = new URL("../src/", import.meta.url);
const RSC_ONLY_ADVISORY = "https://github.com/advisories/GHSA-qwww-vcr4-c8h2";
const blockingSeverities = new Set(["high", "critical"]);

function runAudit(args) {
  const result = spawnSync("npm", ["audit", ...args, "--json"], {
    cwd: root,
    encoding: "utf8",
  });

  if (!result.stdout?.trim()) {
    console.error(result.stderr || "npm audit não retornou JSON.");
    process.exit(2);
  }

  try {
    return JSON.parse(result.stdout);
  } catch (error) {
    console.error("Não foi possível interpretar o relatório do npm audit.");
    console.error(result.stdout);
    throw error;
  }
}

async function walk(directory, files = []) {
  const entries = await readdir(directory, { withFileTypes: true });
  for (const entry of entries) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) await walk(path, files);
    else if (/\.(?:ts|tsx|js|jsx)$/.test(entry.name)) files.push(path);
  }
  return files;
}

async function assertRscIsNotPresent() {
  const packageJson = JSON.parse(await readFile(new URL("../package.json", import.meta.url), "utf8"));
  const allDependencies = {
    ...(packageJson.dependencies || {}),
    ...(packageJson.devDependencies || {}),
  };

  const reactVersion = String(allDependencies.react || "");
  if (!/18(?:\.|$)/.test(reactVersion)) {
    throw new Error(
      "A exceção RSC só é válida enquanto o frontend permanecer em React 18; revise a política antes de atualizar."
    );
  }

  const forbiddenPackages = Object.keys(allDependencies).filter(
    (name) => name.startsWith("react-server-dom-") || name.startsWith("@react-router/")
  );
  if (forbiddenPackages.length) {
    throw new Error(`Infraestrutura RSC detectada: ${forbiddenPackages.join(", ")}`);
  }

  const forbiddenSourcePatterns = [
    /react-server-dom-/,
    /createRequestHandler\s*\(/,
    /RSCRouterConfig/,
    /unstable_createCallServer/,
    /unstable_RSCStaticRouter/,
    /unstable_RSCHydratedRouter/,
  ];
  for (const file of await walk(sourceRoot.pathname)) {
    const content = await readFile(file, "utf8");
    if (forbiddenSourcePatterns.some((pattern) => pattern.test(content))) {
      throw new Error(`Uso de API RSC detectado em ${file}; remova a exceção do audit antes do merge.`);
    }
  }
}

function leafAdvisories(report, packageName, visited = new Set()) {
  if (visited.has(packageName)) return [];
  visited.add(packageName);

  const vulnerability = report.vulnerabilities?.[packageName];
  if (!vulnerability) return [];

  const leaves = [];
  for (const cause of vulnerability.via || []) {
    if (typeof cause === "string") {
      leaves.push(...leafAdvisories(report, cause, visited));
    } else {
      leaves.push(cause);
    }
  }
  return leaves;
}

function isOnlyApprovedRscAdvisory(report, packageName) {
  const leaves = leafAdvisories(report, packageName);
  return (
    leaves.length > 0 &&
    leaves.every(
      (advisory) =>
        advisory?.severity === "high" &&
        advisory?.url === RSC_ONLY_ADVISORY
    )
  );
}

function blockingPackages(report, { allowRscException = false, criticalOnly = false } = {}) {
  const blocked = [];
  const allowed = [];

  for (const [packageName, vulnerability] of Object.entries(report.vulnerabilities || {})) {
    const severity = vulnerability.severity;
    const blocks = criticalOnly ? severity === "critical" : blockingSeverities.has(severity);
    if (!blocks) continue;

    if (allowRscException && isOnlyApprovedRscAdvisory(report, packageName)) {
      allowed.push(packageName);
      continue;
    }
    blocked.push({ packageName, severity, via: vulnerability.via });
  }
  return { blocked, allowed };
}

await assertRscIsNotPresent();

const productionReport = runAudit(["--omit=dev"]);
const completeReport = runAudit([]);
const production = blockingPackages(productionReport, { allowRscException: true });
const complete = blockingPackages(completeReport, { criticalOnly: true });

if (production.allowed.length) {
  console.log(
    `Exceção RSC não aplicável confirmada para: ${production.allowed.join(", ")}. ` +
      "React 18 SPA, sem pacotes ou APIs RSC."
  );
}

if (production.blocked.length || complete.blocked.length) {
  console.error("Vulnerabilidades bloqueantes encontradas:");
  for (const item of [...production.blocked, ...complete.blocked]) {
    console.error(`- ${item.packageName}: ${item.severity}`);
  }
  process.exit(1);
}

const productionMeta = productionReport.metadata?.vulnerabilities || {};
const completeMeta = completeReport.metadata?.vulnerabilities || {};
console.log(
  "Audit aprovado. " +
    `Produção: ${productionMeta.high || 0} alta(s), ${productionMeta.critical || 0} crítica(s); ` +
    `grafo completo: ${completeMeta.critical || 0} crítica(s).`
);
