# Tudo com Tudo — novo verbete-hub de Miocardite (geral) — 27/08/2026

## Lacuna identificada

Auditoria do corpus (`content/` + `doencas/metadados.json`) confirmou que não
havia nenhum verbete-hub geral de **miocardite do adulto** no Guia de Doenças.
Existiam apenas dois verbetes de subpopulação, já publicados e preservados
sem alteração:

- `miocardite-pediatrica`
- `miocardite-por-inibidor-checkpoint`

Enquanto isso, `content/` já reunia um volume relevante de documentos
narrativos profundos sobre o tema — diretriz ESC 2025, fluxogramas de
retorno ao esporte, protocolo de células gigantes, miopericardite pós-vacina
de mRNA, miocardite chagásica/tropical — sem nenhum verbete-síntese que os
conectasse. Este é o sétimo ciclo Tudo com Tudo do dia, após endocardite
infecciosa (PR #553), pericardite (PR #554), hipertensão pulmonar (PR #555),
síncope (PR #560), valvopatias (PR #563) e cardiomiopatias (PR #565).

## Escopo e cuidado com duplicação

Novo slug `miocardite`, área `geral`. Antes de escrever qualquer campo, um
agente de pesquisa fez varredura exaustiva (`grep -rliE` por
"miocardite|miopericardite|inflamação miocárdica" em `content/`, 123
ocorrências) e confirmou explicitamente `colisao_detectada: false` — nenhum
outro verbete geral de miocardite do adulto existe em `doencas/metadados.json`.
Os dois verbetes-irmãos de subpopulação foram checados e **não** foram
duplicados nem em `related_document_slugs` nem em conteúdo.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo, cada um lendo os
documentos-fonte primários antes de escrever:

1. **Epidemiologia e diagnóstico** — `epidemiology`, `presentation`,
   `diagnostic_approach` (estruturado em dict: avaliação inicial, RM/Lake
   Louise, estratificação de risco, forma fulminante, biópsia
   endomiocárdica, contexto pós-vacina/pós-COVID, Chagas/tropicais),
   `differentials`, `tests`, `red_flags`, `source_refs`, `source_urls`.
2. **Tratamento e fluxos** — `treatment_summary` (5427 caracteres,
   cobrindo separadamente miocardite viral clássica, forma fulminante —
   com o paradoxo prognóstico apresentado com a ressalva científica correta,
   contrapondo a série fundadora de McCarthy 2000 a uma coorte contemporânea
   maior que mostrou o oposto no recorte viral —, células gigantes,
   miopericardite pós-mRNA, Chagas aguda e indicação de suporte elétrico),
   `ambulatory_flow`, `emergency_flow`, `monitoring`, `assistant_questions`
   (10 perguntas), `assistant_rules` (11 regras, incluindo
   `choque-cardiogenico-fase-aguda` em priority=100).
3. **Populações especiais e conexões** — `special_populations` (6 itens:
   criança/adolescente, oncológico/checkpoint, atleta competitivo, área
   endêmica de Chagas, receptor recente de vacina de mRNA, suspeita de
   células gigantes), `related_document_slugs` (12), `patient_material_slug`.

Nenhuma dose de fármaco foi incluída em nenhum campo. As strings banidas
("mwho", "hfa-icos") não aparecem em lugar nenhum — validado
programaticamente.

## Fontes primárias

9 referências, todas com PMID/DOI verificado via NCBI E-utilities:

- Schulz-Menger et al. 2025 ESC Guidelines for myocarditis and pericarditis — PMID 40878297
- Ferreira et al. 2018, CMR expert recommendations (critérios de Lake Louise) — PMID 30545455
- Block et al. 2022, MMWR PCORnet — PMID 35389977
- Karlstad et al. 2022, JAMA Cardiol (coorte nórdica) — PMID 35442390
- Patone et al. 2022, Nat Med — PMID 34907393
- Kim et al. 2025, AHA/ACC sports statement — PMID 39973614
- McCarthy et al. 2000, NEJM (fulminante vs. agudo) — PMID 10706898
- Naseeb et al. 2023, Cureus (revisão células gigantes) — PMID 37456487
- Montera et al. 2022, diretriz SBC de miocardite — PMID 35830116

## Relações Tudo com Tudo

12 `related_document_slugs`, cada um confirmado com menção central e
explícita ao tema (não proximidade temática) via leitura direta do texto:

```
miocardite-diagnostico-estratificacao-de-risco-e-biopsia-endomiocardica-esc-2025
miocardite-de-celulas-gigantes-diagnostico-diferencial-com-sarcoidose-cardiaca-e-terapia-imunossupressora
miopericardite-associada-a-vacina-de-mrna-contra-covid-19
sindromes-inflamatorias-miocardicas-e-pericardicas-imps-framework-unificado-esc-2025
fluxograma-miocardite-aguda-esc-2025
miocardite-chagasica-aguda-e-miocardites-tropicais-sbc-2022
miocardite-fulminante-viral-choque-de-inicio-rapido-e-o-paradoxo-do-prognostico-a-longo-prazo
miocardite-apos-vacina-de-mrna-e-risco-cardiovascular-pos-covid-o-que-os-numeros-dizem
covid-19-miocardite-pos-viral-atleta-triagem-retorno-esporte
fluxograma-miocardite-retorno-esporte-atleta
fluxograma-miocardite-retorno-progressivo-ao-esporte-aha-acc-2025
miocardite-retorno-ao-esporte
```

`patient_material_slug`: `miocardite-inflamacao-do-musculo-do-coracao-e-recuperacao`
(confirmado existente em `material-paciente/metadados.json`).

## Coordenação com Codex

Antes de commitar, foi feita checagem de coordenação com o trabalho
concorrente do Codex/ChatGPT no mesmo repositório (não há canal de
comunicação em tempo real entre as ferramentas — a única via disponível é
assíncrona, via o repositório GitHub compartilhado):

- `gh pr list --state open` filtrado a `headRefName` iniciando com `codex/`:
  13 PRs abertos inspecionados.
- Nenhum PR Codex cria ou edita um slug em `doencas/metadados.json` que
  colida com `miocardite`.
- 5 PRs (#522-#526) de um lote noturno do Codex editam/revisam documentos
  já existentes adjacentes ao tema (fluxogramas de miocardite por
  checkpoint, protocolo de miopericardite gestacional, diferencial de
  cardite reumática, desfechos de MIS-C) — sem criar um hub geral
  concorrente.
- Achado corroborado de forma independente pelo próprio agente de pesquisa
  3 deste ciclo, que checou e retornou `colisao_detectada: false`.

Esta checagem precisa ser repetida no início de cada novo ciclo, já que não
existe notificação automática de novos PRs Codex.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não é publicado até
  revisão humana.
- O paradoxo prognóstico da forma fulminante é apresentado com a ressalva
  científica de que uma coorte contemporânea maior contestou o achado
  original; ambas as leituras são mantidas explicitamente no texto, sem
  resolver o contraditório como fato assentado.
- Nenhuma dose de fármaco é citada.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  `total_records: 9497`, `total_files: 2193` (nenhum documento novo criado).
- `backend/tests/test_tudo_com_tudo_miocardite.py`: 6 testes, todos passando.
- `backend/tests/test_canonical_content_review_status.py`: passando com
  `miocardite` na allowlist `PENDENTES_LOTES_TUDO_COM_TUDO`.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-7-20260827`, baseada em `origin/main`
sem drift no momento do commit (`HEAD == origin/main` antes do append).
