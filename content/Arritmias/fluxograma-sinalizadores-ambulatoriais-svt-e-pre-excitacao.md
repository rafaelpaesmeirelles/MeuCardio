---
slug: fluxograma-sinalizadores-ambulatoriais-svt-e-pre-excitacao
title: 'Fluxograma: sinalizadores ambulatoriais de SVT e pré-excitação — PS agora vs. EP eletiva'
kind: fluxograma
theme: Arritmias
summary: 'Árvore ambulatorial: TSV recorrente ou pré-excitação/WPW no consultório — gate de PS (FA pré-excitada,
  síncope, instabilidade) versus via eletiva de eletrofisiologia/ablação.'
tags: []
source_refs:
- 'Brugada J, Katritsis DG, Arbelo E, et al. 2019 ESC Guidelines for the management of patients with supraventricular
  tachycardia. Eur Heart J. 2020;41(5):655-720. DOI: 10.1093/eurheartj/ehz467. PMID: 31504425'
- 'Page RL, Joglar JA, Caldwell MA, et al. 2015 ACC/AHA/HRS Guideline for the Management of Adult Patients With
  Supraventricular Tachycardia. Circulation. 2016;133(14):e506-e574. DOI: 10.1161/CIR.0000000000000311. PMID: 26399663'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma: sinalizadores ambulatoriais de SVT e pré-excitação

Prosa: [`sinalizadores-ambulatoriais-de-svt-recorrente-quando-escalar`](/biblioteca/sinalizadores-ambulatoriais-de-svt-recorrente-quando-escalar) e [`pre-excitacao-wpw-no-consultorio-sinais-vermelhos-quando-ir-ao-ps`](/biblioteca/pre-excitacao-wpw-no-consultorio-sinais-vermelhos-quando-ir-ao-ps). Agudo QRS estreito: [`fluxograma-taquicardia-supraventricular-qrs-estreito-esc-2019`](/biblioteca/fluxograma-taquicardia-supraventricular-qrs-estreito-esc-2019).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: TSV recorrente e/ou pré-excitação/WPW"] --> D1{"Há síncope recente associada à crise atual, instabilidade,<br/>QRS largo irregular muito rápido<br/>ou FA pré-excitada suspeita?"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>Não bloquear nó AV se FA pré-excitada<br/>Documentar ECG 12 derivações"])

  D1 -->|"Não"| DA{"TSV ativa persistente ou refratária?"}
  DA -->|"Sim"| CA(["Atendimento agudo monitorado<br/>Algoritmo canônico de TSV"])
  DA -->|"Não / episódio encerrado"| D2{"Pré-excitação manifesta<br/>no ECG basal?"}

  D2 -->|"Sim"| D3{"Sintomas de TSV,<br/>esporte/ocupação de risco<br/>ou dúvida de alto risco?"}
  D3 -->|"Sim"| C2(["EP eletiva rápida<br/>Discutir estratificação ± ablação<br/>Orientação escrita de alarmes"])
  D3 -->|"Não / incidental"| C3(["EP eletiva para estratificação<br/>Ver WPW assintomático"])

  D2 -->|"Não"| D4{"TSV recorrente<br/>documentada/sintomática?"}
  D4 -->|"Sim"| C4(["Via eletiva: oferecer ablação<br/>Discutir riscos e benefícios conforme mecanismo<br/>Eco se suspeita estrutural/TCM"])
  D4 -->|"Não / 1ª crise leve"| C5(["Documentar traçado<br/>Retorno com Holter/evento<br/>Educar manobras vagais e alarmes"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class CA,C2,C3,C4,C5 conduta;
```

## Notas

- **D1** = triagem de segurança (ESC 2019 / ACC/AHA/HRS 2015).
- **D2** = pré-excitação muda o algoritmo — não tratar como TSV “comum”.
- **C4** = ablação como discussão de primeira linha na TSV sintomática recorrente (ESC 2019), sem doses neste fluxograma.
- Não decide protocolo IV de emergência nem anticoagulação de FA.
