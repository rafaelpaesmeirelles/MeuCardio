---
slug: fluxograma-sinalizadores-ambulatoriais-qt-longo
title: 'Fluxograma: sinalizadores ambulatoriais de QT longo — urgência vs. canalopatias vs. revisão farmacológica'
kind: fluxograma
theme: Arritmias
summary: 'QT longo no consultório: reconhecer emergência, investigar contexto congênito e revisar fármacos, eletrólitos
  e QTc; risco elétrico elevado exige avaliação imediata e monitorização, com decisão coordenada sobre o agente
  implicado.'
tags: []
source_refs:
- 'Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for the management of patients with ventricular
  arrhythmias and the prevention of sudden cardiac death. Eur Heart J. 2022;43(40):3997-4126. DOI: 10.1093/eurheartj/ehac262.
  PMID: 36017572'
- 'Priori SG, Wilde AA, Horie M, et al. HRS/EHRA/APHRS expert consensus statement on the diagnosis and management
  of patients with inherited primary arrhythmia syndromes. Heart Rhythm. 2013;10(12):1932-1963. DOI: 10.1016/j.hrthm.2013.05.014.
  PMID: 24011539'
- 'Drew BJ, Ackerman MJ, Funk M, et al. Prevention of torsade de pointes in hospital settings: a scientific statement
  from the American Heart Association and the American College of Cardiology Foundation. Circulation. 2010;121(8):1047-1060.
  DOI: 10.1161/CIRCULATIONAHA.109.192704. PMID: 20142454'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma: sinalizadores ambulatoriais de QT longo

Prosa: [sinalizadores-ambulatoriais-de-qt-longo-congenito-e-adquirido-quando-escalar](/biblioteca/sinalizadores-ambulatoriais-de-qt-longo-congenito-e-adquirido-quando-escalar) e [qt-longo-ambulatorial-quando-suspender-farmacos-prolongadores-de-qt](/biblioteca/qt-longo-ambulatorial-quando-suspender-farmacos-prolongadores-de-qt).

Canalopatias: [canalopatias-sindrome-do-qt-longo-e-sindrome-de-brugada-diagnostico-e-manejo](/biblioteca/canalopatias-sindrome-do-qt-longo-e-sindrome-de-brugada-diagnostico-e-manejo).

Psicofármacos: [fluxograma-escolha-de-antidepressivo-e-antipsicotico-no-cardiopata-risco-de-qt](/biblioteca/fluxograma-escolha-de-antidepressivo-e-antipsicotico-no-cardiopata-risco-de-qt).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: QTc prolongado<br/>ou SQTL conhecida/suspeita"] --> D1{"Há emergência no paciente AGORA?<br/>TdP/TV polimórfica/FV, instabilidade,<br/>overdose, eletrólito grave ou síncope<br/>muito recente ainda de alto risco"}

  D1 -->|"Sim"| C1(["PS / urgência / monitorização adequada<br/>ECG e causas reversíveis<br/>Rever ofensor imediatamente"])

  D1 -->|"Não"| D2{"Contexto congênito/familiar?<br/>QTc persistente compatível, escore clínico,<br/>variante familiar ou forte suspeita"}

  D2 -->|"Sim"| C2(["Canalopatias / EP / genética<br/>Teste em cascata pode ser indicado<br/>mesmo sem fenótipo confirmado"])

  D2 -->|"Não / predominantemente adquirido"| D3{"Há fármaco prolongador de QT?"}

  D3 -->|"Não"| C3(["Rever técnica QTc e causas secundárias<br/>Reavaliar conforme risco e sintomas"])

  D3 -->|"Sim"| P1["Confirmar QTc + basal<br/>QRS largo/pacing: ajuste especializado<br/>K/Mg/Ca, bradicardia, interações<br/>e outros prolongadores"]
  P1 --> D4{"QTc >500 ms ou Δ≥60 ms<br/>OU precursores/sintomas/fatores acumulados<br/>que elevem materialmente o risco?"}

  D4 -->|"Sim"| D5{"Fármaco é essencial / alto benefício<br/>e interrupção também traz risco?"}
  D5 -->|"Não / substituível"| C4(["Retirar/pausar ofensor quando apropriado<br/>Definir monitorização/urgência pelo quadro<br/>Prescritor decide substituto"])
  D5 -->|"Sim"| C5(["Avaliação médica imediata e monitorização adequada<br/>Decisão risco-benefício com prescritor<br/>Discutir retirada ou alternativa segura"])

  D4 -->|"Não"| C6(["Não suspender reflexamente<br/>Revisar risco-benefício e reavaliar ECG<br/>Educar sinais de alarme"])

  C5 --> D6{"É psicofármaco essencial?"}
  D6 -->|"Sim"| C7(["Usar orientação canônica Psycho-Cardio/QT<br/>Co-manejo com prescritor"])
  D6 -->|"Não"| C8(["Seguir plano coordenado com prescritor"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Notas

- Evento agudo **em familiar** não transforma paciente assintomático estável em emergência; aumenta prioridade para avaliação genética/canalopatias.
- Síncope remota já esclarecida é diferente de síncope muito recente ainda de alto risco.
- QTc >500 ms ou Δ≥60 ms são marcadores de ação/risk review; não significam “suspender tudo” sem considerar benefício e contexto.
- Genética pode ser indicada por variante familiar conhecida ou rastreamento em cascata mesmo com QTc normal.
- O ramo psicofármaco exige co-manejo com o prescritor; risco elétrico alto não permite aguardar consulta eletiva.
