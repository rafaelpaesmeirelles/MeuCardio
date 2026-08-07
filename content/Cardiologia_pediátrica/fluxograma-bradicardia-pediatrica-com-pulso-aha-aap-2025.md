---
title: "Fluxograma: Bradicardia pediátrica com pulso (AHA/AAP 2025)"
slug: fluxograma-bradicardia-pediatrica-com-pulso-aha-aap-2025
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de conduta para bradicardia pediátrica com pulso: suporte ventilatório primeiro, avaliação de comprometimento cardiopulmonar, RCP se FC <60/min persistente e epinefrina/atropina conforme indicação."
review_status: revisado
source_refs: ["Lasa JJ, Dhillon GS, Duff JP, et al. Part 8: Pediatric Advanced Life Support: 2025 American Heart Association and American Academy of Pediatrics Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(16_suppl_2):S479-S537. DOI: 10.1161/CIR.0000000000001368. PMID: 41122885.", "American Heart Association/American Academy of Pediatrics. Pediatric Bradycardia With a Pulse Algorithm. 2025 CPR & ECC Guidelines. Algoritmo oficial consultado em heart.org nesta sessão."]
---

# Bradicardia pediátrica com pulso

```mermaid
flowchart TD
  R0["Lactente ou criança com bradicardia e pulso"]
  D1{"Há comprometimento cardiopulmonar?<br/>Alteração mental aguda, sinais de choque ou hipotensão"}
  C1(["Sem comprometimento: suporte ABC,<br/>considerar oxigênio e ECG de 12 derivações,<br/>identificar/tratar causa e observar"])
  P1["Manter via aérea pérvia e fornecer oxigênio;<br/>assistir ventilação com pressão positiva se necessário;<br/>monitor cardiorrespiratório e pulso"]
  D2{"Bradicardia persiste com<br/>comprometimento cardiopulmonar?"}
  C2(["Melhorou: identificar e tratar a causa;<br/>manter observação e reavaliação"])
  D3{"FC permanece <60/min apesar de<br/>oxigenação/ventilação adequadas?"}
  P2["Iniciar RCP + obter acesso IV/IO"]
  D4{"Mecanismo provável"}
  C3(["Epinefrina IV/IO 0,01 mg/kg<br/>(0,1 mg/mL; máximo 1 mg)<br/>e tratar causa reversível"])
  C4(["Atropina IV/IO 0,02 mg/kg<br/>se tônus vagal aumentado ou BAV primário;<br/>pode repetir 1 vez; mínimo 0,1 mg,<br/>máximo 0,5 mg por dose"])
  P3["Considerar estimulação cardíaca<br/>transtorácica/transvenosa conforme cenário"]
  D5{"Checagem de pulso a cada 2 min:<br/>pulso presente?"}
  C5(["Sem pulso: migrar imediatamente para<br/>algoritmo de parada cardíaca pediátrica"])
  C6(["Pulso presente: reavaliar comprometimento,<br/>ventilação, causa e resposta ao tratamento"])

  R0 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P1
  P1 --> D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| D3
  D3 -->|"Não"| C2
  D3 -->|"Sim"| P2
  P2 --> D4
  D4 -->|"Bradicardia sintomática sem indicação específica de atropina"| C3
  D4 -->|"Tônus vagal aumentado ou BAV primário"| C4
  C3 --> P3
  C4 --> P3
  P3 --> D5
  D5 -->|"Não"| C5
  D5 -->|"Sim"| C6
  C6 --> D2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Ponto-chave

Na bradicardia pediátrica, **ventilação eficaz vem antes da escalada farmacológica**. O limiar de FC <60/min leva à RCP somente quando a criança continua com comprometimento cardiopulmonar apesar de oxigenação e ventilação adequadas.
