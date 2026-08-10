import { readFile, readdir } from "node:fs/promises";
import { join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const sourceRoot = new URL("../src/", import.meta.url);

// Exceção única e deliberada: o Corvia Mail precisa interpretar HTML recebido
// por e-mail. Esse HTML é sanitizado e renderizado em iframe isolado, com CSP
// própria e sandbox sem allow-scripts. As invariantes abaixo tornam a exceção
// mais restritiva que uma simples allowlist e falham se a proteção for removida.
//
// Achado de auditoria (issue #52, subfase 5): esta constante apontava para
// "pages/CaixaDeEmail.tsx", que virou um shim de 1 linha
// (`export { default } from "./CaixaDeEmailProfessional"`) quando a caixa foi
// redesenhada — a sanitização de verdade (DOMParser, remoção de tag/atributo
// perigoso, iframe sandboxed sem allow-scripts, CSP própria) está em
// CaixaDeEmailProfessional.tsx desde então. O gate ficou cego ao arquivo real
// (checava um shim sem nenhum dos padrões e sinalizava o arquivo de verdade
// como uso não aprovado de DOMParser/srcDoc) sem que ninguém notasse — o
// CI não bloqueia local, só roda em push. Confirmado por leitura, não só
// pelo check: a implementação real em CaixaDeEmailProfessional.tsx já
// satisfazia todas as invariantes antes desta correção; produção nunca
// esteve exposta, só o gate estava apontando para o arquivo errado.
const APPROVED_EMAIL_RENDERER = "pages/CaixaDeEmailProfessional.tsx";

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
    id: "dom-parser",
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
    id: "srcdoc",
    pattern: /\bsrcDoc\s*=/,
    reason: "iframe srcDoc exige sanitização e sandbox dedicados",
  },
];

function validateApprovedEmailRenderer(content, display) {
  const failures = [];
  const iframe = (content.match(/<iframe\b[\s\S]*?\/>/gi) || [])
    .find((tag) => /\bsrcDoc\s*=/.test(tag));

  if (!/new\s+DOMParser\s*\(/.test(content)) {
    failures.push(`${display}: a exceção aprovada exige DOMParser explícito`);
  }
  if (!iframe) {
    failures.push(`${display}: a exceção aprovada exige iframe com srcDoc`);
  } else {
    const sandbox = iframe.match(/\bsandbox\s*=\s*["']([^"']*)["']/i);
    if (!sandbox) {
      failures.push(`${display}: iframe de e-mail precisa de sandbox explícito`);
    } else if (/\ballow-scripts\b/i.test(sandbox[1])) {
      failures.push(`${display}: allow-scripts é proibido no iframe de e-mail`);
    }
  }
  if (!/Content-Security-Policy/i.test(content) || !/default-src\s+'none'/i.test(content)) {
    failures.push(`${display}: documento do e-mail precisa de CSP com default-src 'none'`);
  }
  if (/\ballow-scripts\b/i.test(content)) {
    failures.push(`${display}: allow-scripts é proibido em toda a implementação aprovada`);
  }
  return failures;
}

export function validateRenderingSource(content, display) {
  const failures = [];
  for (const rule of forbiddenPatterns) {
    const approvedException = display === APPROVED_EMAIL_RENDERER
      && (rule.id === "dom-parser" || rule.id === "srcdoc");
    if (!approvedException && rule.pattern.test(content)) {
      failures.push(`${display}: ${rule.reason}`);
    }
  }

  if (display === APPROVED_EMAIL_RENDERER) {
    failures.push(...validateApprovedEmailRenderer(content, display));
  }

  const blankTargets = content.match(/<a\b(?=[^>]*target=["']_blank["'])(?![^>]*rel=["'][^"']*(?:noopener|noreferrer))[^>]*>/gis) || [];
  if (blankTargets.length) {
    failures.push(`${display}: link target=_blank sem rel=noopener/noreferrer`);
  }
  return failures;
}

async function walk(directory, failures) {
  const entries = await readdir(directory, { withFileTypes: true });
  for (const entry of entries) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) {
      await walk(path, failures);
      continue;
    }
    if (!/\.(?:ts|tsx|js|jsx)$/.test(entry.name)) continue;

    const content = await readFile(path, "utf8");
    const display = relative(sourceRoot.pathname, path);
    failures.push(...validateRenderingSource(content, display));
  }
}

export async function checkRenderingTree(root = sourceRoot.pathname) {
  const failures = [];
  await walk(root, failures);
  return failures;
}

const isMain = process.argv[1]
  && fileURLToPath(import.meta.url) === resolve(process.argv[1]);

if (isMain) {
  const failures = await checkRenderingTree();
  if (failures.length) {
    console.error("Falha na política de renderização segura:\n");
    for (const failure of failures) console.error(`- ${failure}`);
    process.exit(1);
  }

  console.log("Renderização segura: sinks proibidos bloqueados e renderer de e-mail isolado validado.");
}
