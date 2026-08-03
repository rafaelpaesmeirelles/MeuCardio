import { readFile, readdir } from "node:fs/promises";
import { join, relative } from "node:path";

const root = new URL("../src/", import.meta.url);
const failures = [];

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  for (const entry of entries) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) {
      await walk(path);
      continue;
    }
    if (!/\.(ts|tsx|js|jsx)$/.test(entry.name)) continue;

    const content = await readFile(path, "utf8");
    const display = relative(new URL("..", root).pathname, path);

    // A caixa CorvIA Mail tem credencial e sessão separadas; este guard protege
    // exclusivamente a sessão principal da plataforma nesta etapa.
    if (display.endsWith("lib/apiEmail.ts")) continue;

    const forbidden = [
      {
        pattern: /localStorage\.(?:getItem|setItem)\s*\([^\n]*meucardio\.token/i,
        reason: "JWT da plataforma não pode ser lido ou gravado no localStorage",
      },
      {
        pattern: /headers\.set\s*\(\s*["']Authorization["'][^\n]*Bearer/i,
        reason: "cliente web principal não deve montar Authorization Bearer",
      },
      {
        pattern: /access_token\s*:\s*string/i,
        reason: "login web não deve receber access_token no JavaScript",
      },
    ];

    for (const rule of forbidden) {
      if (rule.pattern.test(content)) {
        failures.push(`${display}: ${rule.reason}`);
      }
    }
  }
}

await walk(root.pathname);

const apiPath = new URL("../src/lib/api.ts", import.meta.url);
const api = await readFile(apiPath, "utf8");
for (const required of [
  'credentials: "include"',
  '"/auth/sessao"',
  "localStorage.removeItem(LEGACY_TOKEN_KEY)",
]) {
  if (!api.includes(required)) {
    failures.push(`src/lib/api.ts: proteção esperada ausente: ${required}`);
  }
}

if (failures.length) {
  console.error("Falha na política de armazenamento da sessão web:\n");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Sessão web sem JWT persistido ou exposto ao JavaScript.");
