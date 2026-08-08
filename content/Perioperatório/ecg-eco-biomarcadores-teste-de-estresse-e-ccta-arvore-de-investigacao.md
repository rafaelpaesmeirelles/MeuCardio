---
title: "Investigação cardiovascular pré-operatória: ECG, eco, biomarcadores, estresse e CCTA"
slug: ecg-eco-biomarcadores-teste-de-estresse-e-ccta-arvore-de-investigacao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Árvores de decisão baseadas na AHA/ACC 2024 para selecionar exames cardiovasculares antes de cirurgia não cardíaca sem rastreamento excessivo."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024. DOI: 10.1161/CIR.0000000000001285."
  - "Gualandro DM, Fornari LS, Caramelli B, et al. Diretriz de Avaliação Cardiovascular Perioperatória da Sociedade Brasileira de Cardiologia – 2024. Arq Bras Cardiol. 2024;121(9):e20240590. PMID: 39442131. DOI: 10.36660/abc.20240590."
---

# Qual exame cardiovascular pedir antes da cirurgia?

## Regra-mãe

**Não pedir um exame apenas porque existe uma cirurgia programada.** A investigação deve ser indicada quando o resultado puder modificar diagnóstico, tratamento, timing cirúrgico, técnica anestésica ou intensidade da monitorização.

## Árvore geral de investigação

```mermaid
flowchart TD
  A["Cirurgia não cardíaca planejada"] --> B{"Emergência?"}
  B -->|"Sim"| C["Prosseguir; avaliação/monitorização simultâneas conforme estabilidade"]
  B -->|"Não"| D{"SCA, arritmia instável ou IC descompensada?"}
  D -->|"Sim"| E["Pausar cirurgia quando clinicamente possível e tratar condição ativa"]
  D -->|"Não"| F["Calcular risco + avaliar modificadores + DASI/METs"]
  F --> G{"Baixo risco e sem modificadores?"}
  G -->|"Sim"| H["Sem exame cardíaco adicional de rotina"]
  G -->|"Não"| I["Selecionar exame conforme pergunta clínica específica"]
  I --> J["ECG: baseline/arrítmico/isquêmico"]
  I --> K["Eco: função ventricular/valva"]
  I --> L["BNP/NT-proBNP ± troponina: refinamento prognóstico"]
  I --> M["Estresse/CCTA: somente se risco elevado + capacidade pobre/desconhecida + resultado mudará manejo"]
```

# ECG de 12 derivações

```mermaid
flowchart TD
  A["Pré-operatório"] --> B{"DAC conhecida, arritmia significativa, DAP, doença cerebrovascular, cardiopatia estrutural ou sintomas de CVD?"}
  B -->|"Sim"| C{"Cirurgia de risco elevado?"}
  C -->|"Sim"| D["ECG pré-operatório é razoável — AHA/ACC 2024, IIa B-NR"]
  C -->|"Não"| E["ECG conforme indicação clínica habitual, não apenas pela cirurgia"]
  B -->|"Não"| F{"Assintomático + cirurgia de risco elevado?"}
  F -->|"Sim"| G["ECG pode ser considerado para baseline — IIb B-NR"]
  F -->|"Não: procedimento de baixo risco"| H["ECG rotineiro não recomendado para melhorar desfechos — III: sem benefício"]
  D --> I{"ECG novo com anormalidade?"}
  G --> I
  I -->|"Sim"| J["Avaliação adicional é razoável conforme alteração e contexto"]
  I -->|"Não"| K["Integrar ao plano perioperatório"]
```

Sintomas/sinais relevantes citados pela diretriz incluem dor torácica, dispneia, palpitações não diagnosticadas, taquicardia, síncope e sopro.

# Ecocardiograma / avaliação de função ventricular

