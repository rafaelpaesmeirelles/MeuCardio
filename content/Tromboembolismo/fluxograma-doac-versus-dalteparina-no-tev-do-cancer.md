---
title: "Fluxograma: DOAC vs dalteparina no TEV do câncer — Hokusai (composto NI, mais sangramento), CARAVAGGIO (recorrência NI), SELECT-D (piloto)"
slug: fluxograma-doac-versus-dalteparina-no-tev-do-cancer
theme: "Tromboembolismo"
kind: fluxograma
summary: "Hokusai VTE Cancer: composto NI; sangramento maior sobe. CARAVAGGIO: recorrência NI; sangramento maior igual. SELECT-D: piloto, CRNMB sobe. ADAM-VTE é outro n. Não fundir com Hokusai-VTE sem câncer."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em Hokusai VTE Cancer PMID 29231094, CARAVAGGIO PMID 32223112, SELECT-D. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Raskob GE, et al. Hokusai VTE Cancer. N Engl J Med. 2018;378(7):615-624. PMID: 29231094."
  - "Agnelli G, et al. CARAVAGGIO. N Engl J Med. 2020;382(17):1599-1607. PMID: 32223112."
  - "Documento da casa select-d-rivaroxabana-versus-dalteparina-no-tev-associado-ao-cancer."
  - "Documento da casa adam-vte-apixabana-versus-dalteparina-no-tev-associado-ao-cancer."
  - "Documento da casa fluxograma-hbpm-versus-varfarina-e-doac-no-tev-do-cancer."
---

# Fluxograma: DOAC no TEV do câncer

```mermaid
flowchart TD
  R0["TEV no câncer. Qual ensaio?"] --> D1{"Qual a pergunta?"}

  D1 -->|"Edoxabana vs dalteparina"| C1(["Hokusai-Câncer: composto NI<br/>Sangramento maior sobe"])

  D1 -->|"Apixabana vs dalteparina"| C2(["CARAVAGGIO: recorrência NI<br/>Sangramento maior 3,8% vs 4,0%"])

  D1 -->|"Rivaroxabana piloto"| C3(["SELECT-D: não é confirmatório<br/>CRNMB sobe"])

  D1 -->|"Hokusai sem câncer?"| C4(["Outro ensaio — dump AMPLIFY/EINSTEIN"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**NI não é superioridade.** Hokusai-Câncer e Hokusai-VTE não são o mesmo paper.
