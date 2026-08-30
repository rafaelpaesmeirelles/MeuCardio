---
title: "Fluxograma: aspirina em prevenção primária — ASCEND, ASPREE e ARRIVE"
slug: fluxograma-aspirina-em-prevencao-primaria-ascend-aspree-arrive
theme: "Prevenção e lipídios"
kind: fluxograma
summary: "Sem DAC/AVC/DAP prévios: em geral não iniciar AAS. Idoso saudável (ASPREE) — neutro para CV, mais sangramento, sinal de mortalidade. Diabete sem DAC (ASCEND) — benefício vascular pequeno, sangramento sobe. 'Risco moderado' sem diabete (ARRIVE) — primário neutro, GI dobrou. Prevenção secundária sai desta árvore."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada no abstract do ARRIVE (PMID 30158069) relido nesta revisão editorial e nos documentos já revisados da casa ASPREE e ASCEND (não relidos de novo). MESA/escore de cálcio é outra árvore. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Gaziano JM, et al. ARRIVE. Lancet. 2018;392(10152):1036-1046. PMID: 30158069."
  - "Documentos da casa aspirina-em-prevencao-primaria-no-idoso-saudavel-o-ensaio-aspree, aspirina-em-prevencao-primaria-no-diabetes-o-ensaio-ascend e arrive-aspirina-em-prevencao-primaria-risco-moderado."
  - "Documento da casa fluxograma-escore-de-calcio-coronariano-na-decisao-de-estatina-e-aspirina — outra árvore."
---

# Fluxograma: aspirina em prevenção primária — ASCEND, ASPREE, ARRIVE

```mermaid
flowchart TD
  R0["Pedido de AAS 100 mg<br/>em quem nunca teve DAC, AVC ou DAP"] --> D1{"Já tem indicação de<br/>prevenção secundária<br/>(SCA, stent, AVC isquêmico, DAP)?"}

  D1 -->|"Sim"| C0(["Sai desta árvore.<br/>AAS de prevenção secundária"])

  D1 -->|"Não"| D2{"Idoso saudável no molde ASPREE<br/>(≥70 anos, sem DAC/demência/incapacidade)?"}

  D2 -->|"Sim"| C1(["Não iniciar AAS.<br/>ASPREE: CV HR 0,95; sangramento maior HR 1,38;<br/>mortalidade geral HR 1,14"])

  D2 -->|"Não"| D3{"Diabete tipo 2 sem DAC<br/>(molde ASCEND)?"}

  D3 -->|"Sim"| C2(["Em geral não iniciar.<br/>ASCEND: benefício vascular pequeno,<br/>sangramento maior aumenta"])

  D3 -->|"Não"| D4{"Risco 'moderado' sem diabete<br/>(molde ARRIVE)?"}

  D4 -->|"Sim"| C3(["Não iniciar AAS.<br/>ARRIVE: primário 4,29% vs 4,48%, P=0,60;<br/>GI HR 2,11. A amostra veio baixa de eventos"])

  D4 -->|"Não"| C4(["Sem tríade a favor.<br/>Não medicalizar com AAS.<br/>Cálcio coronariano: árvore MESA"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Prevenção primária: a tríade ARRIVE / ASPREE / ASCEND não autoriza AAS rotineira.** Sangra mais do que previne. Cálcio coronariano é outro documento.
