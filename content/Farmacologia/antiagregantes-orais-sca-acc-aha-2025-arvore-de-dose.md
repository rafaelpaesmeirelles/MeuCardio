---
title: "Antiagregantes orais na SCA — árvore de dose ACC/AHA 2025"
slug: antiagregantes-orais-sca-acc-aha-2025-arvore-de-dose
theme: "Farmacologia"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
source_refs:
  - "Rao SV, O'Donoghue ML, Ruel M, et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes. J Am Coll Cardiol. 2025. DOI: 10.1016/j.jacc.2024.11.009."
---

# Antiagregantes orais na SCA — árvore de dose

```mermaid
flowchart TD
    A[SCA] --> B[AAS salvo contraindicação]
    B --> C[162-325 mg VO carga; preferir não entérico e mastigar]
    C --> D[75-100 mg VO/dia manutenção]

    A --> E{P2Y12 escolhido}
    E -->|Clopidogrel| F{Fibrinólise?}
    F -->|Não| G[300 ou 600 mg carga; 75 mg/dia]
    F -->|Sim| H{Idade}
    H -->|<75| I[300 mg carga; depois 75 mg/dia]
    H -->|=75| J[VERIFICAÇÃO HUMANA NECESSÁRIA]
    H -->|>75| K[Sem carga; iniciar 75 mg/dia]

    E -->|Ticagrelor| L{Fibrinólise imediata?}
    L -->|Não| M[180 mg carga; 90 mg 2x/dia]
    M --> N[AAS manutenção ≤100 mg/dia]
    L -->|Sim| O[Não usar esta árvore como carga imediata pós-lítico]

    E -->|Prasugrel| P{Sem fibrinolítico e vai para PCI?}
    P -->|Não| Q[Não sugerir dose por esta metodologia]
    P -->|Sim| R[60 mg carga]
    R --> S{Peso <60 kg OU idade ≥75?}
    S -->|Sim| T[5 mg/dia; usar cautela]
    S -->|Não| U[10 mg/dia]
```

## AAS

- carga: **162–325 mg VO**;
- preferir formulação não entérica e mastigar quando possível para início mais rápido;
- manutenção: **75–100 mg/dia**.

A diretriz orienta administrar carga mesmo ao paciente que já usava AAS.

## Clopidogrel

### SCA sem fibrinólise
- carga: **300 ou 600 mg VO**;
- manutenção: **75 mg/dia**.

### STEMI com fibrinólise
A diretriz de 2025 contém uma inconsistência textual no ponto de corte de 75 anos:

- a **Tabela 7** diz: carga de 300 mg se idade **≤75 anos** e dose inicial de 75 mg se >75;
- o texto de suporte diz: carga de 300 mg se **<75 anos** e início sem carga, 75 mg/dia, se **≥75 anos**.

Por isso a implementação da Corvia faz:

- idade <75 anos: **300 mg de carga**, depois 75 mg/dia;
- idade >75 anos: **sem carga**, iniciar 75 mg/dia;
- idade **exatamente 75 anos**: `VERIFICAÇÃO HUMANA NECESSÁRIA`.

Essa decisão é deliberada: não se escolhe arbitrariamente entre duas frases conflitantes da mesma diretriz.

## Ticagrelor

Na SCA **sem fibrinolítico**:

- carga **180 mg VO**;
- manutenção **90 mg duas vezes ao dia**.

Quando ticagrelor é usado, a diretriz recomenda AAS de manutenção **≤100 mg/dia**.

A diretriz também discute transição para ticagrelor após fibrinólise em situações selecionadas; essa situação não foi transformada em “carga imediata no momento do lítico” na calculadora.

## Prasugrel

No cenário da Tabela 7 — SCA sem fibrinolítico e paciente submetido a PCI:

- carga **60 mg VO**;
- manutenção **10 mg/dia** se peso ≥60 kg e idade <75 anos;
- manutenção **5 mg/dia** se peso <60 kg ou idade ≥75 anos, com cautela.

## Limites da árvore

A escolha do P2Y12 depende de muito mais que a dose: história de AVC/AIT, risco hemorrágico, necessidade de anticoagulação, possibilidade de cirurgia, anatomia coronariana, interações e estratégia invasiva. Esses fatores precisam de avaliação clínica separada.

## Fonte

Rao SV, O'Donoghue ML, Ruel M, et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes. J Am Coll Cardiol. 2025. DOI **10.1016/j.jacc.2024.11.009**.
