---
title: "Grok — expansão científica 20 mil (lotes 1–4)"
slug: science-evidence-scale-20k-grok-20260904
---

# Grok — expansão científica 20 mil (lotes 1–4)

Data da preparação: 2026-08-30.

## Estado do candidato

- Branch de origem: `grok/science-evidence-scale-20k-20260904`.
- HEAD de origem: `d2282e46f378a57849f1cf81162901d337fd54d1`.
- Base certificada: `main` em `754673cc6dc7844eb3e46380e0c5f784dbd4d7ac`.
- Escopo líquido: **565 itens** — 227 estudos e 338 evidências.
- Arquivos canônicos alterados: `estudos/metadados.json` e `evidencias/metadados.json`. Não há 565 arquivos Markdown individuais neste branch.
- Estado editorial preservado: `review_status: pendente_revisao`, `published: false`, `fonte_producao: grok`.
- Este candidato não inclui o PR #778 do Claude e não executa merge nem deploy.
- Inventário completo por slug: `docs/science-evidence-scale-20k-grok-20260904-inventory.json`.

## Lotes

| Lote | Commit | Estudos | Evidências | Total |
|---|---|---:|---:|---:|
| 1 | `08e89121` | 69 | 109 | 178 |
| 2 | `df88f0ec` | 61 | 88 | 149 |
| 3 | `e54597e3` | 52 | 73 | 125 |
| 4 | `d2282e46` | 45 | 68 | 113 |
| **Total** |  | **227** | **338** | **565** |

O lote 2 excluiu seis DOI já presentes no corpus: CASTLE-AF, DECLARE-TIMI 58, EAST-AFNET 4, MADIT-CRT, PARTNER 3 e RAFT.

## Certificação executada

### Estágio 1 — integridade determinística: aprovado

- 565/565 itens com status, publicação e proveniência coerentes.
- 227/227 PMIDs resolvidos no PubMed; nenhum abstract ausente.
- Nenhuma divergência de DOI ou ano contra o registro PubMed.
- Números usados nas sínteses e evidências contidos nos abstracts de origem.
- Zero colisões novas de slug, PMID, DOI ou título com a `main`.
- Zero referências internas quebradas; cobertura temática 565/565.
- Inventário estrito do corpus aprovado: 10.754 itens após a aplicação do lote.
- Sem linguagem absoluta de alto risco detectada pelo gate conservador.

### Estágio 2 — revisão clínica/editorial: bloqueado

Os itens foram produzidos a partir de abstracts. O PDF integral não foi lido e as 338 evidências usam `recommendation_class: Ponderado` como rótulo editorial, não como classe oficial de ESC/AHA/SBC. Os próprios registros exigem confronto com a tabela oficial e revisão independente. Por isso, este preparo **não** promove os itens a `revisado` e **não** os autoriza para publicação.

Antes do merge, é necessário escolher uma das duas rotas seguras:

1. revisar texto integral/tabelas oficiais e promover somente os itens confirmados; ou
2. remodelar as 338 entradas como achados de estudos, sem campo que possa ser confundido com recomendação de diretriz.
