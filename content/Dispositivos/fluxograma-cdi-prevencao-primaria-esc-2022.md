---
title: "Fluxograma: CDI em prevenção primária — além da fração de ejeção (ESC 2022)"
slug: fluxograma-cdi-prevencao-primaria-esc-2022
theme: "Dispositivos"
kind: fluxograma
summary: "Indicação de cardiodesfibrilador implantável em prevenção primária na diretriz ESC 2022: fração de ejeção com classe funcional na doença coronariana crônica, e a ressonância magnética cardíaca elevada como fator de decisão na cardiomiopatia dilatada."
review_status: revisado
source_refs: ["2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death · European Heart Journal · 2022 · 43(40):3997-4126 · https://academic.oup.com/eurheartj/article/43/40/3997/6675633", "Spotlight on the 2022 ESC guideline management of ventricular arrhythmias and prevention of sudden cardiac death: 10 novel key aspects · EP Europace · 2023 · 25(5):euad091 · https://academic.oup.com/europace/article/25/5/euad091/7143805", "'10 commandments' for the 2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death · European Heart Journal · 2023 · 44(3):176-178 · https://academic.oup.com/eurheartj/article/44/3/176/6881120"]
---

# Fluxograma: CDI em prevenção primária (ESC 2022)

A mudança mais importante da diretriz ESC 2022 para a decisão sobre
cardiodesfibrilador implantável é o **enfraquecimento da fração de ejeção como
critério isolado**. Ela continua central na doença coronariana crônica, mas na
cardiomiopatia dilatada a indicação deixou de poder ser reduzida a um corte
numérico.

## Caminho decisório

```mermaid
flowchart TD
  A["Avaliação para CDI<br/>em prevenção primária"] --> B{"Substrato de base"}

  B -->|"Doença coronariana crônica"| C["FEVE combinada à<br/>classe funcional NYHA"]
  B -->|"Cardiomiopatia dilatada ou<br/>cardiomiopatia não dilatada<br/>hipocinética"| D["Decisão não restrita<br/>à FEVE menor ou igual a 35%"]

  C --> E["Indicação conforme<br/>os critérios da diretriz"]

  D --> F["Considerar em conjunto"]
  F --> F1["Apresentação clínica"]
  F --> F2["Ressonância magnética cardíaca"]
  F --> F3["Teste genético"]

  F1 --> G["Decisão individualizada<br/>sobre o implante"]
  F2 --> G
  F3 --> G

  E --> H["Reavaliação periódica"]
  G --> H
```

## Onde a fração de ejeção ainda decide

A FEVE é usada — frequentemente **em combinação com a classe funcional NYHA** —
para a indicação de CDI em prevenção primária no contexto de **doença arterial
coronariana crônica** e de **cardiomiopatia dilatada**.

## Onde ela deixou de bastar

Em pacientes com **cardiomiopatia dilatada ou cardiomiopatia não dilatada
hipocinética**, a diretriz é explícita: a indicação de CDI em prevenção primária
**não deve ser restrita a uma FEVE ≤ 35%**. A apresentação clínica e o resultado
de exames adicionais são importantes na decisão, com destaque para:

- **ressonância magnética cardíaca**
- **teste genético**

## A elevação da ressonância magnética cardíaca

O papel da RMC foi **significativamente elevado** nesta diretriz, tanto na
avaliação diagnóstica quanto — sobretudo — na estratificação de risco e na
decisão sobre terapia com CDI em prevenção primária. É a mudança que mais altera
a rotina de investigação antes do implante.

## Contexto da revisão

A diretriz de 2022 atualiza a de 2015. A revisão foi motivada por novos dados
sobre a epidemiologia da morte súbita cardíaca, por evidência nova em genética,
imagem e achados clínicos para estratificação de risco de arritmia ventricular e
morte súbita, e por avanços na avaliação diagnóstica e nas estratégias
terapêuticas.
