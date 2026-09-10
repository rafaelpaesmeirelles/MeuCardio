---
slug: fluxograma-sinalizadores-ambulatoriais-vacinacao-cardiopata
title: 'Fluxograma: sinalizadores ambulatoriais de vacinação no cardiopata — PS vs. prioridade vs. eletivo'
kind: fluxograma
theme: Geral
summary: 'Árvore ambulatorial: emergência/doença aguda moderada-grave → via aguda ou adiamento; doença leve não
  bloqueia; contraindicação é específica da vacina/componente; após influenza, continuar a checagem das demais vacinas.'
tags: []
source_refs:
- 'Fröbert O, Götberg M, Erlinge D, et al.; IAMI Investigators. Influenza Vaccination After Myocardial Infarction:
  A Randomized, Double-Blind, Placebo-Controlled, Multicenter Trial. Circulation. 2021;144(18):1476-1484. DOI: 10.1161/CIRCULATIONAHA.121.057042.
  PMID: 34459211'
- 'Udell JA, Zawi R, Bhatt DL, et al. Association between influenza vaccination and cardiovascular outcomes in high-risk
  patients: a meta-analysis. JAMA. 2013;310(16):1711-1720. DOI: 10.1001/jama.2013.279206. PMID: 24150467'
- 'Visseren FLJ, Mach F, Smulders YM, et al.; ESC Scientific Document Group. 2021 ESC Guidelines on cardiovascular
  disease prevention in clinical practice. Eur Heart J. 2021;42(34):3227-3337. DOI: 10.1093/eurheartj/ehab484. PMID:
  34458905'
- 'McDonagh TA, Metra M, Adamo M, et al.; ESC Scientific Document Group. 2021 ESC Guidelines for the diagnosis and
  treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368.
  PMID: 34447992'
- 'Brasil. Ministério da Saúde. Manual de Normas e Procedimentos para Vacinação. 2ª ed. Brasília: Ministério da
  Saúde; 2024.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma: sinalizadores ambulatoriais de vacinação no cardiopata

Prosa: [sinalizadores-ambulatoriais-vacinacao-cardiopata-quando-escalar](/biblioteca/sinalizadores-ambulatoriais-vacinacao-cardiopata-quando-escalar) e [vacinacao-cardiopata-no-consultorio-pos-sca-ic-checklist](/biblioteca/vacinacao-cardiopata-no-consultorio-pos-sca-ic-checklist).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta cardiologia:<br/>status vacinal e condição clínica"] --> D1{"Emergência CV<br/>ou doença aguda moderada/grave?"}

  D1 -->|"Sim"| C1(["Via aguda / tratar quadro atual<br/>Adiar vacinação até melhora clínica"])
  D1 -->|"Não"| D1B{"Apenas doença leve<br/>sem instabilidade?"}
  D1B -->|"Sim"| D2
  D1B -->|"Não / assintomático"| D2{"Contraindicação verdadeira<br/>a alguma vacina/componente?"}

  D2 -->|"Sim"| C2(["Não aplicar o produto implicado<br/>Avaliar alternativa / referência<br/>CONTINUAR outras vacinas elegíveis"])
  C2 --> D3
  D2 -->|"Não"| D3{"SCA / IAM recente<br/>ou DAC de alto risco recente?"}

  D3 -->|"Sim"| D4{"Influenza da<br/>temporada ok?"}
  D4 -->|"Não"| C3(["PRIORIDADE: oferecer se elegível<br/>Não aplicar produto contraindicado<br/>Registrar / referir e seguir calendário"])
  C3 --> D5
  D4 -->|"Sim"| D5

  D3 -->|"Não"| D5{"IC crônica?"}

  D5 -->|"Sim"| D6{"Vacinas indicadas<br/>pelo calendário estão ok?"}
  D6 -->|"Não"| C4(["Atualizar somente produtos elegíveis<br/>ou encaminhar com prazo definido<br/>ESC HF + calendário vigente"])
  D6 -->|"Sim"| C5(["Manter calendário vigente"])

  D5 -->|"Não"| D7{"ASCVD /<br/>alto risco CV?"}
  D7 -->|"Sim"| D8{"Influenza<br/>temporada ok?"}
  D8 -->|"Não"| C6(["Oferecer se elegível, excluindo produto contraindicado"])
  D8 -->|"Sim"| C5
  C4 --> FINAL["Conferir outras vacinas pelo PNI<br/>inclusive COVID; registrar plano e consentimento"]
  C6 --> FINAL
  C5 --> FINAL
  D7 -->|"Não"| C7(["Calendário geral<br/>Sem gate cardiológico extra"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef prioridade fill:#fff4e5,stroke:#b36b00,color:#3b2200;
  class C1 alerta;
  class C3,C4 prioridade;
  class C2,C5,C6,C7 conduta;
```

## Notas

- **D1** = doença aguda moderada/grave ou emergência: tratar primeiro; doença leve isolada não deve gerar adiamento automático.
- **D2/C2** = contraindicação é vinculada à vacina/componente implicado; o fluxo segue para as demais vacinas elegíveis.
- **D3/D4/C3** = prioridade de influenza no contexto coronariano recente; não cria janela rígida universal de 1 ano.
- **C3 → D5** = após influenza, continuar a mesma visita e verificar IC/outras vacinas indicadas.
- **D5/D6/C4** = usar calendário oficial vigente para pneumococo/COVID/demais imunobiológicos; este fluxograma não define produto, dose ou intervalo.
- **D7/C6** = ASCVD estável ainda merece oferta de influenza conforme prevenção cardiovascular.

Consultar o [calendário nacional vigente](https://www.gov.br/saude/pt-br/vacinacao/calendario) e conferir contraindicações/precauções **antes de cada produto**, mesmo após passar pelo primeiro nó. Alergia a ovo não deve ser automaticamente equiparada a anafilaxia à vacina influenza: seguir a orientação específica vigente. Benefícios cardiovasculares dos ensaios de influenza não podem ser atribuídos com a mesma magnitude a pneumococo ou COVID.
