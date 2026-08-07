---
title: "Fluxograma: bloqueio AV congênito completo no recém-nascido"
slug: fluxograma-bloqueio-av-congenito-completo-no-recem-nascido
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore neonatal para CCAVB, usando sintomas, função ventricular, escape e FC média ≤50 bpm como critérios PACES para pacing."
review_status: revisado
source_refs: ["Shah MJ, Silka MJ, Avari Silva JN, et al. Heart Rhythm. 2021. DOI: 10.1016/j.hrthm.2021.07.051. PMID: 34363987."]
---

# BAV congênito completo neonatal

```mermaid
flowchart TD
  R0["Recém-nascido com BAV<br/>congênito completo"]
  P1["ECG + frequência média + escape/QRS<br/>+ ectopia + eco/função ventricular"]
  D1{"Bradicardia sintomática,<br/>baixo débito ou IC?"}
  C1(["Sim: marcapasso permanente<br/>indicado — PACES Classe I"])
  D2{"Escape QRS largo, ectopia ventricular<br/>complexa ou disfunção ventricular?"}
  C2(["Sim: marcapasso permanente<br/>indicado — Classe I"])
  D3{"Assintomático, neonato/lactente<br/>com FC ventricular média ≤50 bpm?"}
  C3(["Sim: marcapasso permanente<br/>indicado — Classe I"])
  C4(["Não: seguimento especializado;<br/>FC isolada não exclui baixo débito"])
  D4{"Instável enquanto aguarda<br/>implante definitivo?"}
  P2["Pacing/cronotropismo de ponte<br/>conforme protocolo neonatal"]

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| C4
  C1 --> D4
  C2 --> D4
  C3 --> D4
  D4 -->|"Sim"| P2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Regra prática

**≤50 bpm é critério de pacing no neonato/lactente assintomático, mas não é um corte de segurança acima do qual o bebê esteja automaticamente bem.**