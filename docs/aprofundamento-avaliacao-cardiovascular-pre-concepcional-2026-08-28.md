# Aprofundamento Tudo com Tudo — Avaliação cardiovascular pré-concepcional — 28/08/2026

## Contexto

Trigésimo segundo lote de conteúdo do dia. A ficha
`avaliacao-cardiovascular-pre-concepcional` (área `gravidez`, categoria
`planejamento_reprodutivo`, `prevalence_rank: 1`) estava rotulada
`completeness: completo`, mas na prática rasa: já tinha `presentation`
(2), `differentials` (3), `tests` (4), `red_flags` (5),
`ambulatory_flow` (4), `emergency_flow` (1), `assistant_questions` (6),
`assistant_rules` (6) — mas zero `epidemiology`, `diagnostic_approach`,
`treatment_summary`, `monitoring`, `special_populations` e
`related_document_slugs` (1 `source_ref`). Rótulo inconsistente
descoberto durante auditoria do corpus.

## Conteúdo produzido

Todo o conteúdo clínico pré-existente foi preservado sem alteração.
Adicionado apenas o que faltava:

- `epidemiology`: aumento de mulheres com cardiopatia em idade fértil,
  doença cardiovascular como principal causa de morbimortalidade
  materna indireta em vários registros, lacuna entre recomendação
  formal e prática clínica real.
- `diagnostic_approach`: 6 etapas (revisão diagnóstica completa,
  classificação de risco mWHO 2.0 — citada por nome sem reproduzir
  critérios, por restrição de licenciamento já registrada no
  `review_note` original da ficha —, avaliação funcional, revisão de
  medicamentos, aconselhamento genético, definição de Pregnancy Heart
  Team).
- `treatment_summary`: 5 eixos (otimização clínica pré-concepcional,
  revisão medicamentosa sem doses, discussão de risco materno/fetal,
  aconselhamento contraceptivo, plano de acompanhamento antecipado).
- `monitoring` (7 itens).
- `special_populations` (8 itens).
- `related_document_slugs` (3, do zero).

## Verificação de citações

Todos os 6 PMIDs desta rodada foram verificados individualmente via
NCBI e-utils antes da montagem — todas as referências corretas quanto
a título/periódico/ano/volume/páginas, incluindo a diretriz ESC 2025 e
seu "Ten Commandments" companheiro, o AHA scientific statement sobre
cardiopatia congênita complexa e gravidez, o estudo CARPREG II, e o
registro ROPAC/ESC.

## Verificações feitas na montagem

- Os 3 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema no texto — todos com seção dedicada ao Pregnancy Heart Team/
  aconselhamento pré-concepcional, confirmada por leitura de trecho.
- **Overlap pré-existente e legítimo**: `classificacao-de-risco-mwho-
  2-0-na-gravidez-esc-2025` também vinculado por
  `valva-aortica-bicuspide-pediatrica` — documentado.
- Todo o conteúdo clínico pré-existente (presentation, differentials,
  tests, red_flags, ambulatory_flow, emergency_flow,
  assistant_questions, assistant_rules) confirmado como preservado sem
  alteração por asserção explícita no `assemble.py` e por teste
  dedicado.

Nenhuma dose de fármaco em nenhum campo. A sigla "mWHO" aparece em
`diagnostic_approach` e `monitoring` apenas citando o nome da
classificação de risco vigente (mesmo padrão já usado no
`review_note` original da ficha) — nunca em `assistant_rules` nem
`special_populations`, escopo real do gate de compliance, verificado
por teste dedicado.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `prevalence_rank` originais
preservados sem alteração.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_avaliacao_cardiovascular_pre_concepcional.py`:
  11 testes, todos passando (1 correção durante desenvolvimento, para
  documentar overlap pré-existente descoberto pelo próprio teste).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando, 6 testes.
- `app.main` importa sem erro.
- Total: 17 testes executados, 17 passando.

## Branch e PR

Branch `claude/vincular-tudo-com-tudo-avaliacao-cardiovascular-pre-concepcional-20260828`,
baseada em `origin/main` sem drift no momento do commit.
