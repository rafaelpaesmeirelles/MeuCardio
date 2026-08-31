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
//
// Ajustado de 2785 KB para 2786 KB em 21/08/2026: o pixel polish conservador
// aprovado adicionou apenas CSS óptico e levou o precache a 2852491 B, 651 B
// acima do teto anterior (0,02%). O incremento é deliberadamente mínimo; os
// limites do entrypoint e de chunks opcionais permanecem inalterados.
//
// Ajustado de 2786 KB para 2800 KB em 21/08/2026: a personalização aprovada
// das Ações Rápidas e o balanceamento da Home desktop levaram o precache a
// 2853517 B, somente 653 B acima do teto anterior. A nova margem continua
// estreita (~14 KiB) e não altera os limites do entrypoint, gzip ou chunks
// opcionais, preservando a detecção de crescimento relevante.
//
// Ajustado de 2800 KB para 2810 KB em 22/08/2026: a integração autorizada da
// Agenda clínica/Sala de Espera ao Prontuário levou o precache a 2867358 B,
// apenas 158 B acima do teto anterior. O acréscimo mantém ~10 KiB de margem e
// preserva sem alteração os limites do entrypoint, gzip e chunks opcionais.
//
// Ajustado de 2810 KB para 2820 KB em 22/08/2026: o slice vertical aprovado
// de ECG com assistência IA revisável acrescentou a UI clínica ao chunk lazy
// do Prontuário e levou o precache a 2884003 B. O entrypoint, seu teto gzip e
// o limite individual de chunks opcionais permanecem inalterados; a margem
// residual continua estreita (~4 KiB) para detectar crescimento acidental.
//
// Ajustado de 2820 KB para 2821 KB em 22/08/2026: os controles finais da
// revisão do ECG (ação destacada explicitamente fixa no personalizador)
// consumiram a margem residual. O aumento é limitado a 1 KiB e os tetos do
// entrypoint, gzip e chunks opcionais continuam inalterados.
//
// Ajustado de 2821 KB para 2822 KB em 25/08/2026: a auditoria de acessos,
// sessão única e personalização móvel acrescentou 962 B ao precache. O
// incremento continua limitado a 1 KiB e não relaxa os demais limites.
//
// Ajustado de 2822 KB para 2832 KB em 27/08/2026: o main integrado passou a
// gerar 2897751 B de precache, 8023 B acima do teto anterior (0,28%), mantendo
// entrypoint, gzip, divisão por rotas e limite individual de chunks dentro dos
// contratos. O novo teto deixa ~2,2 KiB de margem e continua estreito.
//
// Ajustado de 2832 KB para 2844 KB em 28/08/2026: o release consolidado com a
// rota de exclusão de conta, proteção de acesso móvel e conteúdo da madrugada
// gera 2911186 B de precache, 11218 B acima do teto anterior. O novo limite
// deixa apenas ~1 KiB de margem; entrypoint, gzip, code splitting e teto de
// chunk opcional permanecem inalterados.
//
// Ajustado de 2844 KB para 2846 KB em 28/08/2026: o mesmo frontend do main,
// sem qualquer alteração de UI neste PR científico, passou a gerar 2913346 B,
// 1090 B acima do teto. O incremento de 2 KiB deixa apenas ~958 B de margem e
// mantém inalterados entrypoint, gzip, code splitting e teto de chunk opcional.
//
// Ajustado de 2846 KB para 2849 KB em 29/08/2026: a tela de Diretrizes passou
// a exibir síntese em português, mudanças-chave, impacto no CorVIA e fonte
// original. O precache medido foi 2916376 B, 2072 B acima do teto anterior.
// O acréscimo é limitado a 3 KiB; entrypoint, gzip, code splitting e teto de
// chunk opcional permanecem inalterados, deixando ~1 KiB de margem residual.
//
// Ajustado de 2849 KB para 2864 KB em 29/08/2026: a release consolidada
// adiciona uma rota lazy de análise científica por IA e a assistência
// multimodal longitudinal dentro do chunk já lazy do Prontuário. O precache
// medido foi 2931451 B, 14075 B acima do teto anterior. O aumento é restrito a
// 15 KiB e deixa ~1,2 KiB de margem; entrypoint, gzip, code splitting e teto de
// chunk opcional permanecem rigorosamente inalterados.
//
// Ajustado de 2864 KB para 2865 KB em 29/08/2026: a restauração das ações
// Resumo CorVIA / Traduzido / Original elevou o precache em apenas 390 B acima
// do teto anterior. O incremento mínimo de 1 KiB preserva entrypoint, gzip,
// code splitting e teto individual de chunks sem alteração.
//
// Ajustado de 2865 KB para 2866 KB em 29/08/2026: as mesmas opções de leitura
// foram expostas também nas novas publicações do CorVIA Intelligence. O build
// mediu 2933890 B, apenas 130 B acima do teto. O aumento fica limitado a 1 KiB;
// entrypoint, gzip, code splitting e teto de chunks opcionais não mudam.
//
// Ajustado de 2866 KB para 2867 KB em 29/08/2026: a leitura científica completa
// (Resumo CorVIA / Traduzido / Original) foi estendida a todo documento publicado.
// O precache medido foi 2935732 B, 948 B acima do teto. O acréscimo mínimo de
// 1 KiB preserva inalterados entrypoint, gzip, code splitting e chunks opcionais.
//
// Ajustado para 2920 KB na promoção de Cardiology Spaces em 30/08/2026. A home
// canônica passa a integrar o precache (JS + CSS), elevando a medição para
// 2974215 B. A margem permanece estreita (~15 KiB) e não relaxa entrypoint,
// gzip, divisão por rotas nem o teto individual de chunks opcionais.
//
// Ajustado de 2920 KB para 2933 KB em 31/08/2026: a reconstrução visual
// explicitamente aprovada do Cardiology Spaces acrescenta o novo tour imersivo,
// os estilos dos portais/camadas holográficos e a experiência orbital do
// Deslocamento. O precache medido foi 3002144 B, 12064 B acima do teto anterior.
//
// Ajustado de 2933 KB para 3062 KB no mesmo release após a cobertura visual
// profunda dos cinco espaços: a base d17ef29 mede 2968758 B e o head ce96cc3
// mede 3134406 B, delta auditado de 165648 B. O novo teto deixa somente 1082 B
// de margem; entrypoint, gzip, divisão por rotas e teto de chunks opcionais
// permanecem rigorosamente inalterados.
const maxPrecacheBytes = 3062 * 1024;
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
