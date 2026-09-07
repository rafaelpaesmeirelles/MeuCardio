---
title: "Fluxograma: sinalizadores ambulatoriais de vacinação no cardiopata — PS vs. prioridade vs. eletivo"
slug: fluxograma-sinalizadores-ambulatoriais-vacinacao-cardiopata
theme: "Geral"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: instabilidade → PS; pós-SCA/IC sem calendário → prioridade na consulta; ASCVD estável → oferta eletiva; contraindicação → referir imunização."
review_status: pendente_revisao
review_note: "Árvore irmã dos protocolos de vacinação cardiopata ambulatorial (07/09/2026). Fröbert PMID 34459211; Udell PMID 24150467; Visseren PMID 34458905; McDonagh PMID 34447992. Sem doses."
source_refs:
  - "Fröbert O, Götberg M, Erlinge D, et al.; IAMI Investigators. Influenza Vaccination After Myocardial Infarction: A Randomized, Double-Blind, Placebo-Controlled, Multicenter Trial. Circulation. 2021;144(18):1476-1484. DOI: 10.1161/CIRCULATIONAHA.121.057042. PMID: 34459211"
  - "Udell JA, Zawi R, Bhatt DL, et al. Association between influenza vaccination and cardiovascular outcomes in high-risk patients: a meta-analysis. JAMA. 2013;310(16):1711-1720. DOI: 10.1001/jama.2013.279206. PMID: 24150467"
  - "Visseren FLJ, Mach F, Smulders YM, et al.; ESC Scientific Document Group. 2021 ESC Guidelines on cardiovascular disease prevention in clinical practice. Eur Heart J. 2021;42(34):3227-3337. DOI: 10.1093/eurheartj/ehab484. PMID: 34458905"
  - "McDonagh TA, Metra M, Adamo M, et al.; ESC Scientific Document Group. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992"
---

# Fluxograma: sinalizadores ambulatoriais de vacinação no cardiopata

Prosa: [`sinalizadores-ambulatoriais-vacinacao-cardiopata-quando-escalar`](sinalizadores-ambulatoriais-vacinacao-cardiopata-quando-escalar.md) e [`vacinacao-cardiopata-no-consultorio-pos-sca-ic-checklist`](vacinacao-cardiopata-no-consultorio-pos-sca-ic-checklist.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta cardiologia:<br/>status vacinal / temporada"] --> D1{"Instabilidade CV<br/>ou infecciosa agora?"}

  D1 -->|"Sim"| C1(["PS / via aguda AGORA<br/>Não vacinar nesta visita"])

  D1 -->|"Não"| D2{"Contraindicação /<br/>anafilaxia prévia<br/>nao esclarecida?"}

  D2 -->|"Sim"| C2(["Não aplicar no consultório<br/>Referir imunização / alergia"])

  D2 -->|"Não"| D3{"Pós-SCA / IAM<br/>≤1 ano?"}

  D3 -->|"Sim"| D4{"Influenza da<br/>temporada ok?"}
  D4 -->|"Não"| C3(["PRIORIDADE hoje<br/>Oferecer / registrar<br/>IAMI + Udell"])
  D4 -->|"Sim"| D5

  D3 -->|"Não"| D5{"IC crônica?"}

  D5 -->|"Sim"| D6{"Influenza e<br/>pneumococo ok?"}
  D6 -->|"Não"| C4(["Completar nesta visita<br/>ou prazo curto<br/>ESC HF 2021"])
  D6 -->|"Sim"| C5(["Manter calendário<br/>+ COVID local"])

  D5 -->|"Não"| D7{"ASCVD /<br/>alto risco CV?"}
  D7 -->|"Sim"| D8{"Influenza<br/>temporada ok?"}
  D8 -->|"Não"| C6(["Oferecer na visita<br/>ESC Prevenção 2021"])
  D8 -->|"Sim"| C5
  D7 -->|"Não"| C7(["Calendário geral<br/>Sem gate cardiológico extra"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef prioridade fill:#fff4e5,stroke:#b36b00,color:#3b2200;
  class C1 alerta;
  class C3,C4 prioridade;
  class C2,C5,C6,C7 conduta;
```

## Notas

- **D1** = gate de segurança: não imunizar na descompensação.
- **D3/D4/C3** = maior prioridade relativa (IAMI; interação Udell com SCA recente).
- **D5/D6/C4** = influenza + pneumococo na IC (ESC HF 2021).
- **D7/C6** = ASCVD estável ainda merece oferta (ESC Prevenção 2021), com benefício absoluto tipicamente menor que pós-SCA.
- Não decide doses, marcas, PCV vs PPSV, nem esquemas COVID.
