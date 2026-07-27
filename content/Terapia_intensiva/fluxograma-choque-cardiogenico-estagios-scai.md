---
title: "Fluxograma: Choque Cardiogênico — estágios SCAI e o que o ECLS-SHOCK mudou"
slug: fluxograma-choque-cardiogenico-estagios-scai
theme: "Terapia intensiva"
kind: fluxograma
summary: "Classificação do choque cardiogênico em estágios SCAI, reavaliação contínua como eixo do manejo, e por que o ensaio ECLS-SHOCK não sustenta ECMO venoarterial precoce de rotina."
review_status: revisado
source_refs: ["Prognostic impact of SCAI shock severity classes in AMI-related cardiogenic shock: A sub-study of the ECLS-SHOCK Trial · ESC Heart Failure · 2025 · 12(6):4359 · https://academic.oup.com/eschf/article/12/6/4359/8488198", "A Proposed Algorithm for the Management of Patients with Cardiogenic Shock Based on Contemporary Knowledge and Gaps in Evidence · PMC · https://pmc.ncbi.nlm.nih.gov/articles/PMC12734037/", "Cardiac arrest in the Extracorporeal Life Support (ECLS)-SHOCK trial in perspective · European Heart Journal: Acute Cardiovascular Care · 2023 · 12(12):864 · https://academic.oup.com/ehjacc/article/12/12/864/7425473", "2023 ESC Guidelines for the management of acute coronary syndromes · European Heart Journal · 2023 · 44(38):3720-3826 · 10.1093/eurheartj/ehad191"]
---

# Fluxograma: Choque Cardiogênico — estágios SCAI

O choque cardiogênico não é um estado binário. A classificação SCAI o organiza em
estágios de gravidade crescente, de **A a E**, e o eixo do manejo não é escolher
uma conduta definitiva no início, e sim **reavaliar com frequência** se o paciente
está melhorando ou deteriorando.

## Árvore de decisão: causa do choque

```mermaid
flowchart TD
  R0["Suspeita de choque cardiogênico"] --> D1{"Causa isquêmica?<br/>SCA em curso"}

  D1 -->|Sim| C1(["Critério de risco muito alto na ESC 2023:<br/>angiografia invasiva imediata"])
  D1 -->|Não| C2(["Investigar e tratar<br/>a causa de base"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Árvore de decisão: estágio SCAI e suporte circulatório

```mermaid
flowchart TD
  R0["Choque cardiogênico<br/>classificar o estágio SCAI"] --> D1{"Estágio SCAI"}

  D1 -->|"A — em risco"| C1(["Vigilância, sem suporte<br/>circulatório mecânico"])
  D1 -->|"B — início"| C2(["Vigilância, sem suporte<br/>circulatório mecânico"])
  D1 -->|"C — clássico"| C3(["Considerar suporte circulatório mecânico<br/>decisão individualizada"])
  D1 -->|"D — em deterioração"| C4(["Considerar suporte circulatório mecânico<br/>decisão individualizada"])
  D1 -->|"E — extremo"| C5(["Considerar suporte circulatório mecânico<br/>decisão individualizada"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

O estágio SCAI não é um rótulo fixo. A reavaliação frequente vale para todos os
estágios: quem deteriora é reclassificado e volta a percorrer a árvore acima;
quem melhora tem o suporte desescalonado conforme tolerado. É por isso que a
reavaliação não aparece como folha — ela é o que devolve o paciente à raiz.

## Mortalidade por estágio

No subestudo do ensaio ECLS-SHOCK, com 417 pacientes incluídos entre junho de
2019 e novembro de 2022 em choque cardiogênico relacionado a infarto agudo do
miocárdio, a distribuição e a mortalidade em 30 dias foram:

| Estágio SCAI | Proporção dos pacientes | Mortalidade em 30 dias |
|---|---:|---:|
| C — clássico | 51,6% | 32,6% |
| D — em deterioração | 13,4% | 67,9% |
| E — extremo | 35,0% | 64,4% |

O estágio SCAI, portanto, discrimina prognóstico de forma acentuada — a
mortalidade praticamente dobra do estágio C para o D.

## O que o ECLS-SHOCK mostrou sobre ECMO

Este é o maior ensaio de ECMO venoarterial em choque cardiogênico até o momento,
e o resultado é negativo: os achados **não sustentam uma estratégia de ECMO
venoarterial precoce de rotina** em comparação com terapia clínica.

Um ponto adicional do subestudo merece atenção: **não houve interação entre o
estágio SCAI e o efeito do tratamento** sobre a mortalidade em 30 dias nos
estágios C, D e E. Ou seja, a ausência de benefício não se explica por seleção de
estágio — não se identificou um estágio em que a estratégia precoce de rotina
passasse a compensar.

## Por que a reavaliação é o eixo

Em todos os estágios SCAI é necessária reavaliação frequente para determinar se
o paciente está melhorando ou deteriorando e se novas ações serão necessárias. O
estágio não é um rótulo fixo atribuído na admissão: é uma leitura que se repete,
e a trajetória entre leituras é o que orienta escalonar ou desescalonar suporte.
