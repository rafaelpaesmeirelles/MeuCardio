---
title: "Fluxograma: bloqueio AV e distúrbio de condução após TAVI"
slug: fluxograma-bloqueio-av-e-disturbio-de-conducao-apos-tavi
theme: "Cardiologia geriátrica"
kind: fluxograma
summary: "Árvore pós-TAVI para BAV de alto grau, RBBB prévio e novo BRE com monitorização/pacing segundo ESC 2021."
review_status: revisado
source_refs: ["Glikson M, Nielsen JC, Kronborg MB, et al. 2021 ESC Guidelines on cardiac pacing and cardiac resynchronization therapy. Eur Heart J. 2021;42(35):3427-3520. DOI: 10.1093/eurheartj/ehab364. PMID: 34455430."]
---

# Distúrbio de condução após TAVI

```mermaid
flowchart TD
  R0["Pós-TAVI com novo distúrbio<br/>de condução ou bradicardia"]
  D1{"BAV completo/alto grau<br/>com instabilidade?"}
  P1["Pacing temporário imediato<br/>+ suporte de bradicardia"]
  D2{"BAV completo/alto grau<br/>persiste 24–48 h ou surge tardiamente?"}
  C1(["Sim: marcapasso permanente<br/>indicado"])
  D3{"Novo bloqueio de ramo alternante?"}
  C2(["Sim: marcapasso permanente<br/>indicado"])
  D4{"RBBB prévio + novo distúrbio<br/>de condução pós-TAVI?"}
  C3(["Considerar pacing permanente precoce"])
  D5{"Novo BRE com QRS >150 ms<br/>ou PR >240 ms?"}
  P2["Monitorização contínua ambulatorial<br/>7–30 dias ou EPS"]
  D6{"EPS com HV ≥70 ms<br/>ou BAV documentado?"}
  C4(["Favorece marcapasso permanente"])
  C5(["Sem critérios de alto risco:<br/>observação e seguimento"])

  R0 --> D1
  D1 -->|"Sim"| P1
  D1 -->|"Não"| D2
  P1 --> D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| D4
  D4 -->|"Sim"| C3
  D4 -->|"Não"| D5
  D5 -->|"Sim"| P2
  D5 -->|"Não"| C5
  P2 --> D6
  D6 -->|"Sim"| C4
  D6 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Regra prática

**24–48 h** é a janela decisiva para BAV alto grau persistente pós-TAVI; novo BRE isolado exige estratificação por PR/QRS e monitorização, não implante automático.