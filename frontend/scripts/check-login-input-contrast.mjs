import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

// Guarda de regressão para o bug corrigido em 13/08/2026: os campos de
// e-mail/senha em /entrar (.login .login-formulario input) tinham
// color:#f1fbfc (quase branco) herdado do desenho escuro original desta
// seção; em autofill do Chrome/Samsung Internet/Safari (credencial salva) e
// em alguns navegadores móveis, o fundo passava a ser claro — texto quase
// invisível. A correção original acrescentou uma segunda declaração do
// MESMO seletor (.login .login-formulario input), mais abaixo no arquivo,
// com fundo branco e texto navy escuro, inclusive sob autofill
// (-webkit-text-fill-color, já que `color` sozinho não tem efeito em campo
// autofilled no WebKit) — o CSS resolve por ORDEM DE DECLARAÇÃO quando a
// especificidade empata, então a segunda declaração vence.
//
// Generalizada em 14/08/2026: a regra corrigida deixou de ser escopada a
// `.login.login--entrar` — qualquer tela que reaproveite `.login-formulario`
// (ex.: /solicitar-acesso) herda a correção automaticamente, sem precisar
// de uma variante nova a cada página. Cobre também `<select>`, que a versão
// de 13/08/2026 não precisava tratar (só /entrar tem `<input>`) mas as
// telas com mais campos têm.
//
// Este script NÃO reimplementa um motor de CSS — extrai as declarações da
// última ocorrência do seletor por texto, resolve tokens simples (var(--x))
// contra tokens.css, e calcula o contraste WCAG entre `color` e `background`
// (ou -webkit-text-fill-color/-webkit-box-shadow, sob autofill), para pegar
// qualquer regressão de texto claro sobre fundo claro — não só a
// reintrodução literal dos valores antigos.

const cssPath = new URL("../src/styles/public-clinical-command-v2.css", import.meta.url);
const tokensPath = new URL("../src/styles/tokens.css", import.meta.url);

function resolverTokens(source) {
  const tokens = new Map();
  for (const m of source.matchAll(/--([\w-]+)\s*:\s*([^;]+);/g)) {
    tokens.set(`--${m[1]}`, m[2].trim());
  }
  return tokens;
}

