import { test } from "node:test";
import assert from "node:assert/strict";
import { validateAdminFichaContrast, validateHistoricoRendering, validateInlineStyleTokens } from "./check-admin-ficha-historico.mjs";

// --texto/--texto-secundario/--superficie aqui deliberadamente resolvem
// ESCUROS (como em tokens.css puro) — é assim que a primeira versão deste
// checker via o mundo, e é exatamente por que ela deixou passar o bug
// real: em produção, dentro de .clinical-os, uma camada de compatibilidade
// redefine esses MESMOS tokens para o tema escuro (--texto vira quase
// branco). Por isso a validação de SUPERFICIES_SEMPRE_CLARAS não confia
// em resolver o token contra tokens.css — ela rejeita o token ambíguo
// diretamente, qualquer que seja o valor que ele resolva aqui no teste.
const TOKENS_CSS = `
:root {
  --slate-950: #16242c;
  --slate-700: #465b66;
  --texto: var(--slate-950);
  --texto-secundario: #465b66;
  --white: #ffffff;
  --superficie: var(--white);
}
`;

function cssValido() {
  return `
.admin-assinantes__tabela-wrap { color: var(--texto); background: var(--superficie); }
.admin-ficha__cabecalho { color: var(--texto); background: var(--superficie); }
.admin-ficha__decisao { color: var(--slate-950); background: var(--superficie-suave, #f4f7f8); }
.admin-ficha__historico-detalhe { color: var(--slate-950); background: var(--superficie-suave, #f4f7f8); }
.admin-ficha__historico-detalhe-linha dt { color: var(--slate-700); }
.admin-ficha__historico-detalhe-linha dd { margin: 0; color: var(--slate-950); }
.admin-visualizador__painel { color: var(--slate-950); background: var(--white); }
`;
}

test("passa quando toda superfície clara tem color explícito, token seguro e contraste adequado", () => {
  const failures = validateAdminFichaContrast(cssValido(), TOKENS_CSS);
  assert.deepEqual(failures, []);
});

test("acusa ausência de color explícito em superfície clara (o bug real de 14/08/2026)", () => {
  const css = cssValido().replace(
    ".admin-ficha__historico-detalhe { color: var(--slate-950); background: var(--superficie-suave, #f4f7f8); }",
    ".admin-ficha__historico-detalhe { background: var(--superficie-suave, #f4f7f8); }",
  );
  const failures = validateAdminFichaContrast(css, TOKENS_CSS);
  assert.ok(failures.some((f) => f.includes(".admin-ficha__historico-detalhe") && f.includes("herda")));
});

test("acusa token semântico ambíguo (--texto) numa superfície sempre clara — o bug real do PRIMEIRO fix", () => {
  // --texto parece escuro OLHANDO SÓ tokens.css (como no teste acima), mas
  // dentro de .clinical-os em produção ele é redefinido para quase branco
  // — foi exatamente essa a causa raiz do bug que sobreviveu ao primeiro
  // fix (contraste "passava" aqui e continuava quebrado no navegador real).
  const css = cssValido().replace(
    ".admin-ficha__decisao { color: var(--slate-950); background: var(--superficie-suave, #f4f7f8); }",
    ".admin-ficha__decisao { color: var(--texto); background: var(--superficie-suave, #f4f7f8); }",
  );
  const failures = validateAdminFichaContrast(css, TOKENS_CSS);
  assert.ok(failures.some((f) => f.includes(".admin-ficha__decisao") && f.includes("PAPEL semântico")));
});

test("acusa --texto-secundario no rótulo (dt) do detalhe — mesma armadilha do token ambíguo", () => {
  const css = cssValido().replace(
    ".admin-ficha__historico-detalhe-linha dt { color: var(--slate-700); }",
    ".admin-ficha__historico-detalhe-linha dt { color: var(--texto-secundario); }",
  );
  const failures = validateAdminFichaContrast(css, TOKENS_CSS);
  assert.ok(failures.some((f) => f.includes("dt") && f.includes("PAPEL semântico")));
});

test("acusa dd do detalhe sem color explícito — herdar do <dl> não basta (bare `.clinical-os dd` global vence a herança)", () => {
  const css = cssValido().replace(
    ".admin-ficha__historico-detalhe-linha dd { margin: 0; color: var(--slate-950); }",
    ".admin-ficha__historico-detalhe-linha dd { margin: 0; }",
  );
  const failures = validateAdminFichaContrast(css, TOKENS_CSS);
  assert.ok(failures.some((f) => f.includes("dd") && f.includes("herda")));
});

test("--texto continua permitido nas superfícies que acompanham o tema (cabeçalho/tabela)", () => {
  // .admin-ficha__cabecalho e .admin-assinantes__tabela-wrap usam
  // var(--superficie), que a mesma camada de compatibilidade redefine
  // para um painel ESCURO dentro de .clinical-os — ali --texto (também
  // redefinido, também claro) é o par correto, confirmado ao vivo em
  // produção. Não deve ser rejeitado pela mesma regra do grupo 2.
  const failures = validateAdminFichaContrast(cssValido(), TOKENS_CSS);
  assert.deepEqual(failures, []);
});

test("acusa contraste insuficiente mesmo com token bruto declarado", () => {
  const css = cssValido().replace(
    ".admin-ficha__decisao { color: var(--slate-950); background: var(--superficie-suave, #f4f7f8); }",
    ".admin-ficha__decisao { color: #f1fbfc; background: var(--superficie-suave, #f4f7f8); }",
  );
  const failures = validateAdminFichaContrast(css, TOKENS_CSS);
  assert.ok(failures.some((f) => f.includes(".admin-ficha__decisao") && f.includes("4.5:1")));
});

