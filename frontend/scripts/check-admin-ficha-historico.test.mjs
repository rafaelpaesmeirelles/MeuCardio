import { test } from "node:test";
import assert from "node:assert/strict";
import { validateAdminFichaContrast, validateHistoricoRendering } from "./check-admin-ficha-historico.mjs";

const TOKENS_CSS = `
:root {
  --slate-950: #16242c;
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
.admin-ficha__decisao { color: var(--texto); background: var(--superficie-suave, #f4f7f8); }
.admin-ficha__historico-detalhe { color: var(--texto); background: var(--superficie-suave, #f4f7f8); }
.admin-visualizador__painel { color: var(--texto); background: var(--white); }
`;
}

test("passa quando toda superfície clara tem color explícito e contraste adequado", () => {
  const failures = validateAdminFichaContrast(cssValido(), TOKENS_CSS);
  assert.deepEqual(failures, []);
});

test("acusa ausência de color explícito em superfície clara (o bug real de 14/08/2026)", () => {
  const css = cssValido().replace(
    ".admin-ficha__historico-detalhe { color: var(--texto); background: var(--superficie-suave, #f4f7f8); }",
    ".admin-ficha__historico-detalhe { background: var(--superficie-suave, #f4f7f8); }",
  );
  const failures = validateAdminFichaContrast(css, TOKENS_CSS);
  assert.ok(failures.some((f) => f.includes(".admin-ficha__historico-detalhe") && f.includes("herda")));
});

test("acusa contraste insuficiente mesmo com color declarado", () => {
  const css = cssValido().replace(
    ".admin-ficha__cabecalho { color: var(--texto); background: var(--superficie); }",
    ".admin-ficha__cabecalho { color: #f1fbfc; background: var(--superficie); }",
  );
  const failures = validateAdminFichaContrast(css, TOKENS_CSS);
  assert.ok(failures.some((f) => f.includes(".admin-ficha__cabecalho") && f.includes("4.5:1")));
});

test("acusa regra ausente do arquivo", () => {
  const failures = validateAdminFichaContrast(
    ".admin-ficha__cabecalho { color: var(--texto); background: var(--superficie); }",
    TOKENS_CSS,
  );
  assert.ok(failures.some((f) => f.includes(".admin-assinantes__tabela-wrap")));
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
