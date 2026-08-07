---
title: "Fluxograma: FA pré-excitada/WPW na criança e adolescente"
slug: fluxograma-fibrilacao-atrial-pre-excitada-wpw-na-crianca-e-adolescente
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de emergência para taquicardia irregular pré-excitada, evitando adenosina e demais bloqueadores nodais."
review_status: revisado
source_refs: ["Brugada J, Blom N, Sarquella-Brugada G, et al. Europace. 2013;15(9):1337-1382. DOI: 10.1093/europace/eut082.", "EHRA/EAPCI/AEPC/PACES/HRS/APHRS/LAHRS clinical consensus statement. Europace. 2025;27(4):euaf067."]
---

# FA pré-excitada/WPW pediátrica

```mermaid
flowchart TD
  R0["Criança/adolescente com taquicardia<br/>irregular, muito rápida e QRS largo/variável"]
  P1["Suspeitar FA pré-excitada/WPW;<br/>monitorização + acesso + ECG"]
  D1{"Instabilidade?<br/>choque, isquemia, edema pulmonar,<br/>alteração importante de consciência"}
  C1(["Sim: cardioversão elétrica<br/>sincronizada imediata"])
  D2{"Ritmo irregular com<br/>pré-excitação provável?"}
  P2["NÃO usar adenosina, digoxina,<br/>verapamil/diltiazem ou beta-bloqueador isolado"]
  P3["Estável: procainamida/estratégia que atue<br/>na via acessória ou cardioversão,<br/>conforme protocolo pediátrico"]
  D3{"Degenerou para FV/sem pulso?"}
  C2(["PCR pediátrica + desfibrilação"])
  C3(["Após conversão: eletrofisiologia<br/>e avaliação de ablação da via acessória"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| P2
  D2 -->|"Não"| P3
  P2 --> P3
  P3 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3
  C1 --> C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

Adenosina é excelente em algumas TSVs pediátricas, mas **pode ser perigosa na FA pré-excitada**. A irregularidade do ritmo é a pista que muda o algoritmo.