---
title: "Fluxograma: descompensação aguda da amiloidose cardíaca no idoso"
slug: fluxograma-descompensacao-aguda-da-amiloidose-cardiaca-no-idoso
theme: "Cardiologia geriátrica"
kind: fluxograma
summary: "Árvore de emergência para congestão, hipotensão, FA e bradiarritmia em idoso com amiloidose cardíaca."
review_status: revisado
source_refs: ["Kittleson MM, Ruberg FL, Ambardekar AV, et al. 2023 ACC Expert Consensus Decision Pathway on Comprehensive Multidisciplinary Care for the Patient With Cardiac Amyloidosis. J Am Coll Cardiol. 2023;81(11):1076-1126. DOI: 10.1016/j.jacc.2022.11.022."]
---

# Descompensação aguda da amiloidose cardíaca

```mermaid
flowchart TD
  R0["Idoso com amiloidose cardíaca<br/>+ dispneia, edema, hipotensão,<br/>FA ou síncope"]
  P1["Monitorização + ECG + eco<br/>+ função renal/eletrólitos<br/>+ revisar medicações"]
  D1{"Congestão predominante?"}
  P2["Diurese cautelosa com<br/>reavaliação de PA, perfusão e rim"]
  D2{"FA presente?"}
  P3["Avaliar anticoagulação independentemente<br/>do CHA₂DS₂-VASc; se cardioversão,<br/>ETE pelo alto risco de trombo"]
  D3{"Bradicardia/BAV/pausas<br/>ou síncope suspeita?"}
  P4["Telemetria + corrigir causas;<br/>pacing se indicação convencional"]
  D4{"Hipotensão/baixo débito?"}
  P5["Reavaliar volume, ritmo, disautonomia<br/>e fármacos; evitar grande expansão<br/>sem definir mecanismo"]
  C1(["Estabilizar e ajustar terapia<br/>com equipe de IC/amiloidose"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| D2
  P2 --> D2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| D3
  P3 --> D3
  D3 -->|"Sim"| P4
  D3 -->|"Não"| D4
  P4 --> D4
  D4 -->|"Sim"| P5
  D4 -->|"Não"| C1
  P5 --> C1

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1 conduta;
```

## Regra prática

Em amiloidose, **FA e condução são tão importantes quanto congestão**. A piora aguda pode não responder bem a simplesmente intensificar o tratamento convencional de ICFEr.