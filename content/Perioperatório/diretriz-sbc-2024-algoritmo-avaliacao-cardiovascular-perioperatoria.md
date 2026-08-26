---
title: "SBC 2024: algoritmo brasileiro de avaliação cardiovascular perioperatória"
slug: diretriz-sbc-2024-algoritmo-avaliacao-cardiovascular-perioperatoria
theme: "Perioperatório"
kind: diretriz
fonte_producao: chatgpt
review_status: revisado
review_note: "Reclassificado em 26/08/2026: o conteúdo sintetiza diretamente uma diretriz de sociedade e deve aparecer na frente Guidelines, não apenas como documento genérico. Fonte DOI oficial já declarada e sem pendência de verificação humana."
revisado_por_voce: false
summary: "Árvore de decisão baseada na Diretriz de Avaliação Cardiovascular Perioperatória da SBC 2024, incluindo escolha entre RCRI, AUB-HAS2 e VSG-CRI, risco cirúrgico, capacidade funcional e monitorização perioperatória."
source_refs:
  - "Gualandro DM, Fornari LS, Caramelli B, et al. Diretriz de Avaliação Cardiovascular Perioperatória da Sociedade Brasileira de Cardiologia – 2024. Arq Bras Cardiol. 2024;121(9):e20240590. DOI: 10.36660/abc.20240590."
---

# SBC 2024 — avaliação cardiovascular perioperatória

A Diretriz SBC 2024 propõe um fluxo brasileiro que combina **urgência da operação, presença de condição cardiovascular grave/instável, risco clínico por escore, risco intrínseco da cirurgia e estratégia de monitorização**.

## Árvore-mestre

```mermaid
flowchart TD
    A["Paciente candidato a cirurgia não cardíaca"] --> B{"Cirurgia de emergência/urgência?"}
    B -->|"Sim"| C["Prosseguir diretamente para cirurgia quando o benefício exige<br/>+ cardioproteção e monitorização intra/pós-operatória"]
    B -->|"Não"| D{"Condição cardiovascular grave/instável?"}
    D -->|"Sim"| E["Adiar cirurgia eletiva quando possível<br/>e estabilizar/tratar a condição cardiovascular"]
    D -->|"Não"| F{"Qual tipo de cirurgia?"}
    F -->|"Vascular arterial"| G["Preferir VSG-CRI"]
    F -->|"Demais cirurgias"| H["Preferir RCRI ou AUB-HAS2"]
    G --> I{"Classe de risco clínico"}
    H --> I
    I -->|"Baixo"| J{"Cirurgia de risco intermediário/alto?"}
    I -->|"Intermediário"| K["Avaliação suplementar/otimização conforme contexto"]
    I -->|"Alto"| L["Avaliação suplementar + otimização + planejamento de monitorização"]
    J -->|"Não"| M["Em geral operar diretamente"]
    J -->|"Sim"| N["Avaliar capacidade funcional durante anamnese<br/>e necessidade de investigação complementar"]
    K --> N
    L --> N
    N --> O{"Exame adicional é indicado pelo quadro clínico/diretriz?"}
    O -->|"Não"| P["Prosseguir com farmacoproteção e plano de monitorização"]
    O -->|"Sim"| Q["ECG / troponina / BNP / ecocardiograma / prova funcional<br/>conforme a indicação específica"]
    Q --> R["Definir estratégia cirúrgica e monitorização pós-operatória"]
```

## Condições cardiovasculares graves/instáveis destacadas pela SBC

A Tabela 2 da diretriz inclui situações como:

- síndrome coronariana aguda;
- doença instável da aorta torácica;
- edema agudo pulmonar;
- choque cardiogênico;
- insuficiência cardíaca NYHA III/IV;
- angina CCS III/IV;
- estenose aórtica ou mitral importante sintomática;
- bradiarritmias ou taquiarritmias graves, incluindo BAV total e TV;
- fibrilação atrial com alta resposta ventricular, **FC >120 bpm**;
- hipertensão não controlada, **PA >180 × 110 mmHg**.

A presença de uma dessas condições muda a prioridade: o objetivo passa a ser estabilizar a doença cardiovascular antes da cirurgia eletiva, quando o contexto permite.

## Escolha do escore segundo a SBC 2024

### Operações gerais

A diretriz privilegia:

- **RCRI**;
- **AUB-HAS2**.

### Operações vasculares arteriais

A SBC recomenda alterar a ferramenta para **VSG-CRI**, por ser desenvolvida especificamente em cirurgia vascular arterial.

## Classes usadas no fluxograma central da SBC

| Método | Baixo | Intermediário | Alto |
|---|---:|---:|---:|
| RCRI | 0–1 | 2 | 3–6 |
| AUB-HAS2 | 0–1 | 2–3 | 4–6 |
| VSG-CRI | 0–4 | 5–6 | ≥7 |

## Capacidade funcional

A SBC 2024 recomenda determinar a capacidade funcional durante a anamnese de pacientes programados para operações de risco intermediário ou alto, usando como referência prática a capacidade de **subir dois lances de escada**. Na Corvia, o DASI pode complementar essa avaliação com um instrumento estruturado.

## Idoso e fragilidade

A diretriz recomenda:

- avaliar rotineiramente fragilidade em idosos submetidos a cirurgia de risco intermediário ou alto — **Classe IIa**;
- mensurá-la objetivamente com instrumento específico — **Classe IIa**.

## Regra prática

**No modelo brasileiro, a pergunta não é somente “qual o RCRI?”.** Primeiro exclui-se instabilidade cardiovascular; depois escolhe-se o escore adequado ao tipo de cirurgia, integra-se o risco intrínseco do procedimento e só então se define investigação e monitorização.
