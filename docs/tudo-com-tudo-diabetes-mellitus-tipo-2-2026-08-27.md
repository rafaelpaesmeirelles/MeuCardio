# Tudo com Tudo — novo verbete-hub de Diabetes mellitus tipo 2 e risco cardiovascular — 27/08/2026

## Lacuna identificada

Auditoria do corpus (`content/` + `doencas/metadados.json`) confirmou que não
havia nenhum verbete-hub geral de **diabetes mellitus e risco cardiovascular**
no Guia de Doenças, apesar de `content/Diabetes_e_cardiologia/` reunir 63
documentos narrativos profundos e coesos (todos `review_status: revisado`) —
diretrizes ESC 2023/ADA 2026/SBD 2025, CVOTs de todas as classes
hipoglicemiantes, síndrome cardiovascular-renal-metabólica, cardiomiopatia
diabética, neuropatia autonômica cardíaca. Este é o nono ciclo Tudo com Tudo
do dia, após endocardite infecciosa (PR #553), pericardite (PR #554),
hipertensão pulmonar (PR #555), síncope (PR #560), valvopatias (PR #563),
cardiomiopatias (PR #565), miocardite (PR #568) e dislipidemia (PR #570).

## Escopo e cuidado com duplicação

Novo slug `diabetes-mellitus-tipo-2`, área `geral`. O escopo foi
deliberadamente restrito ao **risco e desfecho cardiovascular** do diabetes
tipo 2 — não é um verbete de manejo endocrinológico primário de glicemia,
que pertence a outra especialidade. Um agente de levantamento inicial
comparou todos os slugs já existentes e todos os 271 PRs abertos (9 deles
tocando `doencas/metadados.json`) e confirmou ausência de qualquer hub
geral equivalente ou em produção concorrente.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo, cada um lendo os
documentos-fonte primários antes de escrever:

1. **Epidemiologia e diagnóstico** — `epidemiology`, `presentation` (8
   itens), `diagnostic_approach` (estruturado em dict: avaliação inicial
   obrigatória, estratificação de risco via SCORE2-Diabetes/SBD 2025,
   avaliação renal, rastreio de doença coronariana assintomática — com a
   posição atual contra rastreio sistemático apoiada no ensaio DIAD —,
   avaliação de neuropatia autonômica cardíaca via testes de Ewing, avaliação
   de cardiomiopatia diabética via strain), `differentials` (6), `tests` (8),
   `red_flags` (7), `source_refs`, `source_urls`.
2. **Tratamento e fluxos** — `treatment_summary` (5280 caracteres,
   priorizando iSGLT2/GLP-1 por benefício cardiovascular/renal comprovado
   independente do controle glicêmico, papel da metformina na IC, leitura
   crítica de ACCORD/ADVANCE/VADT versus o efeito legado do UKPDS, manejo
   perioperatório de iSGLT2), `ambulatory_flow` (7), `emergency_flow` (5),
   `monitoring` (6), `assistant_questions` (8), `assistant_rules` (8, com
   duas regras de prioridade máxima 100: cetoacidose euglicêmica associada a
   iSGLT2 e síndrome coronariana aguda com hiperglicemia de estresse).
3. **Populações especiais e conexões** — `special_populations` (6: DM1 de
   longa duração, DM1 de início precoce, diabetes gestacional, DM2 de início
   precoce, idoso com polifarmácia, DRC diabética), `related_document_slugs`
   (34), `patient_material_slug`.

Nenhuma dose de fármaco foi incluída em nenhum campo — apenas classes
terapêuticas e indicações. As strings banidas ("mwho", "hfa-icos") não
aparecem em lugar nenhum.

## Correção feita pelo agente de pesquisa 1

Um dos documentos-fonte citava referência sobre iSGLT2 em cardiomiopatia
diabética sem PMID; o agente buscou por DOI e confirmou PMID 37055837
(Huang et al., Cardiovasc Diabetol 2023) antes de incluir a citação —
disciplina de verificação aplicada mesmo quando a fonte primária não trazia
o dado completo.

## Fontes primárias

11 referências, todas com PMID/DOI verificado via NCBI E-utilities:

- Marx et al. 2023, ESC Guidelines (diabetes e DCV) — PMID 37622663
- ADA Standards of Care 2026, cap. 10 — PMID 41358899
- Ndumele et al. 2026, AHA/ACC/ADA/ASN (síndrome CKM) — PMID 42265997
- Sociedade Brasileira de Diabetes, Diretriz 2025
- Gogan et al. 2025, revisão de neuropatia autonômica cardíaca — PMID 39941342
- Maser et al. 2003, metanálise (neuropatia autonômica e mortalidade) — PMID 12766130
- Pop-Busui et al. 2017, posicionamento ADA (neuropatia diabética) — PMID 27999003
- Young et al. 2009, JAMA (ensaio DIAD) — PMID 19366774
- Santilli et al. 2025, revisão (rastreio de DAC assintomática) — PMID 41185007
- Capes et al. 2000, Lancet (hiperglicemia de estresse) — PMID 10711923
- Huang et al. 2023, Cardiovasc Diabetol (iSGLT2 em cardiomiopatia diabética) — PMID 37055837

## Relações Tudo com Tudo

34 `related_document_slugs`, selecionados dos 63 documentos disponíveis em
`content/Diabetes_e_cardiologia/` por centralidade clínica, cada um
verificado individualmente como fora de
Farmacologia/Calculadoras/Exames.

`patient_material_slug`: `diabetes-e-o-coracao` (confirmado existente em
`material-paciente/metadados.json`).

## Coordenação com Codex

PRs abertos que tocam `doencas/metadados.json` checados antes do commit —
nenhum cria o slug `diabetes-mellitus-tipo-2`. Os PRs #443 e #437,
relacionados a diabetes, tocam apenas `material-paciente`/`checklists`, não
`doencas/metadados.json`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não é publicado até
  revisão humana.
- Escopo deliberadamente restrito ao eixo cardiovascular — manejo
  endocrinológico primário de glicemia não é objeto deste verbete.
- Nenhuma dose de fármaco é citada.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  `total_records: 9497`, `total_files: 2193` (nenhum documento novo criado).
- `backend/tests/test_tudo_com_tudo_diabetes_mellitus_tipo_2.py`: 6 testes,
  todos passando.
- `backend/tests/test_canonical_content_review_status.py`: passando com
  `diabetes-mellitus-tipo-2` na allowlist `PENDENTES_LOTES_TUDO_COM_TUDO`.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-9-20260827`, baseada em `origin/main`
sem drift no momento do commit.
