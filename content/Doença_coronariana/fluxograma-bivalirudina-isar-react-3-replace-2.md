---
title: "Fluxograma: bivalirudina na ICP eletiva — ISAR-REACT 3 vs REPLACE-2"
slug: fluxograma-bivalirudina-isar-react-3-replace-2
theme: "Doença coronariana"
kind: fluxograma
summary: "Troponina normal, clopidogrel 600: ISAR-REACT 3 líquido P=0,57 vs HNF. REPLACE-2: vs HNF+GPI, primário P=0,32, menos sangra. IAM: HEAT/VALIDATE. Lise: HERO-2 morte NS."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em ISAR-REACT 3 PMID 18703471 e REPLACE-2 PMID 12588269. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Kastrati A, et al. ISAR-REACT 3. N Engl J Med. 2008;359(7):688-696. PMID: 18703471."
  - "Lincoff AM, et al. REPLACE-2. JAMA. 2003;289(7):853-863. PMID: 12588269."
---

# Fluxograma: bivalirudina fora do IAM

```mermaid
flowchart TD
  R0["ICP sem supra, quer citar bivalirudina"] --> D1{"Qual o comparador e o biomarcador?"}

  D1 -->|"Troponina normal vs HNF monoterapia"| C1(["ISAR-REACT 3: líquido P=0,57<br/>Isquêmico P=0,23<br/>Sangramento maior P=0,008"])

  D1 -->|"Vs HNF + GPI planejada"| C2(["REPLACE-2: primário P=0,32<br/>Isquêmico P=0,40<br/>Sangramento maior 2,4% vs 4,1%"])

  D1 -->|"IAM / ICP primária"| C3(["HEAT, VALIDATE, EUROMAX<br/>Não misturar com ISAR-REACT 3"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**ISAR-REACT 3 não é benefício líquido contra HNF. REPLACE-2 empata o isquêmico contra GPI planejada.**
