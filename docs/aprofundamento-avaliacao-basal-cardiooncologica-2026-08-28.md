# Aprofundamento Tudo com Tudo — Avaliação cardiovascular basal antes do tratamento oncológico — 28/08/2026

## Contexto

Trigésimo terceiro lote de conteúdo do dia. A ficha
`avaliacao-basal-cardiooncologica` (área `cardiooncologia`, categoria
`avaliacao_basal`, `prevalence_rank: 1`) estava rotulada
`completeness: completo`, mas na prática rasa: já tinha `presentation`
(2), `differentials` (3), `tests` (4), `red_flags` (5),
`ambulatory_flow` (4), `emergency_flow` (1), `assistant_questions` (6),
`assistant_rules` (6) — mas zero `epidemiology`, `diagnostic_approach`,
`treatment_summary`, `monitoring`, `special_populations` e
`related_document_slugs` (1 `source_ref`). Mesmo padrão de rótulo
inconsistente já visto em `avaliacao-cardiovascular-pre-concepcional`
(mesmo dia).

## Conteúdo produzido

Todo o conteúdo clínico pré-existente foi preservado sem alteração.
Adicionado apenas o que faltava:

- `epidemiology`: crescimento de sobreviventes de câncer com risco
  cardiovascular tardio, ferramenta HFA-ICOS citada uma única vez pelo
  nome, lacuna entre recomendação formal e início real de terapia
  cardiotóxica sem avaliação prévia.
- `diagnostic_approach`: história clínica dirigida, exame físico, ECG
  de 12 derivações, biomarcadores (troponina, peptídeos natriuréticos),
  ecocardiograma com FEVE e strain longitudinal global, estratificação
  formal de risco.
- `treatment_summary`: estratificação orienta vigilância proporcional
  ao risco (sem detalhamento de doses), comunicação estruturada com
  oncologia, princípio de proporcionalidade para não atrasar o
  tratamento oncológico desnecessariamente.
- `monitoring` (7 itens).
- `special_populations` (7 itens).
- `related_document_slugs` (5, do zero).

## Verificação de citações

Todos os 7 PMIDs desta rodada foram verificados individualmente via
NCBI e-utils antes da montagem — todas as referências corretas quanto
a título/periódico/ano/volume/páginas, incluindo a diretriz ESC 2022 de
cardio-oncologia, o guideline ASCO de sobreviventes de câncer, o
position statement de risco basal HFA-ICOS/IC-OS, e a diretriz de
imagem multimodal da ASE/EACVI.

## Verificações feitas na montagem

- Os 5 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema no texto, confirmados por leitura de trecho: padrão IC-OS/
  MASCC 2026, ferramenta HFA-ICOS, cardioproteção guiada por
  NT-proBNP, diretriz geral de cardio-oncologia, cardiotoxicidade de
  antraciclina/trastuzumabe no idoso.
- 9 candidatos adicionais lidos e descartados por menção apenas
  tangencial (dado de coorte específica, item de lista dentro de
  protocolo de outro tema, ou foco central em outro assunto).
- Nenhuma sobreposição com outra ficha do corpus encontrada.
- `patient_material_slug` definido como `cardio-oncologia`, confirmado
  como existente.
- Todo o conteúdo clínico pré-existente confirmado como preservado sem
  alteração por asserção explícita no `assemble.py` e por teste
  dedicado.

Nenhuma dose de fármaco em nenhum campo. A sigla "HFA-ICOS" aparece
uma única vez em `epidemiology`, citando o nome da ferramenta de
estratificação (nunca em `diagnostic_approach`, `treatment_summary`,
`monitoring`, `assistant_rules` ou `special_populations` — verificado
por teste dedicado específico para essa restrição).

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
- `backend/tests/test_aprofundamento_avaliacao_basal_cardiooncologica.py`:
  12 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando, 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-avaliacao-basal-cardiooncologica-20260828`,
baseada em `origin/main` sem drift no momento do commit.
