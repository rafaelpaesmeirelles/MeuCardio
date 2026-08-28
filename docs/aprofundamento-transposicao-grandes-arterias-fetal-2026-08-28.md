# Aprofundamento Tudo com Tudo — Transposição das grandes artérias no período fetal — 28/08/2026

## Contexto

Vigésimo terceiro lote de conteúdo do dia, sétimo do cluster de
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
`flutter-atrial-fetal`, PR #633; `coarctacao-aorta-fetal`, PR #636;
`tetralogia-fallot-fetal`, PR #637). A ficha
`transposicao-grandes-arterias-fetal` (área `cardiopediatria`,
categoria `cardiologia_fetal`, `prevalence_rank: 39`) já tinha
`patient_material_slug` e 1 `related_document_slug` preenchidos, mas
zero campos clínicos.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (baixa detecção
   pré-natal quando o rastreio se limita ao plano de 4 câmaras —
   normal na TGA —, redução de mortalidade/morbidade neonatal com
   diagnóstico pré-natal), `presentation` (10 formas),
   `diagnostic_approach` (5 subtópicos: identificação de vasos
   paralelos, avaliação do septo interventricular, avaliação de
   forame oval/canal arterial, diferenciação de conotruncais,
   avaliação de anatomia coronariana), `differentials` (6), `tests`
   (8), `red_flags` (7), `source_refs` (7, todos os PMIDs verificados
   individualmente via NCBI e-utils).
2. **Conduta e assistente** — `treatment_summary` (ausência de
   intervenção intraútero, natureza ducto-dependente universal,
   prostaglandina E1 imediata ao nascer, septo íntegro + forame oval
   restritivo como preditor de septostomia de Rashkind emergencial,
   parto em centro terciário, cirurgia de switch arterial nas
   primeiras semanas), `ambulatory_flow` (10), `emergency_flow` (8),
   `monitoring` (8), `assistant_questions` (12), `assistant_rules`
   (10, priority 98 para septo íntegro + forame restritivo + parto
   fora de centro adequado).
3. **Populações especiais e conexões** — `special_populations` (6:
   TGA com septo íntegro/forame restritivo, com CIV, com estenose
   pulmonar, com anatomia coronariana atípica, aguardando
   septostomia/switch, orientação de parto em centro terciário),
   `related_document_slugs` (6, união do original com 5 novos).

## Verificação de citações

Todos os PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem — todas as 7 referências confirmadas
corretas, sem necessidade de correção.

## Verificações feitas na montagem

- Os 6 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção
  explícita de TGA/transposição das grandes artérias no texto.
- **Overlap extenso mas legítimo** com a ficha adulta
  `transposicao-das-grandes-arterias` (5 dos 6 documentos
  compartilhados — o tema é intrinsecamente contínuo entre o
  diagnóstico fetal e o manejo neonatal/switch arterial já descrito
  nessa ficha), além de `tetralogia-de-fallot` e
  `planejamento-parto-cardiopatia-fetal` — documentado no teste
  dedicado.
- O agente da Parte 3 documentou explicitamente ter descartado
  candidatos com menção apenas tangencial (ex.: triagem neonatal por
  oximetria, dupla via de saída de ventrículo direito, documentos
  sobre TGA no adulto/Fontan fora do escopo fetal/neonatal imediato).
- `patient_material_slug` original (`transposicao-grandes-arterias-
  fetal`) preservado sem alteração — reconfirmado como existente.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente; fármaco/procedimento citado apenas por nome
(prostaglandina E1, septostomia de Rashkind), sem posologia. Estrutura
de perguntas e regras validada com o motor de regras real — todos os
operadores usados pertencem ao conjunto permitido, nenhum uso de
"includes", nenhuma regra usa a chave `monitoring` (não permitida)
dentro de `add`.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

7 referências com PMID verificado individualmente via NCBI e-utils,
incluindo a diretriz científica da AHA 2014, o estudo clássico de
Bonnet et al. (1999) sobre detecção pré-natal e redução de morbidade,
o estudo de Maeno et al. (1999) sobre preditores pré-natais de
constrição do canal e forame restritivo, e o estudo populacional de
Nagata et al. (2020) sobre redução de mortalidade pós-natal.

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `transposicao-grandes-arterias-fetal`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap extenso mas documentado com 3 fichas do mesmo tema (TGA
  adulto, tetralogia de Fallot, planejamento de parto).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_transposicao_grandes_arterias_fetal.py`:
  12 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-transposicao-grandes-arterias-fetal-20260828`,
baseada em `origin/main` sem drift no momento do commit.
