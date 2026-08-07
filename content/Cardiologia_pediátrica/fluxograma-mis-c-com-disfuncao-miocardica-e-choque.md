---
title: "Fluxograma: MIS-C com disfunção miocárdica e choque"
slug: fluxograma-mis-c-com-disfuncao-miocardica-e-choque
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de emergência para MIS-C cardiovascular grave, integrando choque, IVIG, glicocorticoide, função ventricular e risco trombótico."
review_status: revisado
source_refs: ["Henderson LA, Canna SW, Friedman KG, et al. Arthritis Rheumatol. 2022;74(4):e1-e20. DOI: 10.1002/art.42062. PMID: 35118829."]
---

# MIS-C com disfunção miocárdica/choque

```mermaid
flowchart TD
  R0["Suspeita de MIS-C + choque,<br/>troponina/BNP elevados ou disfunção cardíaca"]
  P1["ECG + troponina/BNP + TTE<br/>+ inflamatórios/coagulação + telemetria"]
  D1{"Choque/disfunção ventricular?"}
  P2["UTI + suporte hemodinâmico<br/>guiado por eco/estado volêmico"]
  P3["Avaliar função/volume antes da IVIG"]
  D2{"Hospitalizado com MIS-C<br/>e indicação de imunomodulação?"}
  P4["IVIG 2 g/kg (máx. 100 g)<br/>+ glicocorticoide 1–2 mg/kg/dia"]
  D3{"Disfunção cardíaca importante/<br/>risco de sobrecarga?"}
  P5["Considerar IVIG dividida:<br/>1 g/kg/dia por 2 dias"]
  D4{"Refratário após primeira IVIG?"}
  P6["Não repetir IVIG rotineiramente;<br/>considerar intensificação especializada"]
  D5{"FE <35%, trombose ou CAA z ≥10?"}
  P7["Considerar anticoagulação terapêutica<br/>conforme protocolo pediátrico"]
  C1(["Seguimento cardiológico:<br/>ECG/biomarcadores + eco seriado"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P3
  P2 --> P3
  P3 --> D2
  D2 -->|"Sim"| P4
  D2 -->|"Não"| C1
  P4 --> D3
  D3 -->|"Sim"| P5
  D3 -->|"Não"| D4
  P5 --> D4
  D4 -->|"Sim"| P6
  D4 -->|"Não"| D5
  P6 --> D5
  D5 -->|"Sim"| P7
  D5 -->|"Não"| C1
  P7 --> C1

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1 conduta;
```

## Regra prática

No MIS-C com coração comprometido, **não administre IVIG como se a função ventricular fosse normal**: primeiro defina o volume e a função, depois imunomodulação e antitrombose.