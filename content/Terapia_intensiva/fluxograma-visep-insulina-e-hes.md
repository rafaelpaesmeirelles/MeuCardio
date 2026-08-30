---
title: "Fluxograma: VISEP — insulina intensiva (hipoglicemia) e HES 200/0,5 (rim); ≠ 6S e ≠ NICE-SUGAR"
slug: fluxograma-visep-insulina-e-hes
theme: "Terapia intensiva"
kind: fluxograma
summary: "VISEP fatorial. Insulina: mais hipoglicemia e SAE; morte 28 d sem taxa no abstract. HES 200/0,5: mais LRA/TRS. 6S é outro amido. NICE-SUGAR é outro n de glicemia."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em VISEP PMID 18184958. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Brunkhorst FM, et al. VISEP. N Engl J Med. 2008;358(2):125-139. PMID: 18184958."
  - "Documento da casa 6s-amido-hidroxietilico-versus-ringer-acetato-na-sepse-grave."
  - "Documento da casa nice-sugar-controle-glicemico-intensivo-na-uti."
---

# Fluxograma: VISEP tem dois braços

```mermaid
flowchart TD
  R0["VISEP 2×2"] --> D1{"Qual o braço?"}

  D1 -->|"Insulina intensiva"| C1(["Hipoglicemia 17,0% vs 4,1%<br/>Morte 28 d: NS sem taxa no abstract"])

  D1 -->|"HES 200/0,5 10%"| C2(["Mais LRA e TRS vs Ringer<br/>Não é o 6S"])

  D1 -->|"Glicemia UTI geral"| C3(["NICE-SUGAR / Glucontrol / Leuven<br/>Outra árvore"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```
