---
title: "METS Study: capacidade funcional, DASI, CPET e NT-proBNP antes da cirurgia"
slug: mets-study-capacidade-funcional-dasi-cpet-ntprobnp-preoperatorio
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
revisado_por_voce: false
summary: "Estudo prospectivo internacional que comparou avaliação subjetiva da capacidade funcional com DASI, CPET e NT-proBNP antes de cirurgia não cardíaca."
source_refs:
  - "Wijeysundera DN, Pearse RM, Shulman MA, et al. Assessment of functional capacity before major non-cardiac surgery: an international, prospective cohort study. Lancet. 2018;391(10140):2631-2640. PMID: 30070222. DOI: 10.1016/S0140-6736(18)31131-0."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
---

# METS Study — Measurement of Exercise Tolerance before Surgery

A capacidade funcional sempre foi parte central da avaliação pré-operatória, mas por muitos anos foi estimada pela pergunta informal: **“o paciente consegue fazer mais de 4 METs?”**.

O METS Study testou se essa avaliação subjetiva realmente identifica capacidade funcional e prediz eventos melhor que métodos estruturados.

## Desenho

Estudo prospectivo, internacional e multicêntrico realizado em **25 hospitais** do Canadá, Reino Unido, Austrália e Nova Zelândia.

Foram incluídos **1.401 pacientes** com idade ≥40 anos, candidatos a cirurgia não cardíaca maior e com pelo menos um fator de risco cardiovascular relevante ou doença coronariana.

Antes da cirurgia, todos passaram por:

- estimativa subjetiva da capacidade funcional pelo anestesiologista;
- **Duke Activity Status Index (DASI)**;
- teste cardiopulmonar de exercício (**CPET**), incluindo VO₂ de pico;
- dosagem de **NT-proBNP**.

No pós-operatório, houve vigilância estruturada com ECG, troponina e creatinina até o terceiro dia ou alta.

O desfecho primário foi **morte ou infarto do miocárdio em 30 dias**.

## Resultados

Ocorreram **28 eventos primários (2%)** entre 1.401 pacientes.

A estimativa subjetiva do médico apresentou apenas:

- sensibilidade **19,2%** — IC95% 14,2–25,0;
- especificidade **94,7%** — IC95% 93,2–95,9;

para identificar incapacidade de atingir **4 METs** no CPET.

Ou seja: quando o médico classificava alguém como “capacidade funcional ruim”, geralmente estava correto, mas **muitos pacientes com baixa capacidade objetiva não eram reconhecidos pela avaliação subjetiva**.

Entre as medidas de capacidade avaliadas, o **DASI foi associado ao desfecho primário**:

- OR ajustado por incremento do escore: **0,96**;
- IC95% **0,83–0,99**;
- P=0,03.

A conclusão dos autores foi que a avaliação subjetiva da capacidade funcional **não deveria ser usada isoladamente** para avaliação de risco pré-operatório e que medidas estruturadas, como o DASI, deveriam ser consideradas.

## Árvore de decisão derivada da metodologia

```mermaid
flowchart TD
    A["Paciente candidato a cirurgia não cardíaca"] --> B{"Capacidade funcional é claramente alta<br/>e bem documentada?"}
    B -->|"Sim"| C["Integrar com risco clínico e procedimento"]
    B -->|"Não / incerta"| D["Não depender apenas da impressão subjetiva"]
    D --> E["Aplicar DASI estruturado"]
    E --> F{"DASI >34?"}
    F -->|"Sim"| G["Capacidade funcional favorável pelo ponto de decisão<br/>AHA/ACC 2024"]
    F -->|"Não — DASI ≤34"| H["Capacidade funcional ruim pelo algoritmo atual"]
    H --> I{"Risco perioperatório calculado é elevado<br/>e exame adicional mudaria a conduta?"}
    I -->|"Não"| J["Prosseguir sem cascata automática de exames"]
    I -->|"Sim"| K["Considerar biomarcador e/ou teste adicional<br/>conforme algoritmo e indicação clínica"]
    K --> L{"É necessária quantificação objetiva avançada<br/>da reserva/exercício?"}
    L -->|"Sim"| M["CPET pode ser considerado em contexto selecionado"]
    L -->|"Não"| N["Usar DASI + biomarcadores + dados clínicos"]
    G --> O["Evitar teste isquêmico de rotina<br/>quando não houver outra indicação"]
    C --> O
    J --> O
    M --> P["Decisão clínica integrada"]
    N --> P
```

## O que o METS não demonstrou

O estudo não diz que CPET seja inútil. Ele mostra que, na população avaliada, **a impressão subjetiva do clínico foi uma medida fraca de capacidade objetiva e risco**, e que um questionário simples como DASI ofereceu informação prognóstica útil.

CPET continua tendo aplicações selecionadas, especialmente quando uma medida fisiológica detalhada pode mudar planejamento cirúrgico, anestésico ou de terapia intensiva.

## Relação com a AHA/ACC 2024

A diretriz atual incorporou avaliação estruturada da capacidade funcional e usa **DASI ≤34** como um dos critérios de capacidade funcional ruim no algoritmo de decisão sobre investigação adicional.

A sequência correta é:

1. estimar risco perioperatório com método validado;
2. medir capacidade funcional de forma estruturada quando ela é relevante;
3. só considerar investigação adicional se o risco for elevado, a capacidade for ruim/desconhecida e o resultado puder modificar manejo.

## Regra prática

**“Parece ativo” não é uma medida suficientemente sensível de capacidade funcional.** Quando essa informação pode mudar a conduta, prefira DASI estruturado a uma estimativa informal de METs.
