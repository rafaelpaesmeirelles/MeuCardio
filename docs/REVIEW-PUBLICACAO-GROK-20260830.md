---
title: "Revisão de preparação para publicação — Grok 29–30/08/2026"
slug: review-publicacao-grok-20260830
---

# Revisão de preparação para publicação — Grok

Data da auditoria: 30/08/2026.

## Fontes recebidas

1. `20260829.zip`, bundle no HEAD `8b00af0c42f3089493e41aa200df3c5403109051` (lote 75).
2. `meucardio-producao-nao-publicada-20260830.zip`, bundle no HEAD `258f4f387e284766ea73eb3bc939f8c7fa78f7d8` (lote 77).

Os ZIPs passaram integralmente em `unzip -t`. O lote 75 é ancestral do lote 77; portanto, o segundo pacote é o sucessor canônico do primeiro.

## Reconciliação com a main

Base auditada: `origin/main` em `97899cf66f3d467cfefa3253d5f0f1e1a2258176`.

- pacote final: 332 caminhos de conteúdo ausentes da `main`;
- pacote antigo: 25 caminhos ausentes, todos já presentes no pacote final;
- pacote antigo: 31 caminhos já existentes na `main`, com conteúdo divergente;
- bundle final: 32 caminhos divergentes já existentes na `main` — os 31 anteriores mais um patch de corticosteroide no choque séptico;
- decisão: importar os 332 inéditos do pacote final e não tocar nos 32 caminhos colidentes;
- documentos de rastreabilidade inéditos: 3;
- total inicial preparado: 335 arquivos; este relatório acrescenta o 336º arquivo da branch.

## Auditoria estrutural

- 332/332 documentos Markdown iniciam com frontmatter YAML;
- 332/332 possuem `title`, `slug`, `review_status: revisado` e `source_refs`;
- nenhum slug se repete dentro do lote ou colide com o corpus atual;
- nenhum documento é duplicata exata de outro documento do lote;
- menor documento: 1.329 bytes; mediana: 2.782 bytes; nenhum arquivo vazio ou fallback;
- busca dirigida não encontrou TODO, placeholder, Lorem Ipsum, mensagem de conteúdo indisponível ou texto aguardando reconstrução.

## Auditoria de fontes

- todos os 332 documentos citam pelo menos um PMID;
- 322 PMIDs únicos foram extraídos;
- consulta em lote ao NCBI PubMed resolveu 322/322 identificadores;
- 265/332 documentos também registram DOI;
- o log científico identifica explicitamente resultados neutros, desfechos compostos, ensaios interrompidos, não inferioridade, amostras pequenas e dados ausentes do abstract, evitando completar números não verificados.

A resolução de um PMID confirma a existência e a identidade bibliográfica da publicação; não substitui a revisão clínica humana integral de cada interpretação.

## Validações do CorVIA

- `python scripts/content_inventory.py --strict`: aprovado, 2.325 documentos no corpus combinado, `invalid: []`, `missing: []`;
- `python scripts/audit_tudo_com_tudo.py`: aprovado, 10.120 itens, `broken_references: []`;
- o ambiente Python foi materializado e a coleta dos testes direcionados ocorreu, mas a suíte usa fixture autouse com PostgreSQL; como não havia banco em `localhost:5432`, os 14 testes pararam no setup com `Connection refused`, antes de qualquer asserção. O CI da branch deve executá-los com o serviço PostgreSQL.

## Decisão editorial final

Conteúdo revisado em branch isolada, sem alterações funcionais e sem sobrescrita de material publicado. Os 332 documentos foram promovidos para `review_status: revisado`. A auditoria consolidada também revisou os 35 documentos do ChatGPT que integravam o mesmo ciclo editorial e normalizou 145 registros associados (evidências, estudos, checklists, trilhas, materiais para paciente, emergências e casos clínicos). Nenhum merge na `main` ou deploy foi realizado nesta preparação.
