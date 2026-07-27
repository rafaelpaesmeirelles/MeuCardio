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

## Árvore de decisão

```mermaid
flowchart TD
  R0["Suspeita de doença<br/>arterial periférica"] --> P1["Índice tornozelo-braquial<br/>ITB em repouso — primeiro teste"]

  P1 --> D1{"Valor do ITB"}

  D1 -->|"maior que 1,40"| C1(["Artérias não compressíveis<br/>ITB não interpretável para excluir DAP"])

  D1 -->|"entre 0,91 e 1,40"| C2(["Faixa não diagnóstica<br/>manter investigação se a suspeita persistir"])

  D1 -->|"menor ou igual a 0,90"| P2["Diagnóstico de DAP confirmado<br/>estratificar o risco isquêmico"]

  P2 --> D2{"Algum critério de<br/>alto risco isquêmico?"}

  D2 -->|Sim| C3(["Alto risco isquêmico — prevenção e<br/>modificação de estilo de vida, com<br/>atividade física e controle intensificado<br/>de fatores de risco"])

  D2 -->|Não| C4(["Prevenção e modificação de estilo<br/>de vida: atividade física e<br/>controle de fatores de risco"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
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
