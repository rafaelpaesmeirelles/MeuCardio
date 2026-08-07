---
title: "Fluxograma: Parada cardiorrespiratória pediátrica (AHA/AAP 2025)"
slug: fluxograma-parada-cardiorrespiratoria-pediatrica-aha-aap-2025
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de decisão para PCR pediátrica, separando FV/TV sem pulso de assistolia/AESP e incorporando energia por peso, epinefrina e antiarrítmico conforme AHA/AAP 2025."
review_status: revisado
source_refs: ["Lasa JJ, Dhillon GS, Duff JP, et al. Part 8: Pediatric Advanced Life Support: 2025 American Heart Association and American Academy of Pediatrics Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(16_suppl_2):S479-S537. DOI: 10.1161/CIR.0000000000001368. PMID: 41122885.", "American Heart Association/American Academy of Pediatrics. Pediatric Cardiac Arrest Algorithm. 2025 CPR & ECC Guidelines. Algoritmo oficial consultado em heart.org nesta sessão."]
---

# Parada cardiorrespiratória pediátrica

```mermaid
flowchart TD
  R0["Lactente/criança sem pulso<br/>ou com sinais de PCR"]
  P1["Iniciar RCP + bolsa-máscara/O2<br/>e conectar monitor/desfibrilador"]
  D1{"Ritmo chocável?"}
  P2["FV/TV sem pulso: choque 2 J/kg"]
  P3["RCP 2 min + acesso IV/IO"]
  D2{"Permanece chocável?"}
  P4["2º choque: 4 J/kg"]
  P5["RCP 2 min + epinefrina 0,01 mg/kg IV/IO<br/>a cada 3–5 min; considerar via aérea avançada"]
  D3{"Permanece chocável?"}
  P6["Choque ≥4 J/kg<br/>(máx. 10 J/kg ou dose adulta)"]
  P7["RCP 2 min + amiodarona 5 mg/kg<br/>(máx. 300 mg; até 3 doses) OU lidocaína 1 mg/kg;<br/>tratar causas reversíveis"]
  P8["Assistolia/AESP: RCP 2 min,<br/>acesso IV/IO e epinefrina ASAP<br/>0,01 mg/kg; repetir a cada 3–5 min"]
  D4{"Ritmo tornou-se chocável?"}
  P9["RCP 2 min + tratar causas reversíveis"]
  D5{"ROSC?"}
  C1(["ROSC: iniciar cuidados pós-PCR pediátrica"])
  C2(["Sem ROSC: continuar ciclos de 2 min,<br/>reavaliar ritmo e causas reversíveis"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P8
  P2 --> P3
  P3 --> D2
  D2 -->|"Sim"| P4
  D2 -->|"Não"| P8
  P4 --> P5
  P5 --> D3
  D3 -->|"Sim"| P6
  D3 -->|"Não"| P8
  P6 --> P7
  P7 --> D3
  P8 --> D4
  D4 -->|"Sim"| P4
  D4 -->|"Não"| P9
  P9 --> D5
  D5 -->|"Sim"| C1
  D5 -->|"Não"| C2
  C2 --> P8

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## RCP de alta qualidade

- 100–120 compressões/min.
- Profundidade ≥1/3 do diâmetro anteroposterior do tórax.
- Retorno completo e interrupções mínimas.
- Trocar compressor a cada 2 minutos ou antes se houver fadiga.
- Com via aérea avançada: compressões contínuas e 1 ventilação a cada 2–3 segundos.

## Causas reversíveis

Hipovolemia, hipóxia, acidose, hipoglicemia, hipo/hipercalemia, hipotermia, pneumotórax hipertensivo, tamponamento cardíaco, toxinas, trombose pulmonar e trombose coronariana.
