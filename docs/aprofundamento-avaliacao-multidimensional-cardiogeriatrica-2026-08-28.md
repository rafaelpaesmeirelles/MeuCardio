# Aprofundamento Tudo com Tudo — Avaliação multidimensional em cardiogeriatria — 28/08/2026

## Contexto

Nono lote de aprofundamento do dia (após `doenca-coronariana-idoso`,
PR #603; `valva-aortica-bicuspide-pediatrica`, PR #604; `hipotensao-
ortostatica-no-idoso`, PR #606; `sopros-na-infancia`, PR #608;
`hipertensao-arterial-pediatrica`, PR #609; `dor-toracica-pediatrica`,
PR #610; `dislipidemias-pediatricas`, PR #611; `arritmias-pediatricas`,
PR #612). Diferente de uma doença, a ficha `avaliacao-multidimensional-
cardiogeriatrica` (área `cardiogeriatria`, categoria `avaliacao_global`,
`prevalence_rank: 6`) é um **framework de avaliação geriátrica ampla
(CGA)** aplicado à decisão cardiovascular no idoso — tinha apenas
metadados de catalogação e 3 `related_document_slugs`.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo, com instrução
explícita para adaptar a estrutura clássica de "doença" ao formato de
processo/framework:

1. **Epidemiologia e diagnóstico** — `epidemiology` (prevalência de
   fragilidade em candidatos a TAVI, evidência de que "eyeballing"
   subestima fragilidade vs. avaliação estruturada — de la Rubia-Molina
   et al. 2025, Kempton et al. 2024), `presentation` (10 cenários de
   decisão clínica em que a avaliação muda a conduta, não sintomas
   clássicos), `diagnostic_approach` (7 subtópicos: rastreio de
   fragilidade, avaliação cognitiva breve, rastreio de depressão,
   avaliação nutricional, revisão de polifarmácia STOPP/START, suporte
   social, integração em decisão compartilhada), `differentials` (8
   armadilhas de avaliação, não diagnósticos diferenciais clássicos —
   ex. confundir sarcopenia isolada com fragilidade global), `tests` (10
   instrumentos/escalas), `red_flags` (7), `source_refs` (12).
2. **Conduta e assistente** — `treatment_summary` (interpretação
   graduada de fragilidade leve/moderada/grave na decisão de alto risco,
   envolvimento de Heart Team geriátrico, articulação com cuidados
   paliativos quando apropriado), `ambulatory_flow` (8), `emergency_flow`
   (4, triagem rápida à beira-leito), `monitoring` (7), `assistant_questions`
   (13), `assistant_rules` (10, priority 92 para fragilidade grave +
   sobrevida estimada <6 meses).
3. **Populações especiais e conexões** — `special_populations` (7:
   muito idoso candidato a TAVI, comprometimento cognitivo não
   diagnosticado, desnutrição/sarcopenia pré-cirúrgica, quedas e
   anticoagulação, isolamento social, comorbidades múltiplas com
   sobrevida limitada, internação aguda como oportunidade de rastreio),
   `related_document_slugs` (5, teto deliberadamente abaixo do máximo de
   7 permitido).

## Decisão de escopo: teto abaixo de 7 documentos

O agente da parte 3 avaliou 5 candidatos adicionais fortes sobre
fragilidade e escolheu incluir apenas 2, por decisão explícita de
qualidade sobre quantidade: esta ficha é sobre avaliação
**multidimensional** (múltiplos domínios — função, cognição, humor,
nutrição, medicamentos, suporte social), não fragilidade física
isolada, que já tem ficha própria e mais específica
(`fragilidade-pre-procedimento-cardiovascular`). Três candidatos com
menção apenas de passagem a "outros domínios geriátricos" (não
central) foram descartados para não duplicar excessivamente aquele
escopo. O documento mais forte encontrado (`framework-de-manejo-por-
dominio-para-insuficiencia-cardiaca-no-idoso-aha-2026`, declaração
científica AHA 2026 que organiza o cuidado em 4 domínios explícitos —
Médico, Cognitivo, Físico, Social) é quase um espelho conceitual desta
própria ficha, recortado para IC.

## Verificações feitas na montagem

- Todos os 5 `related_document_slugs` verificados individualmente.
- **2 dos 5 compartilhados** com outras fichas já publicadas:
  `estenose-aortica-grave-no-idoso-fragil-tavi-e-futilidade` (também em
  `fragilidade-pre-procedimento-cardiovascular` e `valvopatias`, ambas
  pré-existentes antes deste lote) e `framework-de-manejo-por-dominio-
  para-insuficiencia-cardiaca-no-idoso-aha-2026` (também em
  `insuficiencia-cardiaca-no-idoso`) — mantidos por serem genuína e
  centralmente relevantes também à avaliação multidimensional.

Nenhuma dose de fármaco em nenhum campo — verificado programaticamente.
Estrutura de perguntas e regras validada com o motor de regras real
antes da montagem.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

12 referências novas, com PMID verificado, incluindo as 3 declarações
científicas AHA dedicadas ao cuidado cardiovascular do idoso (Rich et
al. 2016, Damluji et al. 2020 e 2023) e o estudo seminal do fenótipo de
fragilidade de Fried (2001).

## Coordenação com Codex

Nenhum dos 35 PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `avaliacao-multidimensional-cardiogeriatrica`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug` (já existente,
  `escala-de-fragilidade-e-o-cuidado-do-seu-coracao`) reconfirmado.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_avaliacao_multidimensional_cardiogeriatrica.py`:
  11 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist unificada).
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-avaliacao-multidimensional-cardiogeriatrica-20260828`,
baseada em `origin/main` sem drift no momento do commit.
