import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

// Guarda de regressão para o bug corrigido em 14/08/2026, na ficha do
// assinante (Admin → Assinantes → ficha → aba "Histórico"):
//
// 1) Contraste — admin-assinantes.css foi escrito assumindo o tema claro
//    antigo (texto escuro ambiente), mas a página é renderizada dentro do
//    shell escuro .clinical-os, cujo `color` ambiente é quase branco.
//    Qualquer contêiner de fundo claro (--superficie/--superficie-suave/
//    --white/--slate-100) sem `color` explícito herdava esse branco por
//    cima de fundo claro — texto só perceptível ao selecionar.
// 2) Renderização — o campo `detail` do histórico (JSON livre, por ação)
//    era despejado cru com `JSON.stringify` dentro de um <pre>, em vez de
//    aparecer como lista rotulada (chave: valor) legível para quem não é
//    desenvolvedor.
//
// Este script não reimplementa um motor de CSS nem um parser de JSX — extrai
// declarações por regex (mesma técnica de check-login-input-contrast.mjs) e
// verifica a fonte de AdminFichaAssinante.tsx por padrão estático.

const cssPath = new URL("../src/styles/admin-assinantes.css", import.meta.url);
const tokensPath = new URL("../src/styles/tokens.css", import.meta.url);
const tsxPath = new URL("../src/pages/AdminFichaAssinante.tsx", import.meta.url);

function resolverTokens(source) {
  const tokens = new Map();
  for (const m of source.matchAll(/--([\w-]+)\s*:\s*([^;]+);/g)) {
    tokens.set(`--${m[1]}`, m[2].trim());
  }
  return tokens;
}

function resolverCor(valor, tokens, profundidade = 0) {
  if (profundidade > 5) return valor.trim();
  const m = /var\(\s*(--[\w-]+)\s*(?:,\s*([^)]+))?\)/.exec(valor);
  if (!m) return valor.trim();
  const resolvido = tokens.get(m[1]) ?? m[2];
  return resolvido ? resolverCor(resolvido, tokens, profundidade + 1) : valor.trim();
}

function hexParaRgb(hex) {
  const limpo = hex.replace("#", "");
  const seis = limpo.length === 3 ? limpo.split("").map((c) => c + c).join("") : limpo;
  const num = parseInt(seis, 16);
  return { r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 };
}

function luminanciaRelativa({ r, g, b }) {
  const canal = (c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b);
}

function contraste(hexA, hexB) {
  const la = luminanciaRelativa(hexParaRgb(hexA));
  const lb = luminanciaRelativa(hexParaRgb(hexB));
  const [claro, escuro] = la > lb ? [la, lb] : [lb, la];
  return (claro + 0.05) / (escuro + 0.05);
}

function corpoDoSeletor(css, seletorLiteral) {
  const escapado = seletorLiteral.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const re = new RegExp(`${escapado}\\s*(?:,[^{]*)?\\{([^}]*)\\}`);
  return re.exec(css)?.[1] ?? null;
}

function declaracao(corpo, propriedade) {
  const re = new RegExp(`(?:^|;)\\s*${propriedade}\\s*:\\s*([^;]+);?`);
  return re.exec(corpo)?.[1]?.trim() ?? null;
}

// Cada contêiner de fundo claro desta ficha que precisa de `color` escuro
// explícito — a lista é exaustiva, não um exemplo: qualquer novo bloco de
// fundo claro acrescentado a este arquivo deveria entrar aqui também.
const SUPERFICIES_CLARAS = [
  ".admin-assinantes__tabela-wrap",
  ".admin-ficha__cabecalho",
  ".admin-ficha__decisao",
  ".admin-ficha__historico-detalhe",
  ".admin-visualizador__painel",
];

export function validateAdminFichaContrast(css, tokensCss) {
  const failures = [];
  const tokens = resolverTokens(tokensCss);

  for (const seletor of SUPERFICIES_CLARAS) {
    const corpo = corpoDoSeletor(css, seletor);
    if (!corpo) {
      failures.push(`não encontrei a regra ${seletor} em admin-assinantes.css`);
      continue;
    }
    const cor = declaracao(corpo, "color");
    const fundo = declaracao(corpo, "background");
    if (!cor) {
      failures.push(
        `${seletor} declara um fundo claro sem \`color\` explícito — herda o texto quase-branco ` +
          "ambiente do shell .clinical-os, ficando ilegível sobre este fundo claro",
      );
      continue;
    }
    if (!fundo) continue; // sem fundo próprio declarado nesta regra — nada a conferir aqui
    const corResolvida = resolverCor(cor, tokens);
    const fundoResolvido = resolverCor(fundo, tokens);
    if (/^#/.test(corResolvida) && /^#/.test(fundoResolvido)) {
      const razao = contraste(corResolvida, fundoResolvido);
      if (razao < 4.5) {
        failures.push(
          `${seletor}: contraste entre color (${corResolvida}) e background (${fundoResolvido}) é ` +
            `${razao.toFixed(2)}:1 — abaixo do mínimo WCAG AA de 4.5:1`,
        );
      }
    }
  }

  return failures;
}

