---
title: "CMH com LVOTO e cirurgia não cardíaca — árvore hemodinâmica AHA/ACC 2024"
slug: cmh-lvoto-cirurgia-nao-cardiaca-arvore-aha-acc-2024
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
revisado_por_voce: false
summary: "Árvore para paciente com cardiomiopatia hipertrófica obstrutiva: manutenção de terapia, preservação de pré/pós-carga, ritmo sinusal e manejo da hipotensão sem piorar LVOTO."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. J Am Coll Cardiol. 2024;84(19):1869-1969. PMID: 39320289. DOI: 10.1016/j.jacc.2024.06.013."
  - "Ommen SR, Ho CY, Asif IM, et al. 2024 AHA/ACC/AMSSM/HRS/PACES/SCMR Guideline for the Management of Hypertrophic Cardiomyopathy. Circulation. 2024. DOI: 10.1161/CIR.0000000000001250."
---

# Cardiomiopatia hipertrófica com LVOTO no perioperatório

Na cardiomiopatia hipertrófica obstrutiva, o gradiente da via de saída do ventrículo esquerdo é **dinâmico**. Pode piorar rapidamente com:

- redução de pré-carga;
- redução de pós-carga;
- aumento de contratilidade;
- taquicardia;
- perda de ritmo sinusal.

Por isso, o manejo perioperatório não deve seguir reflexivamente estratégias usadas para outras causas de hipotensão ou congestão.

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente com CMH conhecida ou suspeita<br/>candidato a cirurgia não cardíaca"] --> B["Definir sintomas, LVOTO em repouso/provocado,<br/>FEVE, IM/SAM, arritmias e terapia atual"]
    B --> C{"Há sintomas descompensados,<br/>síncope arrítmica ou instabilidade?"}
    C -->|"Sim"| D["Avaliar/tratar condição cardíaca antes de cirurgia eletiva;<br/>considerar centro experiente em CMH"]
    C -->|"Não"| E["Planejar objetivos hemodinâmicos perioperatórios"]
    E --> F["Manter betabloqueador e/ou verapamil/diltiazem<br/>quando já indicados e tolerados"]
    F --> G["Evitar hipovolemia e redução excessiva de pré-carga"]
    G --> H["Evitar vasodilatação abrupta/redução de pós-carga"]
    H --> I["Evitar taquicardia; preservar ritmo sinusal quando possível"]
    I --> J{"Hipotensão intraoperatória?"}
    J -->|"Não"| K["Prosseguir com monitorização proporcional ao risco"]
    J -->|"Sim"| L{"Há suspeita de hipovolemia?"}
    L -->|"Sim"| M["Reposição IV cautelosa para restaurar pré-carga"]
    L -->|"Não / persiste"| N["Preferir vasoconstritor predominantemente alfa<br/>ou vasopressina; evitar beta-agonismo indiscriminado"]
    M --> O{"Hipotensão/LVOTO persiste?"}
    N --> O
    O -->|"Não"| K
    O -->|"Sim"| P["Considerar eco intraoperatório para identificar LVOTO,<br/>SAM/IM, volume e função"]
    P --> Q{"Hiperdinamismo/LVOTO importante?"}
    Q -->|"Sim"| R["Em paciente selecionado, beta-bloqueio IV pode reduzir<br/>contratilidade/gradiente sob monitorização"]
    Q -->|"Não"| S["Buscar outras causas de choque/hipotensão"]
    R --> T["Pós-operatório: evitar dor, taquicardia,<br/>desidratação e alterações bruscas de volume"]
    S --> T
    K --> T
```

## Terapia crônica

A diretriz perioperatória recomenda **continuar betabloqueadores e/ou bloqueadores de canal de cálcio não diidropiridínicos** usados para CMH, evitando interrupção desnecessária.

Na CMH obstrutiva sintomática, a diretriz específica de CMH considera betabloqueadores não vasodilatadores a primeira linha; verapamil/diltiazem são alternativas em pacientes apropriados.

## Quatro objetivos hemodinâmicos

### 1. Preservar pré-carga

Hipovolemia e diurese excessiva podem reduzir o volume ventricular e **aumentar o gradiente de LVOTO**.

Isso não significa “dar volume sempre”: sobrecarga também pode causar congestão. O objetivo é **euvolemia**, com correção de hipovolemia quando presente.

### 2. Preservar pós-carga

Vasodilatação abrupta reduz pressão sistêmica e pode intensificar a obstrução dinâmica.

Em hipotensão associada a CMH obstrutiva, a diretriz favorece vasoconstritores sem efeito beta-adrenérgico predominante, citando **fenilefrina ou vasopressina** como exemplos.

### 3. Evitar aumento de contratilidade

Inotrópicos beta-adrenérgicos podem piorar o gradiente em LVOTO. Se a hipotensão for decorrente de obstrução dinâmica, “mais inotropismo” pode piorar o problema.

### 4. Evitar taquicardia e preservar ritmo sinusal

Taquicardia reduz enchimento diastólico; perda da contração atrial pode ser mal tolerada em ventrículo rígido/hipertrófico. Dor, hipovolemia, anemia, hipóxia e arritmias devem ser tratadas rapidamente.

## Eco intraoperatório

Se houver hipotensão inexplicada ou refratária, ecocardiografia intraoperatória pode ajudar a diferenciar:

- LVOTO dinâmica;
- hipovolemia;
- disfunção ventricular;
- SAM com insuficiência mitral;
- outras causas de instabilidade.

Essa distinção é crucial porque tratamentos hemodinâmicos podem ser opostos.

## Monitorização

Em CMH obstrutiva de maior risco, podem ser considerados:

- pressão arterial invasiva;
- acesso venoso/monitorização hemodinâmica conforme porte da cirurgia;
- disponibilidade de ecocardiografia intraoperatória;
- pós-operatório monitorizado ou terapia intensiva em casos selecionados.

Não existe indicação universal de monitorização invasiva para todos os pacientes com CMH.

## Regra prática

**Na CMH obstrutiva, a pergunta diante da hipotensão é “o gradiente aumentou?” antes de simplesmente aumentar inotropismo ou reduzir mais a pós-carga.** Preserve pré-carga, pós-carga e ritmo; limite taquicardia e contratilidade excessiva; use imagem quando a fisiologia não estiver clara.
