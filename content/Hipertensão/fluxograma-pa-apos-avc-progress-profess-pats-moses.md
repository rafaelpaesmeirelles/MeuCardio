---
title: "Fluxograma: PA após AVC — PROGRESS combinação sim; PRoFESS BRA isolado NS; PATS morte NS; MOSES conta recorrente"
slug: fluxograma-pa-apos-avc-progress-profess-pats-moses
theme: "Hipertensão"
kind: fluxograma
summary: "PROGRESS: perindopril+indapamida reduz AVC; monoterapia sem redução discernível. PRoFESS: telmisartana P=0,23. PATS: indapamida reduz AVC, morte NS (preliminar). MOSES: primário com eventos recorrentes — não confrontar com PRoFESS."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em PROGRESS PMID 11589932, PRoFESS PMID 18753639, PATS PMID 8575241, MOSES PMID 15879332. Revisão científica concluída em 30/08/2026."
source_refs:
  - "PROGRESS Collaborative Group. Lancet. 2001;358(9287):1033-1041. PMID: 11589932."
  - "Yusuf S, et al. PRoFESS. N Engl J Med. 2008;359(12):1225-1237. PMID: 18753639."
  - "PATS Collaborating Group. Chin Med J (Engl). 1995;108(9):710-717. PMID: 8575241."
  - "Schrader J, et al. MOSES. Stroke. 2005;36(6):1218-1226. PMID: 15879332."
---

# Fluxograma: baixar a PA depois do AVC

```mermaid
flowchart TD
  R0["AVC ou AIT prévio. Qual ensaio está sendo citado?"] --> D1{"Qual o regime e o desfecho?"}

  D1 -->|"Perindopril+indapamida (PROGRESS)"| C1(["AVC caiu. Monoterapia de perindopril:<br/>sem redução discernível"])

  D1 -->|"Telmisartana isolada cedo (PRoFESS)"| C2(["Primário NS. HR 0,95; P=0,23<br/>PA −3,8/2,0"])

  D1 -->|"Indapamida 2,5 mg (PATS)"| C3(["AVC 3 a RR 0,71. Morte NS.<br/>Preliminar, DOI ausente"])

  D1 -->|"Eprosartana vs nitrendipina (MOSES)"| C4(["Primário soma eventos recorrentes<br/>n=1.405. Não é tempo até o primeiro"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**A âncora da casa continua sendo a combinação do PROGRESS.** PRoFESS não autoriza BRA isolado. MOSES não derruba PRoFESS.
