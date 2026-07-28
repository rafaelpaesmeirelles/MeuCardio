---
title: "Fluxograma: Hipertensão Pulmonar — algoritmo diagnóstico em três passos (ESC/ERS 2022)"
slug: fluxograma-hipertensao-pulmonar-diagnostico-esc-ers-2022
theme: "Hipertensão pulmonar"
kind: fluxograma
summary: "Da suspeita clínica à confirmação hemodinâmica: probabilidade ecocardiográfica, nova definição por PAPm acima de 20 mmHg em repouso e cateterismo cardíaco direito em centro de referência."
review_status: revisado
source_refs: ["2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension · European Heart Journal · 2022 · 43(38):3618-3731 · https://academic.oup.com/eurheartj/article/43/38/3618/6673929", "2022 ESC/ERS Guidelines for Pulmonary Hypertension: Key Points · American College of Cardiology · 2022 · https://www.acc.org/latest-in-cardiology/ten-points-to-remember/2022/08/30/19/11/2022-esc-guidelines-for-pulmonary-hypertension-esc-2022", "'Ten Commandments' of the 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension · European Heart Journal · 2023 · 44(10):792-793 · https://academic.oup.com/eurheartj/article/44/10/792/7022121"]
---

# Fluxograma: Hipertensão Pulmonar — algoritmo diagnóstico (ESC/ERS 2022)

A diretriz ESC/ERS 2022 simplificou o diagnóstico da hipertensão pulmonar em uma
abordagem de **três passos**, com divisão explícita de responsabilidade: a
suspeita nasce com o médico de primeiro contato, a detecção é ecocardiográfica, e
a confirmação é hemodinâmica em centro especializado.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Passo 1 — Suspeita<br/>médico de primeiro contato<br/>sintomas, fatores de risco, comorbidades"] --> P1["Passo 2 — Detecção<br/>ecocardiograma transtorácico<br/>atribuir probabilidade ecocardiográfica"]

  P1 --> D1{"Probabilidade<br/>ecocardiográfica de HP"}

  D1 -->|Baixa| C1(["Considerar diagnóstico alternativo<br/>reavaliar se persistir a suspeita"])

  D1 -->|"Intermediária ou alta"| P2["Investigar causas comuns<br/>doença cardíaca esquerda e<br/>doença pulmonar"]

  P2 --> P3["Passo 3 — Confirmação<br/>cateterismo cardíaco direito<br/>em centro de HP"]

  P3 --> D2{"PAPm em repouso"}
  D2 -->|"maior que 20 mmHg"| C2(["Hipertensão pulmonar confirmada<br/>classificar o grupo hemodinâmico"])
  D2 -->|"menor ou igual a 20 mmHg"| C3(["HP afastada pela definição atual"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C1,C2,C3 conduta;
```

A probabilidade ecocardiográfica do Passo 2 não é um achado isolado: resulta da
leitura conjunta da **velocidade de regurgitação tricúspide**, dos **demais
sinais ecocardiográficos de HP**, da **relação TAPSE/PSAP** e do **diâmetro da
artéria pulmonar comparado ao da raiz da aorta**. São entradas da mesma
avaliação, e por isso não figuram como ramos da árvore.

## A definição mudou

A hipertensão pulmonar passou a ser definida por **pressão arterial pulmonar
média (PAPm) acima de 20 mmHg em repouso**. É uma alteração relevante em relação
à definição usada na diretriz de 2015 e amplia a população que atende ao
critério hemodinâmico.

## O que entrou na probabilidade ecocardiográfica

A atribuição de probabilidade não se apoia em um único número. Além da
velocidade de regurgitação tricúspide, a versão de 2022 incorporou:

- a **relação TAPSE/PSAP**, como marcador de acoplamento ventrículo-arterial
  direito;
- a **avaliação combinada do diâmetro da artéria pulmonar e da raiz da aorta**.

## Por que a confirmação é centralizada

O cateterismo cardíaco direito permanece obrigatório para o diagnóstico e a
diretriz o situa em **centro de hipertensão pulmonar**. A razão é dupla: a
medida hemodinâmica exige padronização técnica para ser confiável, e a
classificação correta do grupo determina tratamentos com perfis de risco muito
distintos entre si.
