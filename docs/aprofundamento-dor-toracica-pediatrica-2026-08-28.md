# Aprofundamento Tudo com Tudo — Dor torácica pediátrica — 28/08/2026

## Contexto

Sexto lote de aprofundamento do dia (após `doenca-coronariana-idoso`,
PR #603; `valva-aortica-bicuspide-pediatrica`, PR #604; `hipotensao-
ortostatica-no-idoso`, PR #606; `sopros-na-infancia`, PR #608;
`hipertensao-arterial-pediatrica`, PR #609). A ficha `dor-toracica-
pediatrica` (área `cardiopediatria`, `prevalence_rank: 29`) — segunda
causa mais comum de encaminhamento ambulatorial à cardiologia
pediátrica, atrás só de sopro cardíaco — tinha apenas metadados de
catalogação e 1 `related_document_slug`.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (causa cardíaca em
   apenas 1-4% dos casos, séries de Selbst 1988, Massin 2004, Saleeb
   2011 — zero mortes cardíacas em 3.700 crianças classificadas como
   não cardíacas em 4,6 anos de seguimento), `presentation` (10 itens
   por etiologia), `diagnostic_approach` (5 subtópicos: anamnese
   dirigida, exame físico direcionado, indicação seletiva de ECG,
   indicação seletiva de ecocardiograma, critérios de encaminhamento),
   `differentials` (13 por sistema), `tests` (8), `red_flags` (12),
   `source_refs` (10).
2. **Conduta e assistente** — `treatment_summary` (conduta expectante
   para causa musculoesquelética, investigação seletiva não universal,
   critérios objetivos de encaminhamento urgente vs. eletivo),
   `ambulatory_flow` (8), `emergency_flow` (7), `monitoring` (6),
   `assistant_questions` (12), `assistant_rules` (10, priority até 95
   para dor de esforço + síncope + história familiar de morte súbita).
3. **Populações especiais e conexões** — `special_populations` (7:
   atleta, ansiedade/pânico, anemia falciforme, história familiar de
   morte súbita, Marfan, oncológico cardiotóxico, cardiopatia congênita
   operada), `related_document_slugs` (13 propostos), `patient_material_slug`.

## Correções feitas na montagem

- Todos os 13 `related_document_slugs` verificados individualmente —
  confirmada menção explícita a "dor torácica" no texto de cada um.
- **5 documentos compartilhados** com fichas já publicadas: o documento
  já existente antes deste lote (também em `sincope-pediatrica`,
  descoberto pelo teste dedicado na primeira rodada, não pelo agente de
  pesquisa — os agentes não tocaram nos itens já existentes) e 4 novos
  (`sindrome-de-turner-na-crianca-...`, também em `coarctacao-da-aorta`;
  `isquemia-coronaria-aguda-apos-switch-arterial`, também em
  `transposicao-das-grandes-arterias`; `descompensacao-aguda-da-
  circulacao-de-fontan`, também em `fisiologia-ventriculo-unico`;
  `cardiomiopatia-restritiva-na-crianca-...`, também em
  `cardiomiopatias-pediatricas`) — todos mantidos por serem genuína e
  centralmente relevantes também à dor torácica pediátrica.
- O agente de pesquisa descartou explicitamente vários candidatos
  tentadores por não mencionarem criança/adolescente no corpo do texto
  (documentos de saúde mental sobre dor torácica não cardíaca, todos com
  amostras de 18-70 anos; escore HEART, validado só para adulto;
  documentos de cardiologia do esporte que cobrem atleta de qualquer
  idade sem recorte pediátrico explícito) — disciplina de vínculo direto
  aplicada consistentemente.

Nenhuma dose de fármaco em nenhum campo — verificado programaticamente.
Estrutura de perguntas e regras validada com o motor de regras real
antes da montagem (nenhum operador inválido).

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada, então ainda não tinha a correção de allowlist em
`test_disease_fragments_canonical.py`. Apliquei aqui a mesma correção já
aprovada pelo Rafael no PR #606.

## Fontes primárias

10 referências novas, com PMID verificado, incluindo Selbst et al.
(Pediatrics 1988, série clássica de dor torácica pediátrica), Saleeb et
al. (Pediatrics 2011, efetividade do rastreio) e os protocolos SCAMP de
Friedman/Verghese (2011/2012, redução de exames desnecessários).

## Coordenação com Codex

Nenhum dos 30 PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `dor-toracica-pediatrica`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug` (já existente, `dor-toracica-pediatrica`)
  reconfirmado.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_dor_toracica_pediatrica.py`: 12
  testes, 1 falha na primeira rodada (sobreposição pré-existente não
  documentada, corrigida) e 12/12 na segunda.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist unificada).
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-dor-toracica-pediatrica-20260828`, baseada em
`origin/main` (`64db98f8`) sem drift no momento do commit.
