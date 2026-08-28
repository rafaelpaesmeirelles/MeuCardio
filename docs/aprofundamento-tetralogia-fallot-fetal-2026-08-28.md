# Aprofundamento Tudo com Tudo — Tetralogia de Fallot no período fetal — 28/08/2026

## Contexto

Vigésimo segundo lote de conteúdo do dia, sexto do cluster de
cardiologia fetal (após `doenca-coronariana-idoso`, PR #603;
`valva-aortica-bicuspide-pediatrica`, PR #604;
`hipotensao-ortostatica-no-idoso`, PR #606; `sopros-na-infancia`,
PR #608; `hipertensao-arterial-pediatrica`, PR #609;
`dor-toracica-pediatrica`, PR #610; `dislipidemias-pediatricas`,
PR #611; `arritmias-pediatricas`, PR #612;
`avaliacao-multidimensional-cardiogeriatrica`, PR #613;
`cuidados-paliativos-cardiovasculares`, PR #615;
`cardiopatia-congenita-gravidez`, PR #616;
`hipertensao-pulmonar-gravidez`, PR #621;
`cardiotoxicidade-bcr-abl`, PR #624;
`medicamentos-cardiovasculares-gestacao-lactacao`, PR #625;
`plano-parto-cardiopatia-materna`, PR #626;
`seguimento-cardiovascular-pos-parto`, PR #628;
`indicacoes-ecocardiograma-fetal`, PR #630;
`bloqueio-atrioventricular-fetal`, PR #631;
`hidropisia-fetal-cardiovascular`, PR #632;
`flutter-atrial-fetal`, PR #633; `coarctacao-aorta-fetal`, PR #636). A
ficha `tetralogia-fallot-fetal` (área `cardiopediatria`, categoria
`cardiologia_fetal`, `prevalence_rank: 38`) já tinha
`patient_material_slug` e 1 `related_document_slug` preenchidos (o
único vínculo original é majoritariamente sobre manejo pós-natal, não
fetal), mas zero campos clínicos.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (cardiopatia
   cianótica mais comum, 15-20% associados a deleção 22q11.2,
   detecção pré-natal melhorada com avaliação sistemática das vias de
   saída), `presentation` (10 formas), `diagnostic_approach` (6
   subtópicos: avaliação sistemática de vias de saída, calibre de
   artérias pulmonares, diferenciação de conotruncais, investigação
   genética 22q11.2, avaliação extracardíaca, seguimento seriado),
   `differentials` (6), `tests` (7), `red_flags` (8), `source_refs`
   (7, todos os PMIDs verificados individualmente via NCBI e-utils).
2. **Conduta e assistente** — `treatment_summary` (ausência de
   intervenção intraútero na forma clássica, investigação de 22q11.2,
   vigilância seriada de artérias pulmonares, planejamento de parto
   em centro terciário, manejo neonatal com prostaglandina E1 nas
   formas ducto-dependentes), `ambulatory_flow` (10), `emergency_flow`
   (8), `monitoring` (8), `assistant_questions` (12),
   `assistant_rules` (10, priority 95 para valva pulmonar ausente com
   compressão de via aérea).
3. **Populações especiais e conexões** — `special_populations` (6:
   Fallot com 22q11.2, com atresia pulmonar, com valva pulmonar
   ausente, com artérias pulmonares hipoplásicas, forma clássica
   estável, orientação de parto em centro terciário),
   `related_document_slugs` (5, união do original com 4 novos).

## Verificação de citações

Todos os PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem, seguindo a prática estabelecida nas duas
rodadas anteriores (que tiveram erros de citação corrigidos em
`coarctacao-aorta-fetal`/PR #636 e `hidropisia-fetal-cardiovascular`/
PR #632). Nesta rodada, todas as 7 referências foram confirmadas
corretas sem necessidade de correção.

## Verificações feitas na montagem

- Os 5 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção
  explícita de tetralogia de Fallot no texto.
- O agente da Parte 3 documentou explicitamente 2 candidatos
  descartados (`seguimento-tardio-de-tetralogia-de-fallot-e-
  coarctacao-de-aorta-no-adulto` e `estratificacao-de-risco-
  arritmico-...-tetralogia-de-fallot-operada`) por tratarem
  especificamente de seguimento tardio no adulto operado, sem conexão
  com o período fetal/neonatal precoce — priorizando descoberta
  temática sobre volume, conforme diretriz de curadoria estabelecida.
- **Overlap extenso mas legítimo** com fichas já publicadas sobre o
  mesmo tema: documentos também vinculados a `tetralogia-de-fallot`
  (adulto), `atresia-pulmonar`, `indicacoes-ecocardiograma-fetal`/
  PR #630 e `planejamento-parto-cardiopatia-fetal` — documentado no
  teste dedicado.
- `patient_material_slug` original (`tetralogia-fallot-fetal`)
  preservado sem alteração — reconfirmado como existente.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente; fármaco citado apenas por nome (prostaglandina E1),
sem posologia. Estrutura de perguntas e regras validada com o motor de
regras real — todos os operadores usados pertencem ao conjunto
permitido, nenhum uso de "includes", nenhuma regra usa a chave
`monitoring` (não permitida) dentro de `add`.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

7 referências com PMID verificado individualmente via NCBI e-utils,
incluindo a diretriz ASE 2023, o estudo de Sharma et al. (2022) sobre
diagnósticos extracardíacos, o estudo de Chelliah et al. (2021) sobre
desfechos na forma com valva pulmonar ausente, e a revisão de Putotto
et al. (2022) sobre o impacto genético da deleção 22q11.2.

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `tetralogia-fallot-fetal`. Reconfirmado
que os PRs #634/#635 (usados por outra sessão concorrente no
repositório compartilhado) não tocam esta ficha.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap extenso mas documentado com 4 fichas do mesmo tema
  (Fallot adulto, atresia pulmonar, indicações de eco fetal,
  planejamento de parto).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_tetralogia_fallot_fetal.py`:
  12 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-tetralogia-fallot-fetal-20260828`, baseada
em `origin/main` sem drift no momento do commit.
