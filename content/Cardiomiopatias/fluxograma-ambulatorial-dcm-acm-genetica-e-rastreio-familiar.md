---
slug: fluxograma-ambulatorial-dcm-acm-genetica-e-rastreio-familiar
title: 'Fluxograma ambulatorial: CMD e ACM — aconselhamento genético e rastreio familiar'
kind: fluxograma
theme: Cardiomiopatias
summary: 'Árvore de consultório para CMD/NDLVC ou ACM/ARVC: alarme → PS; sem alarme → aconselhamento genético se
  fenótipo claro; resultado P/LP → cascata; VUS/negativo → rastreio clínico familiar — alinhada à ESC 2023 e EHRA
  2022.'
tags: []
source_refs:
- 'Arbelo E, Protonotarios A, Gimeno JR, et al. 2023 ESC Guidelines for the management of cardiomyopathies. Eur
  Heart J. 2023;44(37):3503-3626. DOI: 10.1093/eurheartj/ehad194. PMID: 37622657'
- 'Wilde AAM, Semsarian C, Márquez MF, et al. EHRA/HRS/APHRS/LAHRS Expert Consensus Statement on the State of Genetic
  Testing for Cardiac Diseases. Europace. 2022;24(8):1307-1367. DOI: 10.1093/europace/euac030. PMID: 35373836'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: CMD e ACM — genética e rastreio familiar

Prosa: [sinalizadores-ambulatoriais-dcm-quando-referir-aconselhamento-genetico](/biblioteca/sinalizadores-ambulatoriais-dcm-quando-referir-aconselhamento-genetico) e [sinalizadores-ambulatoriais-acm-arvc-rastreamento-familiar-quando-escalar](/biblioteca/sinalizadores-ambulatoriais-acm-arvc-rastreamento-familiar-quando-escalar).

Não substitui [fluxograma-investigacao-genetica-cardiomiopatia-historia-familiar-morte-subita](/biblioteca/fluxograma-investigacao-genetica-cardiomiopatia-historia-familiar-morte-subita) (árvore EHRA completa, já revisada).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: CMD/NDLVC ou ACM/ARVC<br/>conhecida ou alta suspeita"] --> D1{"Alarme urgente?<br/>síncope recente inexplicada / TV sustentada atual<br/>choques repetidos ou com sintomas<br/>BAV avançado / IC aguda"}

  D1 -->|"Sim"| C1(["Encaminhar AGORA<br/>PS / urgência<br/>Genética NÃO atrasa"])

  D1 -->|"Não"| D2{"Fenótipo de alta probabilidade<br/>(diagnóstico ou Task Force/Padua<br/>em discussão estruturada)?"}

  D2 -->|"Não — fenótipo fraco"| C2(["Não pedir painel amplo<br/>Reavaliar clínica/imagem<br/>EHRA: não testar evidência fraca"])

  D2 -->|"Sim"| C3(["Referir ACONSELHAMENTO genético<br/>antes de qualquer amostra<br/>Educação + direito de não testar"])

  C3 --> D3{"Após aconselhamento:<br/>segue teste no índice?"}

  D3 -->|"Não"| C4(["Vigilância do índice<br/>+ rastreio CLÍNICO<br/>dos parentes de 1º grau"])

  D3 -->|"Sim"| D4{"Resultado no índice?"}

  D4 -->|"P/LP"| C5(["Cascata dirigida à variante<br/>Confirmar causalidade familiar<br/>Separar resultado e fenótipo"])
  D4 -->|"VUS"| C6(["VUS não autoriza cascata preditiva<br/>Segregação especializada se informativa<br/>Parentes → rastreio CLÍNICO"])
  D4 -->|"Negativo / inconclusivo"| C7(["Sem cascata genética<br/>Parentes → rastreio CLÍNICO<br/>periódico"])

  C5 --> DP{"Portador ou fenótipo presente?"}
  DP -->|"Sim"| D5
  DP -->|"Não"| DC{"Variante causal familiar<br/>bem estabelecida?"}
  DC -->|"Sim"| CF(["Alta do rastreio periódico<br/>Orientar novos sintomas"])
  DC -->|"Não / dúvida"| C7
  D5{"Parente em rastreio<br/>com sintoma/ECG/imagem novos?"}
  C6 --> D5
  C7 --> D5
  C4 --> D5

  D5 -->|"Sim"| C8(["Reaplicar gate D1<br/>no rastreado<br/>PS ou retorno curto"])
  D5 -->|"Não"| C9(["Manter plano familiar<br/>Retorno conforme rede<br/>Sem doses neste fluxograma"])

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
- Cardiomiopatia hipertrófica, amiloidose, Chagas e cardiomiopatia periparto têm investigação etiológica e acompanhamento específicos.

## Segurança do seguimento familiar

P/LP significa patogênica/provavelmente patogênica e exige interpretação compatível com gene, mecanismo e fenótipo familiar. VUS não confirma diagnóstico nem libera parentes; análise de segregação em familiares afetados ou informativos pode ajudar na reclassificação sob equipe especializada. Teste negativo no índice não exclui origem hereditária.

Alteração nova de imagem, mesmo sem sintomas ou mudança de ECG, exige avaliação breve em cardiomiopatias. Na ACM, incluir monitorização ambulatorial de ECG também em parentes assintomáticos. Evento remoto já avaliado, mantendo estabilidade, segue revisão ambulatorial de risco; choque único com recuperação completa pede contato urgente com clínica de dispositivos, enquanto choques repetidos, síncope ou instabilidade pedem emergência.
