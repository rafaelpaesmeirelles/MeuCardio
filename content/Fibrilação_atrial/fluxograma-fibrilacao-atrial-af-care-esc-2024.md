---
title: "Fluxograma: Fibrilação Atrial — trajetória AF-CARE (ESC 2024)"
slug: fluxograma-fibrilacao-atrial-af-care-esc-2024
theme: "Fibrilação atrial"
kind: fluxograma
summary: "Trajetória AF-CARE da diretriz ESC 2024: comorbidades como ponto de partida, decisão de anticoagulação pelo CHA2DS2-VA, controle de frequência e ritmo, e reavaliação dinâmica."
review_status: revisado
source_refs: ["2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the EACTS · European Heart Journal · 2024 · 45(36):3314-3414 · https://academic.oup.com/eurheartj/article/45/36/3314/7738779", "2024 ESC Guidelines for Management of Atrial Fibrillation: Key Points · American College of Cardiology · 2024 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2024/09/17/04/05/2024-ESC-guidelines-for-AF-esc-2024", "Spotlight on the 2024 ESC/EACTS management of atrial fibrillation guidelines: 10 novel key aspects · EP Europace · 2024 · 26(12):euae298 · https://academic.oup.com/europace/article/26/12/euae298/7931832"]
---

# Fluxograma: Fibrilação Atrial — trajetória AF-CARE (ESC 2024)

A diretriz ESC 2024 reorganizou o manejo da FA em torno do acrônimo **AF-CARE**.
A mudança de ênfase mais relevante é a ordem: o tratamento de comorbidades e
fatores de risco deixa de ser cuidado acessório e passa a ser **o ponto de
partida**, porque as terapias para FA são mais eficazes e a recorrência menos
provável quando as condições associadas estão controladas.

## Caminho decisório

```mermaid
flowchart TD
  A["Fibrilação atrial confirmada"] --> C["C — Comorbidades e fatores de risco<br/>ponto de partida do manejo"]

  C --> B["A — Anticoagulação<br/>evitar AVC e tromboembolismo"]

  B --> D{"Escore CHA2DS2-VA"}
  D -->|"maior ou igual a 2"| E["Anticoagulante oral indicado<br/>DOAC preferencial"]
  D -->|"igual a 1"| F["Considerar anticoagulante oral<br/>decisão individualizada"]
  D -->|"igual a 0"| G["Anticoagulação não indicada<br/>apenas pelo escore"]

  E --> H["R — Reduzir sintomas<br/>controle de frequência e ritmo"]
  F --> H
  G --> H

  H --> I{"Estratégia de ritmo<br/>indicada?"}
  I -->|"FA paroxística, candidato adequado"| J["Ablação por cateter<br/>opção de primeira linha"]
  I -->|"Demais casos"| K["Controle de frequência<br/>e/ou antiarrítmico"]

  J --> L["E — Avaliação e<br/>reavaliação dinâmica"]
  K --> L
  L --> C
```

## Cardioversão: a janela mudou

O limiar de duração da FA para cardioversão precoce **caiu de 48 para 24 horas**.
Junto com isso, a diretriz passou a recomendar uma conduta de espera vigiada
(*wait-and-see*) pela reversão espontânea, em nome da segurança do paciente.

## O escore CHA2DS2-VA

O CHA2DS2-VA substitui o CHA2DS2-VASc — a diferença é a retirada do componente
de sexo feminino do cálculo. Pontuação:

| Componente | Pontos |
|---|---:|
| Insuficiência cardíaca congestiva | 1 |
| Hipertensão | 1 |
| Idade ≥ 75 anos | 2 |
| Diabetes mellitus | 1 |
| AVC / AIT / tromboembolismo arterial prévio | 2 |
| Doença vascular | 1 |
| Idade 65–74 anos | 1 |

## Por que a ordem do acrônimo importa

O AF-CARE não é uma lista de tarefas paralelas, e sim uma sequência com
justificativa clínica. Começar por **C** (comorbidades) antes de discutir ritmo
reflete a evidência de que o controle de hipertensão, apneia do sono, obesidade
e demais fatores associados melhora o resultado das intervenções seguintes. O
**E** final devolve o paciente ao começo do ciclo: a reavaliação é dinâmica, não
um desfecho.
