# Aprofundamento Tudo com Tudo — Hipotensão ortostática no idoso — 28/08/2026

## Contexto

Terceiro lote de aprofundamento do dia (após `doenca-coronariana-idoso`,
PR #603, e `valva-aortica-bicuspide-pediatrica`, PR #604). Diferente dos
dois anteriores, este é um **aprofundamento pontual**: a ficha
`hipotensao-ortostatica-no-idoso` (área `cardiogeriatria`,
`prevalence_rank: 2`) já tinha `presentation`, `differentials`, `tests`,
`red_flags`, `ambulatory_flow`, `emergency_flow`, `assistant_questions` e
`assistant_rules` substantivos e revisados — preservados sem alteração.
Faltavam apenas 4 campos: `epidemiology`, `treatment_summary`,
`monitoring`, `special_populations`, e o `related_document_slugs` tinha
só 3 itens.

## Conteúdo produzido

Produzido por 2 agentes de pesquisa em paralelo (escopo menor que os
ciclos anteriores, proporcional ao tamanho da lacuna real):

1. **Epidemiologia e tratamento** — `epidemiology` (prevalência por
   idade/institucionalização, associação com queda/fratura/mortalidade,
   HO como marcador de disautonomia), `treatment_summary` (medidas não
   farmacológicas de primeira linha, desprescrição, midodrina/
   fludrocortisona/droxidopa por classe sem dose, hipotensão pós-prandial,
   dilema da hipertensão supina concomitante), `source_refs` (10).
2. **Monitoramento e conexões** — `monitoring` (7 itens), `special_populations`
   (7: Parkinson, neuropatia diabética, amiloidose, hipertensão supina,
   institucionalizado, demência, hipotensão pós-prandial),
   `related_document_slugs_adicionais` (11, verificados individualmente).

## Correções e verificações feitas na montagem

- **Sobreposição com outras fichas** (descoberta em duas etapas): o teste
  dedicado pegou, na primeira rodada de pytest, não só as sobreposições
  dos 11 documentos novos que o agente já havia relatado (6, com `sincope`
  e `risco-quedas-cardiogeriatria`), mas também **2 dos 3 documentos
  originais** (`hipotensao-ortostatica-e-sindrome-de-taquicardia-postural-
  pots-diagnostico-diferencial`, já em `sincope`; `hipotensao-pos-prandial-
  no-idoso-cardiopata-mecanismo-prevalencia-e-manejo`, já em `risco-quedas-
  cardiogeriatria`) — pré-existentes antes deste lote, nunca antes
  documentados. Todos os 8 verificados como genuína e centralmente também
  sobre HO, mantidos.
- **Gate novo descoberto no rebase**: `origin/main` recebeu, entre o início
  e o fim deste ciclo, o commit `64db98f8` (`feat(doencas): permitir
  fragmentos canônicos sem colisão`, do próprio Rafael) — novo mecanismo
  `doencas/fragmentos/*.json` + `doencas/correcoes/*.json` para reduzir
  colisões entre PRs paralelos editando `doencas/metadados.json`, com um
  novo teste (`test_disease_fragments_canonical.py`) que exigia **todo**
  registro combinado com `review_status: revisado`, sem nenhuma allowlist
  — quebraria as 17 PRs Tudo com Tudo abertas hoje assim que cada uma
  rebasear. Perguntei ao Rafael antes de tocar no teste; por decisão dele,
  o teste novo passou a reaproveitar a mesma allowlist
  `PENDENTES_LOTES_TUDO_COM_TUDO` já usada em
  `test_canonical_content_review_status.py` (importada como fonte única,
  não duplicada), evitando duas allowlists divergentes.
- Nenhuma dose de fármaco em nenhum campo — verificado programaticamente.
  Estrutura de perguntas/regras já existente reverificada contra o motor
  de regras real, sem alteração.

## Catalogação e conteúdo prévio preservados

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`,
`presentation`, `differentials`, `tests`, `red_flags`, `ambulatory_flow`,
`emergency_flow`, `assistant_questions`, `assistant_rules`,
`patient_material_slug` originais preservados sem alteração.

## Fontes primárias

12 referências (2 originais + 10 novas), com PMID verificado, incluindo
revisão de Ricci/De Caterina/Fedorowski (JACC 2015), diretriz ESC 2018 de
síncope, e ensaios de midodrina/droxidopa.

## Coordenação com Codex

Nenhum dos 22 PRs abertos que tocam `doencas/metadados.json` edita
`hipotensao-ortostatica-no-idoso`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug` (já existente) reconfirmado.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_hipotensao_ortostatica_no_idoso.py`:
  13 testes, 1 falha na primeira rodada (sobreposição não documentada dos
  3 originais, corrigida) e 13/13 na segunda.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist unificada).
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-hipotensao-ortostatica-no-idoso-20260828`,
rebaseada em `origin/main` sem drift no momento do commit (dois commits
intermediários absorvidos: `4a8c0978`, aprofundamento de AAOCA, e
`64db98f8`, mecanismo de fragmentos/correções — este último exigiu
decisão do Rafael sobre um gate novo, documentada acima).
