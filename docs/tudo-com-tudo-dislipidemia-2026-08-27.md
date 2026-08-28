# Tudo com Tudo — novo verbete-hub de Dislipidemia (geral) — 27/08/2026

## Lacuna identificada

Auditoria do corpus (`content/` + `doencas/metadados.json`) confirmou que não
havia nenhum verbete-hub geral de **dislipidemia do adulto** no Guia de
Doenças. Existia apenas um verbete de subpopulação, já publicado e
preservado sem alteração:

- `dislipidemias-pediatricas` (área cardiopediatria)

Enquanto isso, `content/Prevenção_e_lipídios/` reunia 63 documentos
narrativos profundos, dos quais 42 especificamente sobre manejo lipídico
(estatinas, PCSK9i, Lp(a), hipercolesterolemia familiar, hipertrigliceridemia,
inibidores de ApoC3/ANGPTL3, intolerância a estatina), sem nenhum
verbete-síntese que os conectasse. Este é o oitavo ciclo Tudo com Tudo do
dia, após endocardite infecciosa (PR #553), pericardite (PR #554),
hipertensão pulmonar (PR #555), síncope (PR #560), valvopatias (PR #563),
cardiomiopatias (PR #565) e miocardite (PR #568).

## Escopo e cuidado com duplicação

Novo slug `dislipidemia`, área `geral`. Um agente de levantamento inicial
comparou todos os slugs "geral" já existentes em `origin/main` e confirmou
ausência de qualquer hub geral equivalente. O verbete-irmão pediátrico foi
checado e **não** foi duplicado nem em `related_document_slugs` nem em
conteúdo.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo, cada um lendo os
documentos-fonte primários antes de escrever:

1. **Epidemiologia e diagnóstico** — `epidemiology`, `presentation` (8
   itens), `diagnostic_approach` (estruturado em dict: avaliação de risco
   global com SCORE2/PREVENT-ASCVD, perfil lipídico completo com
   ApoB/Lp(a), hipercolesterolemia familiar com escore DLCN, hipertrigliceridemia
   grave e risco de pancreatite, monitorização de segurança/hepatotoxicidade —
   incluindo o abandono da monitorização rotineira de transaminases desde a
   revisão de segurança da FDA de 2012), `differentials` (8), `tests` (8),
   `red_flags` (8), `source_refs`, `source_urls`.
2. **Tratamento e fluxos** — `treatment_summary` (7179 caracteres),
   `ambulatory_flow` (9), `emergency_flow` (5), `monitoring` (7),
   `assistant_questions` (8), `assistant_rules` (8, com prioridade máxima
   100 para hipertrigliceridemia grave/risco iminente de pancreatite).
3. **Populações especiais e conexões** — `special_populations` (5: idoso/
   muito idoso, mulher em idade fértil/gestação/lactação, HF homozigota,
   doença renal crônica, diabetes/síndrome metabólica), `related_document_slugs`,
   `patient_material_slug`.

Nenhuma dose de fármaco foi incluída em nenhum campo — apenas classes
terapêuticas e indicações. As strings banidas ("mwho", "hfa-icos") não
aparecem em lugar nenhum — validado programaticamente.

## Correção feita na montagem

O agente de pesquisa 3 propôs inicialmente 36 `related_document_slugs`,
incluindo 9 documentos de `content/Farmacologia/` (monografias de fármacos
individuais: atorvastatina, rosuvastatina, sinvastatina, ezetimiba, ácido
bempedoico, evolocumabe/alirocumabe, inclisirana, evinacumabe, e um
fluxograma de ajuste de estatina). Esses 9 foram **removidos na montagem**
por estarem fora do escopo permitido de `related_document_slugs`, que deve
apontar apenas para documentos narrativos fora de
Farmacologia/Calculadoras/Exames. Restaram 27 conexões válidas, todas
verificadas programaticamente contra o sistema de arquivos.

## Fontes primárias

12 referências, todas com PMID/DOI verificado via NCBI E-utilities:

- Mach et al. 2025, ESC/EAS Focused Update — PMID 40878289
- Mach et al. 2019, ESC/EAS Guidelines — PMID 31504418
- Blumenthal et al. 2026, ACC/AHA Guideline on Dyslipidemia — PMID 41824590
- Nordestgaard et al. 2013, EAS consensus (HF underdiagnosed) — PMID 23956253
- Cuchel et al. 2023, EAS consensus update (HoFH) — PMID 37130090
- Kronenberg et al. 2022, EAS consensus (Lp(a)) — PMID 36036785
- Kamstrup et al. 2009, JAMA (Lp(a) genética e infarto) — PMID 19509380
- Virani et al. 2021, ACC Expert Consensus (hipertrigliceridemia persistente) — PMID 34332805
- Pedersen et al. 2016, JAMA Intern Med (coorte dinamarquesa, pancreatite) — PMID 27820614
- Ridker et al. 2008, NEJM (JUPITER) — PMID 18997196
- Björnsson 2017, Liver Int (hepatotoxicidade de estatina) — PMID 27860156
- FDA Drug Safety Communication, 28/02/2012

## Relações Tudo com Tudo

27 `related_document_slugs`, cada um confirmado com menção central e
explícita ao tema, e programaticamente verificado fora de
Farmacologia/Calculadoras/Exames.

`patient_material_slug`: `colesterol-alto-e-prevencao-cardiovascular`
(confirmado existente em `material-paciente/metadados.json`).

## Coordenação com Codex

Antes de commitar, foi checado o estado dos PRs abertos que tocam
`doencas/metadados.json` (569, 568, 567, 565, 564, 551, 544, 535) — nenhum
cria ou edita o slug `dislipidemia`. Checagem repetida a cada ciclo, dado
que não há notificação automática de novos PRs Codex.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não é publicado até
  revisão humana.
- Nenhuma dose de fármaco é citada — apenas classes terapêuticas.
- Documentos de moléculas experimentais em fase 2/nicho (muvalaplin,
  obicetrapibe, lerodalcibepe) foram deliberadamente deixados fora de
  `related_document_slugs` por não serem centrais ao hub geral consolidado.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  `total_records: 9497`, `total_files: 2193` (nenhum documento novo criado).
- `backend/tests/test_tudo_com_tudo_dislipidemia.py`: 6 testes, todos passando.
- `backend/tests/test_canonical_content_review_status.py`: passando com
  `dislipidemia` na allowlist `PENDENTES_LOTES_TUDO_COM_TUDO`.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-8-20260827`, baseada em `origin/main`
sem drift no momento do commit.
