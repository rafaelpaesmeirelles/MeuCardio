---
slug: fluxograma-ambulatorial-ic-piora-progressiva-destino
title: 'Fluxograma ambulatorial: IC com piora progressiva — PS agora vs. retorno precoce'
kind: fluxograma
theme: Insuficiência cardíaca
summary: 'Piora progressiva de insuficiência cardíaca no ambulatório: identificar necessidade de emergência e realizar
  avaliação inicial da congestão antes de programar retorno precoce. Inclui acompanhamento após alta e coordenação
  do tratamento.'
tags: []
source_refs:
- 'McDonagh TA; Metra M; Adamo M. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart
  failure. Eur Heart J. 2021;42:3599. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992.'
- 'McDonagh TA; Metra M; Adamo M. 2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment
  of acute and chronic heart failure. Eur Heart J. 2023;44:3627. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666.'
- 'Mebazaa A; Davison B; Chioncel O. Safety, tolerability and efficacy of up-titration of guideline-directed medical
  therapies for acute heart failure (STRONG-HF): a multinational, open-label, randomised, trial. Lancet. 2022;400:1938.
  DOI: 10.1016/S0140-6736(22)02076-1. PMID: 36356631.'
- 'Køber L, Adamo M, et al. 2026 ESC Guidelines for the management of heart failure. DOI: 10.1093/eurheartj/ehag100.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: IC com piora progressiva — destino

Prosa: [sinalizadores-ambulatoriais-de-descompensacao-de-ic-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-de-descompensacao-de-ic-quando-encaminhar). Pós-alta 14 dias: [pos-alta-de-ic-checklist-de-alarme-nas-duas-primeiras-semanas](/biblioteca/pos-alta-de-ic-checklist-de-alarme-nas-duas-primeiras-semanas). Aguda hospitalar: [fluxograma-insuficiencia-cardiaca-aguda-descompensada](/biblioteca/fluxograma-insuficiencia-cardiaca-aguda-descompensada).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial / contato pós-alta<br/>com IC e piora referida"] --> D1{"Há alarme de PS?<br/>dispneia em repouso nova/progressiva / ortopneia grave<br/>DPN recorrente com desconforto respiratório<br/>hipoxemia<br/>hipoperfusão / síncope<br/>dor anginosa / arritmia instável"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Seguir fluxograma-insuficiencia-cardiaca-aguda-descompensada"])

  D1 -->|"Não"| D2{"Congestão progressiva leve–moderada?<br/>edema / ganho de peso / ortopneia<br/>sem hipoperfusão"}

  D2 -->|"Sim"| P1["Checar adesão, sal, AINE, infecção<br/>Exame focado + peso; decidir ajuste do tratamento agora"]
  P1 --> C2["Reavaliação precoce após avaliação e tratamento iniciais<br/>24–72 h somente se clinicamente seguro<br/>Orientação escrita de alarmes<br/>Labs se mudarem conduta"]

  D2 -->|"Não / muito brando"| D3{"Pós-alta nas últimas 6 semanas?"}

  D3 -->|"Sim"| C3(["Aplicar checklist pós-alta; manter seguimento até semana 6<br/>Manter vigilância; retorno ≤7 dias<br/>se sinalizadores brandos"])
  D3 -->|"Não"| C4(["Plano usual + educação de alarmes<br/>Peso diário se congestão recorrente<br/>Retorno conforme estabilidade"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / fragilidade / piora rápida"| C5(["Providenciar avaliação presencial em serviço acessível;<br/>piora rápida ou alarme exige urgência imediata"])
  D4 -->|"Sim"| C6(["Reavaliar antes se piorar; 24–72 h se seguro<br/>Não titular GDMT neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (perfil de IC aguda / ESC 2021).
- **D2** = congestão ambulatorial sem hipoperfusão → destino clínico precoce.
- **D3** = janela pós-alta alinhada à vigilância das primeiras semanas (ESC 2023 / STRONG-HF).
- Não decide doses de GDMT, diurético IV, ultrafiltração nem manejo cardiorrenal.

## Limites e segurança do seguimento

Peso isolado não define congestão nem PS; interpretar com sintomas, perfusão e peso basal. Prazos são operacionais e dependem da rede. Avaliar SCA, arritmia, TEP, infecção, anemia, DRC/LRA, fármacos e valvopatia como alternativas/precipitantes; não atribuir todo edema à IC. Após ajuste terapêutico, programar creatinina/TFGe e potássio conforme o fármaco, além dos exames motivados pela clínica. STRONG-HF não validou cortes de peso nem vigilância isolada.
