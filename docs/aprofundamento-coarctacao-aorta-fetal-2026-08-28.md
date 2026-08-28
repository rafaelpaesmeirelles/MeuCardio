# Aprofundamento Tudo com Tudo — Suspeita fetal de coarctação da aorta — 28/08/2026

## Contexto

Vigésimo primeiro lote de conteúdo do dia, quinto do cluster de
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
`flutter-atrial-fetal`, PR #633). A ficha `coarctacao-aorta-fetal`
(área `cardiopediatria`, categoria `cardiologia_fetal`,
`prevalence_rank: 37`) já tinha `patient_material_slug` e 1
`related_document_slug` preenchidos, mas zero campos clínicos.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (taxa de
   falso-positivo do diagnóstico pré-natal 40-60%, natureza
   ducto-dependente, importância do planejamento de parto),
   `presentation` (10 formas), `diagnostic_approach` (5 subtópicos:
   critérios ecocardiográficos seriados, avaliação de fluxo
   istmo/ducto, diferenciação de hipoplasia de VE limítrofe,
   investigação genética, limitações/taxa de falso-positivo),
   `differentials` (6), `tests` (8), `red_flags` (8), `source_refs`
   (8, todos os PMIDs verificados individualmente via NCBI e-utils).
2. **Conduta e assistente** — `treatment_summary` (natureza
   ducto-dependente, ausência de indicação de intervenção intraútero,
   planejamento de parto em centro terciário, prostaglandina E1
   precoce, correção cirúrgica pós-natal, investigação de síndrome de
   Turner, aconselhamento sobre falso-positivo), `ambulatory_flow`
   (10), `emergency_flow` (8), `monitoring` (8), `assistant_questions`
   (12), `assistant_rules` (9, priority 95 para choque neonatal com
   parto fora de centro adequado).
3. **Populações especiais e conexões** — `special_populations` (6:
   coarctação com CIV, síndrome de Turner, hipoplasia de VE limítrofe,
   falso-positivo pós-natal, coarctação confirmada aguardando
   cirurgia, orientação de parto em centro terciário),
   `related_document_slugs` (4, união do original com 3 novos).

## Correções de citação feitas na montagem

Todos os PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem (prática adotada a partir do PR anterior,
`flutter-atrial-fetal`/PR #633, após a descoberta de um PMID incorreto
no lote de `hidropisia-fetal-cardiovascular`/PR #632). Duas correções
foram necessárias nesta rodada:

- A referência à diretriz ASE 2023 veio com autor incorreto ("Lopez L,
  Saurers DL, Barker PCA, et al.") — corrigida para o autor real
  (Moon-Grady AJ), o mesmo já usado corretamente em
  `indicacoes-ecocardiograma-fetal`/PR #630 para a mesma referência
  (mesmo PMID 37227365).
- Duas referências (Tuo G et al. 2022, PMID 36299692; Wang HH et al.
  2022, PMID 35754096) vieram sem nome de autor no texto entregue pelo
  agente — completadas com o autor e a paginação corretos após
  confirmação via NCBI e-utils.

## Verificações feitas na montagem

- Os 4 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção de
  coarctação no texto.
- **Overlap extenso mas legítimo** com fichas já publicadas sobre o
  mesmo eixo anatômico: `coarctacao-de-aorta-na-crianca-...` e
  `sindrome-de-turner-...` também vinculados a `coarctacao-da-aorta`
  (adulto); `coarctacao-de-aorta-reparada-e-gestacao-...` também em
  `coarctacao-da-aorta` e `aortopatia-na-gravidez`;
  `valva-aortica-bicuspide-e-aortopatia-associada-esc-2024` também em
  `aortopatia-na-gravidez` e `valva-aortica-bicuspide-pediatrica`/
  PR #604 — todos documentados no teste dedicado.
- O agente da Parte 3 documentou explicitamente candidatos descartados
  por menção apenas tangencial à coarctação (ex.: estenose aórtica
  valvar isolada, que cita coarctação apenas como variável em uma
  tabela de preditor, sem tratar do tema).
- `patient_material_slug` original (`coarctacao-aorta-fetal`)
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

8 referências com PMID verificado individualmente via NCBI e-utils,
incluindo a diretriz ASE 2023 (PMID corrigido para o autor correto), o
estudo de Matsui et al. (2008) sobre preditores morfológicos, a
metanálise de Familiari et al. (2017) sobre fatores de risco, e os
escores-Z de Pasquini et al. (2007) para avaliação de hipoplasia de
arco.

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `coarctacao-aorta-fetal`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap extenso mas documentado com 3 fichas do mesmo eixo
  anatômico (coarctação/valva bicúspide/aortopatia).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_coarctacao_aorta_fetal.py`:
  12 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-coarctacao-aorta-fetal-20260828`, baseada em
`origin/main` sem drift no momento do commit.
