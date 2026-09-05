# CorVIA — remediação de pendências, 05/09/2026

## Escopo e referência

- Base desta branch: `bb13cf23`, que inclui o hotfix `2a75adea`.
- O patch `/root/corvia-hotfix-marca-miniuniverso.patch` já estava aplicado; não foi duplicado.
- O layout aprovado foi preservado. Nenhum arquivo CSS foi alterado nesta remediação.
- Esta entrega não representa conclusão de todas as pendências, merge, deploy ou certificação da área autenticada.

## Correções implementadas nesta branch

### Tudo com Tudo: relações diretas entre todas as frentes

O painel contextual só importava do grafo os grupos `doenca` e `triagem_sintoma`.
As outras treze categorias perdiam vínculos explícitos quando o alvo não passava
pela busca textual dentro do mesmo tema. A importação agora contempla as quinze
categorias de conteúdo já autorizadas pelo grafo, sem incluir pacientes ou outros
dados privados. A política tipada/bidirecional do grafo continua sendo a autoridade.

Relações diretas entram antes dos candidatos textuais no limite por categoria e
na deduplicação, preservando sua procedência, confiança e status de revisão. A
ordem visual, os rótulos e as rotas de grupos preexistentes são mantidos. Relações
meramente temáticas, rejeitadas e marcadas como contexto não são promovidas a nexos
clínicos. Medicamentos sem tema suportado passam a conservar seus vínculos diretos,
sem inventar indicação, tema ou aprovação editorial.

### Cache de emergência e logout

A exceção `StaleWhileRevalidate` de `/api/emergencia` foi removida: a rota passa
pela regra geral `NetworkOnly`. Um script de ativação do service worker remove
somente os caches legados `corvia-emergencia*`, preservando assets e cenas.

O logout também remove esses caches. Em erro de rede, a interface local deixa de
manter o usuário anterior visível. Isso NÃO garante revogação do cookie no servidor
quando o pedido de logout não chega ao backend; não há alegação de logout remoto
bem-sucedido nesse caso.

## Evidências de validação

- 25 testes novos do Tudo com Tudo: todos aprovados na branch corrigida.
- Comparação com o serviço da main anterior à correção: 16 falhas / 9 sucessos nos mesmos casos.
- Testes novos + suíte existente de relevância clínica: 36 aprovados, sem banco de dados.
- Cache, política de rotas, ativação e logout: 8 testes aprovados.
- `npm run build`: aprovado, incluindo TypeScript e geração do service worker.
- Auditoria estrutural do corpus versionado: 11.581 itens; zero referências quebradas.
- Sentinelas semânticas com mecanismos reais: 20 casos; zero erro residual.
- Esses resultados não equivalem à inspeção funcional das telas autenticadas nem à revisão clínica integral.

## Produção: verificação estritamente somente leitura

Uma transação `READ ONLY` consultou apenas tabelas científicas e do grafo.
Foram encontrados **54 documentos publicados sem nó ativo no grafo**. Nas outras
13 categorias consultadas, a contagem de conteúdo publicado sem nó ativo foi zero.
Calculadoras possuem registro próprio e não entram nessa comparação com tabelas de conteúdo.

Foi criada cópia prévia das duas tabelas do grafo:
`/root/corvia-remediation-reports-20260905/knowledge-graph-before.dump`

SHA-256: `f5d16c23b28474ea9d4a396c5bfc816b6286258ed4b195e70e6e0272669b48ad`.
O `pg_dump` concluiu com sucesso. A chamada seguinte, que validaria o catálogo e
executaria reconciliação transacional com guardas e rollback, foi bloqueada pela
camada de segurança da ferramenta. **A reconciliação não foi executada, o catálogo
do dump não foi validado nessa chamada e os 54 documentos permanecem pendentes.**
A cópia local do grafo não substitui backup offsite nem teste de restauração.

## Pendências preservadas, não declaradas como resolvidas

| Frente | Estado desta execução |
|---|---|
| Reconciliação dos 54 documentos e prevenção de recorrência no Intelligence | Bloqueada a gravação; nenhuma promoção de revisão ou publicação. |
| 479 marcadores de revisão humana e 286 lacunas clínicas da auditoria recebida | Não recontados nem revisados clinicamente nesta execução. |
| Backup offsite, monitoramento e restauração integral | Não configurados/certificados. É necessário destino autorizado. |
| Swagger/OpenAPI, APK cancelado, manifest público e uploads | Correção paralela existente preservada; não integrada por esta branch. |
| Portas, IPv6, isolamento de QA, logs e build cache do servidor | Sem nova certificação externa nesta execução. |
| CMED, gates de CI/reconciliação e orçamento de bundle | Não declarados corrigidos por esta entrega. |
| Equivalência visual das quatro telas e rotas autenticadas | Sem nova validação visual/funcional integral. |
| Timeline do conhecimento e evolução de PDF | Planejadas; implementação não iniciada nesta remediação. |

## Reproduzir as verificações focadas

```sh
PYTHONPATH=backend python -m pytest --noconftest -q \
  scripts/tests/test_connected_content_direct_graph.py \
  backend/tests/test_connected_content_clinical_relevance.py
cd frontend
npm run test:clinical-cache-safety
npm run build
```

Os testes acima usam dublês, não pacientes nem o banco de produção. Não se deve
executar a suíte de banco em produção: existem fixtures históricas que truncam
tabelas para isolar testes.
