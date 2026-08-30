---
title: "Fluxograma: tirofibana pré-hospitalar — On-TIME 1 (TIMI 3 NS) vs On-TIME 2 (desvio de ST)"
slug: fluxograma-gpi-pre-hospitalar-on-time-1-on-time-2
theme: "Doença coronariana"
kind: fluxograma
summary: "On-TIME 1: primário TIMI 3 19% vs 15% P=0,22; morte/IAM 1 a 7% vs 7%. On-TIME 2: primário ST 3,6 vs 4,8 mm; morte ausente no abstract. Não fundir os dois nem vender surrogado como mortalidade."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em On-TIME PMID 15140531 e On-TIME 2 PMID 18707985. Revisão científica concluída em 30/08/2026."
source_refs:
  - "van 't Hof AW, et al. On-TIME. Eur Heart J. 2004;25(10):837-846. PMID: 15140531."
  - "Van't Hof AW, et al. On-TIME 2. Lancet. 2008;372(9638):537-546. PMID: 18707985."
  - "Documento da casa atlantic-ticagrelor-pre-hospitalar-no-iamcsst."
---

# Fluxograma: GPI no caminho da ICP primária

```mermaid
flowchart TD
  R0["Tirofibana antes da sala?"] --> D1{"Qual o ensaio?"}

  D1 -->|"On-TIME 1, n=507"| C1(["Primário TIMI 3: 19% vs 15% P=0,22<br/>Morte/IAM 1 a: 7% vs 7%"])

  D1 -->|"On-TIME 2, n=984"| C2(["Primário: desvio residual de ST<br/>Morte/IAM ausentes no abstract"])

  D1 -->|"Ticagrelor na ambulância?"| C3(["ATLANTIC — outro mecanismo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**On-TIME 1 não venceu o primário. On-TIME 2 venceu milímetro de ST.** Nenhum dos abstracts vende morte.
