---
title: "DASI no pré-operatório: cálculo, capacidade funcional e árvore de decisão"
slug: dasi-capacidade-funcional-calculo-e-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Questionário DASI de 12 itens, fórmula para VO2/METs e uso do ponto de corte DASI 34 no algoritmo perioperatório contemporâneo."
source_refs:
  - "Hlatky MA, Boineau RE, Higginbotham MB, et al. Am J Cardiol. 1989;64(10):651-654. PMID: 2782256. DOI: 10.1016/0002-9149(89)90496-7."
  - "Wijeysundera DN, Pearse RM, Shulman MA, et al. Lancet. 2018;391(10140):2631-2640. PMID: 30070222. DOI: 10.1016/S0140-6736(18)31131-0."
  - "Coutinho-Myrrha MA, Dias RC, Fernandes AA, et al. Arq Bras Cardiol. 2014;102(4):383-390. PMID: 24652056. DOI: 10.5935/abc.20140031."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC perioperative guideline. DOI: 10.1161/CIR.0000000000001285."
---

# Duke Activity Status Index — DASI

## Por que usar

A estimativa clínica informal de capacidade funcional é imprecisa. No estudo prospectivo internacional METS, o DASI apresentou valor prognóstico para desfechos perioperatórios e passou a ocupar posição central na avaliação funcional estruturada.

A AHA/ACC 2024 define **capacidade funcional pobre como <4 METs ou DASI ≤34** para decisões de teste de estresse/CCTA no algoritmo perioperatório.

## Questionário e pesos

Somar os pesos apenas quando a resposta for “sim”:

| Atividade | Peso |
|---|---:|
| Cuidar de si mesmo | 2,75 |
| Andar dentro de casa | 1,75 |
| Andar 1–2 quarteirões em terreno plano | 2,75 |
| Subir um lance de escadas ou um morro | 5,50 |
| Correr curta distância | 8,00 |
| Trabalho doméstico leve | 2,70 |
| Trabalho doméstico moderado | 3,50 |
| Trabalho doméstico pesado | 8,00 |
| Jardinagem/atividade equivalente | 4,50 |
| Relação sexual | 5,25 |
| Atividade recreativa moderada | 6,00 |
| Esporte vigoroso | 7,50 |

**DASI total: 0 a 58,2 pontos.**

A equação original para estimar VO₂ de pico é:

`VO₂ pico estimado (mL/kg/min) = 0,43 × DASI + 9,6`

`METs estimados = VO₂ pico / 3,5`

## Árvore de cálculo

```mermaid
flowchart TD
  A["Aplicar 12 perguntas do DASI"] --> B["Somar pesos de todas as respostas SIM"]
  B --> C["DASI total 0-58,2"]
  C --> D["VO2 pico estimado = 0,43 × DASI + 9,6"]
  D --> E["METs estimados = VO2 / 3,5"]
  C --> F{"DASI ≤34?"}
  F -->|"Sim"| G["Capacidade funcional pobre pelo critério AHA/ACC 2024"]
  F -->|"Não"| H["Capacidade funcional adequada pelo limiar do algoritmo AHA/ACC"]
```

## Árvore de uso pré-operatório

```mermaid
flowchart TD
  A["Paciente com risco perioperatório calculado"] --> B["Aplicar DASI"]
  B --> C{"DASI >34?"}
  C -->|"Sim"| D{"Sintomas cardiovasculares estáveis?"}
  D -->|"Sim"| E["Em geral, prosseguir sem teste de isquemia de rotina"]
  D -->|"Não"| F["Investigar a condição clínica pelos critérios usuais, independentemente da cirurgia"]
  C -->|"Não: ≤34"| G{"Risco cirúrgico/cardiovascular elevado?"}
  G -->|"Não"| H["Não transformar DASI baixo isoladamente em indicação automática de teste"]
  G -->|"Sim"| I["Considerar biomarcadores; avaliar se teste de estresse ou CCTA mudará manejo"]
  I --> J{"Exame mudará decisão/terapia?"}
  J -->|"Não"| K["Prosseguir com otimização e monitorização"]
  J -->|"Sim"| L["Selecionar teste apropriado"]
```

## Interpretação correta

- DASI é **medida funcional**, não um escore anatômico de DAC.
- DASI baixo não diagnostica isquemia.
- DASI >34, em paciente estável, ajuda a evitar exames desnecessários.
- DASI ≤34 ganha relevância quando combinado a **risco perioperatório elevado** e quando um exame adicional pode mudar a conduta.

## Validação brasileira

A versão em português brasileiro foi submetida a tradução, adaptação transcultural e validação em pacientes com doença cardiovascular por Coutinho-Myrrha e colaboradores.
