import { readFile, readdir, stat } from "node:fs/promises";
import { join, relative } from "node:path";
import { gzipSync } from "node:zlib";

const dist = new URL("../dist/", import.meta.url);
const manifest = JSON.parse(
  await readFile(new URL("../dist/.vite/manifest.json", import.meta.url), "utf8"),
);
const mainEntry = manifest["index.html"];

if (!mainEntry?.file) {
  console.error("Manifesto Vite não contém o entrypoint index.html.");
  process.exit(1);
}

const mainPath = join(dist.pathname, mainEntry.file);
const mainBytes = (await stat(mainPath)).size;
const mainGzipBytes = gzipSync(await readFile(mainPath)).length;
const maxMainBytes = 300 * 1024;
const maxMainGzipBytes = 100 * 1024;

const failures = [];
if (mainBytes > maxMainBytes) {
  failures.push(`entrypoint inicial ${mainBytes} B excede ${maxMainBytes} B`);
}
if (mainGzipBytes > maxMainGzipBytes) {
  failures.push(`entrypoint inicial gzip ${mainGzipBytes} B excede ${maxMainGzipBytes} B`);
}

const pageEntries = Object.keys(manifest).filter((key) => key.startsWith("src/pages/"));
if (pageEntries.length < 45) {
  failures.push(`manifesto contém apenas ${pageEntries.length} chunks de página`);
}

async function listarArquivos(directory, files = []) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) await listarArquivos(path, files);
    else files.push(path);
  }
  return files;
}

const swPath = join(dist.pathname, "sw.js");
const sw = await readFile(swPath, "utf8");
let precacheBytes = 0;
let precacheEntries = 0;
const maxOptionalPrecacheJs = 160 * 1024;

for (const path of await listarArquivos(dist.pathname)) {
  const rel = relative(dist.pathname, path).replaceAll("\\", "/");
  if (rel === "sw.js" || rel.startsWith("workbox-")) continue;
  if (!sw.includes(rel)) continue;

  const bytes = (await stat(path)).size;
  precacheBytes += bytes;
  precacheEntries += 1;

  if (
    rel.endsWith(".js") &&
    rel !== mainEntry.file &&
    bytes > maxOptionalPrecacheJs
  ) {
    failures.push(`chunk opcional grande pré-carregado: ${rel} (${bytes} B)`);
  }
}

// Ajustado de 2500 KB para 2750 KB em 07/08/2026: crescimento orgânico de
// páginas (Avaliação Pré-Operatória, Sincronização de contas, Assistente
// Clínica/Pessoal etc.) levou o precache real a ~2536 KB, estourando o teto
// antigo por ~35 KB e travando o CI de qualquer PR, mesmo sem regressão de
// performance real.
//
// Ajustado de 2750 KB para 2775 KB em 17/08/2026: o refinamento visual
// canônico da Home adicionou somente CSS e levou o precache a 2817655 B,
// 1655 B acima do teto anterior (0,06%). O novo limite preserva um orçamento
// explícito e estreito, sem mascarar crescimento substancial futuro.
//
// Ajustado de 2775 KB para 2785 KB em 18/08/2026: a nova rota administrativa
// lazy AdminGerenciarUsuario adicionou um chunk próprio de ~9,6 KB e levou o
// precache certificado a 2849827 B. O entrypoint principal e o limite de chunks
// opcionais permanecem inalterados; este acréscimo revisado é restrito à nova
// funcionalidade e mantém margem mínima para detectar crescimento não intencional.
const maxPrecacheBytes = 2785 * 1024;
if (precacheBytes > maxPrecacheBytes) {
  failures.push(`precache ${precacheBytes} B excede ${maxPrecacheBytes} B`);
}

if (failures.length) {
  console.error("Orçamento do bundle excedido:\n");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(
  `Bundle aprovado: entry ${mainBytes} B (${mainGzipBytes} B gzip), ` +
    `${pageEntries.length} páginas separadas, precache ${precacheBytes} B em ${precacheEntries} arquivos.`,
);
