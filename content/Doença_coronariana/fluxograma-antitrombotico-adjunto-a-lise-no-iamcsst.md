---
title: "Fluxograma: adjunto à lise no IAMCSST — CLARITY, COMMIT, ExTRACT, OASIS-6"
slug: fluxograma-antitrombotico-adjunto-a-lise-no-iamcsst
theme: "Doença coronariana"
kind: fluxograma
summary: "Lise ainda acontece. Clopidogrel: CLARITY (300+75, ≤75 anos) e COMMIT (75 mg, inclui >75). Enoxaparina na internação supera HNF 48 h (ExTRACT) com mais sangramento. Fondaparinux é OASIS-6, outra comparação. Nenhum destes é a ICP primária."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em CLARITY (PMID 15758000), COMMIT (PMID 16271642), ExTRACT-TIMI 25 (PMID 16537665) e OASIS-6 (PMID 16537725). Doses de enoxaparina no idoso/TFG NÃO relidas — a árvore aponta a monografia. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Sabatine MS, et al. CLARITY-TIMI 28. N Engl J Med. 2005;352(12):1179-1189. PMID: 15758000."
  - "Chen ZM, et al. COMMIT. Lancet. 2005;366(9497):1607-1621. PMID: 16271642."
  - "Antman EM, et al. ExTRACT-TIMI 25. N Engl J Med. 2006;354(14):1477-1488. PMID: 16537665."
  - "Yusuf S, et al. OASIS-6. JAMA. 2006;295(13):1519-1530. PMID: 16537725."
---

# Fluxograma: adjunto à lise no IAMCSST

```mermaid
flowchart TD
  R0["IAMCSST em fibrinolítico<br/>(ICP primária não disponível a tempo)"] --> D1{"Idade?"}

  D1 -->|"≤75 anos"| C1(["Clopidogrel 300 mg + 75 mg/d sobre AAS.<br/>CLARITY: primário 15,0% vs 21,7%"])

  D1 -->|"≥75 anos"| C2(["Clopidogrel 75 mg, sem os 300 mg.<br/>COMMIT: morte 7,5% vs 8,1% em 15 d.<br/>Não é 'zero ataque' — é 75 mg já"])

  R0 --> D2{"Anticoagulação parenteral?"}

  D2 -->|"Enoxaparina na internação vs HNF 48 h"| C3(["ExTRACT: morte/reinfarto 9,9% vs 12,0%.<br/>Sangramento maior 2,1% vs 1,4%.<br/>Dose no idoso/TFG: monografia da casa"])

  D2 -->|"Fondaparinux 2,5 mg"| C4(["OASIS-6: 9,7% vs 11,2% na lise/sem reperfusão.<br/>Não na ICP primária"])

  D2 -->|"Já é ICP primária"| C5(["Sai desta árvore.<br/>HEAT/VALIDATE, não CLARITY/ExTRACT"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**Lise: clopidogrel (ataque conforme a idade) + enoxaparina ou fondaparinux conforme o ensaio.** ICP primária é outro fluxograma.
