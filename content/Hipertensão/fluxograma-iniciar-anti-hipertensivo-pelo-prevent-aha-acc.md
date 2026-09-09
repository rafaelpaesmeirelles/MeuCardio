---
title: "Fluxograma: iniciar anti-hipertensivo pela PREVENT (AHA/ACC)"
slug: fluxograma-iniciar-anti-hipertensivo-pelo-prevent-aha-acc
theme: "Hipertensão"
kind: fluxograma
fonte_producao: grok
review_status: revisado
published: false
review_note: "Revisão clínica e editorial concluída em 08/09/2026. Árvore restrita ao algoritmo AHA/ACC; não aplica limiares PREVENT-ASCVD de lipídios."
source_refs:
  - "Khan SS, Lloyd-Jones DM, Abdalla M, et al. Use of Risk Assessment to Guide Decision-Making for Blood Pressure Management in the Primary Prevention of Cardiovascular Disease. J Am Coll Cardiol. 2025;86(18):1539-1559. DOI: 10.1016/j.jacc.2025.08.001. PMID: 40879587."
  - "Documento da casa aha-acc-risco-prevent-para-iniciar-anti-hipertensivo-prevencao-primaria"
---

# Fluxograma — fármaco para PA na prevenção primária

```mermaid
flowchart TD
  A[PA confirmada em consultório e fora dele quando indicado] --> B{PA média ≥140/90?}
  B -->|Sim| Z[Iniciar fármaco e estilo de vida; meta usual menor que 130/80]
  B -->|Não| C{PA média ≥130/80?}
  C -->|Não| D[Estilo de vida e reavaliação]
  C -->|Sim| E{DCV clínica, AVC, DM, DRC ou PREVENT-CVD em 10 anos ≥7,5%?}
  E -->|Sim| Z
  E -->|Não| F[Estilo de vida 3–6 meses]
  F --> G{PA ainda ≥130/80?}
  G -->|Sim| Z
  G -->|Não| D
```

## Leitura rápida

- PREVENT aqui é **CVD total** (ASCVD + IC), corte **7,5%**.
- Não use o 5% ou 10% da diretriz de LDL neste fluxograma.
- Fragilidade avançada e gravidez saem desta árvore — módulos próprios.

## Conteúdo CorVIA conectado

- [PREVENT para iniciar anti-hipertensivo na prevenção primária](/biblioteca/aha-acc-risco-prevent-para-iniciar-anti-hipertensivo-prevencao-primaria)
- [As três equações PREVENT e quando usar cada uma](/biblioteca/tres-equacoes-prevent-cvd-ascvd-hf-quando-usar-cada-uma)
- [Pooled Cohort Equations e equações PREVENT](/biblioteca/pooled-cohort-equations-e-equacoes-prevent-risco-cardiovascular-em-prevencao-primaria)
