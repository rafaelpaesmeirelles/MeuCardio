---
title: "Fluxograma: enoxaparina na SCA — ESSENCE, TIMI 11B, SYNERGY, ExTRACT"
slug: fluxograma-enoxaparina-essence-timi-11b-synergy
theme: "Doença coronariana"
kind: fluxograma
summary: "ESSENCE: tríplice com angina, era conservadora. TIMI 11B: composto com IC que toca 1,00; fase extra-hospitalar sangra. SYNERGY: era invasiva, primário NS, mais TIMI major. ExTRACT: STEMI com lise. FRISC I é dalteparina vs placebo. OASIS-5 é fondaparinux."
review_status: pendente_revisao
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em ESSENCE PMID 9250846, TIMI 11B 10517729, SYNERGY 15238590, ExTRACT 16537665, FRISC 8596317. Publicação sujeita à aprovação do responsável técnico."
source_refs:
  - "Cohen M, et al. ESSENCE. N Engl J Med. 1997;337(7):447-452. PMID: 9250846."
  - "Antman EM, et al. TIMI 11B. Circulation. 1999;100(15):1593-1601. PMID: 10517729."
  - "Ferguson JJ, et al. SYNERGY. JAMA. 2004;292(1):45-54. PMID: 15238590."
---

# Fluxograma: qual ensaio de enoxaparina está sendo citado?

```mermaid
flowchart TD
  R0["Quer citar enoxaparina na SCA"] --> D1{"Qual população e comparador?"}

  D1 -->|"Angina/IAM sem Q vs HNF, era 1997"| C1(["ESSENCE: tríplice com angina<br/>14 d P=0,019; maior empata<br/>não vender morte/IAM isolado"])

  D1 -->|"Mesma pergunta + fase extra-hospitalar"| C2(["TIMI 11B: 8 e 43 d P=0,048<br/>IC toca 1,00<br/>extra-hospitalar sangra sem ganho"])

  D1 -->|"SCA sem supra invasiva"| C3(["SYNERGY: morte/IAM OR 0,96<br/>IC inclui 1; TIMI major P=0,008"])

  D1 -->|"STEMI com lise"| C4(["ExTRACT: arquivo próprio"])

  D1 -->|"Dalteparina vs placebo"| C5(["FRISC I: 6 d sim; 4–5 meses NS<br/>não é FRISC II"])

  D1 -->|"Fondaparinux vs enoxaparina"| C6(["OASIS-5: arquivo próprio"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Mensagem prática

**Não transportar o ESSENCE para a SCA invasiva contemporânea — o SYNERGY já testou isso e empatou o isquêmico.** FRISC I não é FRISC II.
