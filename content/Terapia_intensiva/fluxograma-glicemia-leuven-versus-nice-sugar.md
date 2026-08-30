---
title: "Fluxograma: glicemia na UTI — Leuven 2001 (um centro) ≠ NICE-SUGAR (morte 90 d sobe com 81–108)"
slug: fluxograma-glicemia-leuven-versus-nice-sugar
theme: "Terapia intensiva"
kind: fluxograma
summary: "Leuven: UTI cirúrgica única, morte na UTI cai. NICE-SUGAR: 6.104, alvo 81–108 aumenta morte 90 d. Portland/cirurgia cardíaca é outro dump."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em NICE-SUGAR PMID 19318384 e Leuven PMID 11794168. Revisão científica concluída em 30/08/2026."
source_refs:
  - "NICE-SUGAR Study Investigators. N Engl J Med. 2009;360(13):1283-1297. PMID: 19318384."
  - "van den Berghe G, et al. N Engl J Med. 2001;345(19):1359-1367. PMID: 11794168."
  - "Documento da casa glicemia-perioperatoria-em-cirurgia-cardiaca-do-protocolo-portland-ao-nice-sugar."
  - "Documento da casa leuven-2-insulina-intensiva-na-uti-medica — ITT morte NS."
  - "Documento da casa glucontrol-insulina-intensiva-versus-alvo-intermediario — parou cedo."
  - "Documento da casa visep-insulina-intensiva-e-pentastarch-na-sepse-grave — hipoglicemia 17%."
---

# Fluxograma: alvo glicêmico na UTI

```mermaid
flowchart TD
  R0["Alvo 80–110 na UTI?"] --> D1{"Qual a evidência?"}

  D1 -->|"Leuven 2001"| C1(["UTI cirúrgica, 1 centro, n=1548<br/>Morte na UTI 4,6% vs 8,0%"])

  D1 -->|"NICE-SUGAR 2009"| C2(["UTI geral, n=6104<br/>Morte 90 d 27,5% vs 24,9% — intensivo pior"])

  D1 -->|"Cirurgia cardíaca"| C3(["Dump Portland / NICE-SUGAR<br/>Não é este fluxograma"])

  D1 -->|"Leuven 2 UTI médica"| C4(["ITT morte hospitalar NS<br/>Subgrupo ≥3 d não é primário"])

  D1 -->|"Glucontrol / VISEP"| C5(["Pararam cedo<br/>Mais hipoglicemia no intensivo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```
