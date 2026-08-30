---
title: "Fluxograma: esteroide no choque séptico — CORTICUS morte NS; não fundir com ADRENAL/APROCCHSS"
slug: fluxograma-esteroide-corticus-adrenal-aprocchss
theme: "Terapia intensiva"
kind: fluxograma
summary: "CORTICUS: morte 28 d NS no não-respondedor e no total. Reversão de choque mais rápida não é mortalidade. ADRENAL e APROCCHSS estão no dump combinado — outros n, outras perguntas."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em CORTICUS PMID 18184957. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Sprung CL, et al. CORTICUS. N Engl J Med. 2008;358(2):111-124. PMID: 18184957."
  - "Documento da casa corticosteroide-no-choque-septico-refratario-corticus-adrenal-aprocchss."
  - "Documento da casa corticus-hidrocortisona-no-choque-septico."
---

# Fluxograma: CORTICUS não é ADRENAL

```mermaid
flowchart TD
  R0["Esteroide no choque séptico?"] --> D1{"Qual ensaio?"}

  D1 -->|"CORTICUS 50 mg 6/6 h"| C1(["Morte 28 d NS<br/>Não-respondedor 39,2% vs 36,1%"])

  D1 -->|"ADRENAL / APROCCHSS"| C2(["Dump combinado<br/>Outro n, outra dose"])

  D1 -->|"Reversão mais rápida de choque"| C3(["Não vender como mortalidade<br/>CORTICUS: mais superinfecção"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```
