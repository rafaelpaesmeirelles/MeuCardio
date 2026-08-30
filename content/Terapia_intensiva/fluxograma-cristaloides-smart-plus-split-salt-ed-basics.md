---
title: "Fluxograma: cristaloide balanceado vs salina — SMART/PLUS/SPLIT/SALT-ED/BaSICS"
slug: fluxograma-cristaloides-smart-plus-split-salt-ed-basics
theme: "Terapia intensiva"
kind: fluxograma
summary: "SALT-ED: dias fora do hospital P=0,41 (MAKE-30 secundário). SMART: MAKE-30 P=0,04, morte P=0,06, 1 centro. PLUS: morte 90 d P=0,90. BaSICS tipo: morte 90 d P=0,47. BaSICS taxa: P=0,46. SPLIT: LRA P=0,77. Não vender MAKE-30 do PS nem morte do SPLIT."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em SMART PMID 29485925, PLUS PMID 35041780, SALT-ED PMID 29485926, SPLIT PMID 26444692, BaSICS tipo PMID 34375394, BaSICS taxa PMID 34547081. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Semler MW, et al. SMART. N Engl J Med. 2018;378(9):829-839. PMID: 29485925."
  - "Finfer S, et al. PLUS. N Engl J Med. 2022;386(9):815-826. PMID: 35041780."
  - "Self WH, et al. SALT-ED. N Engl J Med. 2018;378(9):819-828. PMID: 29485926."
  - "Young P, et al. SPLIT. JAMA. 2015;314(16):1701-10. PMID: 26444692."
  - "Zampieri FG, et al. BaSICS tipo. JAMA. 2021;326(9):818. PMID: 34375394."
  - "Zampieri FG, et al. BaSICS taxa. JAMA. 2021;326(9):830-838. PMID: 34547081."
---

# Fluxograma: salina ou balanceado?

```mermaid
flowchart TD
  R0["Cristaloide EV. Qual pergunta?"] --> D1{"Onde está o paciente?"}

  D1 -->|"PS, internará fora de UTI<br/>(SALT-ED)"| C1(["Primário: dias fora do hospital 25 vs 25, P=0,41<br/>MAKE-30 4,7% vs 5,6% é SECUNDÁRIO"])

  D1 -->|"UTI"| D2{"O desfecho é morte ou rim?"}

  D2 -->|"Morte 90 d, multicêntrico"| C2(["PLUS P=0,90. BaSICS tipo P=0,47.<br/>Não houve menos morte"])

  D2 -->|"MAKE-30, 1 centro"| C3(["SMART P=0,04. Morte P=0,06.<br/>Não vender mortalidade"])

  D2 -->|"LRA como primário"| C4(["SPLIT P=0,77. TRS P=0,91.<br/>Morte hospitalar é secundário"])

  D2 -->|"Velocidade do bolus"| C5(["BaSICS taxa 333 vs 999 mL/h, P=0,46.<br/>Não é o tipo de fluido"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**Morte 90 d empatou em PLUS e BaSICS.** SMART ganhou composto renal num centro. SALT-ED não mudou dias fora do hospital — o MAKE-30 do PS não é o primário.
