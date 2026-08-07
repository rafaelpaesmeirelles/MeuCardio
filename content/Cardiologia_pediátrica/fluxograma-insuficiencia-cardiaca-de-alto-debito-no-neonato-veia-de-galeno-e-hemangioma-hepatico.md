---
title: "Fluxograma: insuficiência cardíaca de alto débito no neonato"
slug: fluxograma-insuficiencia-cardiaca-de-alto-debito-no-neonato-veia-de-galeno-e-hemangioma-hepatico
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de emergência para neonato com alto débito por malformação da veia de Galeno ou shunt vascular hepático, priorizando reconhecimento do shunt e intervenção causal."
review_status: revisado
source_refs: ["Cory MJ, Durand P, Sillero R, et al. Vein of Galen aneurysmal malformation: rationalizing medical management of neonatal heart failure. Pediatr Res. 2023;93(1):39-48. DOI: 10.1038/s41390-022-02064-1. PMID: 35422084.", "Vein of Galen Aneurysmal Malformations: Updates on Technical Aspects and Functional Outcomes Post-Endovascular Treatment—A Systematic Review and Meta-Analysis. PMID: 39768831.", "Infantile hepatic hemangiomas: looking backwards and forwards. PMID: 35692445."]
---

# IC de alto débito neonatal

```mermaid
flowchart TD
  R0["Neonato com IC/choque de alto débito,<br/>HP, pulsos amplos ou shunt vascular suspeito"]
  P1["TTE/POCUS: débito, VD/HP, ducto;<br/>examinar crânio/fígado + US Doppler"]
  D1{"Veia de Galeno ou grande<br/>shunt AV cerebral suspeito?"}
  P2["Neuroimagem/Doppler urgente;<br/>acionar neurorradiologia intervencionista"]
  D2{"Hemangioma/shunt hepático<br/>de alto fluxo suspeito?"}
  P3["US Doppler hepático + equipe vascular/<br/>hepatologia/dermatologia pediátrica"]
  D3{"Choque, hipoperfusão ou HP grave?"}
  P4["Suporte neonatal individualizado;<br/>corrigir hipóxia/acidose e preservar perfusão"]
  D4{"Falência de alto débito persiste<br/>apesar da estabilização?"}
  C1(["Veia de Galeno: discutir embolização<br/>endovascular urgente/estagiada"])
  C2(["Lesão hepática: terapia causal específica<br/>± intervenção conforme anatomia"])
  C3(["Estável: planejar tratamento definitivo<br/>e monitorar cérebro, rim e coração"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| D2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| D3
  P2 --> D3
  P3 --> D3
  D3 -->|"Sim"| P4
  D3 -->|"Não"| C3
  P4 --> D4
  D4 -->|"Sim + Veia de Galeno"| C1
  D4 -->|"Sim + hepático"| C2
  D4 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

No alto débito neonatal, **o coração pode ser vítima de um shunt extracardíaco**. Suporte hemodinâmico compra tempo; o tratamento causal fecha/reduz o circuito de alto fluxo.