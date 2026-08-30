---
title: "Fluxograma: PROGRESS — o que prescrever depois do AVC"
slug: fluxograma-progress-pos-avc-perindopril-indapamida
theme: "Hipertensão"
kind: fluxograma
summary: "AVC ou AIT prévio, hipertenso ou não: combinação perindopril+indapamida (RRR 43% de AVC). Perindopril isolado: sem redução discernível. Não é HOPE (alto risco misto). Não é SHEP/Syst-Eur (HAS isolada do idoso sem AVC obrigatório)."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em PROGRESS PMID 11589932. Revisão científica concluída em 30/08/2026."
source_refs:
  - "PROGRESS Collaborative Group. Lancet. 2001;358(9287):1033-1041. PMID: 11589932."
  - "Documentos da casa shep-clortalidona-na-hipertensao-sistolica-isolada-do-idoso e hope-ramipril-em-alto-risco-sem-ic-nem-fe-baixa."
  - "Documento da casa fluxograma-pa-apos-avc-progress-profess-pats-moses — PRoFESS NS, PATS morte NS, MOSES recorrente."
---

# Fluxograma: PA depois do AVC (PROGRESS)

```mermaid
flowchart TD
  R0["AVC ou AIT prévio.<br/>Quer baixar a PA para prevenir outro AVC?"] --> D1{"Regime"}

  D1 -->|"Perindopril 4 mg + indapamida"| C1(["PROGRESS: PA −12/5<br/>AVC RRR 43% (30–54)"])

  D1 -->|"Perindopril 4 mg isolado"| C2(["PROGRESS: PA −5/3<br/>sem redução discernível de AVC"])

  R0 --> D2{"Precisa estar hipertenso?"}

  D2 -->|"Não"| C3(["O ensaio ganhou no hipertenso<br/>e no não hipertenso (P<0,01 nos dois)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**Depois do AVC, a evidência deste ensaio é da combinação, não do IECA sozinho.** Independente da PA de entrada. PRoFESS (telmisartana isolada) empatou — ver fluxograma-pa-apos-avc-progress-profess-pats-moses.
