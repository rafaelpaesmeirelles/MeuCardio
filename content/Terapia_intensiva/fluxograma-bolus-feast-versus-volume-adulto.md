---
title: "Fluxograma: bolus na criança africana (FEAST, morte sobe) ≠ volume no adulto (CLASSIC/CLOVERS)"
slug: fluxograma-bolus-feast-versus-volume-adulto
theme: "Terapia intensiva"
kind: fluxograma
summary: "FEAST: bolus 20–40 mL/kg aumentou morte 48 h. CLASSIC e CLOVERS são adultos em UTI rica, outras perguntas. Não fundir."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em FEAST PMID 21615299. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Maitland K, et al. FEAST. N Engl J Med. 2011;364(26):2483-2495. PMID: 21615299."
  - "Documento da casa classic-restricao-de-fluido-intravenoso-no-choque-septico."
  - "Documento da casa clovers-fluido-restritivo-versus-liberal-na-hipotensao-por-sepse."
  - "Documento da casa fluxograma-volume-e-vasopressor-na-sepse-classic-clovers-censer."
---

# Fluxograma: bolus de fluido — criança africana ≠ adulto

```mermaid
flowchart TD
  R0["Bolus de fluido?"] --> D1{"Qual o cenário?"}

  D1 -->|"Criança febril, África, sem desnutrição"| C1(["FEAST: morte 48 h sobe<br/>Albumina = SF. Sem bolus foi melhor"])

  D1 -->|"Adulto, UTI rica, sepse"| C2(["CLASSIC / CLOVERS<br/>Outra pergunta, outro desfecho"])

  D1 -->|"Choque séptico, vasopressor"| C3(["CENSER / SOAP II / VANISH<br/>Não é ensaio de bolus"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**FEAST não autoriza bolus nesta criança.** Também não apaga CLASSIC. Não colapsar os três.
