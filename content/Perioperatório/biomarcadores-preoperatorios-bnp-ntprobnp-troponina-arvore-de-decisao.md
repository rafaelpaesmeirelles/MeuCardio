---
title: "Biomarcadores pré-operatórios: BNP, NT-proBNP e troponina"
slug: biomarcadores-preoperatorios-bnp-ntprobnp-troponina-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Quando medir BNP/NT-proBNP ou troponina antes da cirurgia não cardíaca, como interpretar os limiares usados pela AHA/ACC 2024 e como integrar o resultado à investigação."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC perioperative guideline. DOI: 10.1161/CIR.0000000000001285."
  - "Duceppe E, Patel A, Chan MTV, et al. Preoperative N-Terminal Pro-B-Type Natriuretic Peptide and Cardiovascular Events After Noncardiac Surgery. Ann Intern Med. 2020;172(2):96-104. PMID: 31869834."
  - "Halvorsen S, Mehilli J, Cassese S, et al. Eur Heart J. 2022;43(39):3826-3924. PMID: 36017553. DOI: 10.1093/eurheartj/ehac270."
---

# Biomarcadores no pré-operatório

## Quem deve ser considerado para dosagem

Na AHA/ACC 2024, em pacientes submetidos a cirurgia não cardíaca de **risco elevado**, é razoável medir BNP ou NT-proBNP quando houver:

- doença cardiovascular conhecida; **ou**
- idade ≥65 anos; **ou**
- idade ≥45 anos com sintomas sugestivos de doença cardiovascular.

Nessa mesma população, a medida pré-operatória de troponina pode ser considerada para complementar a estratificação.

## Limiares usados no algoritmo AHA/ACC 2024

O algoritmo considera anormal:

- **BNP >92 ng/L**;
- **NT-proBNP ≥300 ng/L**;
- **troponina acima do percentil 99 do limite superior de referência do ensaio**.

Esses limiares são pontos operacionais do algoritmo; não substituem a interpretação do contexto clínico, idade, função renal, fibrilação atrial, IC e o método laboratorial utilizado.

## Árvore de decisão

```mermaid
flowchart TD
  A["Paciente candidato a cirurgia não cardíaca"] --> B{"Cirurgia de risco elevado?"}
  B -->|"Não"| C["Não dosar biomarcador rotineiramente apenas para rastreamento"]
  B -->|"Sim"| D{"CVD conhecida OU idade ≥65 OU idade ≥45 com sintomas de CVD?"}
  D -->|"Não"| E["Biomarcador não é obrigatório pelo critério AHA/ACC; integrar risco clínico"]
  D -->|"Sim"| F["Dosar BNP ou NT-proBNP; considerar troponina"]
  F --> G{"BNP >92 ou NT-proBNP ≥300 ou troponina >P99?"}
  G -->|"Não"| H["Risco biológico menor; integrar RCRI/MICA, DASI e tipo de cirurgia"]
  G -->|"Sim"| I["Risco aumentado: revisar sintomas, ECG, função ventricular e causas não isquêmicas"]
  I --> J{"Há condição cardiovascular ativa ou indicação independente de investigação?"}
  J -->|"Sim"| K["Investigar/tratar conforme doença específica"]
  J -->|"Não"| L{"Capacidade funcional pobre/desconhecida + risco calculado elevado e teste mudará manejo?"}
  L -->|"Sim"| M["Considerar teste de estresse ou CCTA"]
  L -->|"Não"| N["Prosseguir com otimização e plano de monitorização perioperatória"]
```

## Evidência do NT-proBNP

Na coorte prospectiva internacional com 10.402 pacientes ≥45 anos submetidos a cirurgia não cardíaca com internação, valores pré-operatórios de NT-proBNP se associaram de modo escalonado ao composto de morte vascular e MINS em 30 dias:

- <100 pg/mL: referência;
- 100 a <200 pg/mL: incidência do desfecho primário **12,3%**;
- 200 a <1500 pg/mL: **20,8%**;
- ≥1500 pg/mL: **37,5%**.

A mortalidade por todas as causas em 30 dias também aumentou de **0,3%** (<100 pg/mL) para **4,0%** (≥1500 pg/mL).

## O que um biomarcador elevado NÃO significa

- Não significa automaticamente DAC obstrutiva.
- Não é indicação automática de coronariografia.
- Não deve gerar teste de estresse se o resultado não tiver potencial de alterar conduta.
- Ele sinaliza risco e deve levar a uma avaliação clínica mais cuidadosa, incluindo causas de estresse miocárdico/hemodinâmico além de isquemia.

## Vigilância pós-operatória

A AHA/ACC 2024 admite vigilância com troponina em 24 e 48 horas após cirurgia de risco elevado em pacientes selecionados com doença cardiovascular, sintomas de CVD ou idade ≥65 anos associada a fatores de risco cardiovasculares.
