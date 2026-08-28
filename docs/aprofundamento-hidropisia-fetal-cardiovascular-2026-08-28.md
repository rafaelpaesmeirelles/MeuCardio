# Aprofundamento Tudo com Tudo — Hidropisia fetal de possível causa cardiovascular — 28/08/2026

## Contexto

Décimo nono lote de conteúdo do dia, terceiro do cluster de
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
`bloqueio-atrioventricular-fetal`, PR #631). A ficha
`hidropisia-fetal-cardiovascular` (área `cardiopediatria`, categoria
`cardiologia_fetal`, `prevalence_rank: 36`) já tinha
`patient_material_slug` e 2 `related_document_slugs` preenchidos, mas
zero campos clínicos.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (incidência geral
   1/1.500-3.800 gestações, causa cardiovascular responde por ~20-25%
   dos casos não imunes, mortalidade não tratada historicamente >50%),
   `presentation` (10 etiologias/formas de apresentação),
   `diagnostic_approach` (5 subtópicos: avaliação ecocardiográfica
   sistemática, exclusão de causas não cardiovasculares, avaliação de
   gravidade/progressão, avaliação materna para síndrome em espelho,
   indicação de intervenção fetal urgente), `differentials` (7),
   `tests` (8), `red_flags` (8), `source_refs` (7, incluindo AHA 2014,
   as revisões sistemáticas de Bellini et al. sobre etiologia de HFNI,
   a revisão de Braun et al. sobre síndrome em espelho, e o estudo de
   Jaeggi et al. sobre tratamento transplacentário de taquiarritmia).
2. **Conduta e assistente** — `treatment_summary` (investigação
   etiológica sistemática, tratamento dirigido à causa — cardioversão
   transplacentária, corticosteroide, transfusão intrauterina,
   drenagem de derrame —, avaliação materna obrigatória para síndrome
   em espelho, decisão compartilhada sobre antecipação do parto,
   planejamento em centro terciário), `ambulatory_flow` (10),
   `emergency_flow` (7), `monitoring` (7), `assistant_questions` (13),
   `assistant_rules` (10, priority 98 para síndrome em espelho materna
   confirmada).
3. **Populações especiais e conexões** — `special_populations` (6:
   hidropisia por taquiarritmia, por bloqueio atrioventricular
   completo, por cardiopatia estrutural complexa, por tumor cardíaco
   obstrutivo, síndrome em espelho materna, hidropisia próxima ao
   limite de viabilidade), `related_document_slugs` (5, união dos 2
   originais com 3 novos).

## Verificações feitas na montagem

- Os 5 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção de
  hidropisia no texto.
- O agente da Parte 3 documentou explicitamente ter descartado
  `taquiarritmia-fetal-hidropsia-nao-imune-e-tratamento-
  transplacentario` por sobreposição substancial de conteúdo com o
  documento de arritmias fetais já vinculado (mesmos mecanismos,
  mesma lógica de tratamento) — decisão de evitar redundância dentro
  da regra Tudo com Tudo.
- **Overlap** com 5 fichas irmãs do cluster fetal: uma já aprofundada
  hoje (`bloqueio-atrioventricular-fetal`/PR #631, 2 documentos
  compartilhados) e quatro ainda não
  (`taquicardia-supraventricular-fetal`,
  `sindrome-coracao-esquerdo-hipoplasico-fetal`, `anomalia-ebstein`,
  `tumores-cardiacos-fetais`) — overlap pré-existente e/ou legítimo,
  documentado no teste dedicado.
- `patient_material_slug` original (`hidropisia-fetal-cardiovascular`)
  preservado sem alteração — reconfirmado como existente.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente; fármacos citados apenas por nome (digoxina,
flecainida, sotalol, dexametasona), sem posologia. Estrutura de
perguntas e regras validada com o motor de regras real — todos os
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

7 referências com PMID verificado, incluindo a diretriz científica da
AHA 2014, as duas revisões sistemáticas de Bellini et al. (2009, 2015)
sobre etiologia de hidropisia fetal não imune, a revisão de Braun et
al. (2010) sobre síndrome em espelho, e o estudo comparativo de Jaeggi
et al. (2011) sobre tratamento transplacentário de taquiarritmia
fetal.

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `hidropisia-fetal-cardiovascular`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap de 5 documentos com fichas irmãs, documentado e
  pré-existente/legítimo.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_hidropisia_fetal_cardiovascular.py`:
  12 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-hidropisia-fetal-cardiovascular-20260828`,
baseada em `origin/main` sem drift no momento do commit.
