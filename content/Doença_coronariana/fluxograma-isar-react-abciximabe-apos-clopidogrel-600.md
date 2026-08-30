---
title: "Fluxograma: ISAR-REACT — eletivo NS, SCA P=0,03, bivalirudina líquido NS"
slug: fluxograma-isar-react-abciximabe-apos-clopidogrel-600
theme: "Doença coronariana"
kind: fluxograma
summary: "ISAR-REACT: eletivo após clopidogrel 600, abciximabe 4% vs 4% P=0,82. ISAR-REACT 2: SCA sem supra, 8,9% vs 11,9% P=0,03; interação troponina P=0,07. ISAR-REACT 3: bivalirudina vs HNF, líquido P=0,57. ISAR-REACT 5 é P2Y12, outro arquivo."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em ISAR-REACT PMID 14724302, ISAR-REACT 2 PMID 16533938, ISAR-REACT 3 PMID 18703471. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Kastrati A, et al. ISAR-REACT. N Engl J Med. 2004;350(3):232-238. PMID: 14724302."
  - "Kastrati A, et al. ISAR-REACT 2. JAMA. 2006;295(13):1531-1538. PMID: 16533938."
  - "Kastrati A, et al. ISAR-REACT 3. N Engl J Med. 2008;359(7):688-696. PMID: 18703471."
---

# Fluxograma: qual ISAR-REACT está sendo citado?

```mermaid
flowchart TD
  R0["Clopidogrel 600 mg ≥2 h. GPI ou bivalirudina?"] --> D1{"Qual a população?"}

  D1 -->|"ICP eletiva, baixo-intermediário risco<br/>(ISAR-REACT)"| C1(["Não. Primário 4% vs 4%; P=0,82<br/>Trombocitopenia profunda 1% vs 0"])

  D1 -->|"SCA sem supra na ICP<br/>(ISAR-REACT 2)"| C2(["Primário 8,9% vs 11,9%; P=0,03<br/>Troponina normal empatou; interação P=0,07"])

  D1 -->|"Troponina normal, bivalirudina vs HNF<br/>(ISAR-REACT 3)"| C3(["Líquido P=0,57. Sangra menos, isquemia não cai"])

  D1 -->|"Prasugrel vs ticagrelor"| C4(["ISAR-REACT 5 — outro arquivo da casa"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**O número no nome não é a mesma pergunta.** Eletivo NS; SCA mede; bivalirudina empata no líquido.
