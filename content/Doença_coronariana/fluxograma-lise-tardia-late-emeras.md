---
title: "Fluxograma: lise depois de 6 h — LATE (t-PA, ITT NS) e EMERAS (SK, hospitalar NS)"
slug: fluxograma-lise-tardia-late-emeras
theme: "Doença coronariana"
kind: fluxograma
summary: "LATE: ITT morte NS; 35 d 8,86% vs 10,31% (IC toca 0). Janela <12 h pré-especificada p=0,0229. EMERAS: morte hospitalar 11,9% vs 12,4% NS. Não vender lise rotineira até 24 h."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em LATE PMID 8103874 e EMERAS PMID 8103875. Revisão científica concluída em 30/08/2026."
source_refs:
  - "LATE Study Group. Lancet. 1993;342(8874):759-766. PMID: 8103874."
  - "EMERAS Collaborative Group. Lancet. 1993;342(8874):767-772. PMID: 8103875."
  - "Documento da casa isis-2-estreptoquinase-e-aas-no-iam-suspeito."
  - "Documento da casa gissi-1-estreptoquinase-ev-no-iam."
  - "Documento da casa brave-2-icp-12-a-48-h-no-iamcsst-sem-sintoma-persistente — ICP tardia, primário SPECT."
---

# Fluxograma: lise depois de 6 horas

```mermaid
flowchart TD
  R0["IAM >6 h do início"] --> D1{"Qual o ensaio?"}

  D1 -->|"t-PA 6–24 h"| C1(["LATE: ITT morte NS<br/>35 d 8,86% vs 10,31% (IC 0–28%)"])

  D1 -->|"Recorte <12 h do LATE"| C2(["Pré-especificado 8,90% vs 11,97%<br/>Não é o ITT"])

  D1 -->|"SK até 24 h"| C3(["EMERAS: 11,9% vs 12,4% hospitalar NS<br/>7–12 h IC cruza o nulo"])

  D1 -->|"SK + AAS até 24 h"| C4(["ISIS-2 — outro desenho, mediana 5 h"])

  D1 -->|"ICP 12–48 h sem sintoma persistente"| C5(["BRAVE-2: SPECT menor; composto 30 d P=0,37"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**Nem LATE nem EMERAS vencem o ITT de morte.** Não transformar janela <12 h em “lise até 24 h”.
