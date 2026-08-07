---
title: "Investigação cardiovascular pré-operatória: ECG, eco, biomarcadores e isquemia"
slug: rota-investigacao-cardiovascular-pre-operatoria-ecg-eco-biomarcadores-isquemia
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
revisado_por_voce: false
summary: "Árvores de decisão baseadas na AHA/ACC 2024 para definir quando solicitar ECG, ecocardiograma/avaliação de função ventricular, BNP/NT-proBNP, troponina, teste de estresse ou CCTA antes de cirurgia não cardíaca."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
---

# Investigação cardiovascular pré-operatória

A investigação cardiovascular antes de cirurgia não cardíaca deve responder a uma pergunta clínica específica. A diretriz AHA/ACC 2024 recomenda evitar rastreamento indiscriminado e usar os mesmos princípios de indicação de exames empregados fora do contexto cirúrgico.

# 1. ECG de 12 derivações

```mermaid
flowchart TD
    A["Paciente em avaliação pré-operatória"] --> B{"Há doença cardiovascular estabelecida,<br/>arritmia significativa, doença arterial periférica,<br/>cerebrovascular, cardiopatia estrutural ou sintomas cardiovasculares?"}
    B -->|"Sim"| C{"Cirurgia de risco elevado?"}
    C -->|"Sim"| D["ECG pré-operatório é razoável para estabelecer basal e orientar manejo"]
    C -->|"Não"| E["Solicitar ECG se houver indicação clínica independente do ato cirúrgico"]
    B -->|"Não"| F{"Risco calculado elevado e cirurgia de risco elevado?"}
    F -->|"Sim"| G["ECG pode ser considerado mesmo no assintomático"]
    F -->|"Não"| H["Não solicitar ECG de rotina apenas porque haverá cirurgia"]
    D --> I{"ECG mostra nova alteração relevante?"}
    G --> I
    I -->|"Sim"| J["Avaliação dirigida conforme achado e sintomas"]
    I -->|"Não"| K["Prosseguir na estratificação"]
```

# 2. Ecocardiograma / função ventricular

```mermaid
flowchart TD
    A["Paciente pré-operatório"] --> B{"Dispneia nova, IC clínica, piora de sintomas<br/>ou suspeita de nova/pior disfunção ventricular?"}
    B -->|"Sim"| C["Avaliar função ventricular com ecocardiografia"]
    B -->|"Não"| D{"Suspeita de valvopatia moderada/grave<br/>ou mudança clínica em valvopatia conhecida?"}
    D -->|"Sim"| E["Ecocardiografia para definir gravidade e repercussão"]
    D -->|"Não"| F{"Paciente clinicamente estável com função ventricular conhecida<br/>e sem mudança de sintomas?"}
    F -->|"Sim"| G["Não repetir avaliação de função ventricular rotineiramente"]
    F -->|"Não / informação essencial ausente"| H["Individualizar conforme a condição cardiovascular específica"]
```

**Princípio:** ecocardiograma não é exame obrigatório para “risco cirúrgico”. Ele é indicado quando há suspeita clínica de disfunção ventricular ou doença valvar cuja definição possa alterar o manejo.

# 3. BNP/NT-proBNP e troponina pré-operatórios

```mermaid
flowchart TD
    A["Cirurgia não cardíaca de risco elevado"] --> B{"Paciente tem doença cardiovascular conhecida,<br/>idade ≥65 anos, ou idade ≥45 anos + sintomas sugestivos de DCV?"}
    B -->|"Não"| C["Biomarcadores não fazem parte de rastreamento universal"]
    B -->|"Sim"| D["BNP ou NT-proBNP pré-operatório é razoável<br/>(AHA/ACC 2024: Classe 2a)"]
    D --> E["Troponina pré-operatória pode ser considerada<br/>(Classe 2b)"]
    E --> F{"Biomarcadores normais?"}
    F -->|"Sim"| G["Em geral prosseguir para cirurgia"]
    F -->|"Não"| H["Discussão multidisciplinar:<br/>o resultado justifica avaliação cardiovascular adicional? "]
    H -->|"Não"| I["Prosseguir com plano de vigilância perioperatória"]
    H -->|"Sim"| J["Investigação dirigida conforme hipótese clínica"]
```

