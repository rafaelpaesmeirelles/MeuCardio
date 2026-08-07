---
title: "Fluxograma: Síndrome aórtica aguda na gestação e no puerpério"
slug: fluxograma-sindrome-aortica-aguda-na-gestacao-e-puerperio
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de decisão para suspeita de dissecção aórtica na gestante/puérpera, distinguindo tipo A, que exige cirurgia urgente, do tipo B inicialmente médico salvo complicações."
review_status: revisado
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al.; ESC Scientific Document Group. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294.", "Isselbacher EM, Preventza O, Black JH 3rd, et al. 2022 ACC/AHA Guideline for the Diagnosis and Management of Aortic Disease. Circulation. 2022;146(24):e334-e482. DOI: 10.1161/CIR.0000000000001106. PMID: 36322642. PMCID: PMC9876736."]
---

# Síndrome aórtica aguda na gestação/puerpério

```mermaid
flowchart TD
  R0["Gestante ou puérpera com dor abrupta intensa,<br/>assimetria de pulsos/PA, síncope, déficit neurológico,<br/>choque ou aortopatia conhecida + sintomas"]
  P1["ABC + monitorização + analgesia + estratégia anti-impulso;<br/>acionar equipe de aorta + Pregnancy Heart Team;<br/>obter imagem definitiva sem atraso indevido"]
  D1{"Síndrome aórtica aguda confirmada?"}
  C1(["Não: investigar SCAD/SCA, TEP, PPCM,<br/>causas obstétricas e demais diagnósticos"])
  D2{"Dissecção tipo A?"}
  D3{"Momento gestacional"}
  C2(["1º/2º trimestre: cirurgia aórtica urgente<br/>com monitorização fetal — ACC/AHA Classe I C-LD"])
  C3(["3º trimestre: cesariana urgente imediatamente<br/>seguida de cirurgia aórtica — ACC/AHA Classe I C-LD;<br/>individualizar segundo viabilidade/capacidade do centro"])
  C4(["Puerpério: cirurgia aórtica urgente<br/>conforme protocolo de tipo A e equipe de aorta"])
  D4{"Tipo B com complicação aguda?<br/>ruptura, malperfusão ou deterioração clínica/hemodinâmica"}
  C5(["Não complicada: tratamento médico inicial<br/>e monitorização intensiva — ACC/AHA Classe I C-EO"])
  C6(["Complicada: discutir intervenção endovascular/cirúrgica<br/>urgente em centro experiente, individualizando<br/>condição materna e obstétrica"])
  C7(["Após estabilização: seguimento de aortopatia,<br/>genética quando indicada e plano pós-parto"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Sim"| D3
  D2 -->|"Não — tipo B"| D4
  D3 -->|"1º/2º trimestre"| C2
  D3 -->|"3º trimestre"| C3
  D3 -->|"Pós-parto"| C4
  D4 -->|"Não"| C5
  D4 -->|"Sim"| C6
  C2 --> C7
  C3 --> C7
  C4 --> C7
  C5 --> C7
  C6 --> C7

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Regra prática

**Tipo A na gestação é emergência cirúrgica. Tipo B é inicialmente médico se não complicada.** A gestação modifica a coordenação materno-fetal, não elimina a urgência da doença aórtica.
