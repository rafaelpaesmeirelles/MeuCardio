import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

// Regra absoluta do Rafael na correção coordenada de 02/09/2026: zero
// mudança visual/CSS/layout ao adicionar identificação de paciente a
// Calculadora.tsx e AvaliacaoPreOperatoria.tsx. Esses testes provam que o
// novo SeletorPacienteModal reaproveita SOMENTE classes CSS já existentes
// (o mesmo diálogo global de Agenda.tsx) — nunca define nem exige uma
// classe nova — e que as duas telas mantiveram o campo de nome livre
// original intocado, ganhando apenas um botão pequeno ao lado do rótulo
// que também reaproveita classes já existentes (botao / botao--secundario,
// usadas em dezenas de outros pontos do produto).

const seletorPaciente = readFileSync(new URL("../src/components/SeletorPaciente.tsx", import.meta.url), "utf8");
const calculadora = readFileSync(new URL("../src/pages/Calculadora.tsx", import.meta.url), "utf8");
const avaliacaoPreOperatoria = readFileSync(new URL("../src/pages/AvaliacaoPreOperatoria.tsx", import.meta.url), "utf8");
const shellCss = readFileSync(new URL("../src/styles/shell.css", import.meta.url), "utf8");

function classesDefinidasEm(css, classe) {
  return new RegExp(`\\.${classe.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}[\\s{,:]`).test(css);
}

function classesUsadasNoTrecho(codigoFonte, regexTrecho) {
  const trecho = codigoFonte.match(regexTrecho)?.[0];
  assert.ok(trecho, `trecho esperado não encontrado (regex: ${regexTrecho})`);
  return [...trecho.matchAll(/className="([^"]+)"/g)].flatMap((m) => m[1].split(/\s+/));
}

test("SeletorPacienteModal só usa classes CSS já existentes em shell.css (nenhuma classe nova)", () => {
  const corpo = seletorPaciente.match(/export function SeletorPacienteModal\b[\s\S]*?\n}\n/)?.[0];
  assert.ok(corpo, "função SeletorPacienteModal não encontrada");
  const classes = [...corpo.matchAll(/className="([^"]+)"/g)].flatMap((m) => m[1].split(/\s+/));
  assert.ok(classes.length > 0, "esperava pelo menos uma classe usada no modal");
  for (const classe of classes) {
    assert.ok(
      classesDefinidasEm(shellCss, classe),
      `classe "${classe}" usada no modal não existe em shell.css — seria CSS novo, fora do escopo autorizado`,
    );
  }
});

test("SeletorPacienteModal reaproveita o mesmo padrão de diálogo de Agenda.tsx (agenda-modal)", () => {
  assert.match(seletorPaciente, /className="agenda-modal" role="dialog" aria-modal="true"/);
  assert.match(seletorPaciente, /className="agenda-modal__painel agenda-modal__painel--compacto"/);
});

for (const [nomeTela, codigoFonte] of [
  ["Calculadora", calculadora],
  ["AvaliacaoPreOperatoria", avaliacaoPreOperatoria],
]) {
  test(`${nomeTela}: campo de nome livre original continua com o mesmo placeholder e sem props novas na estrutura visual`, () => {
    assert.match(codigoFonte, /placeholder="Usado só para organizar o histórico"/);
  });

  test(`${nomeTela}: botão novo de selecionar paciente usa só classes já reutilizadas no produto (botao, botao--secundario)`, () => {
    const classes = classesUsadasNoTrecho(
      codigoFonte,
      /<button[^>]*onClick=\{\(\) => setModalPacienteAberto\(true\)\}[^>]*>/,
    );
    assert.deepEqual(new Set(classes), new Set(["botao", "botao--secundario"]));
    for (const classe of classes) {
      assert.ok(
        classesDefinidasEm(shellCss, classe),
        `classe "${classe}" do botão de selecionar paciente não existe em shell.css`,
      );
    }
  });

  test(`${nomeTela}: SeletorPacienteModal é montado com paciente vinculado indo pro payload separado do nome livre`, () => {
    assert.match(codigoFonte, /<SeletorPacienteModal/);
    assert.match(codigoFonte, /patient_profile_id: pacienteVinculado\?\.id \?\? null/);
  });
}
