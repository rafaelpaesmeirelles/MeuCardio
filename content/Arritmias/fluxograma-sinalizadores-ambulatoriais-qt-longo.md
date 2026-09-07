---
title: "Fluxograma: sinalizadores ambulatoriais de QT longo — PS vs. EP/genética vs. suspender ofensor"
slug: fluxograma-sinalizadores-ambulatoriais-qt-longo
theme: "Arritmias"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: QTc longo / SQTL no consultório — gate de PS; braço congênito (EP/genética eletiva); braço adquirido (suspender prolongador sem inventar regime)."
review_status: pendente_revisao
review_note: "Árvore irmã dos protocolos de QT longo ambulatorial (07/09/2026), além #839/#864/#867/#899. Anti-colisão #881. ESC 2022 PMID 36017572; Priori 2013 PMID 24011539; Drew 2010 PMID 20142454. Sem doses."
source_refs:
  - "Zeppenfeld K, Tfelt-Hansen J, de Riva M, et al. 2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death. Eur Heart J. 2022;43(40):3997-4126. DOI: 10.1093/eurheartj/ehac262. PMID: 36017572"
  - "Priori SG, Wilde AA, Horie M, et al. HRS/EHRA/APHRS expert consensus statement on the diagnosis and management of patients with inherited primary arrhythmia syndromes. Heart Rhythm. 2013;10(12):1932-1963. DOI: 10.1016/j.hrthm.2013.05.014. PMID: 24011539"
  - "Drew BJ, Ackerman MJ, Funk M, et al. Prevention of torsade de pointes in hospital settings: a scientific statement from the American Heart Association and the American College of Cardiology Foundation. Circulation. 2010;121(8):1047-1060. DOI: 10.1161/CIRCULATIONAHA.109.192704. PMID: 20142454"
---

# Fluxograma: sinalizadores ambulatoriais de QT longo

Prosa: [`sinalizadores-ambulatoriais-de-qt-longo-congenito-e-adquirido-quando-escalar`](sinalizadores-ambulatoriais-de-qt-longo-congenito-e-adquirido-quando-escalar.md) e [`qt-longo-ambulatorial-quando-suspender-farmacos-prolongadores-de-qt`](qt-longo-ambulatorial-quando-suspender-farmacos-prolongadores-de-qt.md). Canalopatias (diagnóstico/manejo): [`canalopatias-sindrome-do-qt-longo-e-sindrome-de-brugada-diagnostico-e-manejo`](canalopatias-sindrome-do-qt-longo-e-sindrome-de-brugada-diagnostico-e-manejo.md). Psicofármaco: **#881**.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: QTc prolongado<br/>ou SQTL conhecida/suspeita"] --> D1{"Alarme?<br/>síncope / TdP / TV polimórfica<br/>QTc >500 ms ou ↑≥60 ms com risco<br/>eletrólito grave / instabilidade"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>ECG 12 derivações<br/>Suspender ofensor se houver<br/>Sem doses neste fluxo"])

  D1 -->|"Não"| D2{"Contexto congênito?<br/>QTc ≥480 repetido / familiar<br/>escore alto / SQTL conhecida"}

  D2 -->|"Sim"| C2(["EP / genética eletiva<br/>Evitar prolongadores de QT<br/>Não inventar betabloqueador aqui"])

  D2 -->|"Não / predominantemente adquirido"| D3{"Há fármaco prolongador de QT<br/>(ou início/↑ recente)?"}

  D3 -->|"Sim"| P1["Confirmar QTc e basal<br/>Revisar eletrólitos / bradicardia<br/>Polifarmácia QT"]
  P1 --> C3(["Suspender ofensor<br/>(sem inventar substituto)<br/>Retorno 24–72 h + ECG"])

  D3 -->|"Não"| C4(["Investigar causa secundária<br/>Reavaliar técnica de QTc<br/>Educar alarmes · retorno usual"])

  C3 --> D4{"Ofensor é psicofármaco<br/>essencial / risco de crise?"}
  D4 -->|"Sim"| C5(["Usar também pacote #881<br/>Psycho-Cardio — não interromper<br/>só por receio genérico neste fluxo"])
  D4 -->|"Não"| C6(["Manter suspensão + retorno<br/>Prescritor original decide substituto"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C5,C6 conduta;
```

## Notas

- **D1** = gate de segurança (Drew 2010 + sintoma/TdP).
- **D2** = braço congênito (ESC 2022 / Priori 2013) → EP/genética, não “ Holter daqui a um ano”.
- **D3/C3** = braço adquirido → **suspender ofensor** sem regime inventado.
- **D4** = ponte explícita anti-colisão com **#881**.
- Não decide doses, CDI, mexiletina nem classes de betabloqueador.
