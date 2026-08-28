# Aprofundamento Tudo com Tudo — Toxicidade cardiovascular por inibidores BCR-ABL — 28/08/2026

## Contexto

Décimo terceiro lote de conteúdo do dia (após `doenca-coronariana-idoso`,
PR #603; `valva-aortica-bicuspide-pediatrica`, PR #604;
`hipotensao-ortostatica-no-idoso`, PR #606; `sopros-na-infancia`,
PR #608; `hipertensao-arterial-pediatrica`, PR #609;
`dor-toracica-pediatrica`, PR #610; `dislipidemias-pediatricas`,
PR #611; `arritmias-pediatricas`, PR #612;
`avaliacao-multidimensional-cardiogeriatrica`, PR #613;
`cuidados-paliativos-cardiovasculares`, PR #615;
`cardiopatia-congenita-gravidez`, PR #616;
`hipertensao-pulmonar-gravidez`, PR #621). A ficha
`cardiotoxicidade-bcr-abl` (área `cardiooncologia`, categoria
`terapia_alvo`, `prevalence_rank: 7`) tinha apenas metadados de
catalogação — zero campos clínicos, zero `related_document_slugs`,
sem `patient_material_slug`.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (perfil de risco
   cardiovascular diferenciado entre os 5 TKI BCR-ABL — imatinibe,
   dasatinibe, nilotinibe, bosutinibe, ponatinibe — com dados do
   estudo PACE de ponatinibe e coortes comparativas de nilotinibe),
   `presentation` (11 itens), `diagnostic_approach` (6 subtópicos:
   avaliação pré-tratamento/estratificação de risco, ECG seriado e
   QTc, ecocardiograma, rastreio de doença arterial periférica,
   avaliação de hipertensão pulmonar, monitorização pressórica),
   `differentials` (6, sempre no sentido de excluir causas não
   relacionadas ao TKI), `tests` (9), `red_flags` (8), `source_refs`
   (9, com todos os PMIDs verificados individualmente via NCBI
   E-utilities pelo próprio agente — dois PMIDs inicialmente lembrados
   de memória estavam incorretos e foram corrigidos antes da entrega).
2. **Conduta e assistente** — `treatment_summary` (estratificação de
   risco basal, monitorização longitudinal, manejo de fatores de risco
   modificáveis, decisão compartilhada hemato-oncologia/cardio-
   oncologia sobre troca de TKI, classes terapêuticas sem posologia),
   `ambulatory_flow` (10), `emergency_flow` (8), `monitoring` (8),
   `assistant_questions` (14), `assistant_rules` (11, priority 98 para
   evento vascular oclusivo agudo).
3. **Populações especiais e conexões** — `special_populations` (6:
   doença arterial periférica/coronariana prévia, QT longo
   congênito/fatores de risco, hipertensão pulmonar prévia, idosos
   com múltiplas comorbidades, troca de TKI por toxicidade, uso
   prolongado com reavaliação periódica), `related_document_slugs` (6,
   dentro do máximo de 7).

## Correção de artefato de texto na montagem

O texto de uma `assistant_rules.add.red_flags` gerado pelo agente da
Parte 2 continha o artefato de formatação "&gt;=" (entidade HTML) em
vez do texto plano "500 ms ou mais" — corrigido na montagem antes de
gravar no JSON, para não persistir marcação HTML crua em conteúdo que
será exibido como texto.

## Verificações feitas na montagem

- Todos os 6 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo (fora de
  Farmacologia/Calculadoras/Exames) e à menção explícita a "BCR-ABL"
  ou a um dos 5 fármacos (imatinibe, dasatinibe, nilotinibe,
  bosutinibe, ponatinibe) no texto.
- O agente da Parte 3 documentou explicitamente 2 documentos
  descartados por tratarem de TKIs de outras vias (VEGF-TKI/BTK/RET)
  sem qualquer menção a BCR-ABL, e 2 versões em formato "fluxograma"
  deixadas como reserva por redundância temática com os documentos
  técnicos já escolhidos.
- Nenhuma sobreposição de `related_document_slugs` detectada com
  outras fichas do corpus.
- `patient_material_slug` (`cardiotoxicidade-bcr-abl`, mesmo slug da
  própria ficha, coincidência de nomenclatura já existente no
  material) confirmado como existente em
  `material-paciente/metadados.json`, com correspondência direta ao
  tema (hipertensão pulmonar por bosutinibe/dasatinibe/ponatinibe em
  LMC) e fontes primárias próprias já revisadas.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente (incluindo o padrão `j/kg`). Classes terapêuticas e
nomes de fármacos citados sem posologia. Estrutura de perguntas e
regras validada com o motor de regras real antes da montagem — todos
os operadores usados pertencem ao conjunto permitido (`eq`, `in`,
`gte`, `contains`, `truthy`, `falsy`), nenhum uso de "includes".

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

9 referências, com PMID verificado individualmente via NCBI
E-utilities, incluindo a diretriz ESC 2022 de Cardio-Oncologia
(Lyon et al.), o estudo PACE de ponatinibe (Cortes et al. 2013 e 2018),
o estudo comparativo de doença arterial periférica com nilotinibe
(Kim et al. 2013) e a série de hipertensão pulmonar por dasatinibe
(Montani et al. 2012).

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `cardiotoxicidade-bcr-abl`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_cardiotoxicidade_bcr_abl.py`:
  11 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 17 testes executados, 17 passando.

## Branch e PR

Branch `claude/aprofundar-cardiotoxicidade-bcr-abl-20260828`, baseada
em `origin/main` sem drift no momento do commit.
