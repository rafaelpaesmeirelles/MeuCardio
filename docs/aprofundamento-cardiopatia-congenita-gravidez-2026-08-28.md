# Aprofundamento Tudo com Tudo — Cardiopatia congênita na gravidez — 28/08/2026

## Contexto

Décimo primeiro lote de aprofundamento do dia (após `doenca-
coronariana-idoso`, PR #603; `valva-aortica-bicuspide-pediatrica`,
PR #604; `hipotensao-ortostatica-no-idoso`, PR #606; `sopros-na-
infancia`, PR #608; `hipertensao-arterial-pediatrica`, PR #609;
`dor-toracica-pediatrica`, PR #610; `dislipidemias-pediatricas`,
PR #611; `arritmias-pediatricas`, PR #612; `avaliacao-multidimensional-
cardiogeriatrica`, PR #613; `cuidados-paliativos-cardiovasculares`,
PR #615). A ficha `cardiopatia-congenita-gravidez` (área `gravidez`,
categoria `cardiopatia_congenita`, `prevalence_rank: 10`) tinha apenas
metadados de catalogação — zero campos clínicos, zero
`related_document_slugs`, sem `patient_material_slug`.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (cardiopatia
   congênita é hoje a causa mais comum de cardiopatia estrutural na
   gravidez em países desenvolvidos, dados do registro ROPAC),
   `presentation` (9 itens por tipo de lesão), `diagnostic_approach` (6
   subtópicos: avaliação pré-concepcional, classificação de risco
   materno da OMS/ESC, escores CARPREG II e ZAHARA, ecocardiograma
   seriado, ressonância cardíaca, risco de recorrência na prole/
   ecocardiograma fetal direcionado), `differentials` (7 categorias de
   estratificação de risco, não diagnósticos clássicos), `tests` (8),
   `red_flags` (8), `source_refs` (12).
2. **Conduta e assistente** — `treatment_summary` (aconselhamento pré-
   concepcional, Pregnancy Heart Team multidisciplinar, via de parto
   individualizada, puerpério como período de maior risco hemodinâmico,
   classes terapêuticas sem posologia, contraindicações absolutas),
   `ambulatory_flow` (8), `emergency_flow` (7), `monitoring` (7),
   `assistant_questions` (12), `assistant_rules` (11, priority 95 para
   Eisenmenger/hipertensão pulmonar grave).
3. **Populações especiais e conexões** — `special_populations` (6:
   Eisenmenger, Fontan, coarctação reparada, tetralogia de Fallot
   reparada, valva aórtica bicúspide com aortopatia, risco de
   recorrência na prole), `related_document_slugs` (7, o máximo
   permitido — 6 candidatos avaliados, 1 descartado e 1 adicionado por
   busca própria).

## Correção de compliance feita na montagem

O texto de `special_populations` produzido pelo agente de pesquisa usava
a sigla "mWHO" ("mWHO IV", "mWHO 2.0") para a classificação de risco
materno da OMS/ESC — isso contém a substring banida "mwho". Reescrito
por extenso ("classe de risco materno IV da classificação da OMS/ESC",
"classificação de risco materno da OMS/ESC (versão 2.0)") mantendo o
conteúdo clínico intacto — mesmo precedente já aplicado em
`cardiopatia-congenita-do-adulto` (PR #596). Diferente do padrão
observado no lote anterior (`valva-aortica-bicuspide-pediatrica`,
PR #604), aqui a substring apareceu em texto autoral nosso (não em um
slug de documento pré-existente), então foi corrigida por completo —
o único uso remanescente de "mwho" é dentro do slug do documento
`sindrome-de-eisenmenger-contraindicacao-absoluta-a-gestacao-mecanismo-
mwho-iv`, vinculado em `related_document_slugs`, não em texto que
escrevemos.

## Verificações feitas na montagem

- Todos os 7 `related_document_slugs` verificados individualmente —
  confirmada menção explícita a "cardiopatia congênita" no texto de
  cada um.
- **4 dos 7 compartilhados** com fichas já publicadas: `gravidez-e-
  contracepcao-na-cardiopatia-congenita-do-adulto-ahaacc-2018` e
  `risco-de-recorrencia-...-ecocardiograma-fetal-direcionado` (também
  em `tetralogia-de-fallot`; o segundo também em `indicacoes-
  ecocardiograma-fetal`); `coarctacao-de-aorta-reparada-e-gestacao-do-
  ropac` (também em `coarctacao-da-aorta` e `aortopatia-na-gravidez`) —
  todos mantidos por serem genuína e centralmente relevantes também
  aqui.
- O agente descartou `rebecga-registro-brasileiro-de-cardiopatia-e-
  gravidez` por a cardiopatia congênita ser apenas 35,7% de uma coorte
  geral de "cardiopatia e gravidez" (não central) e acrescentou, por
  busca própria, `sindrome-de-eisenmenger-e-gestacao-mortalidade-
  materna-do-registro-britanico-ao-ropac` — não estava na lista inicial
  mas é claramente central e complementar ao documento de mecanismo já
  incluído.
- `patient_material_slug`: dois materiais existiam ligados ao tema;
  escolhido o mais abrangente (`gravidez-e-cardiopatia-congenita-o-que-
  saber`), compatível com o escopo geral da ficha.

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

12 referências novas, com PMID verificado, incluindo a diretriz ESC
2025 de doença cardiovascular na gravidez (De Backer et al.), o
guideline AHA/ACC 2018 de ACHD (Stout et al.) e os estudos de derivação
dos escores CARPREG II (Silversides et al. 2018) e ZAHARA (Drenthen et
al. 2010).

## Coordenação com Codex

Nenhum dos 36 PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `cardiopatia-congenita-gravidez`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug` novo (não existia antes deste lote) —
  reconfirmado como existente.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_cardiopatia_congenita_gravidez.py`:
  13 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist unificada).
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-cardiopatia-congenita-gravidez-20260828`,
baseada em `origin/main` sem drift no momento do commit.
