---
title: "Fluxograma: coloides na UTI — SAFE/ALBIOS NS; CHEST mais TRS; 6S mais morte; CRISTAL 28 d NS"
slug: fluxograma-coloides-safe-albios-chest-6s-cristal
theme: "Terapia intensiva"
kind: fluxograma
summary: "SAFE: albumina 4% morte 28 d P=0,87. ALBIOS: albumina 20% na sepse P=0,94. CHEST: HES morte P=0,26, TRS P=0,04. 6S: HES na sepse morte 51% vs 43% P=0,03. CRISTAL: classe mista, 28 d P=0,26; 90 d secundário. Não vender 90 d do CRISTAL nem lesão renal do CHEST."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em SAFE PMID 15163774, ALBIOS PMID 24635772, CHEST PMID 23075127, 6S PMID 22738085, CRISTAL PMID 24108515. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Finfer S, et al. SAFE. N Engl J Med. 2004;350(22):2247-56. PMID: 15163774."
  - "Caironi P, et al. ALBIOS. N Engl J Med. 2014;370(15):1412-21. PMID: 24635772."
  - "Myburgh JA, et al. CHEST. N Engl J Med. 2012;367(20):1901-11. PMID: 23075127."
  - "Perner A, et al. 6S. N Engl J Med. 2012;367(2):124-34. PMID: 22738085."
  - "Annane D, et al. CRISTAL. JAMA. 2013;310(17):1809-17. PMID: 24108515."
  - "Documento da casa visep-insulina-intensiva-e-pentastarch-na-sepse-grave — HES 200/0,5; ≠ 6S."
---

# Fluxograma: coloide na UTI?

```mermaid
flowchart TD
  R0["Quer infundir coloide"] --> D1{"Qual coloide e em quem?"}

  D1 -->|"Albumina 4% para repor volume<br/>(SAFE)"| C1(["Morte 28 d P=0,87. Empatou"])

  D1 -->|"Albumina 20% até 30 g/L na sepse<br/>(ALBIOS)"| C2(["Morte 28 d P=0,94. PAM/balanço não são morte"])

  D1 -->|"HES 130/0,4 em UTI mista<br/>(CHEST)"| C3(["Morte 90 d P=0,26. Mais TRS P=0,04<br/>Não cherry-pick da lesão renal"])

  D1 -->|"HES 130/0,42 na sepse grave<br/>(6S)"| C4(["Mais morte 51% vs 43%, P=0,03<br/>Mais TRS. Não usar"])

  D1 -->|"Coloide 'qualquer' vs cristaloide<br/>(CRISTAL)"| C5(["Morte 28 d P=0,26. Dia 90 é secundário<br/>Classe mista, aberto. Não anula 6S"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**Amido na sepse mata mais (6S).** Albumina não salvou (SAFE/ALBIOS). CRISTAL não reabre coloide — o primário de 28 dias empatou.