```mermaid
flowchart TD
  A["Pré-operatório"] --> B{"Dispneia nova, sinais de IC ou suspeita de disfunção ventricular nova/pior?"}
  B -->|"Sim"| C["Avaliar função ventricular — Classe I, B-NR"]
  B -->|"Não"| D{"IC conhecida com piora de dispneia ou mudança do estado clínico?"}
  D -->|"Sim"| E["Avaliação de função ventricular é razoável — IIa C-LD"]
  D -->|"Não"| F["Assintomático e clinicamente estável"]
  F --> G["Não realizar avaliação rotineira de função ventricular — III: sem benefício"]
```

Em suspeita de estenose/regurgitação valvar moderada ou grave, a ecocardiografia segue a indicação valvar específica e o impacto esperado sobre a cirurgia.

# Biomarcadores

```mermaid
flowchart TD
  A["Cirurgia de risco elevado"] --> B{"CVD conhecida OU idade ≥65 OU idade ≥45 com sintomas sugestivos de CVD?"}
  B -->|"Não"| C["Não usar biomarcador como rastreamento universal"]
  B -->|"Sim"| D["BNP/NT-proBNP é razoável; troponina pode ser considerada"]
  D --> E{"BNP >92 ng/L OU NT-proBNP ≥300 ng/L OU cTn >P99?"}
  E -->|"Não"| F["Integrar como dado prognóstico favorável e prosseguir conforme restante da avaliação"]
  E -->|"Sim"| G["Risco aumentado: revisar condição clínica e discutir necessidade de avaliação adicional"]
```

# Teste de estresse

```mermaid
flowchart TD
  A["Considerando teste de estresse"] --> B{"Cirurgia de risco elevado?"}
  B -->|"Não"| C["Não testar por rotina"]
  B -->|"Sim"| D{"Risco cardiovascular elevado por ferramenta validada?"}
  D -->|"Não"| C
  D -->|"Sim"| E{"Capacidade funcional pobre/desconhecida: <4 METs ou DASI ≤34?"}
  E -->|"Não"| C
  E -->|"Sim"| F{"Resultado mudará decisão ou manejo perioperatório?"}
  F -->|"Não"| C
  F -->|"Sim"| G["Teste de estresse pode ser considerado — IIb B-NR"]
```

AHA/ACC 2024 classifica teste de estresse rotineiro como **sem benefício** quando o paciente tem baixo risco perioperatório, capacidade funcional adequada com sintomas estáveis ou será submetido a procedimento de baixo risco.

## Contraindicações gerais relevantes ao teste de estresse

A diretriz cita como contraindicações gerais: SCA, IC descompensada, estenose aórtica grave/sintomática, arritmia não controlada, hipertensão arterial importante (exemplo ≥200/110 mmHg), dissecção aguda de aorta, pericardite/miocardite, embolia pulmonar e hipertensão pulmonar grave.

# CCTA

```mermaid
flowchart TD
  A["Considerando CCTA"] --> B{"Cirurgia de risco elevado + risco cardiovascular elevado?"}
  B -->|"Não"| C["Não realizar CCTA de rotina"]
  B -->|"Sim"| D{"Capacidade funcional pobre ou desconhecida?"}
  D -->|"Não"| C
  D -->|"Sim"| E{"Identificar anatomia coronária de alto risco mudará a conduta?"}
  E -->|"Não"| C
  E -->|"Sim"| F["CCTA pode ser considerada — IIb B-NR"]
  F --> G{"Anatomia de alto risco?"}
  G -->|"Não"| H["Prosseguir conforme quadro clínico"]
  G -->|"Sim"| I["Discussão multidisciplinar; manejar DAC pela indicação cardiovascular própria"]
```

No algoritmo AHA/ACC, anatomia coronária de alto risco inclui **tronco da coronária esquerda ≥50%** ou **doença de três vasos ≥70%**.

## Mensagem final

A melhor avaliação pré-operatória não é a que pede mais exames; é a que identifica **quem não precisa deles** e reserva investigação adicional para situações em que o resultado realmente muda a estratégia.
