# Aprofundamento Tudo com Tudo — Toxicidade cardiovascular por inibidores RAF/MEK — 28/08/2026

## Contexto

Trigésimo oitavo lote de conteúdo do dia. A ficha
`cardiotoxicidade-raf-mek` (área `cardiooncologia`, categoria
`terapia_alvo`, `prevalence_rank: 9`) estava `completeness: basico`, só
catalogação (1 `source_ref`: ESC 2022), zero campos clínicos, mas já
tinha 1 `related_document_slug` e `patient_material_slug` preenchidos.

## Nota de transparência: desbloqueio tardio

Segunda ficha desbloqueada hoje pela mesma reavaliação: esteve bloqueada
o dia todo por suspeita de colisão com a PR #551 aberta, cujo escopo
real mudou ao longo do dia.

## Conteúdo produzido

- `epidemiology`: disfunção ventricular em 5-10% e hipertensão em
  15-30% dos pacientes com terapia combinada BRAF+MEK, mecanismo via
  RAS-RAF-MEK-ERK importante para sobrevivência de cardiomiócitos.
- `presentation` (10), `diagnostic_approach` (avaliação basal de FEVE +
  monitorização seriada de FEVE/PA/QTc), `differentials` (7), `tests`
  (7), `red_flags` (7).
- `treatment_summary`: monitorização ecocardiográfica seriada como
  pilar central, reversibilidade geralmente favorável da disfunção
  ventricular (sem doses), decisão compartilhada com oncologia,
  alerta explícito contra suspensão automática de tratamento
  oncológico eficaz.
- `ambulatory_flow` (10), `emergency_flow` (6), `monitoring` (7).
- `special_populations` (6) — inclui nota explícita distinguindo o
  uso oncológico (mutação somática, adulto) do uso off-label
  pediátrico em síndrome de Noonan (variante germinativa, indicação
  distinta).
- `assistant_questions` (12), `assistant_rules` (10, priority 90 para
  QTc prolongado).
- `related_document_slugs` expandido de 1 para 4.

## Verificação de citações

Todos os 6 PMIDs de epidemiologia foram verificados individualmente
via NCBI e-utils antes da montagem, incluindo a metanálise de Mincu et
al. (JAMA Netw Open 2019) e o estudo longitudinal de Glen et al. (JACC
CardioOncol 2023). Um 7º PMID, citado em `special_populations` para o
uso pediátrico off-label em síndrome de Noonan (Wolf CM et al., JACC
Basic Transl Sci 2025), também foi verificado — nenhuma correção
necessária em nenhum dos 7.

## Verificações feitas na montagem

- Os 4 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema no texto.
- **Correção de um erro do agente de pesquisa**: o agente da Parte 3
  confundiu o `related_document_slug` pré-existente (um documento
  narrativo real e distinto) com o slug da própria ficha, sinalizando
  isso como possível erro. Verifiquei diretamente: são strings
  diferentes ("cardiotoxicidade-raf-mek" é o slug da ficha;
  "toxicidade-cardiovascular-dos-inibidores-de-braf-e-mek-...-
  vigilancia" é o documento real, existente e central) — mantive o
  vínculo.
- **Overlap pré-existente e legítimo**: `lista-de-quimioterapicos-de-
  risco-de-prolongamento-do-qt-...` também vinculado por
  `cardiotoxicidade-bcr-abl` — documentado no teste dedicado.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a
chave `label` corretamente.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `prevalence_rank` originais
preservados sem alteração.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap parcial mas documentado com `cardiotoxicidade-bcr-abl`.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_cardiotoxicidade_raf_mek.py`: 12
  testes, todos passando (1 correção durante desenvolvimento, para
  documentar overlap pré-existente descoberto pelo próprio teste).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando, 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-cardiotoxicidade-raf-mek-20260828`, baseada
em `origin/main` sem drift no momento do commit.
