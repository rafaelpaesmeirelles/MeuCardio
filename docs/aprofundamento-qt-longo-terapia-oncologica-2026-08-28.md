# Aprofundamento Tudo com Tudo — Prolongamento do QT em terapia oncológica — 28/08/2026

## Contexto

Trigésimo nono lote de conteúdo do dia. A ficha
`qt-longo-terapia-oncologica` (área `cardiooncologia`, categoria
`arritmia`, `prevalence_rank: 12`) estava `completeness: basico`, só
catalogação (1 `source_ref`: ESC 2022), zero campos clínicos. Terceira
ficha desbloqueada hoje pela reavaliação de escopo da PR #551.

## Conteúdo produzido

- `epidemiology`: prolongamento de QT transversal a múltiplas classes
  (CDK4/6/ribociclibe, trióxido de arsênio — praticamente universal —,
  inibidores de tirosina-quinase, revumenibe/inibidor de menina).
- `presentation` (10), `diagnostic_approach` (cálculo de QTc por
  Fridericia/Bazett, cronograma de ECG seriado específico por classe,
  fatores de risco somados), `differentials` (7), `tests` (9),
  `red_flags` (8).
- `treatment_summary`: abordagem preventiva central (ECG basal +
  correção de eletrólitos + revisão de polifarmácia QT), conduta
  bifurcada conforme sintomas, torsades de pointes como emergência
  verdadeira, sem doses, alerta explícito contra banalizar ou
  superdimensionar o risco.
- `ambulatory_flow` (10), `emergency_flow` (8), `monitoring` (7).
- `special_populations` (7) — incluindo indução de leucemia com
  múltiplos fatores QT somados.
- `assistant_questions` (13), `assistant_rules` (10, priority 100 para
  torsades confirmada, 98 para parada cardiorrespiratória).
- `related_document_slugs` (6, do zero).

## Verificação de citações

Todos os 7 PMIDs desta rodada foram verificados individualmente via
NCBI e-utils antes da montagem — todas as referências corretas,
incluindo o estudo clássico de Ohnishi et al. (2000) sobre trióxido de
arsênio, a revisão sistemática de Porta-Sánchez et al. (2017), e os
dois estudos AUGMENT-101 mais recentes sobre revumenibe (2025).

## Verificações feitas na montagem

- Os 6 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema no texto — todos confirmados como centrais por leitura de
  trecho (ribociclibe + fluxograma, trióxido de arsênio + fluxograma,
  revumenibe, lista geral de quimioterápicos QT).
- O agente da Parte 3 verificou 5 candidatos adicionais via grep amplo
  em `content/Cardio-oncologia` e confirmou que nenhum tem o tema como
  central (menções tangenciais em diagnóstico diferencial ou item de
  checklist).
- `patient_material_slug` confirmado por correspondência direta e
  inequívoca em `material-paciente/metadados.json`.
- **Overlap pré-existente e legítimo**: `lista-de-quimioterapicos-de-
  risco-de-prolongamento-do-qt-...` também vinculado por
  `cardiotoxicidade-bcr-abl` e `cardiotoxicidade-raf-mek` — documentado
  no teste dedicado.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a
chave `label` corretamente.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `prevalence_rank` originais
preservados sem alteração.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap parcial mas documentado com 2 fichas do mesmo tema
  (cardiotoxicidade oncológica com risco de QT).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_qt_longo_terapia_oncologica.py`:
  12 testes, todos passando (1 correção durante desenvolvimento, para
  documentar overlap pré-existente descoberto pelo próprio teste).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando, 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-qt-longo-terapia-oncologica-20260828`,
baseada em `origin/main` sem drift no momento do commit.
