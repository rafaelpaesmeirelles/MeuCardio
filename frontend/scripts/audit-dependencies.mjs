import { spawnSync } from "node:child_process";

const root = new URL("../", import.meta.url);
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

function blockers(report, { criticalOnly = false } = {}) {
  const found = [];
  for (const [packageName, vulnerability] of Object.entries(report.vulnerabilities || {})) {
    const severity = vulnerability.severity;
    const blocks = criticalOnly ? severity === "critical" : blockingSeverities.has(severity);
    if (blocks) found.push({ packageName, severity });
  }
  return found;
}

const productionReport = runAudit(["--omit=dev"]);
const completeReport = runAudit([]);
const productionBlockers = blockers(productionReport);
const completeBlockers = blockers(completeReport, { criticalOnly: true });

if (productionBlockers.length || completeBlockers.length) {
  console.error("Vulnerabilidades bloqueantes encontradas:");
  for (const item of [...productionBlockers, ...completeBlockers]) {
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
