# Relatório de prontidão para publicação científica — janela de 30 horas

Data/hora de corte: 2026-08-31, aproximadamente 13:36 BRT.  
Janela analisada: aproximadamente 2026-08-30 10:15 BRT até 2026-08-31 13:36 BRT.  
Repositório: `rafaelpaesmeirelles/MeuCardio`.  
Escopo: produção científica de ChatGPT/Codex e Claude Code; itens de interface, Android, Windows, Caddy e deploy foram separados e não entram na contagem científica.

## Resumo executivo

1. A publicação científica única principal da janela foi consolidada e mergeada no PR #785.
2. O PR #785 incorporou 716 itens líquidos ao corpus candidato: 103 de Claude, 48 de Codex e 565 de Grok. Como este relatório foca ChatGPT/Codex e Claude Code, a produção diretamente atribuída a eles no consolidado é de 151 itens.
3. O corpus candidato passou de 10.189 para 10.905 itens canônicos, com `review_status: revisado` em 10.905/10.905, `published: false` preservado e cobertura Tudo com Tudo de 10.905/10.905.
4. O PR #778, de Claude Code, permanece aberto/draft apenas como trilha de origem e não deve ser mesclado isoladamente, porque seu conteúdo já foi integrado no candidato consolidado.
5. O PR #782, de Codex, permanece aberto/draft e contém 396 itens em staging. Os lotes 001–002, totalizando 48 itens, já foram incorporados no consolidado. Os lotes 003–018, totalizando 348 itens, continuam pendentes de revisão independente antes de qualquer publicação.
6. O CI do head atual do PR #782 (`a27c8d3d`) terminou com sucesso, mas isso não substitui revisão editorial/científica independente.
7. Nenhuma publicação adicional ou deploy foi executado por este relatório.

## Produção ChatGPT/Codex

### Já incorporado no PR #785

- Origem: Codex.
- Volume incorporado: 24 estudos + 24 evidências = 48 itens.
- Estado: revisado e incluído no PR #785.
- Observação metodológica: revisão contra metadados e abstracts PubMed; artigos integrais não conferidos; achados de estudos sem classe oficial de diretriz.

### Ainda pendente no PR #782

PR: #782 — `Codex — produção científica contínua 20k (396 itens)`  
Branch: `codex/science-evidence-scale-20k-20260904`  
Head: `a27c8d3d7b12126df22811e5237d944c144f9020`  
Estado: aberto, draft, não mergeado.  
Diff: 18 arquivos, 7.817 adições, 0 deleções.  
CI: workflow `CI` concluído com sucesso no head `a27c8d3d`.

Tabela de lotes:

| Lote | Estudos | Evidências | Estado |
|---|---:|---:|---|
| 001 | 12 | 12 | revisado; incorporado ao corpus consolidado |
| 002 | 12 | 12 | revisado; incorporado ao corpus consolidado |
| 003 | 12 | 12 | pendente de revisão independente |
| 004 | 12 | 12 | pendente de revisão independente |
| 005 | 12 | 12 | pendente de revisão independente |
| 006 | 12 | 12 | pendente de revisão independente |
| 007 | 12 | 12 | pendente de revisão independente |
| 008 | 12 | 12 | pendente de revisão independente |
| 009 | 10 | 10 | pendente de revisão independente |
| 010 | 10 | 10 | pendente de revisão independente |
| 011 | 10 | 10 | pendente de revisão independente |
| 012 | 12 | 12 | pendente de revisão independente |
| 013 | 10 | 10 | pendente de revisão independente |
| 014 | 10 | 10 | pendente de revisão independente |
| 015 | 10 | 10 | pendente de revisão independente |
| 016 | 10 | 10 | pendente de revisão independente |
| 017 | 10 | 10 | pendente de revisão independente |
| 018 | 10 | 10 | pendente de revisão independente |
| **Total bruto na staging** | **198** | **198** | **396 itens** |

Cálculo de publicação futura:

- Já incorporado: lotes 001–002 = 48 itens.
- Ainda pendente: lotes 003–018 = 348 itens.
- Critério para próxima publicação: revisar independentemente os 348 itens pendentes, promover de `.science-staging/codex/` para corpus canônico, revalidar inventário, colisões, referências, schema, PMIDs/DOIs e Tudo com Tudo.

## Produção Claude Code

### PR #778 — trilha de origem

PR: #778 — `Expansão científica 20k — Claude Code (integrado no #783)`  
Branch: `claude/science-scale-20k-20260904`  
Head: `c8cdd5db6d12c764690eb1e061f75461300ace79`  
Estado: aberto, draft, não mergeado isoladamente.  
Diff original: 182 arquivos, 47.113 adições, 0 deleções.  
Conteúdo informado no PR: 92 itens revisados, sendo 79 registros canônicos + 13 documentos Markdown.  
Estado editorial informado: `review_status: revisado`; fontes declaradas e vínculos internos verificados; duas posologias explícitas em materiais leigos foram removidas.