test("acusa regra ausente do arquivo", () => {
  const failures = validateAdminFichaContrast(
    ".admin-ficha__cabecalho { color: var(--texto); background: var(--superficie); }",
    TOKENS_CSS,
  );
  assert.ok(failures.some((f) => f.includes(".admin-assinantes__tabela-wrap")));
});

test("comentário de CSS citando outro seletor em prosa não confunde a extração do corpo real", () => {
  // Bug real encontrado NESTE checker ao escrever os comentários do próprio
  // fix: "mesma ressalva de .admin-ficha__decisao, acima" dentro de um
  // comentário fazia o extrator ler a vírgula como lista de seletores e
  // capturar um trecho arbitrário do arquivo até o próximo "{" real.
  const css = `
.admin-ficha__decisao {
  /* mesma ressalva de .admin-ficha__decisao, acima — não deve confundir o parser */
  color: var(--slate-950);
  background: var(--superficie-suave, #f4f7f8);
}
.admin-ficha__historico-detalhe { color: var(--slate-950); background: var(--superficie-suave, #f4f7f8); }
.admin-ficha__historico-detalhe-linha dt { color: var(--slate-700); }
.admin-ficha__historico-detalhe-linha dd { margin: 0; color: var(--slate-950); }
.admin-visualizador__painel { color: var(--slate-950); background: var(--white); }
.admin-assinantes__tabela-wrap { color: var(--texto); background: var(--superficie); }
.admin-ficha__cabecalho { color: var(--texto); background: var(--superficie); }
`;
  const failures = validateAdminFichaContrast(css, TOKENS_CSS);
  assert.deepEqual(failures, []);
});

const TSX_VALIDO = `
function humanizarChaveDetalhe(chave) { return chave; }
function formatarValorDetalhe(valor) { return String(valor); }

function DetalheHistorico({ detail }) {
  const entradas = Object.entries(detail);
  if (entradas.length === 0) return null;
  return (
    <dl className="admin-ficha__historico-detalhe">
      {entradas.map(([chave, valor]) => (
        <div key={chave}>
          <dt>{humanizarChaveDetalhe(chave)}</dt>
          <dd>{formatarValorDetalhe(valor)}</dd>
        </div>
      ))}
    </dl>
  );
}

function AbaHistorico({ historico }) {
  if (historico.length === 0) {
    return <p>Nenhum evento registrado para este assinante até o momento.</p>;
  }
  return (
    <ul className="admin-ficha__historico">
      {historico.map((h) => (
        <li key={h.id}>
          <p>{rotuloAcao(h.action)}</p>
          {h.detail && <DetalheHistorico detail={h.detail} />}
        </li>
      ))}
    </ul>
  );
}
`;

test("passa com renderização rotulada e estado vazio explícito", () => {
  const failures = validateHistoricoRendering(TSX_VALIDO);
  assert.deepEqual(failures, []);
});

test("acusa dump cru de JSON.stringify dentro de <pre> (o bug real de 14/08/2026)", () => {
  const tsx = `
function AbaHistorico({ historico }) {
  if (historico.length === 0) return null;
  return (
    <ul>
      {historico.map((h) => (
        <li key={h.id}>
          <pre>{JSON.stringify(h.detail, null, 2)}</pre>
        </li>
      ))}
    </ul>
  );
}
`;
  const failures = validateHistoricoRendering(tsx);
  assert.ok(failures.some((f) => f.includes("dump cru")));
});

test("acusa JSON cru dentro do formatador de valores aninhados", () => {
  const tsx = TSX_VALIDO.replace(
    "function formatarValorDetalhe(valor) { return String(valor); }",
    "function formatarValorDetalhe(valor) { return JSON.stringify(valor); }",
  );
  const failures = validateHistoricoRendering(tsx);
  assert.ok(failures.some((f) => f.includes("JSON cru")));
});

test("acusa ausência de tratamento de estado vazio", () => {
  const tsx = TSX_VALIDO.replace(
    'if (historico.length === 0) {\n    return <p>Nenhum evento registrado para este assinante até o momento.</p>;\n  }\n  ',
    "",
  );
  const failures = validateHistoricoRendering(tsx);
  assert.ok(failures.some((f) => f.includes("lista vazia")));
});

test("acusa ausência do formatador DetalheHistorico", () => {
  const tsx = `
function AbaHistorico({ historico }) {
  if (historico.length === 0) return <p>vazio</p>;
  return <ul>{historico.map((h) => <li key={h.id}>{JSON.stringify(h.detail || {})}</li>)}</ul>;
}
`;
  const failures = validateHistoricoRendering(tsx);
  assert.ok(failures.some((f) => f.includes("DetalheHistorico")));
});

test("acusa var(--texto-secundario) inline dentro de PainelDecisaoKyc — mesma armadilha via style inline", () => {
  const tsx = `
function PainelDecisaoKyc() {
  return (
    <div className="admin-ficha__decisao">
      <p style={{ color: "var(--texto-secundario)" }}>Confira os documentos.</p>
    </div>
  );
}
`;
  const failures = validateInlineStyleTokens(tsx);
  assert.ok(failures.some((f) => f.includes("var(--texto-secundario)")));
});

test("passa quando PainelDecisaoKyc usa token bruto no style inline", () => {
  const tsx = `
function PainelDecisaoKyc() {
  return (
    <div className="admin-ficha__decisao">
      <p style={{ color: "var(--slate-700)" }}>Confira os documentos.</p>
    </div>
  );
}
`;
  assert.deepEqual(validateInlineStyleTokens(tsx), []);
});
