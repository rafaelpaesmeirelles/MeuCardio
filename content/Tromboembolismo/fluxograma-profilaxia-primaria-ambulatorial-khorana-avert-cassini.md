---
title: "Fluxograma: profilaxia primária ambulatorial no câncer — AVERT, CASSINI, SAVE-ONCO"
slug: fluxograma-profilaxia-primaria-ambulatorial-khorana-avert-cassini
theme: "Tromboembolismo"
kind: fluxograma
summary: "Khorana ≥2 iniciando quimio: AVERT (apixabana 2,5) reduz TEV (4,2% vs 10,2%; P<0,001) e sobe sangramento maior mITT (P=0,046). CASSINI (rivaroxabana 10) primário 180 d NS (P=0,10); análise de suporte no período da intervenção não substitui o primário. SAVE-ONCO (semuloparina) reduz TEV em tumor avançado sem seleção por Khorana — não é a HBPM da gaveta. 4,5% no CASSINI já tinham trombose na triagem. ITAC no protocolo de Khorana recorta sobretudo pâncreas avançado."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Âncoras: AVERT PMID 30511879, CASSINI PMID 30786186, SAVE-ONCO PMID 22335737. CASSINI primário NS — não vender período da intervenção. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Carrier M, et al. AVERT. N Engl J Med. 2019;380(8):711-719. PMID: 30511879."
  - "Khorana AA, et al. CASSINI. N Engl J Med. 2019;380(8):720-728. PMID: 30786186."
  - "Agnelli G, et al. SAVE-ONCO. N Engl J Med. 2012;366(7):601-609. PMID: 22335737."
  - "Documento da casa trombose-associada-ao-cancer-escore-de-khorana-e-escolha-de-anticoagulante."
---

# Fluxograma: profilaxia primária ambulatorial — o primário decide

```mermaid
flowchart TD
  R0["Ambulatorial com câncer, sem TEV formado"] --> D1{"Como foi selecionado?"}

  D1 -->|"Khorana >= 2, início de quimio"| D2{"Qual oral?"}
  D1 -->|"Tumor sólido avançado, início de quimio, sem Khorana"| C1(["SAVE-ONCO: semuloparina 20 mg<br/>1,2% vs 3,4%; P<0,001<br/>Não é enoxaparina — não extrapolar"])
  D1 -->|"Já tem TEV"| C2(["Não é profilaxia. CLOT/CATCH/Caravaggio<br/>4,5% no CASSINI já tinham trombose na triagem"])

  D2 -->|"Apixabana 2,5 mg 2x/d"| C3(["AVERT: TEV 4,2% vs 10,2%; P<0,001<br/>Sangramento maior mITT P=0,046"])
  D2 -->|"Rivaroxabana 10 mg/d"| C4(["CASSINI: primário 180 d 6,0% vs 8,8%<br/>P=0,10 NS. Período da intervenção<br/>é suporte — não vender"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**AVERT ganhou TEV e pagou sangramento maior. CASSINI não ganhou o primário de 180 dias.** Semuloparina não autoriza HBPM de gaveta. ITAC no protocolo da casa é mais estreita (pâncreas avançado) do que o Khorana ≥2 destes ensaios — não fundir as duas frases.
