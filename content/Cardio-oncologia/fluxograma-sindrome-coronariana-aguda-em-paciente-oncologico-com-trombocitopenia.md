---
title: "Fluxograma: SCA em paciente oncológico com trombocitopenia"
slug: fluxograma-sindrome-coronariana-aguda-em-paciente-oncologico-com-trombocitopenia
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para SCA em paciente com câncer e plaquetopenia, com estratégia invasiva e antiagregação guiadas também pelo risco hemorrágico."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568.", "Gevaert SA, et al. Eur Heart J Acute Cardiovasc Care. 2021;10(8):947-959."]
---

# SCA no paciente oncológico com trombocitopenia

```mermaid
flowchart TD
  R0["Paciente com câncer + suspeita de SCA<br/>± trombocitopenia"]
  P1["ECG + troponina + monitorização<br/>+ hemograma/plaquetas + eco precoce"]
  D1{"STEMI, choque, edema pulmonar,<br/>TV ou NSTE-ACS de alto risco?"}
  P2["Estratégia invasiva urgente;<br/>preferir acesso radial"]
  P3["Estável/baixo risco: individualizar<br/>invasivo vs. conservador conforme prognóstico<br/>oncológico e risco hemorrágico"]
  D2{"Plaquetas ≥30.000/µL?"}
  P4["PCI pode ser considerada<br/>se clinicamente indicada"]
  P5["Abaixo de 30.000/µL:<br/>discutir correção/transfusão e risco-benefício<br/>antes de PCI, sem atrasar decisão vital"]
  D3{"Plaquetas ≥10.000/µL?"}
  P6["AAS pode ser utilizado se não houver<br/>outra contraindicação"]
  P7["AAS requer decisão individualizada/<br/>suporte hematológico"]
  D4{"Plaquetas ≥30.000/µL e DAPT indicada?"}
  P8["Preferir AAS + clopidogrel;<br/>minimizar duração se alto risco de sangramento"]
  P9["Reavaliar DAPT; evitar extrapolar<br/>prasugrel/ticagrelor em plaquetopenia grave"]
  C1(["Revisar terapia oncológica causal<br/>+ decisão cardio-oncológica após estabilização"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P3
  P2 --> D2
  P3 --> D2
  D2 -->|"Sim"| P4
  D2 -->|"Não"| P5
  P4 --> D3
  P5 --> D3
  D3 -->|"Sim"| P6
  D3 -->|"Não"| P7
  P6 --> D4
  P7 --> D4
  D4 -->|"Sim"| P8
  D4 -->|"Não"| P9
  P8 --> C1
  P9 --> C1

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1 conduta;
```

## Regra prática

**Plaquetopenia modifica a estratégia, mas não transforma SCA em contraindicação à reperfusão.** O risco hemorrágico deve ser reduzido sem abandonar tratamento isquêmico potencialmente salvador.