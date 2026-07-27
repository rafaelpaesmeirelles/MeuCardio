---
title: "Fluxograma: Síncope — avaliação inicial e estratificação de risco (ESC 2018)"
slug: fluxograma-sincope-avaliacao-inicial-esc-2018
theme: "Síncope"
kind: fluxograma
summary: "Da perda transitória da consciência à decisão de destino: avaliação inicial obrigatória, separação entre síncope e outras causas de PTC, e estratificação em risco alto, intermediário e baixo."
review_status: revisado
source_refs: ["2018 ESC Guidelines for the diagnosis and management of syncope · European Heart Journal · 2018 · 39(21):1883-1948 · https://academic.oup.com/eurheartj/article-pdf/39/21/1883/66477582/ehy037.pdf", "Practical Instructions for the 2018 ESC Guidelines for the diagnosis and management of syncope · European Heart Journal · 2018 · 39(21):e43-e80 · https://academic.oup.com/eurheartj/article/39/21/e43/4939242", "2018 ESC Guidelines for Diagnosis and Management of Syncope · American College of Cardiology · 2018 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2018/04/04/14/28/2018-ESC-Guidelines-for-Syncope"]
---

# Fluxograma: Síncope — avaliação inicial e estratificação de risco (ESC 2018)

A decisão central na síncope não é diagnóstica, é **de destino**: quem pode ir
para casa, quem fica em observação e quem precisa de investigação intensiva
imediata. O fluxograma abaixo organiza esse caminho.

## Caminho decisório

```mermaid
flowchart TD
  A["Perda transitória da consciência<br/>(PTC)"] --> B["Avaliação inicial<br/>obrigatória nos três componentes"]

  B --> B1["História clínica completa"]
  B --> B2["Exame físico<br/>incluindo PA em ortostase"]
  B --> B3["ECG de 12 derivações"]

  B1 --> C{"A PTC é síncope?"}
  B2 --> C
  B3 --> C

  C -->|Não| D["Investigar causa não sincopal<br/>de PTC"]
  C -->|Sim| E{"Diagnóstico definido<br/>pela avaliação inicial?"}

  E -->|Sim| F["Tratar a causa identificada"]
  E -->|Não| G{"Estratificação de risco"}

  G -->|"Alto risco"| H["Avaliação intensiva e precoce<br/>unidade de síncope, observação<br/>em emergência ou internação"]
  G -->|"Risco intermediário"| I["Observação na emergência<br/>ou unidade de síncope"]
  G -->|"Baixo risco"| J["Manejo ambulatorial"]
```

## Os três componentes da avaliação inicial

A diretriz é explícita quanto a esses três elementos serem realizados em todo
paciente com PTC — nenhum deles é opcional:

1. **História clínica completa** — circunstâncias, pródromos, testemunhas,
   recuperação, episódios prévios, medicações, história familiar.
2. **Exame físico com aferição de pressão arterial em ortostase**.
3. **Eletrocardiograma padrão de 12 derivações**.

## O que a estratificação decide

O propósito da estratificação não é nomear a síncope, e sim alocar recurso e
tempo. Pacientes com características de alto risco recebem avaliação intensiva e
imediata — em unidade de síncope, em unidade de observação da emergência quando
disponível, ou internados. O risco intermediário justifica um período de
observação. O baixo risco é conduzido em ambulatório.

Essa separação existe porque a síncope reúne, sob uma mesma apresentação, causas
de curso benigno e causas de mortalidade elevada; o que muda o desfecho é quanto
tempo se leva para distinguir umas das outras.
