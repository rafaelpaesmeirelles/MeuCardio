---
title: "Fluxograma: trombose coronária/infarto em aneurisma de Kawasaki"
slug: fluxograma-trombose-coronaria-e-infarto-em-aneurisma-de-kawasaki
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore para suspeita de SCA em criança/adolescente com aneurisma coronário de Kawasaki, priorizando angiografia e reperfusão especializada."
review_status: revisado
review_note: "NIGHT-B06-REVIEW (2026-08-25): revisão editorial concluída como árvore de reconhecimento e encaminhamento. O fluxograma mantém apenas modalidades de reperfusão descritas pelas fontes, sem hierarquia terapêutica ou dose; a escolha entre PCI, trombectomia, trombólise e cirurgia permanece condicionada à anatomia, aos recursos e à equipe especializada."
source_refs: ["Jone PN, Tremoulet A, Choueiter N, et al. Circulation. 2024;150:e481-e500. DOI: 10.1161/CIR.0000000000001295. PMID: 39534969.", "McCrindle BW, et al. Circulation. 2017;135:e927-e999. DOI: 10.1161/CIR.0000000000000484. PMID: 28356445."]
---

# Trombose coronária/infarto em Kawasaki

> As modalidades abaixo não formam uma hierarquia universal. Não transformar a listagem em escolha automática de tratamento nem importar doses gerais de anticoagulação/trombólise para este cenário raro.

```mermaid
flowchart TD
  R0["Kawasaki prévia + aneurisma coronário<br/>+ dor/síncope/ECG/troponina sugestivos"]
  P1["ECG + troponina + TTE + monitorização;<br/>acionar centro intervencionista pediátrico"]
  D1{"STEMI, choque, TV/FV ou forte<br/>suspeita de oclusão aguda?"}
  P2["Definir anatomia coronária<br/>urgentemente por angiografia"]
  P3["Sem alto risco imediato:<br/>estratificar anatomia/trombo<br/>sem atrasar se quadro evoluir"]
  D2{"Trombo/oclusão relevante?"}
  C1(["Não: reavaliar causa do evento<br/>e otimizar prevenção trombótica"])
  P4["Sim: reperfusão especializada<br/>PCI/trombectomia/trombólise/cirurgia<br/>conforme anatomia e protocolo"]
  D3{"Choque ou PCR?"}
  C2(["Sim: ressuscitação pediátrica<br/>± MCS como ponte para reperfusão"])
  C3(["Não: pós-reperfusão, reavaliar VE,<br/>aneurisma e antitrombose crônica"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P3
  P2 --> D2
  P3 --> D2
  D2 -->|"Não"| C1
  D2 -->|"Sim"| P4
  P4 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

Aneurisma de Kawasaki não é apenas um problema de seguimento: **pode trombosar e causar IAM pediátrico verdadeiro**.
