---
title: "Fluxograma: estenose aórtica grave sintomática na gestação"
slug: fluxograma-estenose-aortica-grave-sintomatica-na-gestacao
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de emergência para gestante com estenose aórtica grave e sintomas, distinguindo congestão controlável de refratariedade com necessidade de intervenção valvar."
review_status: revisado
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294."]
---

# Estenose aórtica grave sintomática na gestação

```mermaid
flowchart TD
  R0["Gestante com EAo grave<br/>+ dispneia/IC, angina, síncope<br/>ou alteração de ST"]
  P1["Monitorização + ECG + eco urgente<br/>+ Pregnancy Heart Team/Valve Centre"]
  D1{"Choque, edema pulmonar grave<br/>ou isquemia persistente?"}
  P2["Estabilização intensiva;<br/>preservar pré-carga e pressão;<br/>diurese cautelosa se congesta"]
  P3["Sem instabilidade extrema:<br/>repouso/restrição de atividade<br/>+ tratar congestão com cautela"]
  D2{"Sintomas/angina/ST persistem<br/>apesar do manejo médico?"}
  C1(["Não: vigilância estreita<br/>e seguimento especializado"])
  P4["Sim: avaliar intervenção valvar<br/>em centro experiente"]
  D3{"Opção percutânea apropriada?"}
  C2(["BAV ou TAVI podem ser consideradas<br/>em caso muito selecionado"])
  D4{"Feto viável e situação permite<br/>parto antes da intervenção?"}
  C3(["Considerar parto antes<br/>da intervenção valvar"])
  C4(["Sem opção percutânea e risco materno grave:<br/>discutir cirurgia valvar"])

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
  D3 -->|"Não"| D4
  C2 --> D4
  D4 -->|"Sim"| C3
  D4 -->|"Não"| C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Regra prática

Na EAo grave sintomática, **o tratamento médico compra tempo; não remove a obstrução**. Persistência de sintomas, angina ou alterações de ST deve antecipar discussão de intervenção, não apenas intensificar diurético.