---
title: "Fluxograma: Prolongamento de QT por ribociclibe e risco de torsades"
slug: fluxograma-prolongamento-qt-por-ribociclibe-e-risco-de-torsades
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de emergência para paciente oncológico em ribociclibe com QTcF prolongado, síncope ou arritmia ventricular, incorporando interrupção do fármaco, correção de fatores reversíveis e transição imediata para protocolo de torsades quando presente."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al.; ESC Scientific Document Group. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568.", "U.S. Food and Drug Administration / DailyMed. KISQALI (ribociclib) Prescribing Information, Table 4 — Dose Modification and Management for QT Prolongation. Rotulagem vigente consultada nesta sessão (2026).", "Hortobagyi GN, Stemmer SM, Burris HA, et al. Ribociclib as First-Line Therapy for HR-Positive, Advanced Breast Cancer. N Engl J Med. 2016;375(18):1738-1748. DOI: 10.1056/NEJMoa1609709. PMID: 27717303."]
---

# QT prolongado por ribociclibe — emergência

```mermaid
flowchart TD
  R0["Paciente em ribociclibe com QTcF prolongado,<br/>palpitação, síncope, pré-síncope ou arritmia"]
  P1["ECG imediato com QTcF (Fridericia) +<br/>K/Mg/Ca + função renal/hepática +<br/>revisão de outros fármacos que prolongam QT"]
  D1{"TdP, TV polimórfica, instabilidade<br/>ou parada cardíaca?"}
  C1(["Sim: interromper ribociclibe imediatamente<br/>e seguir protocolo de torsades/TV/PCR;<br/>corrigir eletrólitos e retirar co-agressores"])
  D2{"QTcF >500 ms?"}
  P2["Sim: interromper KISQALI até QTcF ≤480 ms;<br/>se recuperar, rotulagem prevê retomada em dose menor;<br/>se >500 ms recidivar, descontinuar"]
  D3{"QTcF >480 e ≤500 ms?"}
  P3["Sim: interromper KISQALI até QTcF ≤480 ms;<br/>retomada depende do cenário oncológico e da rotulagem;<br/>recorrência >480 ms exige redução de dose"]
  C2(["QTcF ≤480 ms sem arritmia grave:<br/>procurar causa alternativa dos sintomas e<br/>seguir monitorização oncológica/cardiológica"])
  D4{"QTcF >500 ms OU aumento >60 ms do basal<br/>E houve TdP, TV polimórfica, síncope ou<br/>sinal/sintoma de arritmia grave?"}
  C3(["Sim: descontinuar KISQALI permanentemente<br/>conforme rotulagem FDA"])
  C4(["Não: decisão de retomada/redução conforme<br/>tabela de dose e contexto oncológico;<br/>ECG mais frequente após evento"])
  C5(["Após estabilização: cardio-oncologia + oncologia;<br/>evitar combinação com novos fármacos QT-prolongadores<br/>e corrigir eletrólitos antes da reexposição"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| P2
  D2 -->|"Não"| D3
  D3 -->|"Sim"| P3
  D3 -->|"Não"| C2
  C1 --> D4
  P2 --> D4
  P3 --> D4
  D4 -->|"Sim"| C3
  D4 -->|"Não"| C4
  C2 --> C5
  C3 --> C5
  C4 --> C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Regras regulatórias verificadas

- **QTcF >480 e ≤500 ms:** interromper ribociclibe até QTcF ≤480 ms; a forma de retomada depende da indicação oncológica e de recorrência, conforme a tabela vigente do KISQALI.
- **QTcF >500 ms:** interromper até QTcF ≤480 ms e, quando a retomada for permitida, reduzir para o próximo nível de dose; se QTcF >500 ms recidivar, descontinuar.
- **Descontinuação permanente:** QTcF >500 ms ou aumento >60 ms do basal associado a torsades de pointes, TV polimórfica, síncope ou sinais/sintomas de arritmia grave.

## Segurança

A emergência elétrica tem prioridade sobre a decisão oncológica de dose. Se houver torsades/TV polimórfica, o paciente migra imediatamente para o protocolo específico de **torsades de pointes e QT longo adquirido** já existente no Modo Emergência.
