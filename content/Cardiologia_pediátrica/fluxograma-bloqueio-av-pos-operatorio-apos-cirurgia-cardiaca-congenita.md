---
title: "Fluxograma: BAV pós-operatório após cirurgia cardíaca congênita"
slug: fluxograma-bloqueio-av-pos-operatorio-apos-cirurgia-cardiaca-congenita
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore para BAV avançado pós-operatório, com pacing temporário e decisão de marcapasso permanente segundo PACES."
review_status: revisado
source_refs: ["Shah MJ, Silka MJ, Avari Silva JN, et al. Heart Rhythm. 2021. DOI: 10.1016/j.hrthm.2021.07.051. PMID: 34363987."]
---

# BAV pós-operatório após cirurgia congênita

```mermaid
flowchart TD
  R0["Pós-operatório de cirurgia congênita<br/>+ BAV avançado"]
  P1["ECG/eletrograma + eletrólitos<br/>+ oxigenação + revisar fármacos"]
  D1{"Instabilidade/baixo débito?"}
  P2["Pacing temporário imediato<br/>+ corrigir causas reversíveis"]
  P3["Monitorar condução e manter<br/>pacing de segurança se necessário"]
  D2{"BAV avançado persiste<br/>entre 7 e 10 dias?"}
  C1(["Sim: indicação de marcapasso<br/>permanente — PACES Classe I"])
  D3{"Antes de 7 dias, dano de condução<br/>é considerado irreversível?"}
  C2(["Sim: marcapasso permanente<br/>pode ser considerado precocemente"])
  C3(["Não: manter observação/pacing;<br/>maioria das recuperações ocorre até dia 10"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P3
  P2 --> P3
  P3 --> D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

A janela de **7–10 dias** existe porque grande parte da condução recuperável volta nesse período; ela não deve atrasar pacing necessário nem impedir implante precoce quando recuperação é improvável.