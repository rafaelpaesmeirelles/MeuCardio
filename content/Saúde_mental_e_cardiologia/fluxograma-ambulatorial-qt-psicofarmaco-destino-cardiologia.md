---
title: "Fluxograma ambulatorial: preocupação com QT por psicofármaco — PS agora vs. retorno precoce vs. Psycho-Cardio"
slug: fluxograma-ambulatorial-qt-psicofarmaco-destino-cardiologia
theme: "Saúde mental e cardiologia"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino: gate de alarme QT/arritmia (PS agora); braço de QTc elevado sem instabilidade (retorno precoce); braço de revisão Psycho-Cardio/escolha de agente sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-preocupacao-qt-psicofarmaco-quando-escalar (07/09/2026). Além de #847. ESC 2025 PMID 40878270; AHA/ACCF 2010 PMID 20142454; Wenzel-Seifert PMID 22114630; Ray 2009 PMID 19144938. Sem doses; anti-colisão com fluxograma de escolha QT e com crise."
source_refs:
  - "Bueno H, Deaton C, Farrero M, et al. 2025 ESC Clinical Consensus Statement on mental health and cardiovascular disease: developed under the auspices of the ESC Clinical Practice Guidelines Committee. Eur Heart J. 2025;46(41):4156-4225. DOI: 10.1093/eurheartj/ehaf191. PMID: 40878270"
  - "Drew BJ, Ackerman MJ, Funk M, et al. Prevention of torsade de pointes in hospital settings: a scientific statement from the American Heart Association and the American College of Cardiology Foundation. Circulation. 2010;121(8):1047-1060. DOI: 10.1161/CIRCULATIONAHA.109.192704. PMID: 20142454"
  - "Wenzel-Seifert K, Wittmann M, Haen E. QTc prolongation by psychotropic drugs and the risk of Torsade de Pointes. Dtsch Arztebl Int. 2011;108(41):687-693. DOI: 10.3238/arztebl.2011.0687. PMID: 22114630"
  - "Ray WA, Chung CP, Murray KT, Hall K, Stein CM. Atypical antipsychotic drugs and the risk of sudden cardiac death. N Engl J Med. 2009;360(3):225-235. DOI: 10.1056/NEJMoa0806994. PMID: 19144938"
---

# Fluxograma ambulatorial: QT por psicofármaco — destino

Prosa: [`sinalizadores-ambulatoriais-preocupacao-qt-psicofarmaco-quando-escalar`](sinalizadores-ambulatoriais-preocupacao-qt-psicofarmaco-quando-escalar.md). Checklist: [`checklist-ambulatorial-alarme-qt-psicofarmaco-cardiopata`](checklist-ambulatorial-alarme-qt-psicofarmaco-cardiopata.md). Escolha de agente (com doses — **não duplicar aqui**): [`fluxograma-escolha-de-antidepressivo-e-antipsicotico-no-cardiopata-risco-de-qt`](fluxograma-escolha-de-antidepressivo-e-antipsicotico-no-cardiopata-risco-de-qt.md). Crise: [`fluxograma-ambulatorial-crise-psiquiatrica-destino-cardiologia`](fluxograma-ambulatorial-crise-psiquiatrica-destino-cardiologia.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>cardiopata em psicofármaco<br/>ou preocupação com QT"] --> D1{"Alarme de arritmia/QT?<br/>síncope / pré-síncope<br/>QTc >500 ms ou ↑≥60 ms<br/>ectopia nova / suspeita TdP<br/>eletrólito grave / overdose"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / emergência AGORA<br/>Não protocolar dose aqui<br/>Corrigir ofensor/eletrólitos no ambiente adequado"])

  D1 -->|"Não"| D2{"QTc elevado ou fatores acumulados<br/>sem instabilidade?<br/>(DCV + bradicardia + outros QT<br/>+ hipocalemia/Mg ± idade)"}

  D2 -->|"Sim"| P1["Confirmar técnica de QTc e basal<br/>Revisar interações e eletrólitos<br/>Sem inventar doses neste fluxograma"]
  P1 --> C2(["Retorno ambulatorial 24–72 h<br/>ECG ± eletrólitos<br/>Orientação escrita de alarmes"])

  D2 -->|"Não / estável com plano claro"| D3{"Precisa revisão Psycho-Cardio<br/>ou árvore de escolha de agente?"}

  D3 -->|"Sim"| C3(["Referência Psycho-Cardio / saúde mental<br/>Usar fluxograma-escolha QT<br/>(sem repetir doses neste documento)"])
  D3 -->|"Não"| C4(["Plano usual + educação de alarmes<br/>Reavaliar em contatos regulares<br/>(ESC 2025)"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora / sintoma arrítmico surge"| C5(["Antecipar contato 24 h ou PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter retorno 24–72 h<br/>Não suspender psicofármaco<br/>só por receio genérico neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança arrítmica (AHA/ACCF 2010 limiares de ação pronta).
- **D2** = risco acumulado ambulatorial controlável (Wenzel-Seifert) → retorno precoce.
- **D3** = ponte para Psycho-Cardio e para o fluxograma de **escolha** já existente — **sem doses aqui**.
- Não decide doses, periodicidade universal de ECG nem troca de classe isolada.
- Ideação/crise → usar pacote #847 em paralelo se coexistir.
