# Tudo com Tudo — Síncope (novo verbete-hub) — 27/08/2026

Quarto ciclo independente do dia de produção Tudo com Tudo (após endocardite
infecciosa PR #553, pericardite PR #554 e hipertensão pulmonar PR #555).

## Lacuna identificada

O corpus já tinha 30 documentos publicados e revisados em `content/Síncope/`
(fluxogramas, evidências, diretrizes) além do material para paciente
`sincope-desmaio`, mas **nenhum verbete correspondente em `doencas/metadados.json`**
— nenhuma outra doença fazia referência a esse conteúdo, e o próprio Guia de
Doenças não tinha uma entrada de síncope. Confirmado via
`gh pr diff <N> -- doencas/metadados.json` em todos os PRs abertos que este
slug não colide com nenhuma frente em andamento (o candidato anterior,
"Tromboembolismo Venoso", foi abandonado por colidir com o PR #544 do Codex,
que já aprofunda embolia pulmonar aguda).

## Escopo e cuidado com duplicação

Síncope é sintoma/síndrome de área geral, com fisiopatologia dividida em três
grandes grupos etiológicos (reflexa, cardíaca, ortostática/POTS) — modelagem
refletida em `subtype: "tres_grupos_etiologicos"`. Já existia o verbete
`sincope-pediatrica` na área de cardiopediatria; o novo `sincope` é um hub
geral/adulto separado, que não substitui nem duplica o fluxo pediátrico.

## Conteúdo produzido

Registro novo `sincope` em `doencas/metadados.json`: epidemiologia (3 grupos
etiológicos, prevalência por faixa etária e cenário), apresentação (7 itens),
diagnóstico (~2.500 caracteres — ECG, tilt test, monitor de eventos
implantável, regras de decisão clínica), diferenciais (6, incluindo crise
epiléptica com assistolia ictal e pseudossíncope psicogênica), testes (7,
com limitações), red flags (7), fluxo ambulatorial e de emergência (6+6),
tratamento (~2.100 caracteres — desde medidas não farmacológicas até
cardioneuroablação e marca-passo empírico ISSUE-3), monitorização (6),
populações especiais (6, incluindo idoso e atleta), 6 perguntas e 6 regras de
assistente determinístico (prioridade máxima dividida entre ECG de alto risco
e síncope de esforço com cardiopatia estrutural — ver nota de gate abaixo).

## Fontes primárias

ESC 2018 (Brignole et al., diretriz de síncope, PMID 29562304), San Francisco
Syncope Rule (Costantino, PMID 24862309), Canadian Syncope Risk Score
(Thiruganasambandamoorthy), EGSYS, POST (Sheldon, PMID 22972872/16505178),
ISSUE-3 (marca-passo na síncope reflexa cardioinibitória, PMID 22565936),
posição conjunta EHRA/HRS/APHRS/LAHRS 2024 sobre cardioneuroablação (PMID
39082698), critérios de alto risco do ECG EuSEM 2024, ensaio SEEDS (unidade
de síncope, Shen, PMID 15536093), entre outras 13 referências listadas em
`source_refs`.

## Relações Tudo com Tudo

30 `related_document_slugs`, todos em `content/Síncope/`, cada um verificado
para (a) resolver contra um documento real existente, (b) não pertencer a
Farmacologia/Calculadoras/Exames, e (c) mencionar "síncope" explicitamente no
próprio texto — vínculo direto, não proximidade temática. `patient_material_slug`
aponta para o material já existente `sincope-desmaio`. Nenhum documento ou
material novo foi criado; o lote é puramente de conexão sobre conteúdo já
publicado e revisado.

## Riscos e limitações

- Ficha promovida a `review_status: revisado` após revisão clínica e de segurança, com correções de alto risco, observação intermediária, indicação de ILR, betabloqueadores e referências primárias.
- Regra de assistente originalmente desenhada como uma condição `any` com um
  sub-grupo `all` aninhado, que o `clinical_rule_engine` não suporta (só
  aceita condições simples dentro de `all`/`any`/`none`, sem aninhamento).
  Corrigida para duas regras irmãs de mesma prioridade (100) e mesmo efeito
  clínico (ECG de alto risco OU síncope de esforço + cardiopatia estrutural
  conhecida, cada uma isoladamente already suficiente para escalar a
  emergência) — detectado e corrigido antes do commit, com teste de
  regressão cobrindo `validate_rule_definitions`.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9495` (baseline de `main` em 27/08/2026 já com lotes 1-4 e
  hubs anteriores mesclados e revisados: 9494; +1 pelo novo registro de
  doença, nenhum documento novo).
- `scripts/content_inventory.py --minimum-records 9495 --minimum-files 2193 --strict`:
  contagens exatas, `invalid: []`, `missing: []`.
- `backend/tests/test_tudo_com_tudo_sincope.py` (novo, 8 casos) +
  `test_canonical_content_review_status.py` + `test_tudo_com_tudo_avc_agudo.py`
  (proteção do hub anterior já em `main`): 15 casos, todos passando.
- `python -c "import app.main"`: importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-4-20260827`, base `main` (ciclo
independente, não empilhado). Sem merge, deploy ou publicação automática.


## Nota sobre o estado do main

Durante este ciclo, `origin/main` avançou substancialmente (mais de 30
commits) em relação ao ponto em que este ciclo havia começado: os lotes 1-4
de profundidade especializada e os hubs Tudo com Tudo de AVC, endocardite
infecciosa, isquemia mesentérica, SCA e embolia pulmonar já foram mesclados e
revisados (`review_status: revisado`) em `main`, além de features não
relacionadas (exportação em PDF/PowerPoint/Word, Central de Cardiologia
Intensiva/UCO). O branch deste hub foi resetado e reconstruído a partir do
`main` atual antes do commit para evitar abrir um PR com diff conflitante ou
revertendo conteúdo já mesclado por terceiros.