Limiar usado na figura de decisão AHA/ACC 2024:

- troponina > percentil 99 do limite superior de referência do ensaio;
- **BNP >92 ng/L**;
- **NT-proBNP ≥300 ng/L**.

Esses valores são pontos de decisão da diretriz e não devem ser interpretados isoladamente como diagnóstico de insuficiência cardíaca ou síndrome coronariana.

# 4. Teste de estresse para isquemia

```mermaid
flowchart TD
    A["Paciente em avaliação pré-operatória"] --> B{"Risco perioperatório calculado elevado?"}
    B -->|"Não"| C["Não realizar teste de estresse de rotina"]
    B -->|"Sim"| D{"Capacidade funcional ruim ou desconhecida?<br/><4 METs ou DASI ≤34"}
    D -->|"Não"| E["Não realizar teste de estresse rotineiro com sintomas estáveis"]
    D -->|"Sim"| F{"O resultado do teste mudará decisão,<br/>tratamento ou momento da cirurgia?"}
    F -->|"Não"| G["Não testar apenas para 'liberar' a cirurgia"]
    F -->|"Sim"| H["Teste de estresse pode ser considerado<br/>(Classe 2b, AHA/ACC 2024)"]
    H --> I{"Isquemia relevante / achado de alto risco?"}
    I -->|"Não"| J["Prosseguir com otimização clínica"]
    I -->|"Sim"| K["Discussão multidisciplinar; manejo da DAC deve seguir indicações usuais,<br/>não revascularizar apenas para atravessar a cirurgia"]
```

# 5. Angiotomografia coronária (CCTA)

```mermaid
flowchart TD
    A["Cirurgia de risco elevado"] --> B{"Risco cardiovascular elevado por ferramenta validada?"}
    B -->|"Não"| C["CCTA de rotina não recomendada"]
    B -->|"Sim"| D{"Capacidade funcional ruim ou desconhecida?<br/><4 METs ou DASI ≤34"}
    D -->|"Não"| E["CCTA de rotina não recomendada"]
    D -->|"Sim"| F{"Definir anatomia coronária mudará a conduta?"}
    F -->|"Não"| G["Não solicitar"]
    F -->|"Sim"| H["CCTA pode ser considerada<br/>(Classe 2b)"]
    H --> I{"Anatomia coronária de alto risco?"}
    I -->|"Tronco esquerdo ≥50% ou doença anatômica significativa de 3 vasos ≥70%"| J["Discussão multidisciplinar e manejo conforme diretrizes de DAC"]
    I -->|"Não"| K["Prosseguir conforme risco global"]
```

# Resumo operacional

| Situação | Próximo passo |
|---|---|
| Baixo risco + cirurgia de baixo risco | Evitar testes cardíacos rotineiros |
| Doença/sintoma cardiovascular relevante | ECG e investigação dirigida conforme condição |
| Dispneia nova/IC piorando | Ecocardiografia |
| Suspeita de valvopatia moderada/grave | Ecocardiografia |
| Risco elevado + DASI ≤34/desconhecido | Perguntar se novo teste mudará manejo |
| Risco elevado + perfil clínico selecionado | BNP/NT-proBNP; troponina pode ser considerada |
| Risco elevado + baixa capacidade + resultado capaz de mudar conduta | Considerar estresse ou CCTA |

## Regra prática

A pergunta que antecede qualquer exame é: **“Se este resultado vier alterado, eu mudarei a estratégia?”** Se a resposta for não, o exame geralmente não deve ser solicitado apenas por causa da cirurgia.
