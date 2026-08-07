---
title: "Fluxograma: Crise hipercianótica na Tetralogia de Fallot"
slug: fluxograma-crise-hipercianotica-na-tetralogia-de-fallot
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de decisão para Tet spell, priorizando acalmar, joelho-peito, oxigênio, correção de pré-carga, aumento da resistência vascular sistêmica e redução do espasmo do TSVD."
review_status: revisado
source_refs: ["Hammett O, Griksaitis MJ. Management of tetralogy of Fallot in the pediatric intensive care unit. Front Pediatr. 2023;11:1104533. DOI: 10.3389/fped.2023.1104533. PMID: 37360374. PMCID: PMC10285149.", "van Roekens CN, Zuckerberg AL. Emergency management of hypercyanotic crises in tetralogy of Fallot. Ann Emerg Med. 1995;25(2):256-258. DOI: 10.1016/S0196-0644(95)70335-7. PMID: 7832359."]
---

# Crise hipercianótica na Tetralogia de Fallot

```mermaid
flowchart TD
  R0["Criança com Tetralogia de Fallot/fisiologia semelhante<br/>+ aumento súbito de cianose, hiperpneia e agitação"]
  P1["Reduzir estímulo e acalmar + posição joelho-peito<br/>+ oxigênio em alta concentração + monitorização"]
  D1{"Há sinais de hipovolemia/choque?"}
  P2["Sim: expansão volêmica titulada<br/>com reavaliação frequente"]
  P3["Não: seguir medidas para aumentar RVS<br/>e reduzir espasmo do TSVD"]
  D2{"Crise melhora rapidamente?"}
  C1(["Sim: manter observação, tratar gatilho<br/>e acionar cardiologia pediátrica;<br/>spell grave/recorrente exige plano definitivo"])
  P4["Persistente: analgesia/sedação titulada;<br/>considerar vasopressor alfa para elevar RVS<br/>e betabloqueador para reduzir espasmo infundibular"]
  D3{"Hipoxemia grave, rebaixamento ou<br/>deterioração apesar das medidas?"}
  C2(["Não: continuar monitorização intensiva<br/>e reavaliar perfusão/oxigenação"])
  P5["Sim: UTI/cardiologia pediátrica imediata;<br/>considerar intubação/ventilação com suporte de RVS;<br/>corrigir acidose e gatilhos"]
  D4{"Refratária apesar de suporte avançado?"}
  C3(["Não: estabilizar e encaminhar para<br/>intervenção/correção conforme anatomia"])
  C4(["Sim: discutir ECLS/ECMO e intervenção<br/>cirúrgica/paliativa urgente em centro especializado"])
  D5{"Pulso presente?"}
  C5(["Não: migrar imediatamente para<br/>PCR pediátrica AHA/AAP 2025"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P3
  P2 --> D2
  P3 --> D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| P4
  P4 --> D3
  D3 -->|"Não"| C2
  D3 -->|"Sim"| P5
  P5 --> D5
  D5 -->|"Não"| C5
  D5 -->|"Sim"| D4
  D4 -->|"Não"| C3
  D4 -->|"Sim"| C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Regra fisiológica

O objetivo é quebrar o ciclo de **agitação → maior obstrução dinâmica do TSVD/queda relativa da RVS → mais shunt direita-esquerda → pior hipóxia/acidemia**. Por isso, joelho-peito, redução de estímulo, pré-carga adequada e aumento de RVS são medidas centrais.
