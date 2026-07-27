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

## Árvore de decisão

```mermaid
flowchart TD
  R0["Perda transitória da consciência<br/>(PTC)"] --> P1["Avaliação inicial, obrigatória nos<br/>três componentes: história clínica completa,<br/>exame físico com PA em ortostase<br/>e ECG de 12 derivações"]

  P1 --> D1{"A PTC é síncope?"}

  D1 -->|Não| C1(["Investigar causa não sincopal<br/>de PTC"])

  D1 -->|Sim| D2{"Diagnóstico definido<br/>pela avaliação inicial?"}

  D2 -->|Sim| C2(["Tratar a causa identificada"])

  D2 -->|Não| D3{"Estratificação de risco"}

  D3 -->|"Alto risco"| C3(["Avaliação intensiva e precoce<br/>unidade de síncope, observação<br/>em emergência ou internação"])
  D3 -->|"Risco intermediário"| C4(["Observação na emergência<br/>ou unidade de síncope"])
  D3 -->|"Baixo risco"| C5(["Manejo ambulatorial"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
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
