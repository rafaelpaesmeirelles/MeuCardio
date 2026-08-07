---
title: "Fluxograma: NBTE associada ao câncer"
slug: fluxograma-endocardite-trombotica-nao-bacteriana-nbte-associada-ao-cancer
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore para câncer + embolização + vegetação, diferenciando NBTE de endocardite infecciosa e orientando anticoagulação."
review_status: revisado
source_refs: ["Delgado V, Ajmone Marsan N, de Waha S, et al. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44(39):3948-4042. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656."]
---

# NBTE associada ao câncer

```mermaid
flowchart TD
  R0["Câncer/estado pró-trombótico<br/>+ AVC/embolia ou vegetação"]
  P1["Hemoculturas + TTE<br/>+ ETE se suspeita persistente"]
  D1{"Endocardite infecciosa plausível/<br/>culturas ou destruição valvar?"}
  C1(["Sim: migrar para protocolo<br/>de endocardite infecciosa"])
  D2{"Vegetação estéril + contexto<br/>hipercoagulável compatível?"}
  P2["Diagnóstico provável de NBTE;<br/>envolver oncologia/hematologia"]
  D3{"Risco hemorrágico permite<br/>anticoagulação?"}
  P3["Considerar LMWH, HNF ou VKA;<br/>DOAC sem evidência específica para NBTE"]
  P4["Risco hemorrágico alto:<br/>individualizar e tratar fator reversível"]
  D4{"Disfunção valvar grave ou<br/>vegetação grande/êmbolos recorrentes?"}
  C2(["Sim: discutir cirurgia<br/>em equipe multidisciplinar"])
  C3(["Tratar câncer/causa subjacente<br/>+ reavaliar embolização e vegetação"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| P2
  D2 -->|"Não"| C1
  P2 --> D3
  D3 -->|"Sim"| P3
  D3 -->|"Não"| P4
  P3 --> D4
  P4 --> D4
  D4 -->|"Sim"| C2
  D4 -->|"Não"| C3
  C2 --> C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

**Vegetação sem bactéria não significa vegetação sem risco:** NBTE é altamente embólica e exige tratar simultaneamente a hipercoagulabilidade e a causa oncológica.