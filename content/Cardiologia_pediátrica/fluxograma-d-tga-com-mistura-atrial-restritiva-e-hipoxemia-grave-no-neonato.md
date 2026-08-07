---
title: "Fluxograma: d-TGA com mistura atrial restritiva no neonato"
slug: fluxograma-d-tga-com-mistura-atrial-restritiva-e-hipoxemia-grave-no-neonato
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore neonatal para d-TGA com hipoxemia por comunicação atrial restritiva, em que PGE1 pode ser insuficiente e septostomia atrial urgente é necessária."
review_status: revisado
source_refs: ["Della Gatta AN, et al. Am J Obstet Gynecol MFM. 2021;3(5):100379. DOI: 10.1016/j.ajogmf.2021.100379. PMID: 33965655.", "Gottschalk I, et al. Arch Gynecol Obstet. 2024;309(4):1353-1367. DOI: 10.1007/s00404-023-06997-8. PMID: 36971845.", "Balloon atrial septostomy for transposition of the great arteries. PMID: 38091308."]
---

# d-TGA com mistura atrial restritiva

```mermaid
flowchart TD
  R0["Neonato com d-TGA<br/>+ cianose/hipoxemia grave"]
  P1["TTE urgente: fluxo interatrial,<br/>ducto, CIV, função e anatomia"]
  P2["PGE1 conforme protocolo canal-dependente<br/>+ suporte de ventilação/perfusão"]
  D1{"Hipoxemia/acidose persistem<br/>e comunicação atrial é restritiva?"}
  C1(["Não: manter estabilização<br/>e planejar switch arterial"])
  P3["Sim: acionar cardiologia intervencionista<br/>para septostomia atrial por balão urgente"]
  D2{"Septostomia disponível<br/>imediatamente no centro?"}
  C2(["Sim: realizar BAS e<br/>reavaliar mistura/perfusão"])
  P4["Não: transferência emergencial<br/>mantendo PGE1 e suporte"]
  C3(["Após estabilização:<br/>switch arterial precoce"])

  R0 --> P1
  P1 --> P2
  P2 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P3
  P3 --> D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| P4
  C2 --> C3
  P4 --> C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

**Ducto patente não garante mistura suficiente.** Se o forame oval é restritivo e o neonato continua hipóxico, BAS é a ponte que muda a fisiologia.