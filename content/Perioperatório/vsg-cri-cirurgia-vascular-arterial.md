---
title: "VSG-CRI: risco cardíaco em cirurgia vascular arterial"
slug: vsg-cri-cirurgia-vascular-arterial
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
revisado_por_voce: false
summary: "Vascular Study Group of New England Cardiac Risk Index com pontuação, classes de risco da SBC 2024 e árvore de decisão específica para cirurgia vascular arterial."
source_refs:
  - "Bertges DJ, Goodney PP, Zhao Y, et al. The Vascular Study Group of New England Cardiac Risk Index (VSG-CRI) predicts cardiac complications more accurately than the Revised Cardiac Risk Index in vascular surgery patients. J Vasc Surg. 2010;52(3):674-683.e1-3. PMID: 20570467. DOI: 10.1016/j.jvs.2010.03.031."
  - "Gualandro DM, Fornari LS, Caramelli B, et al. Diretriz de Avaliação Cardiovascular Perioperatória da Sociedade Brasileira de Cardiologia – 2024. Arq Bras Cardiol. 2024;121(9):e20240590. DOI: 10.36660/abc.20240590."
---

# VSG-CRI

O VSG-CRI foi desenvolvido especificamente para pacientes submetidos a cirurgia vascular, pois o RCRI subestimava complicações cardíacas em vários procedimentos vasculares na coorte do Vascular Study Group of New England.

Na coorte original, o desfecho cardíaco composto incluiu **infarto do miocárdio, arritmia clinicamente relevante ou insuficiência cardíaca congestiva durante a internação**.

## Pontuação

| Fator | Pontos |
|---|---:|
| Idade ≥80 anos | +4 |
| Idade 70–79 anos | +3 |
| Idade 60–69 anos | +2 |
| Doença arterial coronariana | +2 |
| Insuficiência cardíaca | +2 |
| DPOC | +2 |
| Creatinina >1,8 mg/dL | +2 |
| Tabagismo atual ou prévio conforme variável do modelo | +1 |
| Diabetes em uso de insulina | +1 |
| Uso crônico de betabloqueador | +1 |
| Revascularização miocárdica prévia (CABG/PCI) | −1 |

## Classes utilizadas pela SBC 2024

- **0–4:** baixo risco;
- **5–6:** risco intermediário;
- **≥7:** alto risco.

A tabela original também descreveu seis estratos de pontuação, com taxas de complicação cardíaca aumentando de aproximadamente **2,6% em 0–3 pontos** até **14,3% em ≥8 pontos**. Essas taxas refletem a coorte original e não devem ser interpretadas como probabilidade individual contemporânea exata.

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente para cirurgia vascular arterial"] --> B["Calcular VSG-CRI"]
    B --> C{"Pontuação"}
    C -->|"0–4"| D["Baixo risco clínico pela SBC 2024"]
    C -->|"5–6"| E["Risco intermediário"]
    C -->|"≥7"| F["Alto risco"]
    D --> G{"Cirurgia é de risco intermediário/alto?"}
    E --> H["Avaliar capacidade funcional + investigação/otimização conforme contexto"]
    F --> I["Avaliação cardiovascular intensificada + planejamento de monitorização"]
    G -->|"Não"| J["Em geral prosseguir sem investigação cardíaca indiscriminada"]
    G -->|"Sim"| K["Avaliar capacidade funcional"]
    H --> K
    I --> K
    K --> L{"Há indicação para exame adicional e o resultado mudará manejo?"}
    L -->|"Não"| M["Prosseguir com farmacoproteção e vigilância apropriada"]
    L -->|"Sim"| N["ECG/troponina/BNP/eco/prova funcional conforme diretriz e hipótese clínica"]
    N --> O["Planejar vigilância pós-operatória conforme risco"]
```

## Por que o escore é diferente do RCRI

O VSG-CRI incorpora idade em faixas, DPOC, tabagismo e tratamento crônico com betabloqueador, além de reconhecer revascularização coronária prévia como fator protetor no modelo. Ele foi derivado especificamente em procedimentos vasculares não emergenciais.

## Limitações

- Não foi desenvolvido para cirurgias não vasculares.
- Taxas absolutas de evento pertencem à coorte de derivação/validação original.
- Estudos posteriores mostraram desempenho variável em diferentes populações vasculares.
- O uso crônico de betabloqueador é uma **variável prognóstica do modelo** e não deve ser interpretado como evidência de que betabloqueadores causam aumento de risco.
- **VERIFICAÇÃO HUMANA NECESSÁRIA**: dos seis estratos de pontuação da tabela original, só os dois extremos (2,6% em 0–3 pontos e 14,3% em ≥8 pontos) estão confirmados diretamente no abstract do Bertges 2010. Os quatro valores intermediários usados na calculadora da Corvia (3,5%/6,0%/6,6%/8,9% para 4/5/6/7 pontos) vieram de fonte secundária e não foram conferidos contra a tabela do texto completo (paywall, sem PMC) — achado ao revisar este conteúdo em 07/08/2026.

## Regra prática

Para **cirurgia vascular arterial**, a SBC 2024 direciona a estratificação clínica preferencialmente ao VSG-CRI. O escore deve ser integrado à urgência, risco intrínseco do procedimento, capacidade funcional e condições cardiovasculares ativas.
