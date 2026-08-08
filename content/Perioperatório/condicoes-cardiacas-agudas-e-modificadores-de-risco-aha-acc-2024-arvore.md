---
title: "Condições cardíacas agudas e modificadores de risco no pré-operatório — AHA/ACC 2024"
slug: condicoes-cardiacas-agudas-e-modificadores-de-risco-aha-acc-2024-arvore
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
revisado_por_voce: false
summary: "Árvore para separar emergência cirúrgica, condição cardíaca aguda que pode exigir pausa e modificadores de risco que demandam planejamento perioperatório especializado."
source_refs:
  - "Thompson A, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
---

# Condições cardíacas agudas versus modificadores de risco

Uma das decisões mais importantes da avaliação pré-operatória ocorre **antes de qualquer escore**: definir se a cirurgia precisa acontecer imediatamente, se existe doença cardiovascular aguda que exige avaliação/tratamento antes de cirurgia eletiva ou se o paciente está estável, porém apresenta um **modificador de risco** que muda o planejamento.

A diretriz AHA/ACC 2024 organiza a avaliação de forma escalonada e enfatiza que o rastreamento e o tratamento cardiovascular no contexto cirúrgico devem seguir, em geral, as mesmas indicações utilizadas fora do perioperatório, evitando tanto atraso desnecessário quanto investigação excessiva.

## Condições cardíacas agudas no algoritmo

O algoritmo AHA/ACC 2024 destaca:

- **síndrome coronariana aguda**;
- **arritmia cardíaca instável**;
- **insuficiência cardíaca descompensada**.

Na cirurgia eletiva, a presença de uma dessas condições favorece **pausar a progressão automática para o centro cirúrgico**, tratar/avaliar a condição aguda e realizar discussão multidisciplinar sobre adiamento, estratégia alternativa ou, em cenários específicos, cuidados proporcionais aos objetivos do paciente.

Isso é diferente de afirmar que todo paciente com doença coronariana, insuficiência cardíaca ou arritmia precisa ter sua cirurgia adiada: o ponto central é a **instabilidade/atividade clínica atual**.

## Modificadores de risco AHA/ACC 2024

Depois da estimativa inicial de risco, o algoritmo solicita atenção especial aos seguintes modificadores:

- doença valvar grave;
- hipertensão pulmonar grave;
- cardiopatia congênita de risco elevado;
- stent coronário prévio ou cirurgia de revascularização miocárdica prévia;
- AVC recente;
- dispositivo eletrônico cardiovascular implantável — marcapasso/CDI;
- fragilidade.

Esses fatores não são simplesmente “mais um ponto” do RCRI. Eles podem exigir equipe especializada, definição do momento da cirurgia, escolha do local, monitorização específica ou estratégia anestésica/procedimental própria.

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente candidato a cirurgia não cardíaca"] --> B{"Cirurgia é emergência?"}
    B -->|"Sim"| C["Prosseguir para cirurgia conforme necessidade clínica<br/>com tratamento/monitorização cardiovascular apropriados"]
    B -->|"Não"| D{"Existe condição cardíaca aguda?"}
    D -->|"SCA"| E["Avaliar e tratar SCA;<br/>discussão multidisciplinar do momento da cirurgia"]
    D -->|"IC descompensada"| F["Estabilizar IC e definir causa/gravidade<br/>antes de cirurgia eletiva quando possível"]
    D -->|"Arritmia instável"| G["Estabilizar/tratar arritmia<br/>antes de prosseguir quando possível"]
    D -->|"Não"| H["Estimar risco perioperatório<br/>com ferramenta validada"]
    E --> I{"Após tratamento, cirurgia ainda é indicada<br/>e timing é aceitável?"}
    F --> I
    G --> I
    I -->|"Sim"| H
    I -->|"Não"| J["Reavaliar estratégia cirúrgica,<br/>alternativas e objetivos do cuidado"]
    H --> K{"Há modificador de risco?"}
    K -->|"Não"| L["Avaliar capacidade funcional e seguir<br/>algoritmo de exames apenas quando indicados"]
    K -->|"Valvopatia grave"| M["Definir gravidade, sintomas e necessidade<br/>de avaliação de equipe valvar"]
    K -->|"HP grave"| N["Planejamento com equipe experiente/centro de HP<br/>e estratégia para VD/hemodinâmica"]
    K -->|"Cardiopatia congênita de alto risco"| O["Planejamento com especialista em cardiopatia congênita"]
    K -->|"PCI/CABG prévios"| P["Revisar anatomia, timing e especialmente<br/>necessidade/interrupção de antiagregação"]
    K -->|"AVC recente"| Q["Reavaliar timing e risco neurológico/trombótico"]
    K -->|"CIED"| R["Identificar dispositivo, dependência de pacing,<br/>interferência eletromagnética e plano perioperatório"]
    K -->|"Fragilidade"| S["Aplicar instrumento validado e integrar reserva funcional,<br/>pré-habilitação e plano pós-operatório"]
    M --> T["Decisão compartilhada + plano perioperatório individualizado"]
    N --> T
    O --> T
    P --> T
    Q --> T
    R --> T
    S --> T
    L --> T
```

## Como essa árvore se conecta aos escores

Os escores entram **depois** da triagem de urgência e condições cardiovasculares agudas. Eles respondem perguntas quantitativas, mas não anulam os modificadores:

- **RCRI / Gupta MICA / AUB-HAS2 / GSCRI / VSG-CRI:** risco cardiovascular por diferentes endpoints/populações;
- **DASI:** capacidade funcional;
- **FRAIL Scale:** reserva/fraqueza fisiológica como modificador;
- **SORT / S-MPM:** mortalidade cirúrgica global.

Um paciente pode ter um RCRI aparentemente baixo e, ainda assim, demandar planejamento complexo por **hipertensão pulmonar grave, valvopatia grave, CIED ou fragilidade**.

## Regra prática

**Primeiro identifique urgência e instabilidade. Depois estime risco. Só então use capacidade funcional, modificadores e exames adicionais para decidir como — e não apenas se — a cirurgia deve prosseguir.**
