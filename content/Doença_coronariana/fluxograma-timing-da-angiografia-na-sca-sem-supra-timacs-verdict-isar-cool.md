---
title: "Fluxograma: timing da angiografia na SCA sem supra — TIMACS e VERDICT NS; ISAR-COOL piora ao adiar"
slug: fluxograma-timing-da-angiografia-na-sca-sem-supra-timacs-verdict-isar-cool
theme: "Doença coronariana"
kind: fluxograma
summary: "Já decidido o invasivo: TIMACS ≤24 vs ≥36 h primário P=0,15 NS (secundário não vende). VERDICT <12 vs 48–72 h HR 0,92 IC cruza 1; GRACE>140 IC inclui 1. ISAR-COOL 3–5 d vs <6 h piora P=0,04. RIDDLE n=323, efeito pré-cateter. Não reescreve FRISC/TACTICS/ICTUS nem o fluxograma ESC 2023."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em TIMACS PMID 19458363, VERDICT PMID 30565996, ISAR-COOL PMID 14506118 e RIDDLE PMID 26777321. Companheiro, não substituto, de fluxograma-invasivo-precoce-versus-seletivo-frisc-ii-tactics-ictus. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Mehta SR, et al. TIMACS. N Engl J Med. 2009;360(21):2165-2175. PMID: 19458363."
  - "Kofoed KF, et al. VERDICT. Circulation. 2018;138(24):2741-2750. PMID: 30565996."
  - "Neumann FJ, et al. ISAR-COOL. JAMA. 2003;290(12):1593-1599. PMID: 14506118."
  - "Milosevic A, et al. RIDDLE-NSTEMI. JACC Cardiovasc Interv. 2016;9(6):541-549. PMID: 26777321."
---

# Fluxograma: quando cateterizar, uma vez decidido o invasivo

```mermaid
flowchart TD
  R0["SCA sem supra.<br/>Invasivo já escolhido. Qual a hora?"] --> D1{"Qual ensaio está sendo citado?"}

  D1 -->|"≤24 h vs ≥36 h"| C1(["TIMACS: primário 9,6% vs 11,3%; P=0,15 NS<br/>Secundário P=0,003 — não vender"])

  D1 -->|"<12 h vs 48–72 h"| C2(["VERDICT: HR 0,92; IC 0,78–1,08<br/>GRACE>140 HR 0,81; IC inclui 1,00"])

  D1 -->|"Adiar 3–5 d para esfriar"| C3(["ISAR-COOL: 11,6% vs 5,9%; P=0,04<br/>Pior no adiamento. Eventos pré-cateter"])

  D1 -->|"<2 h vs 2–72 h, n=323"| C4(["RIDDLE: 4,3% vs 13% aos 30 d<br/>10 IAM pré-cateter no tardio. Não anula TIMACS"])

  R0 --> D2{"É invasivo vs conservador?"}

  D2 -->|"FRISC II / TACTICS / ICTUS"| C5(["Outro fluxograma da casa.<br/>Pergunta diferente"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**Decidido o invasivo, TIMACS e VERDICT não mostram que muito precoce ganha o primário.** Adiar dias para “esfriar” (ISAR-COOL) piora. RIDDLE é pequeno e não reescreve os dois grandes.