### Incorporação consolidada

O PR #785 informa 103 itens Claude no consolidado final, incluindo casos, checklists, doenças, materiais, trilhas e documentos. Há diferença de contagem entre o PR #778 isolado (92 itens) e a linha final do #785 (103 itens). Para publicação, prevalece o PR consolidado #785 como fonte de verdade operacional, porque ele foi o candidato final mergeado.

Regra operacional: não mesclar #778 isoladamente. Manter apenas como trilha auditável de origem.

## Publicação consolidada já realizada no GitHub

PR: #785 — `science: publicação única — 716 itens revisados (gate final)`  
Branch: `release/science-pending-ready-20260830`  
Head: `d65e36fee11a3faa653e1bec4499ded580d86cc2`  
Merge: realizado em 2026-08-30 21:22:05 UTC.  
Diff: 25 arquivos, 23.633 adições, 1 deleção.

Distribuição informada no PR #785:

| Origem | Conteúdo | Itens |
|---|---|---:|
| Claude | casos, checklists, doenças, materiais, trilhas e documentos | 103 |
| Grok | 227 estudos + 338 evidências | 565 |
| Codex | 24 estudos + 24 evidências | 48 |
| **Total líquido** |  | **716** |

Gates declarados no PR #785:

- inventário estrito: PASS;
- ausentes/inválidos: 0;
- duplicações novas de slug ou título: 0;
- colisões novas de PMID/DOI: 0;
- referências internas quebradas: 0;
- cobertura Tudo com Tudo: 10.905/10.905;
- 79/79 PMIDs da ampliação Claude resolvidos no PubMed;
- `recommendation_class` compatível com o schema;
- `git diff --check`: PASS.

Limitações declaradas:

- lotes Grok/Codex revisados contra metadados e abstracts PubMed;
- artigos integrais não conferidos;
- achados de estudos não receberam classe oficial de diretriz.

## Separação do que não é conteúdo científico novo

Os PRs #789–#795 e parte de #788 tratam principalmente de interface, identidade, Heart Team, WhatsApp, Android, Windows, Caddy, deploy e fluxo operacional. Eles podem afetar publicação/disponibilização, mas não devem ser contados como produção científica documental da janela.

O PR #787 configura validação científica mensal automatizada. É infraestrutura de auditoria científica, não produção documental nova.

## Estado de prontidão para próxima publicação

### Pronto e já integrado em main

- PR #785: consolidado científico principal da janela, mergeado.
- Conteúdo diretamente atribuível a ChatGPT/Codex + Claude dentro do consolidado: 151 itens.
- Total consolidado incluindo Grok: 716 itens.

### Não mesclar isoladamente

- PR #778: Claude Code — integrado no consolidado, manter como trilha auditável.
- PR #781: Grok — integrado no consolidado, manter como trilha auditável.
- PR #782 lotes 001–002: já incorporados no consolidado; não duplicar.

### Preparado para próxima revisão/publicação

- PR #782 lotes 003–018: 348 itens pendentes.
- Estado técnico: CI do head atual aprovado.
- Estado editorial: ainda pendente de revisão independente.
- Recomendação operacional: criar uma release científica única futura apenas com os 348 itens remanescentes após revisão independente, sem mesclar o PR #782 inteiro como se todos os 396 fossem inéditos.

## Checklist mínimo antes de publicar os 348 itens pendentes do Codex

1. Revalidar base contra a `main` atual após os merges #789–#795.
2. Confirmar que apenas lotes 003–018 entram no próximo candidato, excluindo lotes 001–002 já incorporados.
3. Reabrir fontes primárias disponíveis; no mínimo confirmar PMID, DOI, título, ano, primeiro autor, população, desenho, endpoints e resultados principais.
4. Manter `recommendation_class: N/A` e `evidence_level: N/A` para achados de estudos quando não houver classe/nível formal de diretriz conferida.
5. Rodar auditoria de duplicação por slug, título normalizado, PMID e DOI contra `main`, Claude, Grok e staging Codex anterior.
6. Rodar inventário estrito.
7. Rodar auditoria Tudo com Tudo e referências internas.
8. Validar front matter/JSON/schema e limites de banco antes de deploy.
9. Gerar PR único de release; não mesclar staging isolada.
10. Deploy apenas após gates verdes do SHA exato.

## Conclusão operacional

A janela de 30 horas produziu e consolidou grande volume científico. Para o que o usuário pediu agora, o pacote já publicado/preparado no GitHub é o #785, enquanto o próximo trabalho de publicação deve focar exclusivamente os 348 itens Codex remanescentes do PR #782, com revisão independente antes de promoção ao corpus canônico.

Nenhum deploy, merge adicional ou publicação nova foi executado por este relatório.
