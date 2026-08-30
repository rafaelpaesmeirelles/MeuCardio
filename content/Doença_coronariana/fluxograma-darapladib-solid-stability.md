---
title: "Fluxograma: darapladib — SOLID-TIMI 52 e STABILITY"
slug: fluxograma-darapladib-solid-stability
theme: "Doença coronariana"
kind: fluxograma
summary: "Pós-SCA: SOLID-TIMI 52, primário HR 1,00. DAC estável: STABILITY, primário HR 0,94 P=0,20. Secundários de STABILITY não resgatam. Lp-PLA2 não é o alvo da colchicina nem do CANTOS."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em SOLID-TIMI 52 PMID 25173516 e STABILITY PMID 24678955. Revisão científica concluída em 30/08/2026."
source_refs:
  - "O'Donoghue ML, et al. SOLID-TIMI 52. JAMA. 2014;312(10):1006-1015. PMID: 25173516."
  - "White HD, et al. STABILITY. N Engl J Med. 2014;370(18):1702-1711. PMID: 24678955."
---

# Fluxograma: darapladib (Lp-PLA2)

```mermaid
flowchart TD
  R0["Quer inibir Lp-PLA2 com darapladib?"] --> D1{"Qual o cenário?"}

  D1 -->|"≤30 dias após SCA<br/>(SOLID-TIMI 52)"| C1(["Não. Primário 16,3% vs 15,6%<br/>HR 1,00 P=0,93"])

  D1 -->|"DAC estável<br/>(STABILITY)"| C2(["Não. Primário 9,7% vs 10,4%<br/>HR 0,94 P=0,20.<br/>Secundário com IC que toca 1,00 não vale"])

  R0 --> C3(["Inflamação residual é CANTOS/colchicina,<br/>não este enzima"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**Dois ensaios, dois primários falhos.** Não prescrever darapladib. Não misturar com CANTOS.
