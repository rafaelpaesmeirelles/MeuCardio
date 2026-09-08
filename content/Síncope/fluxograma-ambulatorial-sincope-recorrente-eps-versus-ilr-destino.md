---
title: "Fluxograma ambulatorial: síncope recorrente — destino EPS vs. ILR vs. PS"
slug: fluxograma-ambulatorial-sincope-recorrente-eps-versus-ilr-destino
theme: "Síncope"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial pós-avaliação inicial: alto risco → via urgente; cicatriz/IAM ou outros substratos selecionados → EP/EPS; baixo risco sem substrato → monitorização/ILR; avaliação de CDI apenas conforme critérios específicos da doença."
review_status: revisado
review_note: "Revisão final 08/09/2026 contra HEAD congelado: findings anteriores presentes; confirmados risco independente, EPS por cicatriz e CDI específico. Acrescentadas causas reversíveis e ILR após investigação negativa de alto risco."
source_refs:
  - "Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304"
  - "Brignole M, Moya A, de Lange FJ, et al. Practical Instructions for the 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):e43-e80. DOI: 10.1093/eurheartj/ehy071"
  - "Shen WK, Sheldon RS, Benditt DG, et al. 2017 ACC/AHA/HRS Guideline for the Evaluation and Management of Patients With Syncope. Circulation. 2017;136(5):e60-e122. DOI: 10.1161/CIR.0000000000000499. PMID: 28280231"
  - "Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death. Eur Heart J. 2022;43(40):3997-4126. PMID: 36017572."
---

# Fluxograma ambulatorial: síncope recorrente — EPS vs. ILR vs. PS

Prosa: [sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia](/biblioteca/sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia). Gate de risco de MSC: [candidatos-ambulatoriais-avaliacao-cdi-apos-sincope-quando-encaminhar](/biblioteca/candidatos-ambulatoriais-avaliacao-cdi-apos-sincope-quando-encaminhar). Monitorização: [fluxograma-sincope-inexplicada-recorrente-monitor-de-eventos-implantavel](/biblioteca/fluxograma-sincope-inexplicada-recorrente-monitor-de-eventos-implantavel).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>síncope recorrente sem diagnóstico definido<br/>após avaliação inicial"] --> D1{"Há marcador de alto risco?<br/>síncope no esforço ou em decúbito<br/>OU sem pródromo<br/>OU ECG de alto risco / hipoperfusão<br/>OU trauma grave associado<br/>OU história familiar de MSC jovem"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar com prioridade<br/>PS / urgência / unidade de síncope<br/>conforme estabilidade e marcador"])

  D1 -->|"Não"| D2{"Existe critério convencional de<br/>avaliação para prevenção de MSC/CDI<br/>pela doença de base?"}

  D2 -->|"Sim"| C2(["Encaminhar EP / centro da doença<br/>Aplicar guideline específico<br/>Síncope isolada NÃO decide CDI"])

  D2 -->|"Não"| D3{"Substrato selecionado para EPS?<br/>IAM prévio ou outra condição de cicatriz<br/>bifascicular com síncope inexplicada<br/>palpitações imediatamente antes<br/>ou bradicardia selecionada"}

  D3 -->|"Sim"| C3(["Referir eletrofisiologia<br/>EPS apenas no contexto apropriado<br/>Não protocolar dispositivo/ablação aqui"])

  D3 -->|"Não"| D4{"ECG sem marcador de alto risco,<br/>sem cardiopatia estrutural relevante,<br/>sem história familiar de MSC jovem<br/>e recorrência ainda provável?"}

  D4 -->|"Sim — baixo risco após triagem"| C4(["Preferir monitorização prolongada / ILR<br/>conforme frequência dos sintomas<br/>Ver fluxograma ILR da pasta"])
  D4 -->|"Incerto"| C5(["Unidade de síncope / retorno curto<br/>Reavaliar hipótese e risco<br/>Não forçar EPS nem CDI"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C5 conduta;
```

## Notas

- **Síncope sem pródromo** é marcador de alto risco por si só; trauma é um fator separado de disposição/gravidade.
- **História familiar de morte súbita em idade jovem** deve ser checada antes de classificar o paciente como baixo risco.
- O ramo de EPS de maior força na ESC 2018 é ligado a **IAM prévio/outra condição relacionada a cicatriz**, não a qualquer cardiopatia estrutural inespecífica.
- FEVE levemente reduzida, isoladamente, não cria indicação de CDI. Quando houver doença com critério convencional de prevenção primária/ secundária, aplicar o guideline específico, incluindo tratamento otimizado, timing e prognóstico quando pertinentes.
- HCM, Brugada, QT longo, CPVT e outras doenças arrítmicas devem seguir **estratificação específica da doença**, não um agrupamento genérico.

## Limites após a avaliação inicial

Marcadores de risco exigem avaliação prioritária, cuja urgência depende do evento atual e da estabilidade; história remota já esclarecida não cria emergência automática. Instabilidade ou arritmia sustentada atual exige via de emergência. Avaliação de prevenção secundária precisa excluir causas reversíveis e considerar o contexto da arritmia; não equivale a implante automático.

Após investigação completa sem causa e sem indicação de marcapasso/CDI, pacientes inicialmente de alto risco também podem se beneficiar de ILR conforme avaliação especializada. O ramo de baixo risco deste fluxo não exclui essa possibilidade posterior. A nomenclatura de insuficiência cardíaca não muda os limiares específicos de elegibilidade de dispositivos.
