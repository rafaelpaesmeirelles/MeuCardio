---
title: "Fluxograma ambulatorial: síncope pós-avaliação — destino PS vs. retorno precoce"
slug: fluxograma-ambulatorial-sincope-pos-avaliacao-destino
theme: "Síncope"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial pós-alta/pós-avaliação: alarme de alto risco → PS; recorrência ‘benigna’ → retorno precoce; baixo risco estável → plano ambulatorial — alinhada à ESC 2018."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar (07/09/2026). ESC 2018 PMID 29562304. Anti-colisão com fluxograma ED alto risco e EGSYS. Sem doses."
source_refs:
  - "Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304"
  - "Brignole M, Moya A, de Lange FJ, et al. Practical Instructions for the 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):e43-e80. DOI: 10.1093/eurheartj/ehy071"
---

# Fluxograma ambulatorial: síncope pós-avaliação — destino

Prosa: [`sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar`](sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar.md). Gate atividades: [`sincope-gate-ambulatorial-retorno-atividades-trabalho-direcao`](sincope-gate-ambulatorial-retorno-atividades-trabalho-direcao.md). Estratificação no DE: [`fluxograma-sincope-criterios-de-alto-risco-emergencia-esc-2018-eusem-2024`](fluxograma-sincope-criterios-de-alto-risco-emergencia-esc-2018-eusem-2024.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial / pós-alta do DE<br/>síncope já estratificada como baixo risco<br/>ou seguimento após avaliação inicial"] --> D1{"Novo alarme de alto risco?<br/>síncope em esforço / decúbito / sem pródromo<br/>trauma / dor torácica / dispneia aguda<br/>ECG alarmante / dispositivo + síncope<br/>hipoperfusão"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA<br/>PS / urgência / unidade de síncope<br/>Reabrir Tabelas 5–7 ESC 2018"])

  D1 -->|"Não"| D2{"Recorrência com pródromo típico<br/>ou pré-síncope frequente<br/>sem critérios de PS?"}

  D2 -->|"Sim"| P1["História + exame + PA supina/em pé<br/>Revisar / repetir ECG se mudança"]
  P1 --> C2(["Retorno 24–72 h<br/>Alarmes escritos<br/>Educação de gatilhos / pródromo"])

  D2 -->|"Não"| D3{"Baixo risco mantido?<br/>causa reflexa/situacional/ortostática plausível<br/>sem recorrência alarmante<br/>ECG e exame estáveis"}

  D3 -->|"Sim"| C3(["Plano ambulatorial<br/>Orientação escrita de alarmes<br/>Gate separado para trabalho/direção"])
  D3 -->|"Incerto / nem alto nem baixo"| C4(["Tratar como observação / retorno curto<br/>ou encaminhar unidade de síncope<br/>ESC: Classe I B"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora rápida"| C5(["Antecipar retorno 24 h<br/>ou PS se surgir alarme"])
  D4 -->|"Sim"| C6(["Manter retorno 24–72 h<br/>Não protocolar doses / ILR / MP aqui"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (reabertura de alto risco ESC 2018).
- **D2** = recorrência “benigna” → destino clínico precoce, não alta sem plano.
- **D3** = baixo risco só com dados coerentes; na dúvida, sobe para retorno curto / unidade de síncope.
- Trabalho, direção e altura ficam no documento-gate irmão (sem inventar legislação).
