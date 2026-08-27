# Tudo com Tudo — novo verbete-hub de Tromboembolismo venoso (geral) — 27/08/2026

## Lacuna identificada

Auditoria do corpus (`content/` + `doencas/metadados.json`) confirmou que não
havia nenhum verbete-hub geral de **tromboembolismo venoso (TEV)** no Guia
de Doenças. Existia apenas o hub-irmão `embolia-pulmonar-aguda`, com escopo
estrito de TEP agudo/reperfusão (apenas 2 documentos vinculados). Enquanto
isso, `content/Tromboembolismo/` reunia 55 documentos narrativos profundos,
dos quais 40 estavam órfãos — sem nenhum verbete-síntese que os conectasse.
Este é o décimo ciclo Tudo com Tudo do dia, após endocardite infecciosa
(PR #553), pericardite (PR #554), hipertensão pulmonar (PR #555), síncope
(PR #560), valvopatias (PR #563), cardiomiopatias (PR #565), miocardite
(PR #568), dislipidemia (PR #570) e diabetes mellitus tipo 2 (PR #572).

## Escopo e cuidado com duplicação

Novo slug `tromboembolismo-venoso`, área `geral`. O escopo cobre TVP
proximal/distal/membro superior, trombose venosa superficial, síndrome
pós-trombótica, escolha e duração de anticoagulação, populações especiais,
sítios incomuns de trombose venosa, trombofilia/SAF, profilaxia, filtro de
veia cava e monitorização/reversão de anticoagulação — tratando TEP apenas
como desfecho possível, não como foco central. Um agente de levantamento
inicial confirmou que o PR aberto #544, apesar do título "aprofundar
embolia pulmonar aguda", apenas recria a entrada `embolia-pulmonar-aguda`
já mergeada em main com os mesmos 2 documentos, sem tocar em nenhum dos 40
documentos deste hub. Verificação programática confirmou zero sobreposição
entre `related_document_slugs` deste hub e os 2 documentos já vinculados ao
hub-irmão.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo, cada um lendo os
documentos-fonte primários antes de escrever:

1. **Epidemiologia e diagnóstico** — `epidemiology`, `presentation` (8
   itens), `diagnostic_approach` (estruturado, cobrindo escore de Wells,
   D-dímero, ultrassom de compressão, investigação de trombofilia/neoplasia
   oculta), `differentials` (7), `tests` (8), `red_flags` (8), `source_refs`
   (28), `source_urls`.
2. **Tratamento e fluxos** — `treatment_summary` (4131 caracteres,
   cobrindo escolha de anticoagulante por classe — DOAC como primeira
   linha, com exceções bem definidas para SAF, DRC grave/diálise, gestação
   e câncer com risco de sangramento de mucosa —, duração conforme
   provocado/não provocado com o escore HERDOO2, e reversão de
   anticoagulante em sangramento maior), `ambulatory_flow` (7),
   `emergency_flow` (5), `monitoring` (7), `assistant_questions` (8),
   `assistant_rules` (9, com 3 regras de prioridade ≥70: sangramento maior
   =100, TVP extensa com risco de embolização=80, gestante=70).
3. **Populações especiais e conexões** — `special_populations` (7:
   gestação/lactação, câncer ativo, obesidade extrema/pós-bariátrica, DRC
   grave/diálise, paciente crítico de UTI, trombofilia/SAF, sítios
   incomuns), `related_document_slugs` (40), `patient_material_slug`.

Nenhuma dose de fármaco foi incluída em nenhum campo — apenas classes
terapêuticas e indicações. As strings banidas ("mwho", "hfa-icos") não
aparecem em lugar nenhum.

## Fontes primárias

28 referências verificadas via PMID/DOI (NCBI E-utilities) — cobrindo
diretrizes de anticoagulação estendida (AMPLIFY-EXT, EINSTEIN CHOICE),
ensaios de DOAC no TEV agudo (AMPLIFY, EINSTEIN-PE, RE-COVER, Hokusai-VTE),
regra HERDOO2, escore de Khorana, síndrome pós-trombótica (escore de
Villalta, ensaio SOX), trombose de sítios incomuns (trombose venosa
cerebral AHA 2024, RE-SPECT CVT) e reversão de anticoagulante
(idarucizumabe, andexanet alfa).

## Relações Tudo com Tudo

40 `related_document_slugs`, cada um confirmado com menção central e
explícita ao tema, programaticamente verificado fora de
Farmacologia/Calculadoras/Exames e sem sobreposição com o hub-irmão.

`patient_material_slug`: `trombose-venosa-e-embolia-pulmonar` (confirmado
existente em `material-paciente/metadados.json`).

## Coordenação com Codex

PRs abertos que tocam `doencas/metadados.json` checados antes do commit —
nenhum cria o slug `tromboembolismo-venoso`. O PR #544 foi especificamente
investigado por seu título enganoso e confirmado como não conflitante.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não é publicado até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- O escopo foi deliberadamente desenhado para não sobrepor o hub-irmão
  `embolia-pulmonar-aguda` — TEP agudo permanece coberto exclusivamente lá.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  `total_records: 9497`, `total_files: 2193` (nenhum documento novo criado).
- `backend/tests/test_tudo_com_tudo_tromboembolismo_venoso.py`: 7 testes,
  todos passando (inclui teste dedicado de não-sobreposição com o
  hub-irmão).
- `backend/tests/test_canonical_content_review_status.py`: passando com
  `tromboembolismo-venoso` na allowlist `PENDENTES_LOTES_TUDO_COM_TUDO`.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-10-20260827`, baseada em `origin/main`
sem drift no momento do commit.
