---
title: "Insuficiência cardíaca no pré-operatório: eco, GDMT, SGLT2 e árvore AHA/ACC 2024"
slug: insuficiencia-cardiaca-preoperatorio-eco-gdmt-sglt2-arvore-aha-acc-2024
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
revisado_por_voce: false
summary: "Árvore para diferenciar IC descompensada de IC estável, decidir quando repetir função ventricular e manejar GDMT/SGLT2 antes de cirurgia não cardíaca."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. J Am Coll Cardiol. 2024;84(19):1869-1969. DOI: 10.1016/j.jacc.2024.06.013. PMID: 39316661."
---

# Insuficiência cardíaca no pré-operatório

Insuficiência cardíaca (IC) é um dos modificadores prognósticos mais importantes em cirurgia não cardíaca. O risco não depende apenas da FEVE: **sintomas atuais, compensação clínica, classe funcional, tipo de cirurgia e comorbidades** importam de forma substancial.

A pergunta inicial é: **o paciente está estável ou descompensado?**

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente com IC conhecida ou suspeita<br/>candidato a cirurgia não cardíaca"] --> B{"Há nova dispneia, sinais de IC,<br/>piora clínica ou suspeita de nova disfunção?"}
    B -->|"Sim"| C["Avaliar função ventricular no pré-operatório<br/>com ecocardiograma apropriado"]
    B -->|"Não"| D{"IC conhecida está clinicamente estável<br/>e assintomática?"}
    D -->|"Sim"| E["Não repetir ecocardiograma de rotina<br/>apenas por causa da cirurgia"]
    D -->|"Não / sintomas ativos"| C
    C --> F{"IC está descompensada ou há<br/>instabilidade hemodinâmica?"}
    F -->|"Sim"| G["Tratar/estabilizar IC e considerar adiar<br/>cirurgia eletiva; cardiologia/equipe multidisciplinar"]
    F -->|"Não"| H["IC compensada: otimizar plano perioperatório"]
    E --> H
    H --> I{"Em uso de SGLT2i?"}
    I -->|"Sim"| J["Suspender antes da cirurgia:<br/>≥3 dias para cana/dapa/empa; ≥4 dias ertugliflozina"]
    I -->|"Não"| K["Manter demais GDMT quando razoável<br/>e sem contraindicação clínica"]
    J --> K
    K --> L["Integrar risco do procedimento, RCRI/Gupta,<br/>DASI, biomarcadores e estado volêmico"]
    L --> M["Plano de volume, PA, ritmo e monitorização<br/>proporcional ao risco"]
```

## Quando avaliar função ventricular

A AHA/ACC 2024 recomenda avaliação pré-operatória da função ventricular em pacientes com:

- **nova dispneia**;
- achados ao exame físico sugestivos de IC;
- suspeita de disfunção ventricular nova ou piora — Classe 1, B-NR.

Em paciente com IC conhecida e **piora da dispneia ou mudança do estado clínico**, reavaliar função ventricular é razoável — Classe 2a, C-LD.

Em paciente **assintomático e clinicamente estável**, repetir função ventricular de rotina antes da cirurgia **não traz benefício** — Classe 3: No Benefit, B-NR.

## Risco conforme FEVE e sintomas

A diretriz resume uma grande coorte de pacientes submetidos a cirurgia não cardíaca em que a mortalidade em 90 dias aumentou progressivamente conforme a função ventricular piorou:

| Situação | Mortalidade bruta em 90 dias | OR ajustado vs sem IC |
|---|---:|---:|
| Sem IC | 1,22% | referência |
| IC com FEVE ≥50% | 4,88% | 1,51 |
| FEVE 40–49% | 5,11% | 1,53 |
| FEVE 30–39% | 6,58% | 1,85 |
| FEVE <30% | 8,34% | 2,35 |

Esses valores são observacionais e não são uma calculadora individual; servem para demonstrar o gradiente de risco.

Pacientes com IC **sintomática** apresentam risco maior que pacientes compensados, mesmo quando a FEVE é semelhante.

## GDMT no perioperatório

Em pacientes com IC compensada, é razoável continuar a terapia dirigida por diretriz durante o perioperatório, **exceto SGLT2i**, quando não houver contraindicação clínica específica.

Isso evita suspensão reflexa de fármacos importantes apenas porque o paciente será operado.

## SGLT2i — exceção importante

A AHA/ACC 2024 recomenda suspender SGLT2i antes de cirurgia eletiva quando possível para reduzir risco de acidose metabólica/cetoacidose euglicêmica:

- canagliflozina: **≥3 dias**;
- dapagliflozina: **≥3 dias**;
- empagliflozina: **≥3 dias**;
- ertugliflozina: **≥4 dias**.

O risco de cetoacidose pode ocorrer com glicemia normal ou apenas discretamente aumentada; náuseas, dor abdominal, dispneia e acidose com ânion gap devem levantar suspeita.

## Quando considerar pausa da cirurgia eletiva

Pacientes com IC avançada, especialmente NYHA III–IV, **clinicamente descompensados ou hemodinamicamente instáveis**, devem ter estabilização e consulta cardiológica consideradas antes de cirurgia eletiva.

A decisão deve ponderar:

- urgência da cirurgia;
- congestão e perfusão;
- necessidade de diurese/vasoativo/inotrópico;
- arritmias;
- função renal e eletrólitos;
- biomarcadores;
- possibilidade de otimização real antes do procedimento.

## Regra prática

**Não peça ecocardiograma porque o paciente “tem IC”; peça quando a informação atualizada pode mudar o manejo.** Em IC compensada, preserve GDMT quando possível; em IC descompensada, trate a instabilidade primeiro; e lembre que SGLT2i é a principal exceção de rotina, devendo ser suspenso 3–4 dias antes da cirurgia programada.
