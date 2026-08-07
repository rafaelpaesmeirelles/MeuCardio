---
title: "Fluxograma: QT/torsades por trióxido de arsênio"
slug: fluxograma-prolongamento-de-qt-e-torsades-por-trioxido-de-arsenio
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore para QT prolongado durante trióxido de arsênio, com ECG seriado, correção de eletrólitos e escalada para torsades."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568."]
---

# QT prolongado durante trióxido de arsênio

```mermaid
flowchart TD
  R0["Paciente em trióxido de arsênio"]
  P1["QTcF basal + K/Mg/Ca/renal;<br/>ECG semanal nas primeiras 8 semanas"]
  D1{"Síncope, TV polimórfica,<br/>torsades ou PCR?"}
  C1(["Sim: interromper agentes QT-prolongadores<br/>+ protocolo de torsades/PCR"])
  D2{"QTcF ≥500 ms?"}
  P2["Alto risco: corrigir fatores reversíveis<br/>+ revisão cardio-oncológica imediata<br/>+ rever continuidade do arsênio"]
  D3{"QTcF 480–499 ms?"}
  P3["Monitorização mais estreita;<br/>rever eletrólitos, interações e sintomas"]
  D4{"Aumento >60 ms do basal<br/>mas QTcF <500 ms?"}
  P4["Não interromper automaticamente;<br/>avaliar contexto e risco global"]
  C2(["Continuar vigilância;<br/>reavaliar após mudanças clínicas/dose"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| P2
  D2 -->|"Não"| D3
  P2 --> C2
  D3 -->|"Sim"| P3
  D3 -->|"Não"| D4
  P3 --> C2
  D4 -->|"Sim"| P4
  D4 -->|"Não"| C2
  P4 --> C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

Trióxido de arsênio combina **alta frequência de QT prolongado com risco real de arritmia ventricular**; sintomas e QTcF ≥500 ms exigem resposta imediata, não espera pelo próximo ECG programado.