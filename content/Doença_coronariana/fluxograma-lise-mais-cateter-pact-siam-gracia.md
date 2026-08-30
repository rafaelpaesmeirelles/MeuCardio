---
title: "Fluxograma: lise e depois o cateter — PACT (perviedade), SIAM-III (composto+TLR), GRACIA-1 (composto 12 meses)"
slug: fluxograma-lise-mais-cateter-pact-siam-gracia
theme: "Doença coronariana"
kind: fluxograma
summary: "PACT: bolus 50 mg, perviedade sim, FE igual. SIAM-III: stent 6 h vs 2 semanas, composto 6 meses inclui TLR, n=197. GRACIA-1: composto 12 meses, morte/reinfarto P=0,07. ASSENT-4 (lise plena + ICP primária) piora."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em PACT PMID 10588209, SIAM-III PMID 12932593, GRACIA-1 PMID 15380963. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Ross AM, et al. PACT. J Am Coll Cardiol. 1999;34(7):1954-1962. PMID: 10588209."
  - "Scheller B, et al. SIAM III. J Am Coll Cardiol. 2003;42(4):634-641. PMID: 12932593."
  - "Fernandez-Avilés F, et al. GRACIA-1. Lancet. 2004;364(9439):1045-1053. PMID: 15380963."
  - "Documento da casa fluxograma-icp-facilitada-assent-4-finesse."
  - "Documento da casa fluxograma-farmacoinvasiva-transfer-caress-stream-prague-2."
---

# Fluxograma: lise + cateter — três perguntas diferentes

```mermaid
flowchart TD
  R0["Já lisou ou vai lisar de caminho?"] --> D1{"Qual o esquema?"}

  D1 -->|"Bolus 50 mg + angiografia já"| C1(["PACT: perviedade 61% vs 34%<br/>FE entre braços igual"])

  D1 -->|"Stent em 6 h vs eletivo 2 semanas"| C2(["SIAM-III: composto 25,6% vs 50,6%<br/>Inclui TLR. n=197"])

  D1 -->|"Angio rotina em 24 h vs isquemia"| C3(["GRACIA-1: composto 9% vs 21%<br/>Morte/reinfarto P=0,07"])

  D1 -->|"Lise plena na porta da ICP primária"| C4(["ASSENT-4: piora. Não fazer"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Nenhum desses quatro é o mesmo ensaio.** Perviedade ≠ FE ≠ composto com TLR ≠ morte.
