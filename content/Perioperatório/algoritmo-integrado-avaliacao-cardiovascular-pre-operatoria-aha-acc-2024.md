---
title: "Avaliação cardiovascular pré-operatória: algoritmo integrado AHA/ACC 2024"
slug: algoritmo-integrado-avaliacao-cardiovascular-pre-operatoria-aha-acc-2024
theme: "Perioperatório"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Reclassificado em 26/08/2026: o conteúdo é uma árvore Mermaid de decisão baseada na AHA/ACC 2024 e deve aparecer na frente Fluxogramas. PMID e DOI já declarados; sem pendência de verificação humana."
revisado_por_voce: false
summary: "Árvore de decisão baseada na diretriz AHA/ACC 2024 para definir quando prosseguir para cirurgia, pausar para tratar doença cardiovascular ativa, usar escores, avaliar capacidade funcional, biomarcadores e testes adicionais."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
---

# Avaliação cardiovascular pré-operatória — abordagem escalonada

A diretriz AHA/ACC 2024 recomenda uma avaliação **escalonada**, evitando investigação cardiovascular indiscriminada. O princípio é solicitar exames adicionais apenas quando o resultado puder modificar a decisão de operar, o momento da cirurgia ou o manejo perioperatório.

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente com fatores de risco, doença ou sintomas cardiovasculares<br/>programado para cirurgia não cardíaca"] --> B{"Cirurgia emergente?"}
    B -->|"Sim"| C["Prosseguir para cirurgia<br/>com manejo perioperatório apropriado"]
    B -->|"Não"| D{"Há condição cardiovascular ativa?"}
    D -->|"SCA, arritmia instável ou IC descompensada"| E["Tratar condição aguda + discussão multidisciplinar<br/>sobre adiar cirurgia, alternativa não invasiva ou paliação"]
    D -->|"Não"| F["Estimar risco perioperatório com ferramenta validada<br/>ex.: RCRI ou NSQIP/Gupta"]
    F --> G{"Há modificador de risco importante?"}
    G -->|"Sim"| H["Avaliação em equipe conforme condição:<br/>valvopatia grave, HP grave, cardiopatia congênita de alto risco,<br/>stent/CABG prévio, AVC recente, CIED, fragilidade"]
    G -->|"Não"| I{"Risco calculado baixo?"}
    I -->|"Sim"| J["Prosseguir para cirurgia"]
    I -->|"Não / ≥1% de MACE ou RCRI >1 tradicionalmente"| K["Avaliar capacidade funcional de forma estruturada"]
    H --> K
    K --> L{"DASI >34 / capacidade funcional adequada?"}
    L -->|"Sim"| M["Em geral prosseguir; testes adicionais apenas se indicados fora do contexto cirúrgico"]
    L -->|"Não ou desconhecida"| N{"Teste adicional mudará decisão ou manejo?"}
    N -->|"Não"| O["Prosseguir ou escolher alternativa conforme contexto clínico"]
    N -->|"Sim"| P["Biomarcadores pré-operatórios:<br/>BNP/NT-proBNP razoável; troponina pode ser considerada em pacientes selecionados"]
    P --> Q{"Biomarcadores anormais ou dúvida clínica relevante?"}
    Q -->|"Não"| R["Prosseguir para cirurgia"]
    Q -->|"Sim"| S["Considerar teste isquêmico ou CCTA apenas se resultado puder mudar conduta"]
    S --> T{"Anatomia coronária de alto risco / isquemia relevante?"}
    T -->|"Não"| U["Prosseguir com otimização e plano de vigilância"]
    T -->|"Sim"| V["Discussão multidisciplinar sobre revascularização quando indicada independentemente da cirurgia,<br/>adiamento ou estratégia alternativa"]
```

## Limiar de risco usado na diretriz

A figura central da AHA/ACC 2024 observa que, tradicionalmente, **RCRI >1** ou risco calculado de **MACE >1%** por ferramenta perioperatória identifica risco elevado. Esse limiar deve ser interpretado em conjunto com modificadores de risco, capacidade funcional e contexto cirúrgico.

## Capacidade funcional

Para cirurgia de risco elevado, a avaliação estruturada com **Duke Activity Status Index (DASI)** é razoável. A diretriz define capacidade funcional ruim como **DASI ≤34** ou capacidade estimada **<4 METs**.

## Biomarcadores

Na figura de decisão da AHA/ACC 2024, os limiares considerados anormais são:

- troponina acima do percentil 99 do limite superior de referência do ensaio;
- BNP >92 ng/L;
- NT-proBNP ≥300 ng/L.

A mensuração de BNP/NT-proBNP é razoável antes de cirurgia não cardíaca de risco elevado em pacientes com doença cardiovascular conhecida, idade ≥65 anos, ou idade ≥45 anos com sintomas sugestivos de doença cardiovascular. Troponina pré-operatória pode ser considerada nesses mesmos grupos.

## Quando NÃO pedir teste isquêmico de rotina

Teste de estresse não deve ser usado rotineiramente em pacientes de baixo risco, com boa capacidade funcional ou submetidos a procedimentos de baixo risco. Em pacientes de risco elevado com capacidade funcional ruim ou desconhecida, pode ser considerado apenas se o resultado tiver potencial real de modificar decisão ou manejo.

## Regra prática

**O objetivo da avaliação pré-operatória não é “liberar” o paciente por meio de uma bateria de exames.** É identificar doença cardiovascular ativa, estimar risco, reconhecer modificadores de risco e solicitar apenas a investigação que possa mudar a estratégia perioperatória.
