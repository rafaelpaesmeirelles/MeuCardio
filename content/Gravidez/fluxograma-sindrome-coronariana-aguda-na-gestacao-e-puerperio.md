---
title: "Fluxograma: síndrome coronariana aguda na gestação e puerpério"
slug: fluxograma-sindrome-coronariana-aguda-na-gestacao-e-puerperio
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de emergência para SCA na gestante/puérpera, preservando reperfusão e adaptando antiagregação e suspeita de SCAD."
review_status: revisado
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294."]
---

# SCA na gestação/puerpério

```mermaid
flowchart TD
  R0["Gestante/puérpera com dor torácica<br/>ou suspeita de isquemia"]
  P1["ECG + troponina + TTE<br/>+ avaliar TEP, aorta, PPCM e SCAD"]
  D1{"STEMI ou SCA de alto/muito alto risco?"}
  P2["Angiografia imediata + PCI se indicada;<br/>usar princípio ALARA"]
  P3["Sem alto risco: estratificação usual<br/>e estratégia invasiva conforme diagnóstico"]
  D2{"Angiografia mostra SCAD?"}
  C1(["Sim: migrar para protocolo<br/>de SCAD gestacional/puerperal"])
  D3{"PCI/stent realizado e DAPT indicada?"}
  P4["AAS + clopidogrel quando apropriado;<br/>evitar ticagrelor na gestação"]
  D4{"PCI não disponível em tempo adequado<br/>e reperfusão urgente necessária?"}
  P5["Considerar trombólise sistêmica<br/>após avaliar risco hemorrágico"]
  C2(["Planejar DAPT/parto/anestesia<br/>com Pregnancy Heart Team após estabilização"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P3
  P2 --> D2
  P3 --> D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| D3
  D3 -->|"Sim"| P4
  D3 -->|"Não"| D4
  P4 --> C2
  D4 -->|"Sim"| P5
  D4 -->|"Não"| C2
  P5 --> C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

Gestação **não reduz indicação de reperfusão**. A adaptação está em radiação, antiagregantes e planejamento do parto — não em aceitar isquemia persistente.