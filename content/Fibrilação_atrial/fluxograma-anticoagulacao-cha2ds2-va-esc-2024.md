---
kind: fluxograma
published: true
review_note: Conferência individual CASTLE-AF, CASTLE-HTx e RAFT-AF contra resumos
  primários; ESC FA 2024 PDF Tables 6/10 e recomendações de frequência/ablação; ESC
  IC 2026 Table 15 e DRC 2026. Resolvidos PMID 39210723, classes por documento e indicação,
  exceções ao escore, FA subclínica e elegibilidade de DOAC; fluxo refeito sem convergência
  e sem classificar FEVE >35 como necessariamente preservada.
review_status: revisado
slug: fluxograma-anticoagulacao-cha2ds2-va-esc-2024
source_refs:
- 'Van Gelder IC, Rienstra M, Bunting KV, et al.; ESC Scientific Document Group. 2024
  ESC Guidelines for the management of atrial fibrillation developed in collaboration
  with the European Association for Cardio-Thoracic Surgery (EACTS). Eur Heart J.
  2024;45(36):3314-3414. DOI 10.1093/eurheartj/ehae176. PMID: 39210723.'
- Damman K, Herrington WG, et al. 2026 ESC Guidelines for the management of cardiovascular
  disease and chronic kidney disease, in collaboration with the European Renal Association
  (ERA). Eur Heart J. 2026. DOI 10.1093/eurheartj/ehag098. PMID 42661426.
- Van Gelder IC, Rienstra M et al. ESC AF 2024. DOI 10.1093/eurheartj/ehae176. PMID
  39210723; Tables 6, 10, rate control and ablation recommendations.
theme: Fibrilação atrial
title: 'Fluxograma: anticoagulação pelo CHA₂DS₂-VA — ESC 2024'
---

# Fluxograma: anticoagulação pelo CHA₂DS₂-VA — ESC 2024

Este fluxo aplica-se à FA clínica confirmada e exige avaliação das exceções antes do escore. Alerta isolado de wearable não estabelece diagnóstico. Episódios subclínicos confirmados têm indicação própria e não devem ser descartados automaticamente por falta de ECG de superfície.

```mermaid
flowchart TD
  R0["Avaliar anticoagulação na FA clínica confirmada"] --> D0{"Há condição fora da decisão simplificada pelo escore?"}
  D0 -->|"Prótese mecânica ou estenose mitral moderada/grave"| C0(["Avaliar anticoagulação com AVK; não usar preferência por DOAC"])
  D0 -->|"Cardiomiopatia hipertrófica ou amiloidose cardíaca"| C1(["Anticoagulação recomendada independentemente do escore; escolher fármaco após avaliar contraindicações"])
  D0 -->|"DRC com TFGe <30, gestação ou sangramento ativo importante"| C2(["Avaliação individual/especializada; não decidir apenas pelo CHA₂DS₂-VA"])
  D0 -->|"Nenhuma dessas condições"| D1{"CHA₂DS₂-VA: sexo não pontua"}
  D1 -->|"0"| C3(["Baixo risco pelo escore: não iniciar anticoagulante apenas por esse resultado; reavaliar risco"])
  D1 -->|"1"| C4(["Considerar anticoagulação por decisão compartilhada, após risco hemorrágico e elegibilidade"])
  D1 -->|"≥2"| C5(["Anticoagulação recomendada se elegível; DOAC preferido ao AVK, observados critérios da molécula"])
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5 conduta;
```

## Aplicação e classes

A anticoagulação na FA clínica com risco embólico elevado é I A; CHA₂DS₂-VA ≥2 como indicador desse risco é I C, e escore 1 para considerar anticoagulação é IIa C. Não atribuir o nível do escore automaticamente ao tratamento.

IC, hipertensão, diabetes, doença vascular e idade 65–74: 1 ponto cada. Idade ≥75 e AVC/AIT/embolia arterial prévios: 2 pontos cada. Idade 65–74 e ≥75 não se somam. Mulher de 66 anos com hipertensão tem escore 2: o sexo sai, mas a indicação permanece.

Antes de usar apenas o escore, identificar exceções: FA com cardiomiopatia hipertrófica ou amiloidose cardíaca tem indicação de anticoagulação independentemente do CHA₂DS₂-VA (ESC FA 2024, I B). Prótese mecânica ou estenose mitral moderada/grave exigem estratégia com AVK, não DOAC. Na DRC com TFGe <30 mL/min/1,73 m², a ESC DRC 2026 não recomenda escores clínicos de risco embólico para decidir anticoagulação; individualizar benefício/risco e tratamento. Episódios subclínicos confirmados por dispositivo têm avaliação própria (DOAC pode ser considerado em alto risco embólico sem alto risco hemorrágico, IIb B), distinta de alerta isolado de wearable sem confirmação.

Na DRC com TFGe ≥30, preferência por DOAC é I A na ESC DRC 2026. TFGe 15–29: inibidores de fator Xa podem ser considerados (IIa B1), com escolha e dose específicas. Não reduzir dose de DOAC apenas por receio de sangramento sem cumprir critérios da molécula. AF-CARE e reavaliação periódica valem em todos os ramos.

## Tudo com Tudo

Fibrilação atrial · Tromboembolismo · Cardiorrenal · Farmacologia · Insuficiência cardíaca · Hipertensão · Comunicação clínica · Cardiomiopatias · Valvopatias.
