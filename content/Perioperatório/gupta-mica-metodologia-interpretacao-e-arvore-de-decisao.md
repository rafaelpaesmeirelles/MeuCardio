---
title: "Gupta MICA: metodologia, interpretação e árvore de decisão"
slug: gupta-mica-metodologia-interpretacao-e-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Uso do Gupta MICA para estimar risco percentual de IAM ou parada cardíaca perioperatória e integrar o resultado ao algoritmo pré-operatório."
source_refs:
  - "Gupta PK, Gupta H, Sundaram A, et al. Development and validation of a risk calculator for prediction of cardiac risk after surgery. Circulation. 2011;124(4):381-387. PMID: 21730309. DOI: 10.1161/CIRCULATIONAHA.110.015701."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC perioperative guideline. DOI: 10.1161/CIR.0000000000001285."
---

# Gupta MICA

## Endpoint

O Gupta MICA estima a probabilidade de **infarto do miocárdio ou parada cardíaca** no período perioperatório de cirurgia não cardíaca.

No estudo original, 211.410 pacientes do ACS-NSQIP 2007 compuseram a coorte de desenvolvimento; 1.371 (0,65%) apresentaram IAM ou parada cardíaca. O modelo foi validado em 257.385 pacientes do NSQIP 2008.

## Variáveis

O modelo utiliza cinco componentes:

- idade;
- classe ASA;
- status funcional pré-operatório;
- creatinina;
- tipo de procedimento cirúrgico.

O desempenho discriminatório foi alto no estudo original: estatística C de **0,884** na derivação e **0,874** na validação; no mesmo conjunto de validação, o RCRI teve estatística C de **0,747**.

## Árvore metodológica

```mermaid
flowchart TD
  A["Paciente candidato a cirurgia não cardíaca"] --> B["Informar idade"]
  B --> C["Definir ASA I-V"]
  C --> D["Definir status funcional: independente / parcialmente dependente / totalmente dependente"]
  D --> E["Informar função renal/creatinina"]
  E --> F["Selecionar categoria do procedimento"]
  F --> G["Aplicar modelo logístico Gupta MICA"]
  G --> H["Resultado: risco percentual individual de IAM ou parada cardíaca"]
```

## Árvore de interpretação para a Corvia

```mermaid
flowchart TD
  A["Gupta MICA calculado"] --> B{"Risco <1%?"}
  B -->|"Sim"| C["Baixo risco pelo limiar tradicional AHA/ACC"]
  C --> D["Se clinicamente estável e sem condição cardiovascular ativa: em geral prosseguir sem teste de isquemia de rotina"]
  B -->|"Não: ≥1%"| E["Risco perioperatório elevado"]
  E --> F["Avaliar DASI/METs"]
  F --> G{"Capacidade funcional adequada?"}
  G -->|"Sim"| H["Otimizar doença cardiovascular e prosseguir; testes apenas se indicação independente"]
  G -->|"Não / desconhecida"| I["Considerar biomarcadores e perguntar se teste adicional mudará a conduta"]
  I --> J{"Mudará manejo?"}
  J -->|"Não"| K["Evitar teste de rotina"]
  J -->|"Sim"| L["Considerar teste de estresse ou CCTA conforme contexto"]
```

## Vantagens em relação ao RCRI

- Produz **risco percentual contínuo**, não apenas classe ordinal.
- Incorpora idade e dependência funcional.
- Possui granularidade maior por tipo de cirurgia.
- Teve discriminação superior ao RCRI na validação original.

## Limitações

- A classificação correta do procedimento é essencial; aproximar uma cirurgia incomum à categoria errada pode alterar o risco.
- A classe ASA possui componente de julgamento clínico.
- O modelo não substitui a avaliação de sintomas, capacidade funcional, fragilidade, biomarcadores ou doença cardiovascular ativa.
- A indicação de teste adicional deve depender de probabilidade de mudança de manejo, e não do percentual isoladamente.

## Nota de implementação

A calculadora já existente na Corvia deve sempre exibir junto ao resultado: **endpoint previsto (IAM/PCR), horizonte temporal, variáveis utilizadas e limitação do enquadramento do procedimento**.
