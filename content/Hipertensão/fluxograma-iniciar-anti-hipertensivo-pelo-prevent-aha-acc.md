---
slug: fluxograma-iniciar-anti-hipertensivo-pelo-prevent-aha-acc
title: 'Fluxograma: iniciar anti-hipertensivo pela PREVENT (AHA/ACC)'
kind: fluxograma
theme: Hipertensão
summary: null
tags: []
source_refs:
- 'Khan SS, Lloyd-Jones DM, Abdalla M, et al. Use of Risk Assessment to Guide Decision-Making for Blood Pressure
  Management in the Primary Prevention of Cardiovascular Disease. J Am Coll Cardiol. 2025;86(18):1539-1559. DOI:
  10.1016/j.jacc.2025.08.001. PMID: 40879587.'
- Documento da casa aha-acc-risco-prevent-para-iniciar-anti-hipertensivo-prevencao-primaria
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma — fármaco para PA na prevenção primária

Aplicar a adultos estáveis, após excluir emergência hipertensiva e com confirmação adequada da PA. Gestação/puerpério e fragilidade avançada exigem protocolos específicos. PREVENT de10anos deve respeitar faixa validada30–79anos e ausência de DCV prévia; DCV clínica é critério próprio, sem necessidade de calcular risco.

```mermaid
flowchart TD
  A[PA confirmada em consultório e fora dele quando indicado] --> B{PAS média ≥140 OU PAD ≥90?}
  B -->|Sim| Z[Iniciar fármaco e estilo de vida; meta usual menor que 130/80]
  B -->|Não| C{PAS média ≥130 OU PAD ≥80?}
  C -->|Não| D[Estilo de vida e reavaliação]
  C -->|Sim| E{DCV clínica, AVC, DM, DRC ou PREVENT-CVD em 10 anos ≥7,5%?}
  E -->|Sim| Z
  E -->|Não| F[Estilo de vida 3–6 meses]
  F --> G{PAS ainda ≥130 OU PAD ≥80?}
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
