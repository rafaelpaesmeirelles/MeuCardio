---
title: "Fluxograma: QT/torsades por trióxido de arsênio"
slug: fluxograma-prolongamento-de-qt-e-torsades-por-trioxido-de-arsenio
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore para QT prolongado durante trióxido de arsênio, com ECG seriado, correção de eletrólitos e escalada para torsades."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568.", "U.S. National Library of Medicine. DailyMed: TRISENOX (arsenic trioxide) Prescribing Information, sections 2.3 and 5.2. SPL version 20, effective 2025-10-28. Set ID 101fc347-d0ad-4aee-8b06-9feb187fd741."]
review_note: "Revisado em 26/08/2026 contra as seções 2.3 e 5.2 da rotulagem regulatória DailyMed de TRISENOX, SPL versão 20, efetiva em 28/10/2025, e a diretriz ESC 2022 de cardio-oncologia (PMID 36017568). Corrigido erro material que aplicava QTcF >=500 ms e um ramo de mera revisão de continuidade: a regra específica da bula usa QTc de Framingham >450 ms em homens ou >460 ms em mulheres para suspender TRISENOX e outros fármacos que prolongam QT. Foram incluídas as metas K >4 mEq/L e Mg >1,8 mg/dL e a retomada escalonada 0,075 mg/kg/dia por uma semana, 0,11 mg/kg/dia por outra semana e 0,15 mg/kg/dia apenas sem novo prolongamento. Pendente revisão médica independente antes de uso assistencial."
---

# QT prolongado durante trióxido de arsênio

```mermaid
flowchart TD
  R0["Paciente em trióxido de arsênio<br/>com ECG alterado ou em monitorização"]
  P1["QTc por Framingham + K/Mg/Ca + função renal;<br/>revisar fármacos que prolongam QT<br/>ou provocam perda eletrolítica"]
  D1{"Síncope, TV polimórfica,<br/>torsades ou PCR?"}
  C1(["Interromper TRISENOX e co-agressores;<br/>protocolo imediato de torsades/TV/PCR<br/>+ cardio-oncologia/hematologia antes de reexposição"])
  D2{"QTc Framingham >450 ms no homem<br/>ou >460 ms na mulher?"}
  P2["Suspender TRISENOX e fármacos que prolongam QT;<br/>corrigir eletrólitos: manter K >4 mEq/L<br/>e Mg >1,8 mg/dL"]
  D3{"QTc normalizou<br/>e eletrólitos foram corrigidos?"}
  P3["Manter suspenso + ECG e eletrólitos seriados"]
  P4["Retomar 0,075 mg/kg/dia por 1 semana"]
  D4{"Sem novo prolongamento do QTc?"}
  P5["Aumentar para 0,11 mg/kg/dia por 1 semana"]
  D5{"Permanece sem prolongamento<br/>durante os 14 dias de escalada?"}
  P6["Pode aumentar para 0,15 mg/kg/dia"]
  C2(["Abaixo do limiar e sem arritmia:<br/>ECG semanal; mais frequente se instável<br/>ou se co-agressor não puder ser suspenso"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| P2
  D2 -->|"Não"| C2
  P2 --> D3
  D3 -->|"Não"| P3
  P3 --> D3
  D3 -->|"Sim"| P4
  P4 --> D4
  D4 -->|"Não"| P2
  D4 -->|"Sim"| P5
  P5 --> D5
  D5 -->|"Não"| P2
  D5 -->|"Sim"| P6
  P6 --> C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

Trióxido de arsênio combina **alta frequência de QT prolongado com risco real de arritmia ventricular**. Neste fármaco, não se deve importar o limiar genérico de QTcF ≥500 ms: a bula usa QTc de Framingham >450 ms no homem ou >460 ms na mulher para suspensão e exige retomada escalonada. Arritmia ventricular ou QTc prolongado já presentes antes da dose contraindicam administrar TRISENOX até avaliação e correção.
