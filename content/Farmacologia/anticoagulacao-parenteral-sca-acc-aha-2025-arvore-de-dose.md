---
title: "Anticoagulação parenteral na SCA — árvore de dose ACC/AHA 2025"
slug: anticoagulacao-parenteral-sca-acc-aha-2025-arvore-de-dose
theme: "Farmacologia"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
source_refs:
  - "Rao SV, O'Donoghue ML, Ruel M, et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes. J Am Coll Cardiol. 2025. DOI: 10.1016/j.jacc.2024.11.009. Table 10."
---

# Anticoagulação parenteral na SCA — árvore de dose

```mermaid
flowchart TD
    A[Paciente com SCA e indicação de anticoagulação parenteral] --> B{Fármaco / cenário}

    B -->|HNF — inicial ou com fibrinolítico| C[60 UI/kg IV; máx 4.000 UI]
    C --> D[12 UI/kg/h; máx 1.000 UI/h]
    D --> E[Ajustar para aPTT 60-80 s]

    B -->|HNF — PCI| F{Anticoagulante prévio?}
    F -->|Não| G[70-100 U/kg IV; alvo ACT 250-300 s]
    F -->|Sim| H[HNF adicional conforme necessário para ACT 250-300 s]

    B -->|Bivalirudina — PCI| I[0,75 mg/kg IV bolus]
    I --> J{ClCr <30?}
    J -->|Não| K[1,75 mg/kg/h]
    J -->|Sim| L[1 mg/kg/h]
    K --> M[Na PCI primária: infusão 2-4 h pós-procedimento]
    L --> M

    B -->|Fondaparinux| N{ClCr <30?}
    N -->|Sim| O[Contraindicado no esquema da Tabela 10]
    N -->|Não| P{Cenário}
    P -->|Terapia inicial| Q[2,5 mg SC 1x/dia]
    P -->|Com fibrinólise| R[2,5 mg IV; depois 2,5 mg SC/dia a partir do dia seguinte]
    P -->|Suporte isolado da PCI| S[Não usar: risco de trombose de cateter]
```

## Heparina não fracionada

### Terapia inicial da SCA ou associada a fibrinólise
- bolus **60 UI/kg IV**, máximo **4.000 UI**;
- infusão inicial **12 UI/kg/h**, máximo **1.000 UI/h**;
- ajustar para **aPTT 60–80 segundos**.

### Suporte da PCI

Se o paciente **não recebeu anticoagulante antes da PCI**:
- **70–100 U/kg IV**;
- alvo ACT **250–300 s**.

Se já recebeu anticoagulação, a diretriz não fornece um bolus fixo universal: administrar HNF adicional conforme necessário para atingir o ACT alvo. A calculadora deliberadamente não inventa um número nesse cenário.

## Bivalirudina

- bolus **0,75 mg/kg IV**;
- infusão **1,75 mg/kg/h** durante a PCI;
- se **ClCr <30 mL/min**, reduzir a infusão para **1 mg/kg/h**;
- a Tabela 10 descreve, na PCI primária, manutenção da infusão por **2–4 horas** após o procedimento.

## Fondaparinux

### Terapia inicial
- **2,5 mg SC uma vez ao dia**.

### Associado à fibrinólise
- **2,5 mg IV** inicialmente;
- **2,5 mg SC uma vez ao dia** a partir do dia seguinte.

### Função renal
- **ClCr <30 mL/min:** contraindicado no esquema da Tabela 10 ACC/AHA 2025.

### PCI
Fondaparinux **não deve ser usado isoladamente para suporte da PCI** devido ao risco de trombose de cateter. A calculadora bloqueia esse ramo em vez de fornecer 2,5 mg e deixar a impressão de que a anticoagulação da PCI está coberta.

## Enoxaparina

A enoxaparina tem árvore própria na Corvia porque idade, função renal, fibrinólise e tempo desde a última dose SC criam múltiplos ramos. Use o documento **“Enoxaparina na SCA — árvore de dose por idade, função renal e ICP”**.

## Fonte

Rao SV, O'Donoghue ML, Ruel M, et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes. J Am Coll Cardiol. 2025. DOI **10.1016/j.jacc.2024.11.009**.