function resolverCor(valor, tokens) {
  const m = /var\(\s*(--[\w-]+)\s*\)/.exec(valor);
  if (!m) return valor.trim();
  const resolvido = tokens.get(m[1]);
  return resolvido ? resolverCor(resolvido, tokens) : valor.trim();
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

/** Extrai o corpo `{ ... }` de um seletor exato dentro do CSS (primeira
 * ocorrência), tolerando quebra de linha, espaçamento livre, e o seletor
 * sendo um entre vários separados por vírgula compartilhando o mesmo corpo
 * (ex.: a própria regra de :-webkit-autofill/:hover/:focus). */
function corpoDoSeletor(css, seletorLiteral) {
  // A ÚLTIMA ocorrência, não a primeira: o CSS resolve por ordem de
  // declaração quando a especificidade empata, e este arquivo tem
  // propositalmente duas declarações do mesmo seletor (a escura original,
  // mais acima, e a correção, mais abaixo) — pegar a primeira checaria a
  // regra errada, a que o próprio bug corrigido em 13/08/2026 mostrou que
  // nunca vale de fato.
  const escapado = seletorLiteral.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const re = new RegExp(`${escapado}\\s*(?:,[^{]*)?\\{([^}]*)\\}`, "g");
  const ocorrencias = [...css.matchAll(re)];
  return ocorrencias.length ? ocorrencias[ocorrencias.length - 1][1] : null;
}

function declaracao(corpo, propriedade) {
  const re = new RegExp(`(?:^|;)\\s*${propriedade}\\s*:\\s*([^;]+);?`);
  return re.exec(corpo)?.[1]?.trim() ?? null;
}

export function validateLoginInputContrast(css, tokensCss) {
  const failures = [];
  const tokens = resolverTokens(tokensCss);

  const corpoBase = corpoDoSeletor(css, ".login .login-formulario input");
  if (!corpoBase) {
    failures.push(
      "não encontrei a regra .login .login-formulario input — precisa ser mais " +
        "específica que .login .login-formulario input para vencer a cascata de forma definitiva",
    );
    return failures;
  }

  const cor = declaracao(corpoBase, "color");
  const fundo = declaracao(corpoBase, "background");
  const fillColor = declaracao(corpoBase, "-webkit-text-fill-color");
  const caret = declaracao(corpoBase, "caret-color");

  if (!cor || !fundo) {
    failures.push(".login .login-formulario input precisa declarar `color` e `background`");
  } else {
    const corResolvida = resolverCor(cor, tokens);
    const fundoResolvido = resolverCor(fundo, tokens);
    if (/^#/.test(corResolvida) && /^#/.test(fundoResolvido)) {
      const razao = contraste(corResolvida, fundoResolvido);
      if (razao < 4.5) {
        failures.push(
          `contraste entre color (${corResolvida}) e background (${fundoResolvido}) é ${razao.toFixed(2)}:1 — ` +
            "abaixo do mínimo WCAG AA de 4.5:1 para texto normal; o texto digitado ficaria pouco ou nada legível",
        );
      }
    }
  }

  if (!fillColor) {
    failures.push(
      "falta -webkit-text-fill-color na regra base — sem ele, `color` sozinho não é respeitado pelo WebKit " +
        "quando o campo estiver em modo de composição/seleção em alguns navegadores",
    );
  } else if (cor && resolverCor(fillColor, tokens) !== resolverCor(cor, tokens)) {
    failures.push("-webkit-text-fill-color deveria resolver para a mesma cor que `color`");
  }

  if (!caret) {
    failures.push("falta caret-color visível na regra base (cursor precisa ser identificável, teal ou navy)");
  }

  const corpoPlaceholder = corpoDoSeletor(css, ".login .login-formulario input::placeholder");
  if (!corpoPlaceholder) {
    failures.push("falta a regra ::placeholder correspondente, com cor secundária visível");
  } else if (!declaracao(corpoPlaceholder, "-webkit-text-fill-color")) {
    failures.push("::placeholder também precisa de -webkit-text-fill-color (mesmo motivo do campo em si)");
  }

  const corpoAutofill = corpoDoSeletor(css, ".login .login-formulario input:-webkit-autofill");
  if (!corpoAutofill) {
    failures.push(
      "falta tratamento de :-webkit-autofill — é o gatilho mais comum do bug real (credencial salva no " +
        "Chrome/Samsung Internet/Safari substitui o fundo do campo, e `color` normal não sobrescreve o texto " +
        "autofilled)",
    );
  } else {
    if (!declaracao(corpoAutofill, "-webkit-text-fill-color")) {
      failures.push(":-webkit-autofill precisa de -webkit-text-fill-color explícito");
    }
    const boxShadow = declaracao(corpoAutofill, "-webkit-box-shadow");
    if (!boxShadow || !/inset/.test(boxShadow)) {
      failures.push(
        ":-webkit-autofill precisa de -webkit-box-shadow ... inset — é a técnica padrão para sobrescrever o " +
          "fundo que o navegador força em campo autofilled",
      );
    }
  }

  return failures;
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1]);

if (isMain) {
  const [css, tokensCss] = await Promise.all([
    readFile(fileURLToPath(cssPath), "utf8"),
    readFile(fileURLToPath(tokensPath), "utf8"),
  ]);
  const failures = validateLoginInputContrast(css, tokensCss);
  if (failures.length) {
    console.error("Falha no contrato de contraste do login (/entrar):\n");
    for (const failure of failures) console.error(`- ${failure}`);
    process.exit(1);
  }
  console.log("Contraste do login: campos de e-mail/senha legíveis, inclusive sob autofill, sem regressão.");
}
