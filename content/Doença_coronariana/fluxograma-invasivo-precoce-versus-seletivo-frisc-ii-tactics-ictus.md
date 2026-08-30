---
title: "Fluxograma: invasivo precoce vs seletivo — FRISC II e TACTICS ganham; ICTUS não"
slug: fluxograma-invasivo-precoce-versus-seletivo-frisc-ii-tactics-ictus
theme: "Doença coronariana"
kind: fluxograma
summary: "SCA sem supra: FRISC II reduz morte/IAM 6 meses (P=0,031); morte P=0,10 NS. TACTICS-TIMI 18 reduz composto 6 meses (P=0,025); morte/IAM IC toca 1,00. ICTUS (troponina, terapia otimizada) primário 1 ano P=0,33 NS e IAM maior no invasivo (P=0,005). Não é o fluxograma ESC 2023 de timing. Não vender GPI como o contraste do TACTICS."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em FRISC II PMID 10475181, TACTICS PMID 11419424 e ICTUS PMID 16162880. Não reescreve fluxograma-sca-sem-supra-timing-da-estrategia-invasiva-esc-2023. Revisão científica concluída em 30/08/2026."
source_refs:
  - "FRISC II Investigators. Lancet. 1999;354(9180):708-715. PMID: 10475181."
  - "Cannon CP, et al. TACTICS-TIMI 18. N Engl J Med. 2001;344(25):1879-1887. PMID: 11419424."
  - "de Winter RJ, et al. ICTUS. N Engl J Med. 2005;353(11):1095-1104. PMID: 16162880."
  - "Boden WE, et al. VANQWISH. N Engl J Med. 1998;338(25):1785-1792. PMID: 9632444."
---

# Fluxograma: invasivo precoce ou seletivo?

```mermaid
flowchart TD
  R0["SCA sem supra.<br/>Cateterismo de rotina cedo?"] --> D1{"Qual ensaio está sendo citado?"}

  D1 -->|"FRISC II, era 1990, dalteparina fatorial"| C1(["Morte/IAM 6 meses 9,4% vs 12,1%; P=0,031<br/>Morte 1,9% vs 2,9%; P=0,10 NS"])

  D1 -->|"TACTICS-TIMI 18, tirofibana de fundo"| C2(["Composto 6 meses 15,9% vs 19,4%; P=0,025<br/>Morte/IAM OR 0,74; IC toca 1,00<br/>GPI não é o braço randomizado"])

  D1 -->|"ICTUS, troponina T, terapia otimizada"| C3(["Primário 1 ano P=0,33 NS<br/>IAM 15% vs 10%; P=0,005 no invasivo<br/>Morte 2,5% nos dois"])

  R0 --> D2{"É o fluxograma ESC 2023 de timing?"}

  D2 -->|"Sim"| C4(["Outro arquivo da casa.<br/>Não misturar diretriz com estes três RCTs"])

  D1 -->|"VANQWISH, IAM sem Q, era 1990"| C5(["Primário 23 meses P=0,35 NS<br/>Invasivo pior na alta, 1 mês e 1 ano"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**FRISC II e TACTICS sustentam invasivo precoce na sua era; ICTUS mostra que, com troponina e terapia otimizada, o primário empata e o IAM pode subir.** Não colapsar os três num só recado.
