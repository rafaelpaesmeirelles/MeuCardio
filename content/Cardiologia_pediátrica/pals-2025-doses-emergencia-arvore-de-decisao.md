---
title: "PALS 2025 — doses de emergência e árvore de decisão"
slug: pals-2025-doses-emergencia-arvore-de-decisao
theme: "Cardiologia pediátrica"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
source_refs:
  - "Lasa JJ, Dhillon GS, Duff JP, et al. Part 8: Pediatric Advanced Life Support: 2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(Suppl 2):S479-S537. doi:10.1161/CIR.0000000000001368."
---

# PALS 2025 — doses de emergência e árvore de decisão

As recomendações PALS 2025 se aplicam a lactentes e crianças até 18 anos, **excluindo recém-nascidos**, que seguem o algoritmo de reanimação neonatal.

```mermaid
flowchart TD
    A[Criança com emergência cardiovascular] --> B{Pulso?}
    B -->|Não| C{FV/TV sem pulso?}
    C -->|Não: assistolia/AESP| D[RCP + epinefrina 0,01 mg/kg IV/IO, máx 1 mg, a cada 3-5 min]
    C -->|Sim| E[1º choque 2 J/kg]
    E --> F[2º choque 4 J/kg]
    F --> G[Epinefrina 0,01 mg/kg IV/IO a cada 3-5 min]
    G --> H[Choques subsequentes ≥4 J/kg, máx 10 J/kg ou dose adulta]
    H --> I{FV/TV persiste?}
    I -->|Sim| J[Amiodarona 5 mg/kg OU lidocaína 1 mg/kg]
    J --> K[Amiodarona: até 3 doses; 1ª máx 300 mg; subsequentes máx 150 mg]

    B -->|Sim| L{Bradicardia ou taquicardia?}
    L -->|Bradicardia| M[Corrigir via aérea, oxigenação e ventilação]
    M --> N{FC <60/min + comprometimento apesar de ventilação?}
    N -->|Sim| O[Iniciar RCP + epinefrina 0,01 mg/kg]
    O --> P{Tônus vagal aumentado ou bloqueio AV primário?}
    P -->|Sim| Q[Atropina 0,02 mg/kg; mín 0,1 mg; máx 0,5 mg; repetir 1 vez]

    L -->|Taquicardia| R{Comprometimento cardiopulmonar?}
    R -->|Sim| S[Cardioversão sincronizada 0,5-1 J/kg; se falhar 2 J/kg]
    R -->|Não| T{TSV regular?}
    T -->|Sim| U[Manobras vagais]
    U --> V[Adenosina 0,1 mg/kg, máx 6 mg, push rápido + flush]
    V --> W{Persiste?}
    W -->|Sim| X[Adenosina 0,2 mg/kg, máx 12 mg]
```

## PCR pediátrica

### Epinefrina
- 0,01 mg/kg IV/IO na concentração 0,1 mg/mL.
- Máximo 1 mg por dose.
- Repetir a cada 3–5 minutos durante a PCR.

### Amiodarona em FV/TV sem pulso refratária
- 5 mg/kg IV/IO em bolus.
- Pode repetir até 3 doses.
- Primeira dose: máximo 300 mg.
- Doses subsequentes: máximo 150 mg cada.

### Lidocaína
- 1 mg/kg IV/IO como alternativa à amiodarona para FV/TV sem pulso refratária.

### Desfibrilação
- 1º choque: 2 J/kg.
- 2º choque: 4 J/kg.
- Choques subsequentes: ≥4 J/kg.
- Máximo: 10 J/kg ou dose de adulto.

## Bradicardia com pulso

A prioridade é corrigir hipóxia e ventilação inadequada. Se a frequência permanece <60/min com comprometimento cardiopulmonar apesar de ventilação adequada, o PALS direciona para RCP e epinefrina.

**Atropina** é reservada para bradicardia associada a aumento de tônus vagal ou bloqueio AV primário:
- 0,02 mg/kg IV/IO;
- mínimo 0,1 mg;
- máximo por dose 0,5 mg;
- pode repetir uma vez.

Importante: o mínimo de 0,1 mg pertence ao algoritmo de **bradicardia**. A AHA/AAP 2025 diferencia esse contexto da atropina como pré-medicação para intubação, na qual não estabelece dose mínima.

## TSV pediátrica

- 1ª adenosina: 0,1 mg/kg, máximo 6 mg, push IV/IO rápido seguido de flush.
- 2ª adenosina: 0,2 mg/kg, máximo 12 mg.
- Cardioversão sincronizada se comprometimento cardiopulmonar: 0,5–1 J/kg inicialmente; se ineficaz, 2 J/kg.
- Em QRS largo estável, adenosina só deve ser considerada se o ritmo for regular e monomórfico e com apoio especializado.

## Referência

Lasa JJ, Dhillon GS, Duff JP, et al. *Part 8: Pediatric Advanced Life Support: 2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care*. Circulation. 2025;152(Suppl 2):S479-S537. DOI: **10.1161/CIR.0000000000001368**.
