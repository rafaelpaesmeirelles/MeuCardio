---
title: "RCRI (Lee): cálculo, interpretação e árvore de decisão"
slug: arvore-decisao-rcri-lee
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
revisado_por_voce: false
summary: "Resumo do Revised Cardiac Risk Index com seus seis critérios, limitações e integração ao algoritmo pré-operatório contemporâneo."
source_refs:
  - "Lee TH, Marcantonio ER, Mangione CM, et al. Derivation and prospective validation of a simple index for prediction of cardiac risk of major noncardiac surgery. Circulation. 1999;100(10):1043-1049. PMID: 10477528. DOI: 10.1161/01.CIR.100.10.1043."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
---

# RCRI — Revised Cardiac Risk Index

O RCRI é um escore simples de **seis variáveis binárias**, desenvolvido por Lee et al. para prever complicações cardíacas em cirurgia não cardíaca. Cada variável vale 1 ponto:

1. cirurgia de alto risco;
2. cardiopatia isquêmica;
3. insuficiência cardíaca;
4. doença cerebrovascular;
5. diabetes tratado com insulina;
6. creatinina sérica pré-operatória >2,0 mg/dL.

## Árvore de cálculo e interpretação

```mermaid
flowchart TD
    A["Paciente candidato a cirurgia não cardíaca"] --> B["Somar 1 ponto para cada um dos 6 critérios do RCRI"]
    B --> C{"Pontuação"}
    C -->|"0"| D["Classe I<br/>evento cardíaco grave ~0,4% na coorte original"]
    C -->|"1"| E["Classe II<br/>~0,9% na coorte original"]
    C -->|"2"| F["Classe III<br/>~7,0% na coorte original"]
    C -->|"≥3"| G["Classe IV<br/>~11,0% na coorte original"]
    D --> H{"Há modificadores de risco ou condição cardiovascular ativa?"}
    E --> H
    F --> I["Risco calculado elevado no algoritmo contemporâneo"]
    G --> I
    H -->|"Não"| J["Integrar tipo de cirurgia + capacidade funcional<br/>e em geral prosseguir sem testes indiscriminados"]
    H -->|"Sim"| K["Avaliação dirigida da condição modificadora"]
    I --> L["Avaliar capacidade funcional estruturada, preferencialmente DASI"]
    L --> M{"DASI >34?"}
    M -->|"Sim"| N["Em geral prosseguir com otimização clínica"]
    M -->|"Não / desconhecido"| O{"Teste adicional mudará conduta?"}
    O -->|"Não"| P["Prosseguir conforme contexto"]
    O -->|"Sim"| Q["Considerar biomarcadores e investigação adicional conforme AHA/ACC 2024"]
```

## Como usar hoje

A AHA/ACC 2024 mantém o RCRI entre as ferramentas validadas que podem orientar a avaliação perioperatória. Na figura de abordagem escalonada, **RCRI >1** é citado como limiar tradicional para risco elevado.

Isso não significa que RCRI ≤1 encerre automaticamente a avaliação: valvopatia grave, hipertensão pulmonar grave, cardiopatia congênita de alto risco, stent/CABG prévio, AVC recente, dispositivo cardíaco implantável e fragilidade são modificadores que podem exigir estratégia específica independentemente do número final.

## Limitações

- Não incorpora idade como variável contínua.
- Não mede capacidade funcional.
- Não discrimina bem todos os tipos cirúrgicos modernos.
- Não substitui avaliação de doença cardiovascular ativa.
- As taxas de evento acima são da coorte original; não devem ser apresentadas como probabilidade individual contemporânea exata.

## Regra prática

**RCRI é uma porta de entrada para estratificação, não uma autorização cirúrgica.** Quando o risco é elevado, o próximo passo é decidir se capacidade funcional, biomarcadores ou investigação adicional realmente modificarão o manejo.
