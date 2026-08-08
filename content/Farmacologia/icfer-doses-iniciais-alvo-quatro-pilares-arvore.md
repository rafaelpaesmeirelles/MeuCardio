---
title: "ICFER — doses iniciais, doses-alvo e árvore dos quatro pilares"
slug: icfer-doses-iniciais-alvo-quatro-pilares-arvore
theme: "Insuficiência cardíaca"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
source_refs:
  - "Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. Circulation. 2022;145:e895-e1032. DOI: 10.1161/CIR.0000000000001063."
---

# ICFER — doses iniciais, doses-alvo e árvore dos quatro pilares

A diretriz AHA/ACC/HFSA orienta que as classes fundamentais da ICFER podem ser iniciadas **simultaneamente em baixas doses** ou sequencialmente conforme fatores clínicos. **Não é necessário atingir a dose-alvo de uma classe antes de iniciar outra.** Depois, cada fármaco deve ser titulado à dose-alvo dos ensaios clínicos conforme tolerância.

```mermaid
flowchart TD
    A[Paciente com ICFER e indicação de terapia modificadora de prognóstico] --> B[Iniciar/otimizar os 4 pilares conforme tolerância]
    B --> C[ARNI preferencial / IECA / BRA]
    B --> D[Betabloqueador baseado em evidência]
    B --> E[Antagonista mineralocorticoide]
    B --> F[iSGLT2]

    C --> C1[Sacubitril/valsartana: usar árvore específica de dose inicial]
    C1 --> C2[Alvo internacional: 97/103 mg 2x/dia]

    D --> D1{Qual betabloqueador?}
    D1 --> D2[Bisoprolol 1,25 mg/dia → 10 mg/dia]
    D1 --> D3[Carvedilol 3,125 mg 2x/dia → 25-50 mg 2x/dia]
    D1 --> D4[Metoprolol succinato 12,5-25 mg/dia → 200 mg/dia]

    E --> E1[Espironolactona 12,5-25 mg/dia → 25-50 mg/dia]
    E --> E2[Eplerenona 25 mg/dia → 50 mg/dia]
    E1 --> E3[Antes de iniciar: eGFR >30 e K <5,0]
    E2 --> E3

    F --> F1[Dapagliflozina 10 mg/dia]
    F --> F2[Empagliflozina 10 mg/dia]

    C2 --> G[Reavaliar PA, função renal, K e sintomas]
    D2 --> H[Reavaliar FC, PA, congestão e sintomas]
    D3 --> H
    D4 --> H
    E3 --> I[Monitorar K e função renal]
    F1 --> J[Reavaliar volume/função renal e tolerância]
    F2 --> J

    G --> K[Titular conforme tolerância]
    H --> K
    I --> K
    J --> K
    K --> L[Buscar dose-alvo dos ensaios; se não tolerada, manter maior dose tolerada]
```

## Doses de referência

| Classe/fármaco | Dose inicial | Dose-alvo |
|---|---|---|
| Sacubitril/valsartana | 49/51 mg 2x/dia; pode iniciar 24/26 mg 2x/dia | 97/103 mg 2x/dia |
| Bisoprolol | 1,25 mg/dia | 10 mg/dia |
| Carvedilol | 3,125 mg 2x/dia | 25–50 mg 2x/dia |
| Metoprolol succinato CR/XL | 12,5–25 mg/dia | 200 mg/dia |
| Espironolactona | 12,5–25 mg/dia | 25–50 mg/dia |
| Eplerenona | 25 mg/dia | 50 mg/dia |
| Dapagliflozina | 10 mg/dia | 10 mg/dia |
| Empagliflozina | 10 mg/dia | 10 mg/dia |
| Ivabradina | 5 mg 2x/dia | 7,5 mg 2x/dia |
| Vericiguat | 2,5 mg/dia | 10 mg/dia |
| Digoxina | 0,125–0,25 mg/dia | individualizar para nível sérico 0,5 a <0,9 ng/mL |

## O que a tabela NÃO significa

- A dose-alvo não é autorização para titular diante de hipotensão, bradicardia, hipercalemia ou piora renal.
- O benefício não depende de “terminar” um pilar antes de começar outro. A diretriz aceita início simultâneo ou sequencial guiado pelo contexto.
- Para ARNI, a nomenclatura brasileira de Entresto 50/100/200 mg não é escrita da mesma forma que a tabela internacional 24/26, 49/51, 97/103 mg. Use a calculadora específica de **Entresto — bula Brasil** para seleção de dose inicial.

## MRA — bloqueios antes do início

A diretriz considera **eGFR ≤30 mL/min/1,73 m² ou K ≥5,0 mEq/L contraindicações para iniciar MRA**. Em eGFR 31–49, o texto de suporte orienta reduzir pela metade a dose de início/titulação. A Corvia terá calculadora própria para essa decisão, em vez de deixar a tabela de 25 mg ser aplicada automaticamente.

## Fonte

Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. *Circulation*. 2022;145:e895–e1032. DOI **10.1161/CIR.0000000000001063**.
