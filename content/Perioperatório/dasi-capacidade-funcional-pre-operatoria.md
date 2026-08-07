---
title: "DASI: capacidade funcional na avaliação pré-operatória"
slug: dasi-capacidade-funcional-pre-operatoria
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
revisado_por_voce: false
summary: "Duke Activity Status Index como avaliação estruturada de capacidade funcional antes de cirurgia não cardíaca, com os 12 itens, pesos e árvore de decisão AHA/ACC 2024."
source_refs:
  - "Hlatky MA, Boineau RE, Higginbotham MB, et al. A brief self-administered questionnaire to determine functional capacity (the Duke Activity Status Index). Am J Cardiol. 1989;64(10):651-654. PMID: 2782256. DOI: 10.1016/0002-9149(89)90496-7."
  - "Wijeysundera DN, Pearse RM, Shulman MA, et al; METS study investigators. Assessment of functional capacity before major non-cardiac surgery: an international, prospective cohort study. Lancet. 2018;391(10140):2631-2640. PMID: 30070222. DOI: 10.1016/S0140-6736(18)31131-0."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
---

# Duke Activity Status Index (DASI)

O DASI é um questionário de 12 atividades cotidianas. A pontuação é obtida somando o peso de cada atividade que o paciente consegue realizar. A pontuação varia de **0 a 58,2**; valores maiores indicam melhor capacidade funcional.

A AHA/ACC 2024 considera razoável usar avaliação estruturada da capacidade funcional, como o DASI, em pacientes submetidos a cirurgia não cardíaca de risco elevado. No algoritmo da diretriz, **DASI ≤34** é classificado como capacidade funcional ruim.

## Itens e pesos

| Atividade que o paciente consegue realizar | Pontos |
|---|---:|
| Cuidar de si mesmo (alimentar-se, vestir-se, banho, usar banheiro) | 2,75 |
| Caminhar dentro de casa | 1,75 |
| Caminhar 1–2 quarteirões em terreno plano | 2,75 |
| Subir um lance de escadas ou uma ladeira | 5,5 |
| Correr uma curta distância | 8,0 |
| Trabalho doméstico leve | 2,7 |
| Trabalho doméstico moderado | 3,5 |
| Trabalho doméstico pesado | 8,0 |
| Trabalho no quintal/jardim | 4,5 |
| Relações sexuais | 5,25 |
| Atividade recreativa moderada | 6,0 |
| Esporte extenuante | 7,5 |

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente de risco perioperatório elevado<br/>ou com necessidade de avaliar capacidade funcional"] --> B["Aplicar os 12 itens do DASI"]
    B --> C["Somar apenas os pesos das atividades que o paciente consegue executar"]
    C --> D{"DASI >34?"}
    D -->|"Sim"| E["Capacidade funcional não classificada como ruim pelo algoritmo AHA/ACC 2024"]
    D -->|"Não — DASI ≤34"| F["Capacidade funcional ruim"]
    E --> G["Se sintomas estáveis e sem outra indicação de teste,<br/>em geral não realizar teste isquêmico rotineiro"]
    F --> H{"Risco calculado elevado e teste adicional mudará a decisão/manejo?"}
    H -->|"Não"| I["Prosseguir conforme contexto clínico e estratégia perioperatória"]
    H -->|"Sim"| J["Considerar biomarcadores pré-operatórios e,<br/>se apropriado, teste isquêmico ou CCTA"]
```

## Por que usar DASI em vez de perguntar apenas “sobe dois lances de escada?”

No estudo METS, a estimativa subjetiva do médico sobre capacidade funcional teve desempenho limitado. A avaliação estruturada pelo DASI apresentou valor prognóstico perioperatório e foi posteriormente incorporada ao algoritmo AHA/ACC.

## Interpretação prática

- **DASI >34:** capacidade funcional considerada adequada no ponto de decisão da diretriz AHA/ACC 2024.
- **DASI ≤34:** capacidade funcional ruim; isso **não significa solicitar teste isquêmico automaticamente**.
- O próximo passo depende do risco calculado, de modificadores de risco e de a investigação adicional ter potencial real para modificar a estratégia cirúrgica.

## Limitações

- É autorrelato; limitações ortopédicas, neurológicas ou culturais podem reduzir a pontuação sem refletir reserva cardiovascular isoladamente.
- DASI não diagnostica isquemia.
- O escore não substitui avaliação de sintomas, doença cardiovascular ativa ou risco intrínseco do procedimento.
- A conversão de DASI para VO2/METs por equações históricas pode superestimar capacidade funcional em alguns pacientes; para esta ferramenta perioperatória, o ponto de decisão principal será a **pontuação DASI diretamente**, conforme a AHA/ACC 2024.

## Regra prática

**DASI deve responder “qual é a capacidade funcional?”; ele não responde sozinho “o paciente pode operar?”.** A decisão final integra risco clínico, cirurgia, modificadores de risco e utilidade potencial de exames adicionais.
