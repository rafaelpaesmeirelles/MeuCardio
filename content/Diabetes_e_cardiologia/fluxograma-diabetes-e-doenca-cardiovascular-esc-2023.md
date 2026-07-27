---
title: "Fluxograma: Diabetes e Doença Cardiovascular — rastreamento, risco e terapia (ESC 2023)"
slug: fluxograma-diabetes-e-doenca-cardiovascular-esc-2023
theme: "Diabetes e cardiologia"
kind: fluxograma
summary: "Rastreamento sistemático de diabetes em todo paciente com DCV, avaliação de DCV e doença renal crônica em todo diabético, estratificação pelo SCORE2-Diabetes e indicação de iSGLT2 e agonista de GLP-1 independentemente do controle glicêmico."
review_status: revisado
source_refs: ["2023 ESC Guidelines for the management of cardiovascular disease in patients with diabetes · European Heart Journal · 2023 · 44(39):4043-4140 · https://academic.oup.com/eurheartj/article/44/39/4043/7238227", "2023 ESC Guidelines for Managing CVD in Diabetes: Key Points — Part 2 · American College of Cardiology · 2023 · https://www.acc.org/latest-in-cardiology/ten-points-to-remember/2023/09/11/03/37/2023-esc-guidelines-cvd-diabetes-part-2-esc-2023", "'10 commandments' for the 2023 ESC Guidelines for the management of cardiovascular disease in patients with diabetes · European Heart Journal · 2024 · 45(15):1298-1300 · https://academic.oup.com/eurheartj/article/45/15/1298/7513467"]
---

# Fluxograma: Diabetes e Doença Cardiovascular (ESC 2023)

A diretriz ESC 2023 estabelece uma via de mão dupla: **todo paciente com doença
cardiovascular deve ser rastreado para diabetes**, e **todo paciente com diabetes
deve ser avaliado para doença cardiovascular e doença renal crônica**. A partir
daí, a conduta farmacológica deixa de depender exclusivamente do controle
glicêmico.

## Caminho decisório

```mermaid
flowchart TD
  A["Paciente com doença<br/>cardiovascular estabelecida"] --> B["Rastreamento sistemático<br/>de diabetes"]
  C["Paciente com diabetes"] --> D["Avaliar risco e presença de DCV<br/>e de doença renal crônica"]
  B --> D

  D --> E{"Doença aterosclerótica<br/>cardiovascular estabelecida?"}

  E -->|Sim| F["Agonista de receptor de GLP-1<br/>e/ou inibidor de SGLT2<br/>para reduzir risco cardiovascular"]
  F --> G["Independente do controle glicêmico<br/>e somado ao tratamento padrão"]
  G --> G1["Antiagregante plaquetário"]
  G --> G2["Anti-hipertensivo"]
  G --> G3["Hipolipemiante"]

  E -->|Não| H{"Insuficiência cardíaca<br/>presente?"}
  H -->|Sim| I["Inibidor de SGLT2<br/>qualquer fração de ejeção"]

  H -->|Não| J["Estimar risco pelo<br/>SCORE2-Diabetes"]
  J --> J1["Fatores convencionais:<br/>idade, tabagismo, PA sistólica,<br/>colesterol total e HDL"]
  J --> J2["Fatores específicos do diabetes:<br/>idade ao diagnóstico, HbA1c, TFGe"]

  J1 --> K{"Categoria de risco<br/>cardiovascular em 10 anos"}
  J2 --> K
  K -->|Baixo| L["Conduta conforme categoria"]
  K -->|Moderado| L
  K -->|Alto| L
  K -->|Muito alto| L
```

## SCORE2-Diabetes

Modelo de predição introduzido nesta diretriz, para estimar o risco de evento
cardiovascular fatal ou não fatal em 10 anos em pessoas com **diabetes tipo 2 sem
doença aterosclerótica cardiovascular e sem lesão grave de órgão-alvo**. Combina
dois blocos de variáveis:

| Fatores convencionais | Fatores específicos do diabetes |
|---|---|
| idade | idade ao diagnóstico do diabetes |
| tabagismo | HbA1c |
| pressão arterial sistólica | taxa de filtração glomerular estimada |
| colesterol total e HDL | — |

O resultado classifica o paciente em risco **baixo, moderado, alto ou muito alto**.

## A mudança de lógica na indicação farmacológica

O ponto mais importante da diretriz para a prática: em paciente com diabetes e
doença aterosclerótica cardiovascular, o agonista de GLP-1 e/ou o inibidor de
SGLT2 são recomendados **para reduzir risco cardiovascular, independentemente do
controle glicêmico** — e somados ao tratamento padrão com antiagregante,
anti-hipertensivo e hipolipemiante. A indicação deixa de ser "tratar a glicemia"
e passa a ser "reduzir desfecho cardiovascular".

Na insuficiência cardíaca, a recomendação é ainda mais direta: **todo paciente
diabético com IC deve receber inibidor de SGLT2, qualquer que seja a fração de
ejeção**, para reduzir hospitalização por IC e morte cardiovascular.
