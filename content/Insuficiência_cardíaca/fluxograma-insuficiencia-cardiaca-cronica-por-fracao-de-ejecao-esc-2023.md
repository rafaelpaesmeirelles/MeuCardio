---
title: "Fluxograma: Insuficiência Cardíaca crônica — conduta por fração de ejeção (ESC 2021 / atualização 2023)"
slug: fluxograma-insuficiencia-cardiaca-cronica-por-fracao-de-ejecao-esc-2023
theme: "Insuficiência cardíaca"
kind: fluxograma
summary: "Classificação da IC pela fração de ejeção e conduta farmacológica correspondente: os quatro pilares na ICFEr e o iSGLT2 como recomendação Classe I na ICFElr e na ICFEp após a atualização de 2023."
review_status: revisado
source_refs: ["2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure · European Heart Journal · 2021 · 42(36):3599-3726 · https://academic.oup.com/eurheartj/article/42/36/3599/6358045", "2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure · European Heart Journal · 2023 · 44(37):3627-3639 · https://academic.oup.com/eurheartj/article/44/37/3627/7246292", "2023 Focused Update of ESC Guidelines for Acute and Chronic HF: Key Points · American College of Cardiology · 2023 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2023/08/29/14/58/2023-focused-update-esc-guidelines-hf-esc-2023"]
---

# Fluxograma: Insuficiência Cardíaca crônica — conduta por fração de ejeção

A fração de ejeção continua sendo o eixo que organiza o tratamento da IC crônica,
mas a atualização de 2023 reduziu a distância entre os fenótipos: o inibidor de
SGLT2 passou a ser recomendação **Classe I, nível de evidência A** também na IC
com fração de ejeção levemente reduzida e na preservada — faixas que, na diretriz
de 2021, não tinham nenhuma recomendação de iSGLT2 porque ainda não havia ensaio
conduzido nesses grupos.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Sinais e sintomas de IC<br/>+ peptídeos natriuréticos elevados<br/>e/ou alteração estrutural/funcional"] --> P1["Medir fração de ejeção<br/>do ventrículo esquerdo"]

  P1 --> D1{"FEVE"}

  D1 -->|"menor ou igual a 40%"| C1(["ICFEr — iniciar e titular<br/>os quatro pilares:<br/>IECA ou ARNI, betabloqueador,<br/>antagonista mineralocorticoide<br/>e inibidor de SGLT2"])

  D1 -->|"41 a 49%"| C2(["ICFElr — inibidor de SGLT2<br/>dapagliflozina ou empagliflozina<br/>Classe I, nível A"])

  D1 -->|"maior ou igual a 50%"| C3(["ICFEp — inibidor de SGLT2<br/>dapagliflozina ou empagliflozina<br/>Classe I, nível A"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C1,C2,C3 conduta;
```

Qualquer que seja a faixa de fração de ejeção, o tratamento das comorbidades e
da congestão e a reavaliação periódica são parte do manejo — não são um ramo
alternativo do algoritmo, e por isso não aparecem como folha da árvore.

## Os quatro pilares na ICFEr

A terapia de base da IC com fração de ejeção reduzida combina quatro classes,
usadas em conjunto e não em sequência escalonada:

- **inibição do sistema renina-angiotensina** — IECA ou, na forma de inibição da
  neprilisina associada ao bloqueio do receptor de angiotensina, sacubitril/valsartana
- **betabloqueador**
- **antagonista do receptor mineralocorticoide**
- **inibidor de SGLT2**

## O que mudou em 2023

| Faixa de FEVE | Diretriz 2021 | Atualização 2023 |
|---|---|---|
| ICFElr (41–49%) | sem recomendação de iSGLT2 | iSGLT2 Classe I, nível A |
| ICFEp (≥ 50%) | sem recomendação de iSGLT2 | iSGLT2 Classe I, nível A |

A mudança apoia-se nos ensaios EMPEROR-Preserved (empagliflozina) e DELIVER
(dapagliflozina), que forneceram a evidência ausente em 2021. O desfecho alvo da
recomendação é a redução de hospitalização por IC ou morte cardiovascular.

## Diagnóstico da ICFEp

O diagnóstico exige sinais e sintomas de IC acompanhados de evidência de
alteração estrutural e/ou funcional cardíaca e/ou peptídeos natriuréticos
elevados, com FEVE ≥ 50%. Não há teste isolado que confirme: **quanto maior o
número de alterações presentes, maior a probabilidade de ICFEp**.
