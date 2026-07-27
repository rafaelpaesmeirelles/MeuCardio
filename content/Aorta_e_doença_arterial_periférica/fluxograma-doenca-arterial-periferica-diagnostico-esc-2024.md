---
title: "Fluxograma: Doença Arterial Periférica — rastreamento e diagnóstico pelo ITB (ESC 2024)"
slug: fluxograma-doenca-arterial-periferica-diagnostico-esc-2024
theme: "Aorta e doença arterial periférica"
kind: fluxograma
summary: "Índice tornozelo-braquial como primeiro teste: valor igual ou inferior a 0,90 confirma DAP, acima de 1,40 indica artérias não compressíveis, e critérios de alto risco isquêmico da ESC para estratificação."
review_status: revisado
source_refs: ["2024 ESC Guidelines for the management of peripheral arterial and aortic diseases · European Heart Journal · 2024 · 45(36):3538-3700 · https://academic.oup.com/eurheartj/article/45/36/3538/7738955", "2024 ESC Guidelines for PAD and Aortic Diseases: Key Points · American College of Cardiology · 2024 · https://www.acc.org/latest-in-cardiology/ten-points-to-remember/2024/09/03/18/59/2024-esc-guidelines-for-pad-esc-2024", "Commentary on the 2024 European Society of Cardiology Guidelines on Peripheral Arterial and Aortic Diseases · PMC · 2024 · https://pmc.ncbi.nlm.nih.gov/articles/PMC11702006/"]
---

# Fluxograma: Doença Arterial Periférica — diagnóstico (ESC 2024)

A diretriz ESC 2024 uniu, pela primeira vez, doença arterial periférica e doenças
da aorta em um único documento — a justificativa declarada é a
**interconectividade do sistema arterial como um todo**. Ela funde e atualiza as
diretrizes de DAP de 2017 e de aorta de 2014.

## Caminho decisório

```mermaid
flowchart TD
  A["Suspeita de doença<br/>arterial periférica"] --> B["Índice tornozelo-braquial<br/>ITB em repouso — primeiro teste"]

  B --> C{"Valor do ITB"}

  C -->|"menor ou igual a 0,90"| D["Diagnóstico de DAP confirmado"]
  C -->|"maior que 1,40"| E["Artérias não compressíveis<br/>ITB não interpretável para excluir DAP"]
  C -->|"entre 0,91 e 1,40"| F["Faixa não diagnóstica<br/>manter investigação se a suspeita persistir"]

  D --> G["Estratificar risco isquêmico"]

  G --> G1["Amputação prévia"]
  G --> G2["Isquemia crônica ameaçadora<br/>do membro"]
  G --> G3["Revascularização prévia"]
  G --> G4["Comorbidades de alto risco:<br/>insuficiência cardíaca, diabetes,<br/>doença poliarterial"]
  G --> G5["TFGe abaixo de<br/>60 mL/min/1,73 m²"]

  G1 --> H["Alto risco isquêmico"]
  G2 --> H
  G3 --> H
  G4 --> H
  G5 --> H

  D --> I["Prevenção e modificação<br/>de estilo de vida"]
  I --> I1["Atividade física"]
  I --> I2["Controle de fatores de risco"]
```

## O ITB como primeiro teste

A abordagem inicial recomendada é não invasiva, com o **índice tornozelo-braquial
como primeiro exame**. Desempenho do ITB em repouso para o diagnóstico de DAP:

| Métrica | Faixa |
|---|---|
| Sensibilidade | 68% – 84% |
| Especificidade | 84% – 99% |

**ITB ≤ 0,90 confirma o diagnóstico de DAP.** Para valores **> 1,40**, o termo
correto é *artérias não compressíveis* — nesse cenário o índice não serve para
excluir doença, porque a calcificação da parede arterial eleva artificialmente a
pressão no tornozelo.

## Critérios de alto risco isquêmico da ESC

- amputação prévia
- isquemia crônica ameaçadora do membro
- revascularização prévia
- comorbidades de alto risco — insuficiência cardíaca, diabetes, doença
  poliarterial
- taxa de filtração glomerular estimada abaixo de 60 mL/min/1,73 m²

## Ênfase da diretriz

O documento cobre toda a trajetória do paciente, do diagnóstico e da
estratificação de risco na apresentação inicial até o manejo de longo prazo após
a hospitalização, e enfatiza cuidado centrado no paciente, estratégias
preventivas, modificação de estilo de vida e atividade física para evitar
progressão da doença e complicações.
