---
title: "S-MPM: mortalidade cirúrgica em 30 dias"
slug: s-mpm-mortalidade-cirurgica-calculo-e-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
summary: "Modelo simples de 9 pontos para mortalidade por todas as causas em 30 dias após cirurgia não cardíaca, separado dos escores de risco cardíaco."
source_refs:
  - "Glance LG, Lustik SJ, Hannan EL, et al. Ann Surg. 2012;255(4):696-702. PMID: 22418007. DOI: 10.1097/SLA.0b013e31824b45af."
---

# S-MPM — Surgical Mortality Probability Model

## Endpoint

O S-MPM estima **mortalidade por todas as causas em 30 dias** após cirurgia não cardíaca. Portanto, ele complementa — mas não substitui — RCRI, Gupta MICA, AUB-HAS2, VSG-CRI ou GSCRI, cujos endpoints cardiovasculares são diferentes.

O estudo de derivação/validação utilizou **298.772 pacientes** do ACS-NSQIP de 2005–2007.

## Cálculo — 0 a 9 pontos

### ASA

- ASA I: 0;
- ASA II: 2;
- ASA III: 4;
- ASA IV: 5;
- ASA V: 6.

### Risco do procedimento no modelo S-MPM

- baixo: 0;
- intermediário: 1;
- alto: 2.

### Urgência

- não emergência: 0;
- emergência: +1.

## Classes

- **0–4 pontos — Classe I:** mortalidade <0,5%;
- **5–6 pontos — Classe II:** mortalidade 1,5–4,0%;
- **7–9 pontos — Classe III:** mortalidade >10%.

Na validação original, o modelo apresentou estatística C **0,897**.

## Árvore de cálculo

```mermaid
flowchart TD
  A["Paciente candidato a cirurgia não cardíaca"] --> B["ASA I=0 / II=2 / III=4 / IV=5 / V=6"]
  B --> C["Somar risco do procedimento: baixo=0 / intermediário=1 / alto=2"]
  C --> D{"Cirurgia de emergência?"}
  D -->|"Sim"| E["+1 ponto"]
  D -->|"Não"| F["+0"]
  E --> G["Total 0-9"]
  F --> G
  G --> H{"0-4?"}
  H -->|"Sim"| I["Classe I: mortalidade <0,5%"]
  H -->|"Não"| J{"5-6?"}
  J -->|"Sim"| K["Classe II: 1,5-4,0%"]
  J -->|"Não: 7-9"| L["Classe III: >10%"]
```

## Árvore de uso junto à avaliação cardiológica

```mermaid
flowchart TD
  A["S-MPM calculado"] --> B{"Classe I?"}
  B -->|"Sim"| C["Baixa mortalidade cirúrgica global pelo modelo"]
  B -->|"Não"| D{"Classe II ou III?"}
  D -->|"II"| E["Risco global relevante: planejar nível de cuidado pós-operatório e otimização"]
  D -->|"III"| F["Mortalidade global muito elevada: discussão multidisciplinar + decisão compartilhada"]
  C --> G["Avaliar separadamente risco cardiovascular com RCRI/MICA/GSCRI etc."]
  E --> G
  F --> G
  G --> H["Não somar S-MPM com escores cardiovasculares: endpoints diferentes"]
```

## Armadilha importante

A **classe de risco cirúrgico usada pelo S-MPM foi empiricamente derivada** a partir de códigos de procedimentos. Ela não é necessariamente idêntica às categorias contemporâneas de risco cardiovascular ESC/AHA. O próprio estudo destaca que alguns procedimentos podem cair em categoria diferente da intuição clínica tradicional.

Quando o procedimento não puder ser classificado com segurança pela metodologia do S-MPM, registrar **VERIFICAÇÃO HUMANA NECESSÁRIA** em vez de atribuir uma classe arbitrária.

## Valor clínico

O S-MPM ajuda a responder uma pergunta diferente: “qual é o risco de morte cirúrgica global?”, útil para consentimento, alocação de recursos e nível de cuidado pós-operatório. Não deve ser apresentado ao paciente como “risco cardíaco”.
