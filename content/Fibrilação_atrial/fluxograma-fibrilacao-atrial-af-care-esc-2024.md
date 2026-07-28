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

## A trajetória AF-CARE

O AF-CARE é uma **sequência de cuidado**, não uma árvore de decisão: as quatro
etapas se aplicam a todo paciente, em ordem, e o **E** final devolve ao começo.
Por isso ela aparece aqui como sequência, e as duas decisões de fato
ramificadas — anticoagular e como reduzir sintomas — aparecem logo abaixo,
cada uma como sua própria árvore.

1. **C — Comorbidades e fatores de risco.** Ponto de partida do manejo.
2. **A — Anticoagulação.** Evitar AVC e tromboembolismo.
3. **R — Reduzir sintomas.** Controle de frequência e de ritmo.
4. **E — Avaliação e reavaliação dinâmica.** Retorna ao passo 1.

## Árvore de decisão: anticoagulação (A)

```mermaid
flowchart TD
  R0["Fibrilação atrial confirmada<br/>comorbidades já abordadas na etapa C"] --> D1{"Escore CHA2DS2-VA"}

  D1 -->|"maior ou igual a 2"| C1(["Anticoagulante oral indicado<br/>DOAC preferencial"])
  D1 -->|"igual a 1"| C2(["Considerar anticoagulante oral<br/>decisão individualizada"])
  D1 -->|"igual a 0"| C3(["Anticoagulação não indicada<br/>apenas pelo escore"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C1,C2,C3 conduta;
```

## Árvore de decisão: redução de sintomas (R)

```mermaid
flowchart TD
  R0["Etapa R — reduzir sintomas<br/>após definida a anticoagulação"] --> D1{"Estratégia de controle<br/>de ritmo indicada?"}

  D1 -->|"FA paroxística, candidato adequado"| C1(["Ablação por cateter<br/>opção de primeira linha"])
  D1 -->|"Demais casos"| C2(["Controle de frequência<br/>e/ou antiarrítmico"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C1,C2 conduta;
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
