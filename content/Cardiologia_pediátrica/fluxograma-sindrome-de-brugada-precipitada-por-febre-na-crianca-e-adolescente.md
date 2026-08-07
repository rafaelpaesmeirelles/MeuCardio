---
title: "Fluxograma: Brugada precipitada por febre na criança/adolescente"
slug: fluxograma-sindrome-de-brugada-precipitada-por-febre-na-crianca-e-adolescente
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de emergência para febre em paciente pediátrico com Brugada conhecido ou padrão tipo 1, com antitermia, telemetria e tratamento de TV/FV."
review_status: revisado
source_refs: ["Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for ventricular arrhythmias. Eur Heart J. 2022;43(40):3997-4126. DOI: 10.1093/eurheartj/ehac262.", "Gaita F, et al. Heart Rhythm. 2018. PMID: 29649615."]
---

# Brugada + febre

```mermaid
flowchart TD
  R0["Criança/adolescente com febre<br/>+ Brugada conhecido ou ECG suspeito"]
  P1["Antitermia imediata + ECG<br/>+ eletrólitos + tratar causa da febre"]
  D1{"Síncope, TV/FV, choque<br/>ou padrão tipo 1 de alto risco?"}
  P2["Telemetria/UTI conforme gravidade;<br/>eletrofisiologia pediátrica"]
  D2{"TV/FV ou PCR?"}
  C1(["Sim: cardioversão/desfibrilação<br/>+ PCR pediátrica se necessário"])
  D3{"Tempestade elétrica/<br/>choques recorrentes?"}
  P3["Considerar isoproterenol/quinidina<br/>com EP/UTI; dose = VERIFICAÇÃO HUMANA NECESSÁRIA"]
  P4["Sem evento grave: controlar febre,<br/>repetir ECG após defervescência"]
  D4{"Padrão tipo 1/sintomas persistem<br/>ou houve evento arrítmico?"}
  C2(["Sim: avaliação especializada<br/>de risco, genética e ICD quando indicado"])
  C3(["Não: orientação de febre/fármacos<br/>e seguimento cardiológico"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P4
  P2 --> D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| D3
  C1 --> D3
  D3 -->|"Sim"| P3
  D3 -->|"Não"| D4
  P3 --> D4
  P4 --> D4
  D4 -->|"Sim"| C2
  D4 -->|"Não"| C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

**Na criança com Brugada, febre é parte da arritmia.** Trate a temperatura como gatilho elétrico e monitore o coração enquanto trata a infecção.