---
title: "Fluxograma: HAP por dasatinibe com dispneia, síncope ou falência de VD"
slug: fluxograma-hipertensao-pulmonar-arterial-por-dasatinibe-com-descompensacao
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de emergência para paciente em dasatinibe com dispneia/hipóxia/síncope ou sinais de falência direita, diferenciando derrame pleural e outras causas de HAP induzida pelo fármaco e orientando suspensão definitiva quando confirmada."
review_status: revisado
source_refs: ["Montani D, Bergot E, Günther S, et al. Pulmonary arterial hypertension in patients treated by dasatinib. Circulation. 2012;125(17):2128-2137. DOI: 10.1161/CIRCULATIONAHA.111.079921. PMID: 22451584.", "U.S. Food and Drug Administration. SPRYCEL (dasatinib) Prescribing Information, section 5.5 Pulmonary Arterial Hypertension; current DailyMed labeling consulted in this session.", "Weatherald J, Bondeelle L, Chaumais MC, et al. Pulmonary complications of Bcr-Abl tyrosine kinase inhibitors. Eur Respir J. 2020;56(4):2000279. DOI: 10.1183/13993003.00279-2020. PMID: 32527740."]
---

# HAP por dasatinibe com descompensação

```mermaid
flowchart TD
  R0["Paciente em dasatinibe com dispneia nova/progressiva,<br/>fadiga, hipóxia, síncope, edema ou sinais de falência de VD"]
  P1["Avaliar estabilidade + ECG + oximetria + exame pulmonar;<br/>eco urgente se repercussão cardiovascular;<br/>investigar derrame pleural, anemia, infecção, TEP e IC"]
  D1{"Choque, síncope recorrente, hipoxemia grave<br/>ou falência aguda de VD?"}
  C1(["Sim: UTI/centro experiente em HP;<br/>seguir suporte de falência aguda de VD/choque<br/>e acelerar confirmação etiológica"])
  D2{"Eco/sinais clínicos sugerem hipertensão pulmonar<br/>sem causa alternativa suficiente?"}
  C2(["Não: tratar diagnóstico identificado;<br/>manter vigilância se sintomas persistirem"])
  P2["Sim: discutir imediatamente com hematologia/oncologia;<br/>encaminhar para confirmação de HAP pré-capilar<br/>com cateterismo direito quando clinicamente viável"]
  D3{"HAP por dasatinibe confirmada?"}
  C3(["Não: ampliar investigação de hipertensão pulmonar<br/>e reconsiderar causas concomitantes"])
  C4(["Sim: suspender dasatinibe permanentemente<br/>conforme rotulagem FDA; definir alternativa oncológica<br/>e necessidade de terapia específica para HAP"])
  D4{"Há melhora clínica/hemodinâmica após retirada?"}
  C5(["Sim: manter seguimento até reavaliação objetiva;<br/>não presumir normalização completa"])
  C6(["Não/incompleta: centro de hipertensão pulmonar;<br/>avaliar terapia específica e outras causas associadas"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  C1 --> D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| P2
  P2 --> D3
  D3 -->|"Não"| C3
  D3 -->|"Sim"| C4
  C4 --> D4
  D4 -->|"Sim"| C5
  D4 -->|"Não/incompleta"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Ponto-chave

**Dispneia em quem usa dasatinibe não é sinônimo de derrame pleural.** Se HAP for confirmada, a rotulagem do SPRYCEL determina suspensão permanente do fármaco. O seguimento continua necessário porque reversibilidade completa não é garantida.