// Corpo de uma função exportada/declarada, por contagem de chaves (mais
// confiável que regex para JSX/TS aninhado, mesmo padrão de
// check-camera-lifecycle.mjs).
function corpoDaFuncao(source, nomeFuncao) {
  // O match da regex já termina no `{` de abertura do CORPO da função — usar
  // `match.index + match[0].length - 1` (não um `indexOf("{")` separado a
  // partir do início do match), porque parâmetro desestruturado
  // (`{ historico }`) também contém `{`/`}` antes do corpo, e um
  // `indexOf` ingênuo pega essa chave errada, cortando o corpo pela metade.
  const match = new RegExp(`function ${nomeFuncao}\\s*\\([^)]*\\)[^{]*\\{`).exec(source);
  if (!match) return null;
  const abre = match.index + match[0].length - 1;
  let profundidade = 0;
  for (let i = abre; i < source.length; i++) {
    if (source[i] === "{") profundidade++;
    else if (source[i] === "}") {
      profundidade--;
      if (profundidade === 0) return source.slice(abre, i + 1);
    }
  }
  return null;
}

export function validateHistoricoRendering(tsx) {
  const failures = [];

  if (/JSON\.stringify\([^)]*\)\s*\}\s*<\/pre>/.test(tsx) || /<pre[^>]*>\s*\{?\s*JSON\.stringify/.test(tsx)) {
    failures.push(
      "encontrei JSON.stringify(...) renderizado dentro de <pre> — é exatamente o dump cru que o bug " +
        "de 14/08/2026 reportava; o detalhe do histórico precisa passar por DetalheHistorico (chave/valor " +
        "rotulado), não ser despejado literalmente",
    );
  }

  const corpoAba = corpoDaFuncao(tsx, "AbaHistorico");
  if (!corpoAba) {
    failures.push("não encontrei a função AbaHistorico em AdminFichaAssinante.tsx");
  } else {
    if (!/historico\.length === 0/.test(corpoAba)) {
      failures.push("AbaHistorico precisa tratar o caso de lista vazia explicitamente, com texto visível");
    }
    if (!/DetalheHistorico/.test(corpoAba)) {
      failures.push(
        "AbaHistorico precisa delegar a renderização de `detail` a um componente formatador " +
          "(DetalheHistorico) em vez de montar o dump diretamente no JSX",
      );
    }
  }

  const corpoDetalhe = corpoDaFuncao(tsx, "DetalheHistorico");
  if (!corpoDetalhe) {
    failures.push("não encontrei o componente DetalheHistorico — necessário para formatar `detail` em chave/valor");
  } else {
    if (!/humanizarChaveDetalhe/.test(corpoDetalhe)) {
      failures.push("DetalheHistorico precisa humanizar o nome de cada chave, não mostrar o snake_case cru");
    }
    if (!/<dt>|<dd>/.test(corpoDetalhe)) {
      failures.push("DetalheHistorico precisa de uma estrutura rotulada (dt/dd), não texto solto");
    }
  }

  return failures;
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1]);

if (isMain) {
  const [css, tokensCss, tsx] = await Promise.all([
    readFile(fileURLToPath(cssPath), "utf8"),
    readFile(fileURLToPath(tokensPath), "utf8"),
    readFile(fileURLToPath(tsxPath), "utf8"),
  ]);
  const failures = [
    ...validateAdminFichaContrast(css, tokensCss),
    ...validateHistoricoRendering(tsx),
  ];
  if (failures.length) {
    console.error("Falha no contrato da ficha do assinante (aba Histórico e superfícies claras):\n");
    for (const failure of failures) console.error(`- ${failure}`);
    process.exit(1);
  }
  console.log("Ficha do assinante: contraste das superfícies claras e histórico legível, sem regressão.");
}
