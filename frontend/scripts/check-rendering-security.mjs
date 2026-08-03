import { readFile, readdir } from "node:fs/promises";
import { join, relative } from "node:path";

const sourceRoot = new URL("../src/", import.meta.url);
const failures = [];

const forbiddenPatterns = [
  {
    pattern: /dangerouslySetInnerHTML/,
    reason: "injeção direta de HTML no React é proibida",
  },
  {
    pattern: /\.innerHTML\s*=/,
    reason: "atribuição a innerHTML é proibida",
  },
  {
    pattern: /insertAdjacentHTML\s*\(/,
    reason: "insertAdjacentHTML é proibido",
  },
  {
    pattern: /document\.write\s*\(/,
    reason: "document.write é proibido",
  },
  {
    pattern: /createContextualFragment\s*\(/,
    reason: "criação de fragmento HTML não sanitizado é proibida",
  },
  {
    pattern: /new\s+DOMParser\s*\(/,
    reason: "parsing manual de HTML exige revisão e sanitização explícitas",
  },
  {
    pattern: /(?:from\s+["']rehype-raw["']|require\s*\(\s*["']rehype-raw["'])/,
    reason: "Markdown não pode habilitar HTML cru por rehype-raw",
  },
  {
    pattern: /securityLevel\s*:\s*["']loose["']/,
    reason: "Mermaid em modo loose permite conteúdo inseguro",
  },
  {
    pattern: /(?:href|src)\s*=\s*["']\s*javascript:/i,
    reason: "protocolo javascript: é proibido em href/src",
  },
  {
    pattern: /["'`]javascript\s*:/i,
    reason: "strings com protocolo javascript: são proibidas",
  },
  {
    pattern: /\bsrcDoc\s*=/,
    reason: "iframe srcDoc exige sanitização e sandbox dedicados",
  },
];

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  for (const entry of entries) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) {
      await walk(path);
      continue;
    }
    if (!/\.(?:ts|tsx|js|jsx)$/.test(entry.name)) continue;

    const content = await readFile(path, "utf8");
    const display = relative(sourceRoot.pathname, path);
    for (const rule of forbiddenPatterns) {
      if (rule.pattern.test(content)) failures.push(`${display}: ${rule.reason}`);
    }

    const blankTargets = content.match(/<a\b(?=[^>]*target=["']_blank["'])(?![^>]*rel=["'][^"']*(?:noopener|noreferrer))[^>]*>/gis) || [];
    if (blankTargets.length) {
      failures.push(`${display}: link target=_blank sem rel=noopener/noreferrer`);
    }
  }
}

await walk(sourceRoot.pathname);

if (failures.length) {
  console.error("Falha na política de renderização segura:\n");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Renderização segura: nenhum sink HTML proibido ou link inseguro encontrado.");
