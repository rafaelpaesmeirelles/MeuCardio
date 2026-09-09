---
title: "Fluxograma ambulatorial: CMD e ACM — aconselhamento genético e rastreio familiar"
slug: fluxograma-ambulatorial-dcm-acm-genetica-e-rastreio-familiar
theme: "Cardiomiopatias"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório para CMD/NDLVC ou ACM/ARVC: alarme → PS; sem alarme → aconselhamento genético se fenótipo claro; resultado P/LP → cascata; VUS/negativo → rastreio clínico familiar — alinhada à ESC 2023 e EHRA 2022."
review_status: pendente_revisao
review_note: "Irmão do pacote ambulatory DCM/ACM (07/09/2026). Além de #844/#862; anti-colisão #849 e hubs #689/#723. ESC 2023 PMID 37622657; EHRA 2022 PMID 35373836. Sem doses."
source_refs:
  - "Arbelo E, Protonotarios A, Gimeno JR, et al. 2023 ESC Guidelines for the management of cardiomyopathies. Eur Heart J. 2023;44(37):3503-3626. DOI: 10.1093/eurheartj/ehad194. PMID: 37622657"
  - "Wilde AAM, Semsarian C, Márquez MF, et al. EHRA/HRS/APHRS/LAHRS Expert Consensus Statement on the State of Genetic Testing for Cardiac Diseases. Europace. 2022;24(8):1307-1367. DOI: 10.1093/europace/euac030. PMID: 35373836"
---

# Fluxograma ambulatorial: CMD e ACM — genética e rastreio familiar

Prosa: [`sinalizadores-ambulatoriais-dcm-quando-referir-aconselhamento-genetico`](sinalizadores-ambulatoriais-dcm-quando-referir-aconselhamento-genetico.md) e [`sinalizadores-ambulatoriais-acm-arvc-rastreamento-familiar-quando-escalar`](sinalizadores-ambulatoriais-acm-arvc-rastreamento-familiar-quando-escalar.md).

Não substitui [`fluxograma-investigacao-genetica-cardiomiopatia-historia-familiar-morte-subita`](fluxograma-investigacao-genetica-cardiomiopatia-historia-familiar-morte-subita.md) (árvore EHRA completa, já revisada).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: CMD/NDLVC ou ACM/ARVC\nconhecida ou alta suspeita"] --> D1{"Alarme urgente?\nsíncope / TV / choque CDI\nBAV avançado / IC aguda"}

  D1 -->|"Sim"| C1(["Encaminhar AGORA\nPS / urgência\nGenética NÃO atrasa"])

  D1 -->|"Não"| D2{"Fenótipo de alta probabilidade\n(diagnóstico ou Task Force/Padua\nem discussão estruturada)?"}

  D2 -->|"Não — fenótipo fraco"| C2(["Não pedir painel amplo\nReavaliar clínica/imagem\nEHRA: não testar evidência fraca"])

  D2 -->|"Sim"| C3(["Referir ACONSELHAMENTO genético\nantes de qualquer amostra\nEducação + direito de não testar"])

  C3 --> D3{"Após aconselhamento:\nsegue teste no índice?"}

  D3 -->|"Não"| C4(["Vigilância do índice\n+ rastreio CLÍNICO\ndos parentes de 1º grau"])

  D3 -->|"Sim"| D4{"Resultado no índice?"}

  D4 -->|"P/LP"| C5(["Cascata dirigida à variante\nPortador → vigilância clínica\nNão portador → liberar na maioria"])
  D4 -->|"VUS"| C6(["VUS NÃO autoriza cascata genética\nParentes → rastreio CLÍNICO"])
  D4 -->|"Negativo / inconclusivo"| C7(["Sem cascata genética\nParentes → rastreio CLÍNICO\nperiódico"])

  C5 --> D5{"Parente em rastreio\ncom sintoma/ECG novo?"}
  C6 --> D5
  C7 --> D5
  C4 --> D5

  D5 -->|"Sim"| C8(["Reaplicar gate D1\nno rastreado\nPS ou retorno curto"])
  D5 -->|"Não"| C9(["Manter plano familiar\nRetorno conforme rede\nSem doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C8 alerta;
  class C2,C3,C4,C5,C6,C7,C9 conduta;
```

## Notas

- **D1** = gate de segurança (não negociável).
- **D2/C3** = aconselhamento **antes** do teste (EHRA 2022 / ESC 2023).
- **D4** = três destinos familiares distintos (P/LP vs. VUS vs. negativo).
- **D5** = o rastreado vira paciente se sintoma/ECG mudar.
- HCM/amiloide ambulatory: #844. Chagas: #862. PPCM/gestação: #849 (outra pasta).
