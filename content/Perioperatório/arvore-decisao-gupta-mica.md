---
title: "Gupta MICA: cálculo, interpretação e árvore de decisão"
slug: arvore-decisao-gupta-mica
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
revisado_por_voce: false
summary: "Metodologia do Gupta MICA para estimar IAM ou parada cardíaca perioperatória em 30 dias e sua integração ao algoritmo pré-operatório."
source_refs:
  - "Gupta PK, Gupta H, Sundaram A, et al. Development and validation of a risk calculator for prediction of cardiac risk after surgery. Circulation. 2011;124(4):381-387. PMID: 21730309. DOI: 10.1161/CIRCULATIONAHA.110.015701."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
---

# Gupta MICA

O modelo de Gupta foi desenvolvido a partir do ACS-NSQIP para estimar a probabilidade de **infarto do miocárdio ou parada cardíaca em até 30 dias** após cirurgia. Na derivação, foram identificados cinco preditores independentes:

- tipo de cirurgia;
- status funcional dependente;
- creatinina anormal;
- classe ASA;
- idade crescente.

Na validação de 2008, o modelo apresentou estatística C de **0,874**, enquanto o RCRI aplicado à mesma base apresentou estatística C de **0,747**.

## Árvore da metodologia

```mermaid
flowchart TD
    A["Paciente candidato a cirurgia não cardíaca"] --> B["Identificar tipo de procedimento"]
    B --> C["Informar idade"]
    C --> D["Definir status funcional:<br/>independente / parcialmente dependente / totalmente dependente"]
    D --> E["Definir classe ASA"]
    E --> F["Definir se creatinina pré-operatória está acima do limiar do modelo"]
    F --> G["Aplicar regressão logística Gupta MICA"]
    G --> H["Resultado: risco percentual de IAM ou parada cardíaca em 30 dias"]
    H --> I{"Risco calculado >1%?"}
    I -->|"Não"| J["Risco calculado baixo pelo limiar tradicional do algoritmo AHA/ACC"]
    I -->|"Sim"| K["Risco calculado elevado"]
    J --> L{"Há condição cardiovascular ativa ou modificador de risco?"}
    K --> M["Avaliar capacidade funcional estruturada (DASI)"]
    L -->|"Não"| N["Em geral prosseguir para cirurgia"]
    L -->|"Sim"| O["Avaliação dirigida / discussão multidisciplinar"]
    M --> P{"DASI >34?"}
    P -->|"Sim"| Q["Em geral prosseguir com otimização clínica"]
    P -->|"Não / desconhecido"| R{"Investigação adicional mudará manejo?"}
    R -->|"Não"| S["Prosseguir conforme contexto"]
    R -->|"Sim"| T["Biomarcadores ± teste adicional conforme AHA/ACC 2024"]
```

## O que o resultado representa

O Gupta MICA estima um desfecho composto específico: **IAM ou parada cardíaca perioperatória em 30 dias**. Ele não estima, isoladamente, mortalidade global, AVC, insuficiência renal, complicação pulmonar ou sangramento.

## Comparação conceitual com o RCRI

- **RCRI:** soma seis fatores binários e produz classes de risco.
- **Gupta MICA:** usa regressão logística, incorpora idade, status funcional, ASA, creatinina e tipo de cirurgia e produz risco percentual individualizado.

## Observação de governança da implementação Corvia

A publicação original confirma os cinco preditores, o tamanho das coortes e o desempenho discriminatório. **Os coeficientes numéricos implementados atualmente no código da Corvia foram documentados como conferidos contra fontes secundárias reproduzindo o modelo.** Portanto, a árvore metodológica é válida, mas os coeficientes devem permanecer sujeitos a revisão humana contra a tabela/modelo original antes de serem tratados como transcrição primária definitiva.

## Regra prática

O valor percentual não substitui o restante da avaliação. Mesmo risco calculado baixo pode ser superado por doença cardiovascular ativa ou modificadores de risco importantes; risco calculado elevado deve levar à avaliação de capacidade funcional e à pergunta central: **um exame adicional realmente mudará a conduta?**
