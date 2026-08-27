# Tudo com Tudo — novo verbete-hub de Doença arterial periférica de membros (geral) — 27/08/2026

## Lacuna identificada

Auditoria do corpus (`content/` + `doencas/metadados.json`) confirmou que não
havia nenhum verbete-hub geral de **doença arterial periférica (DAP) de
membros** no Guia de Doenças. A pasta `content/Aorta_e_doença_arterial_periférica/`
reúne 35 documentos heterogêneos — misturando doença da aorta (aneurisma,
dissecção) e DAP de membros (claudicação, CLTI, isquemia aguda, Buerger) —
sem coerência suficiente para um único hub. Este é o décimo primeiro ciclo
Tudo com Tudo do dia, após endocardite infecciosa (PR #553), pericardite
(PR #554), hipertensão pulmonar (PR #555), síncope (PR #560), valvopatias
(PR #563), cardiomiopatias (PR #565), miocardite (PR #568), dislipidemia
(PR #570), diabetes mellitus tipo 2 (PR #572) e tromboembolismo venoso
(PR #574).

## Escopo e cuidado com duplicação

Novo slug `doenca-arterial-periferica-de-membros`, área `geral`. O escopo
foi deliberadamente restrito a DAP de membros — claudicação intermitente,
isquemia crônica ameaçadora do membro (CLTI), isquemia aguda de membro
(ALI) e doença de Buerger. **Doença da aorta isolada** (aneurisma
torácico/abdominal, dissecção) fica para um hub futuro separado, dado que
o subtema aórtico da mesma pasta (~9-10 documentos) tem volume e coerência
distintos.

Um candidato inicialmente mais forte por volume absoluto — febre
reumática/cardiopatia reumática, 24 documentos na pasta dedicada — foi
**descartado por colisão direta**: o PR aberto #567 (Codex) já está
expandindo o slug `febre-reumatica-cardite` para hub clínico completo,
conectando 6 documentos do mesmo pool.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo, cada um lendo os
documentos-fonte primários antes de escrever:

1. **Epidemiologia e diagnóstico** — `epidemiology`, `presentation` (8
   itens), `diagnostic_approach` (estruturado em dict: índice
   tornozelo-braço com armadilhas em diabetes/DRC, classificação de
   Rutherford para isquemia aguda, estratificação de CLTI/WIfI,
   investigação de doença de Buerger), `differentials` (6), `tests` (7),
   `red_flags` (7), `source_refs` (6), `source_urls`.
2. **Tratamento e fluxos** — `treatment_summary` (6009 caracteres,
   cobrindo claudicação/exercício supervisionado, revascularização
   individualizada por anatomia em CLTI — BASIL-2 vs. BEST-CLI —,
   controvérsia de dispositivos com paclitaxel — SWEDEPAD 1 e 2 —, terapia
   antitrombótica pós-revascularização — VOYAGER-PAD/COMPASS —, e manejo
   de isquemia aguda de membro), `ambulatory_flow` (8), `emergency_flow`
   (8), `monitoring` (7), `assistant_questions` (6), `assistant_rules` (6,
   com prioridade máxima 100 para isquemia aguda de membro).
3. **Populações especiais e conexões** — `special_populations` (6:
   diabético com neuropatia/ITB falsamente normal, tabagista ativo, Buerger
   em jovem tabagista, DRC/diálise, idoso, oncológico em TKI BCR-ABL com
   risco de DAP/isquemia aguda induzida por droga), `related_document_slugs`
   (24), `patient_material_slug`.

Nenhuma dose de fármaco foi incluída em nenhum campo — apenas classes
terapêuticas e indicações. As strings banidas ("mwho", "hfa-icos") não
aparecem em lugar nenhum.

## Descoberta técnica na montagem

O documento
`voYager-pad-revascularizacao-previa-risco-e-beneficio-rivaroxabana-2026.md`
tem nome de arquivo com "Y" maiúsculo, mas seu slug de frontmatter está em
minúsculas (`voyager-pad-revascularizacao-previa-risco-e-beneficio-rivaroxabana-2026`).
`scripts/audit_tudo_com_tudo.py` resolve documentos por slug de
frontmatter (`meta.get("slug") or path.stem`), então o slug correto a usar
em `related_document_slugs` é o do frontmatter, não o nome do arquivo. O
agente de pesquisa 3 já havia usado o slug correto; o teste dedicado deste
hub foi escrito para replicar a mesma lógica de resolução (frontmatter
primeiro, nome de arquivo como fallback), em vez de assumir que os dois
sempre coincidem — evitando um falso-negativo estrutural no gate.

## Fontes primárias

6 referências, todas com PMID/DOI verificado via NCBI E-utilities:

- Gornik et al. 2024, ACC/AHA Guideline (DAP de membros) — PMID 38743805
- Mazzolai et al. 2024, ESC Guidelines (arterial e aórtica) — PMID 39210722
- Qaja et al. 2023, StatPearls (doença de Buerger) — PMID 28613608
- Farber et al. 2022, SVS Guidelines (aneurisma poplíteo) — PMID 34023430
- Joshi et al. 2019, Cochrane (aneurisma poplíteo) — PMID 31868929
- Antonello et al. 2005, JVS (aneurisma poplíteo, ensaio randomizado) — PMID 16102611

## Relações Tudo com Tudo

24 `related_document_slugs`: 16 de `content/Aorta_e_doença_arterial_periférica/`
(restritos a DAP de membros, excluindo os exclusivamente sobre aorta
isolada) e 8 de outras pastas (Cardio-oncologia: nilotinibe/ponatinibe e
risco de DAP/isquemia aguda; Cardiologia geriátrica; Diabetes e
cardiologia). O documento de rastreio de DAP silenciosa no diabético já
vinculado ao hub `diabetes-mellitus-tipo-2` foi deliberadamente **não
duplicado** aqui — apenas citado textualmente em `special_populations`.

`patient_material_slug`: `dor-nas-pernas-ao-caminhar-doenca-arterial-periferica`
(confirmado existente em `material-paciente/metadados.json`).

## Coordenação com Codex

PRs abertos que tocam `doencas/metadados.json` checados antes do commit —
nenhum cria o slug `doenca-arterial-periferica-de-membros`. O PR #567
(Codex, febre reumática) foi identificado como colidindo com um candidato
inicialmente considerado e descartado a tempo.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não é publicado até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Doença da aorta isolada permanece sem hub geral — candidato explícito
  para uma rodada futura.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  `total_records: 9497`, `total_files: 2193` (nenhum documento novo criado).
- `backend/tests/test_tudo_com_tudo_doenca_arterial_periferica_de_membros.py`:
  6 testes, todos passando.
- `backend/tests/test_canonical_content_review_status.py`: passando com
  `doenca-arterial-periferica-de-membros` na allowlist
  `PENDENTES_LOTES_TUDO_COM_TUDO`.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-11-20260827`, baseada em `origin/main`
sem drift no momento do commit.
