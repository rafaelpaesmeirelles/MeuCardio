---
title: "Preparação de publicação — produção científica Grok 29–30/08/2026"
slug: publicacao-science-grok-20260829
---

# Preparação de publicação — Grok science 29–30/08/2026

## Estado consolidado

| Campo | Valor |
|---|---|
| Bundle final recebido | `258f4f387e284766ea73eb3bc939f8c7fa78f7d8` — lote 77 |
| Bundle anterior recebido | `8b00af0c42f3089493e41aa200df3c5403109051` — lote 75 |
| Relação | lote 75 é ancestral direto do lote 77 |
| Base histórica dos bundles | `36a642e398a36051ea6ecd3ba18d9481e0a61d85` |
| `main` auditada | `97899cf66f3d467cfefa3253d5f0f1e1a2258176` |
| Branch de preparação | `release/grok-unpublished-science-20260830` |
| Status editorial | `revisado` nos 332 documentos |
| Merge / deploy | não executados |

## União dos dois pacotes

- O pacote de 30/08 contém integralmente os **25 documentos inéditos** do pacote de 29/08.
- Os outros **31 arquivos** do pacote antigo têm os mesmos caminhos de conteúdo já publicado, mas com blobs diferentes. O bundle final acrescenta uma 32ª colisão (`corticosteroide-no-choque-septico-refratario-corticus-adrenal-aprocchss`); todas as 32 foram excluídas para preservar as versões revisadas da `main`.
- A união limpa contém **332 documentos científicos inéditos** e **3 documentos de rastreabilidade**.
- Não houve sobrescrita de conteúdo existente, alteração de JSON monolítico, schema, loader, API, frontend ou workflow.

## Cobertura dos 332 documentos

| Área | Documentos |
|---|---:|
| Doença coronariana | 170 |
| Insuficiência cardíaca | 42 |
| Terapia intensiva | 37 |
| Hipertensão | 28 |
| Prevenção e lipídios | 27 |
| Tromboembolismo | 25 |
| Diabetes e cardiologia | 3 |

Os lotes cobrem a produção científica 1–77 da sessão, com as lacunas deliberadas descritas no log. Os lotes 76–77 acrescentam CORTICUS, PROWESS-SHOCK, NICE-SUGAR, Leuven 1/2, VISEP e Glucontrol.

## Gates concluídos

- 332/332 arquivos com frontmatter, título, slug, `source_refs` e `review_status` válidos;
- zero slug duplicado e zero arquivo exatamente duplicado dentro do lote;
- 322 PMIDs únicos declarados, **322 resolvidos no NCBI PubMed**;
- `content_inventory.py --strict`: aprovado, `invalid: []`, `missing: []`;
- `audit_tudo_com_tudo.py`: aprovado, `broken_references: []`;
- colisões da `main` preservadas, sem substituição silenciosa.

Relatório detalhado: `docs/REVIEW-PUBLICACAO-GROK-20260830.md`.

## Gate de publicação

Revisão editorial final concluída na branch de preparação. Os 332 documentos estão com `review_status: revisado`; merge e deploy permanecem etapas separadas e não foram executados.
