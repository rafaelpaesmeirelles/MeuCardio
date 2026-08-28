# Documentos novos para 3 checklists órfãos — 28/08/2026

## Contexto

Trigésimo quinto lote de conteúdo do dia. No lote anterior (PR #650),
identifiquei que 3 dos 8 checklists com `documento_origem` vazio não
tinham candidato real no corpus — não era um problema de vínculo, era
ausência de conteúdo. Duas PRs anteriores fechadas (#460, #465) já
haviam tentado resolver isso apontando para arquivos que **nunca
chegaram a existir** em nenhuma branch do repositório, provável motivo
do fechamento dessas PRs e da lacuna persistir.

Este lote resolve a causa raiz: escreve os 3 documentos narrativos.

## Documentos produzidos

1. **`aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca`**
   (`content/Cardiologia_do_Esporte_e_do_Exercício/`) — indicação
   universal do escore em pré-operatório de cirurgia cardíaca eletiva,
   os 8 componentes, corte ≥3 (sensibilidade 93%/100% para AOS
   moderada-grave/grave, Chung 2012), triagem vs. diagnóstico, fluxo
   bifurcado por tempo até a cirurgia, continuidade de CPAP,
   monitorização estendida, analgesia poupadora de opioide, vínculo
   com fibrilação atrial pós-RM (Qaddoura 2014), planejamento de
   recursos, fechamento do ciclo diagnóstico pós-alta.
2. **`manejo-da-abstinencia-alcoolica-aguda-com-risco-de-tempestade-autonomica-e-arritmia`**
   (`content/Saúde_mental_e_cardiologia/`) — abstinência como
   tempestade autonômica (não intoxicação), CIWA-Ar seriado, ECG/QTc
   na admissão e repetido, potássio/magnésio, benzodiazepínico guiado
   por escore sem detalhar dose, cautela com antipsicótico e QT,
   critério objetivo para suspender monitorização, estratificação de
   risco para delirium tremens, critérios de UTI, orientação sobre a
   origem real do risco, encaminhamento estruturado pré-alta.
3. **`diagnostico-e-tratamento-da-trombose-de-esforco-sindrome-de-paget-schroetter`**
   (`content/Tromboembolismo/`) — perfil clínico típico, diferenciação
   crucial entre trombose primária (esforço) e secundária (cateter/
   neoplasia), Doppler como triagem, venografia como padrão de
   referência, anticoagulação como base sem detalhar dose, trombólise
   seletiva (ESVS 2021, IIb C, janela de 2 semanas), investigação de
   desfiladeiro torácico, encaminhamento cirúrgico (ESVS 2021, IIb C),
   anticoagulação na janela pré-cirúrgica, retorno à atividade,
   seguimento para síndrome pós-trombótica.

Todos os 3 marcados `review_status: pendente_revisao` — não publicam
sem revisão humana.

## Vínculos fechados

Os 3 checklists correspondentes tiveram `documento_origem` preenchido
apontando para os documentos novos.

## Verificação de citações

Todos os 7 PMIDs usados nos 3 documentos (18431116, 22401881, 2597811,
32511109, 9217919, 21079709, 17141130) foram verificados
individualmente via NCBI e-utils antes da escrita — nenhuma correção
necessária. A referência ESVS 2021 (sem PMID, apenas DOI) e a
referência Qaddoura 2014 (sem PMID fornecido) foram mantidas apenas
com os dados bibliográficos disponíveis, sem inventar PMID.

## Verificações feitas

- Nenhuma dose de fármaco em nenhum dos 3 documentos — verificado
  programaticamente.
- Nenhuma sigla banida ("mWHO", "HFA-ICOS") em nenhum documento.
- Profundidade mínima (>700 palavras de corpo cada) confirmada — os 3
  documentos ficaram entre ~1.170 e ~2.550 palavras.
- Acentuação em português correta, verificada programaticamente.

## Riscos e limitações

- Documentos ficam `review_status: pendente_revisao` — não publicam
  sem revisão humana.
- Nenhuma dose de fármaco é citada em nenhum dos 3.
- A referência à síndrome de Paget-Schroetter reconhece explicitamente
  no `review_note` que não existe diretriz de consenso formal (ESC/
  AHA/ACC/SBC) dedicada ao tema — a conduta descrita reflete a prática
  consolidada nas revisões citadas e a diretriz ESVS 2021 de TEV em
  geral, onde aplicável.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_documentos_novos_checklists_orfaos_28_08.py`: 7
  testes, todos passando (1 correção durante desenvolvimento, ajuste de
  palavra de verificação de acentuação por documento).
- `test_canonical_content_review_status.py`: passando (allowlist
  `PENDENTES_MARKDOWN_AVC` com os 3 novos documentos).
- `app.main` importa sem erro.
- Total: 10 testes executados, 10 passando.

## Branch e PR

Branch `claude/escrever-documentos-checklists-orfaos-20260828`, baseada
em `origin/main` sem drift no momento do commit.
