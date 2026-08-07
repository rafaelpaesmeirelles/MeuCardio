---
title: "SBC 2024: troponina, ECG, BNP e vigilância pós-operatória"
slug: sbc-2024-monitorizacao-troponina-ecg-bnp-pos-operatorio
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
revisado_por_voce: false
summary: "Árvores de decisão da Diretriz SBC 2024 para troponina e ECG seriados, BNP/NT-proBNP e monitorização pós-operatória em pacientes de risco cardiovascular aumentado."
source_refs:
  - "Gualandro DM, Fornari LS, Caramelli B, et al. Diretriz de Avaliação Cardiovascular Perioperatória da Sociedade Brasileira de Cardiologia – 2024. Arq Bras Cardiol. 2024;121(9):e20240590. DOI: 10.36660/abc.20240590."
---

# Monitorização cardiovascular perioperatória segundo a SBC 2024

Uma diferença operacional importante da diretriz brasileira é a ênfase em **troponina e ECG seriados** para pacientes selecionados, permitindo reconhecer injúria miocárdica perioperatória mesmo quando analgesia, sedação ou apresentação atípica mascaram sintomas.

## Árvore: quem deve receber troponina + ECG seriados?

```mermaid
flowchart TD
    A["Paciente em cirurgia não cardíaca"] --> B["Calcular risco cardiovascular perioperatório<br/>RCRI/AUB-HAS2 ou VSG-CRI em cirurgia vascular arterial"]
    B --> C{"Risco clínico intermediário ou alto?"}
    C -->|"Não"| D["Evitar troponina de rastreamento rotineiro em paciente de baixo risco"]
    C -->|"Sim"| E{"Cirurgia de risco intermediário ou alto?"}
    E -->|"Não"| F["Individualizar conforme sintomas/indicação clínica"]
    E -->|"Sim"| G["Troponina + ECG basais"]
    G --> H["Repetir troponina no 1º e 2º pós-operatório"]
    H --> I["Repetir ECG no 1º e 2º pós-operatório"]
    I --> J{"Troponina/ECG alterados ou sintomas?"}
    J -->|"Não"| K["Manter vigilância clínica e estratégia perioperatória"]
    J -->|"Sim"| L["Investigar injúria miocárdica perioperatória e etiologia"]
```

Na SBC 2024, troponina pré-operatória e no **1º e 2º dias pós-operatórios** em pacientes de risco clínico intermediário/alto submetidos a operações de risco intermediário/alto é recomendação **Classe I, nível B**. ECG pré-operatório e no 1º e 2º dias pós-operatórios nessa mesma população é **Classe I, nível C**.

## Injúria miocárdica perioperatória

A diretriz recomenda diagnosticar injúria miocárdica perioperatória pela variação absoluta da troponina em relação ao valor basal/pós-operatório, utilizando o **percentil 99 do limite superior de referência do ensaio** como referência operacional. A interpretação deve considerar o ensaio específico e o contexto clínico.

## Árvore: BNP/NT-proBNP pré-operatório

```mermaid
flowchart TD
    A["Paciente para cirurgia não cardíaca"] --> B{"Idade >65 anos?"}
    B -->|"Sim"| C["Considerar mensuração pré-operatória de BNP/NT-proBNP conforme SBC 2024"]
    B -->|"Não"| D{"Idade 45–64 + DCV estabelecida ou fator de risco cardiovascular?"}
    D -->|"Sim"| C
    D -->|"Não"| E["Não usar BNP/NT-proBNP como rastreamento universal"]
    C --> F{"BNP/NT-proBNP elevado?"}
    F -->|"Não"| G["Integrar ao restante da estratificação"]
    F -->|"Sim"| H["Risco aumentado: revisar IC/volume/comorbidades e planejar vigilância apropriada"]
```

A diretriz brasileira cita evidência de maior risco perioperatório com valores pré-operatórios acima de aproximadamente:

- **BNP >92 pg/mL**;
- **NT-proBNP >300 pg/mL**.

Esses valores são marcadores prognósticos e **não constituem isoladamente diagnóstico de insuficiência cardíaca**.

## Árvore: nível de vigilância pós-operatória

```mermaid
flowchart TD
    A["Paciente submetido a cirurgia de risco intermediário/alto"] --> B{"Risco clínico cardiovascular"}
    B -->|"Baixo"| C["Monitorização clínica habitual conforme cirurgia"]
    B -->|"Intermediário"| D["Considerar vigilância intensificada;<br/>UTI por 48h pode ser razoável conforme contexto"]
    B -->|"Alto"| E["Planejar monitorização intensiva pós-operatória;<br/>SBC recomenda UTI por 48h no cenário definido"]
    D --> F["Troponina/ECG seriados quando critérios atendidos"]
    E --> F
```

A SBC 2024 apresenta recomendação de **48 horas de UTI** para pacientes de alto risco submetidos a cirurgia intermediária/alta (**Classe I C**) e considera a estratégia em pacientes de risco intermediário (**Classe IIa C**), de acordo com o contexto clínico e a disponibilidade assistencial.

## Regra prática

**O pós-operatório faz parte da estratificação.** Em pacientes de maior risco, não basta estimar o risco antes da cirurgia: a estratégia deve prever como detectar precocemente injúria miocárdica e deterioração cardiovascular depois do procedimento.
