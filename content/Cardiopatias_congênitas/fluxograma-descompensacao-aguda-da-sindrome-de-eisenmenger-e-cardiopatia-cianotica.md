---
title: "Fluxograma: descompensação aguda de Eisenmenger/cardiopatia cianótica"
slug: fluxograma-descompensacao-aguda-da-sindrome-de-eisenmenger-e-cardiopatia-cianotica
theme: "Cardiopatias congênitas"
kind: fluxograma
summary: "Árvore de emergência para piora aguda em Eisenmenger, evitando flebotomia, oxigênio e anticoagulação reflexos."
review_status: revisado
source_refs: ["Baumgartner H, De Backer J, Babu-Narayan SV, et al. 2020 ESC Guidelines for the management of adult congenital heart disease. Eur Heart J. 2021;42(6):563-645. DOI: 10.1093/eurheartj/ehaa554. PMID: 32860028."]
---

# Descompensação aguda de Eisenmenger

```mermaid
flowchart TD
  R0["Eisenmenger/cardiopatia cianótica<br/>+ piora aguda em relação ao basal"]
  P1["ECG + hemograma/plaquetas + função renal<br/>+ eco + procurar infecção, desidratação,<br/>arritmia, trombose e hemorragia"]
  D1{"Hiperviscosidade sintomática<br/>+ Hct >65%?"}
  D2{"Há desidratação ou<br/>deficiência de ferro?"}
  C1(["Sim: NÃO flebotomizar;<br/>corrigir causa primeiro"])
  P2["Sem desidratação/ferro baixo:<br/>flebotomia terapêutica pode ser considerada<br/>em centro especializado"]
  D3{"Arritmia atrial ou trombose/embolia?"}
  P3["Avaliar anticoagulação individualmente<br/>após estimar risco de sangramento"]
  D4{"Hemoptise/sangramento ativo?"}
  C2(["Sim: controlar sangramento;<br/>não anticoagular automaticamente"])
  D5{"Falência direita/choque?"}
  P4["Tratar gatilho + evitar hipóxia/acidose;<br/>otimizar volume e pressão com cautela"]
  C3(["Centro ACHD/HP especializado;<br/>linhas IV com filtro de ar"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| D2
  D1 -->|"Não"| D3
  D2 -->|"Sim"| C1
  D2 -->|"Não"| P2
  C1 --> D3
  P2 --> D3
  D3 -->|"Sim"| P3
  D3 -->|"Não"| D4
  P3 --> D4
  D4 -->|"Sim"| C2
  D4 -->|"Não"| D5
  C2 --> D5
  D5 -->|"Sim"| P4
  D5 -->|"Não"| C3
  P4 --> C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

No Eisenmenger, **alto hematócrito, baixa saturação e risco trombótico são parte de uma fisiologia adaptada**; nenhum deles deve disparar automaticamente flebotomia, oxigênio contínuo ou anticoagulação.