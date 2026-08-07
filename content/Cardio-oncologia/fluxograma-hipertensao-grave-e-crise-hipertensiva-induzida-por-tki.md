---
title: "Fluxograma: hipertensão grave e crise hipertensiva induzida por TKI"
slug: fluxograma-hipertensao-grave-e-crise-hipertensiva-induzida-por-tki
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de emergência para elevação pressórica em paciente usando TKI, separando hipertensão significativa, hipertensão grave que exige pausa da terapia oncológica e emergência hipertensiva com lesão aguda de órgão-alvo."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al.; ESC Scientific Document Group. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568.", "Poku NK, Ramalingam S, Andres MS, Gevaert S, Lyon AR. Monitoring and treatment of cardiovascular complications during cancer therapies. Part II: Tyrosine kinase inhibitors. ESC CardioPractice. 15 May 2023. European Society of Cardiology — conteúdo conferido em escardio.org nesta revisão."]
---

# Hipertensão durante TKI

```mermaid
flowchart TD
  R0["Paciente em TKI com PA elevada"]
  P1["Repetir PA corretamente + sintomas + ECG/avaliação<br/>de órgão-alvo conforme apresentação"]
  D1{"Há lesão aguda de órgão-alvo?<br/>SCA, edema pulmonar, encefalopatia/AVC,<br/>síndrome aórtica, IRA progressiva etc."}
  P2["Emergência hipertensiva:<br/>pausar TKI causal + protocolo geral de emergência<br/>+ acionar oncologia/cardio-oncologia"]
  D2{"PAS >180 OU PAD >110 mmHg?"}
  P3["Hipertensão grave durante TKI:<br/>interromper temporariamente tratamento oncológico<br/>+ otimizar anti-hipertensivos + MDT"]
  D3{"PAS >160 E PAD >100 mmHg?"}
  P4["Controle rápido: preferir IECA/BRA como base;<br/>considerar di-hidropiridínico se necessário<br/>e função ventricular apropriada"]
  P5["Evitar verapamil/diltiazem como rotina<br/>por interações com vários TKI"]
  D4{"Há IC/disfunção ventricular associada?"}
  P6["Avaliar CTRCD; se moderada/grave,<br/>pausar TKI + terapia de IC baseada em diretriz"]
  C1(["PA abaixo dos limiares graves:<br/>meta <140/90 + monitorização seriada/domiciliar"])
  C2(["Após estabilização: MDT decide reinício,<br/>redução de dose ou terapia oncológica alternativa"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| D2
  P2 --> C2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| D3
  P3 --> D4
  D3 -->|"Sim"| P4
  D3 -->|"Não"| C1
  P4 --> P5
  P5 --> D4
  D4 -->|"Sim"| P6
  D4 -->|"Não"| C2
  P6 --> C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

O **valor da PA define quando pausar o TKI; a lesão aguda de órgão-alvo define a emergência hipertensiva**. Em ambos os cenários graves, a reintrodução do antineoplásico é decisão conjunta após estabilização.