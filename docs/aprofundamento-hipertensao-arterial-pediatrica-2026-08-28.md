# Aprofundamento Tudo com Tudo — Hipertensão arterial pediátrica — 28/08/2026

## Contexto

Quinto lote de aprofundamento do dia (após `doenca-coronariana-idoso`,
PR #603; `valva-aortica-bicuspide-pediatrica`, PR #604; `hipotensao-
ortostatica-no-idoso`, PR #606; `sopros-na-infancia`, PR #608). A ficha
`hipertensao-arterial-pediatrica` (área `cardiopediatria`,
`prevalence_rank: 1` — a condição mais prevalente da categoria) já tinha
`differentials`, `tests`, `red_flags`, `ambulatory_flow`, `emergency_flow`,
`monitoring`, `assistant_questions` e `assistant_rules` razoáveis, mas
`epidemiology` (1 frase, 154 caracteres) e `treatment_summary` (234
caracteres) eram claramente rasos, `presentation` tinha só 3 itens, e
`diagnostic_approach`, `special_populations` e `related_document_slugs`
estavam inteiramente ausentes.

## Conteúdo produzido

Produzido por 2 agentes de pesquisa em paralelo, com instrução explícita
para não tocar nos campos já bons:

1. **Epidemiologia, apresentação e diagnóstico** — `epidemiology`
   expandida (prevalência real 4-5% geral, 10-30% em obesidade,
   subdiagnóstico <3% em atenção primária, hipertrofia ventricular
   esquerda em 30-40% dos hipertensos pediátricos), `presentation`
   expandida (3 → 9 itens por faixa etária), `diagnostic_approach` criado
   (4 subtópicos: técnica de aferição, definição por percentil vs. limiar
   fixo AAP 2017, indicações de MAPA, investigação de causa secundária
   por idade).
2. **Tratamento, populações e conexões** — `treatment_summary` expandido
   (critérios objetivos de início de fármaco, classes de primeira linha
   só por nome, meta terapêutica diferenciada por idade),
   `special_populations` criado (7 itens: recém-nascido, obesidade,
   DRC, atleta, apneia do sono, síndromes genéticas, coarctação),
   `related_document_slugs` criado (6 documentos).

## Correções e verificações feitas na montagem

- Todos os 6 `related_document_slugs` verificados individualmente —
  confirmada menção explícita a "hipertens" no texto de cada um.
- **3 dos 6 documentos compartilhados** com fichas já publicadas:
  `hipertensao-arterial-sistemica-na-crianca-...` e `sindrome-de-turner-
  na-crianca-...` (também em `coarctacao-da-aorta`); `coarctacao-de-
  aorta-na-crianca-...` (também em `coarctacao-da-aorta` e `coarctacao-
  aorta-fetal`) — mantidos por serem genuína e centralmente relevantes
  também à hipertensão pediátrica (coarctação é causa clássica de
  hipertensão secundária/residual; síndrome de Turner tem prevalência de
  HAS 3-4x maior que a população geral).
- `patient_material_slug` permanece `null` — nenhum material voltado a
  paciente/família especificamente sobre HAS pediátrica foi encontrado no
  corpus hoje (verificado em `material-paciente/metadados.json`).

Nenhuma dose de fármaco em nenhum campo — verificado programaticamente.
Estrutura de perguntas e regras já existente reverificada contra o motor
de regras real, sem alteração.

## Catalogação e conteúdo prévio preservados

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`,
`differentials`, `tests`, `red_flags`, `ambulatory_flow`,
`emergency_flow`, `monitoring`, `assistant_questions`, `assistant_rules`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada, então ainda não tinha a correção de allowlist em
`test_disease_fragments_canonical.py`. Apliquei aqui a mesma correção já
aprovada pelo Rafael no PR #606.

## Fontes primárias

10 referências novas, com PMID verificado, incluindo a diretriz AAP 2017
completa (Flynn et al., Pediatrics), a declaração científica AHA 2023
sobre hipertensão primária pediátrica, e a metanálise global de
prevalência (Song et al., JAMA Pediatrics 2019).

## Coordenação com Codex

Nenhum dos 29 PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `hipertensao-arterial-pediatrica`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug` permanece `null`.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_hipertensao_arterial_pediatrica.py`:
  11 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist unificada).
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-hipertensao-arterial-pediatrica-20260828`,
baseada em `origin/main` (`64db98f8`) sem drift no momento do commit.
