---
title: "Fluxograma: hirudina na SCA — GUSTO-IIb e OASIS-2, primários NS"
slug: fluxograma-hirudina-gusto-iib-oasis-2
theme: "Doença coronariana"
kind: fluxograma
summary: "GUSTO-IIb 30 d P=0,06 (IC inclui 1); OASIS-2 7 d P=0,077. Não vender 24 h, 72 h nem o composto com angina. Sangramento maior sobe no OASIS-2. OASIS-1 é piloto. OASIS-5 é fondaparinux."
review_status: pendente_revisao
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em GUSTO-IIb PMID 8778585 e OASIS-2 PMID 9989712. Publicação sujeita à aprovação do responsável técnico."
source_refs:
  - "GUSTO IIb Investigators. N Engl J Med. 1996;335(11):775-782. PMID: 8778585."
  - "OASIS-2 Investigators. Lancet. 1999;353(9151):429-438. PMID: 9989712."
---

# Fluxograma: hirudina na SCA?

```mermaid
flowchart TD
  R0["Quer citar hirudina/lepirudina na SCA"] --> D1{"Qual ensaio?"}

  D1 -->|"Espectro com e sem supra"| C1(["GUSTO-IIb n=12.142<br/>30 d morte/IAM P=0,06<br/>IC inclui 1,00<br/>24 h P=0,001 — não é primário"])

  D1 -->|"Só sem supra"| C2(["OASIS-2 n=10.141<br/>7 d morte CV/IAM P=0,077<br/>composto com angina P=0,0125 — secundário<br/>transfusão P=0,01"])

  D1 -->|"OASIS-1 n=909"| C3(["Piloto. Não confirmar com ele"])

  D1 -->|"Fondaparinux"| C4(["OASIS-5: arquivo próprio<br/>outra molécula"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Dois grandes RCTs, dois primários NS.** Não recitar o abstract que chama de superior. Hirudina saiu de cena.
