# Conteúdo científico revisado — 10/09/2026

Este pacote prepara **391 documentos existentes** para publicação, com revisão clínica e editorial, correções necessárias e preservação de sua origem. A preparação e a gravação dos rascunhos revisados no banco **não publicam conteúdo**: todos os registros do pacote têm `review_status: revisado` e `published: false`.

O escopo foi congelado no inventário desta pasta. Produção posterior ou externa a esses 391 registros não está incluída.

## Conteúdo e verificações

- **391 documentos revisados**, distribuídos pelos 30 temas canônicos, sem pendências abertas no manifesto final.
- **77 diagramas/fluxogramas verificados**, com resultado de análise Mermaid e revisão das decisões clínicas registrada por documento.
- **1.777 vínculos explícitos auditados** para a navegação Tudo com Tudo. Esse número representa relações do pacote, não necessariamente 1.777 endereços distintos.
- **335 novas fontes canônicas** e **56 atualizações de arquivos canônicos existentes** preparadas no overlay.
- Sumários conferidos em relação aos corpos corrigidos; referências, limitações científicas e resoluções de pendências documentadas nos registros individuais.

A revisão foi **assistida por inteligência artificial**. O estado `revisado` registra esta revisão editorial; não atribui assinatura, aprovação ou responsabilidade profissional a um revisor humano. A localização de um PMID/DOI, isoladamente, não constitui verificação de uma alegação clínica. As verificações e correções realizadas constam do ledger individual.

## Arquivos principais

| Arquivo ou pasta | Finalidade |
|---|---|
| `manifest.json` | Contagens finais, temas, identificador da entrega e hashes do pacote e do inventário de origem. |
| `reviewed-package.json` | Dados revisados dos 391 documentos, originais usados nas guardas, relações e mapa dos arquivos canônicos. |
| `records/` | Cópias individuais revisadas, antes da normalização de espaços externos do corpo. |
| `source-snapshot.json` e `source-guards.json` | Inventário congelado de origem e verificações de versão, data e conteúdo. |
| `individual-review-ledger.json` e `review-ledger.json` | Achados, fontes conferidas e hashes individuais; o segundo registra a normalização final do corpo. |
| `canonical-overlay/` | Árvore de arquivos Markdown preparada para incorporação ao repositório. Ainda não é aplicação automática ao diretório `content/`. |
| `canonical-overlay-manifest.json` | Destino de cada arquivo, criação/atualização, hashes anterior/preparado e metadados de revisão anteriores arquivados. |
| `tct-audit.json` e `diagram-audit.json` | Auditorias vinculadas aos hashes dos corpos efetivamente revisados. |
| `resolved-legacy-gaps.json` | Registro das pendências herdadas e sua resolução individual. |
| `verified-pubmed-sources.json` e `source-fetch-audit.json` | Fontes bibliográficas recuperadas e tratamento separado dos identificadores de capítulos de livros. |

## Gravação dos rascunhos revisados

O importador específico é `scripts/apply_reviewed_391_20260910.py`, na raiz do repositório. Seu modo de conferência consulta o banco sem gravar. O modo de aplicação exige o SHA-256 exato do pacote, limita-se aos 391 registros identificados, recusa registros que se tornaram publicados e confere os campos originais, a versão e a data antes de aplicar uma alteração.

A aplicação usa bloqueio, guarda uma cópia dos registros anteriores e executa a atualização em transação. Mudanças de corpo preservam a versão anterior em revisão histórica. A execução mantém `published: false`, não publica relações no site e não executa uma reconciliação geral do acervo.

**Gravação concluída e conferida no banco em 10/09/2026 às 18:05 BRT:** 391 registros revisados, 339 atualizados e 52 já correspondentes ao resultado final. A consulta independente encontrou zero divergências de campos e zero documentos publicados. O comprovante está em `database-import-receipt.json`, incluindo o hash do pacote e a localização da cópia de segurança.

## Incorporação segura das fontes canônicas

Antes da publicação, incorporar ao repositório os arquivos de `canonical-overlay/`, preservando os caminhos relativos listados em `canonical-overlay-manifest.json`:

1. Conferir o hash do pacote contra `manifest.json` e o hash de cada arquivo preparado contra `prepared_file_sha256`.
2. Para cada uma das **56 atualizações**, exigir que o arquivo de destino ainda tenha o `previous_file_sha256` registrado. Se mudou, comparar e integrar a alteração de forma explícita; não sobrescrever trabalho posterior.
3. Para cada uma das **335 criações**, exigir que o destino continue ausente. Se surgiu outro arquivo nesse caminho, resolver o conflito antes de copiar; não remover nem substituir automaticamente conteúdo de outra produção.
4. Preservar os campos de origem/proveniência já mantidos no overlay e o arquivo dos metadados de revisão anteriores. Não reaplicar assinatura ou carimbo humano antigo ao texto alterado.
5. Versionar e manter essas fontes no repositório usado pelo deploy, juntamente com os registros desta revisão.

**As 335 fontes canônicas novas precisam acompanhar o conteúdo no banco.** Atualizar somente os registros do banco deixaria esses documentos novamente vulneráveis à retirada de circulação por uma futura reconciliação que considere apenas o acervo canônico em arquivos. Não executar `reconcile` ou importação global do corpus para concluir esta entrega.

## Publicação no próximo deploy

A ativação durante o próximo deploy já faz parte do encaminhamento autorizado. Este pacote, entretanto, conserva os documentos como rascunhos revisados até essa etapa: **`published: false` deve permanecer durante a preparação e a importação dos rascunhos**.

Na publicação, usar o conjunto exato dos 391 registros e suas fontes canônicas preservadas, conferir novamente os hashes e aplicar a autorização editorial correspondente aos corpos finais. **Autorizações antigas vinculadas a outros hashes não aprovam os textos corrigidos.** Qualquer alteração posterior de corpo exige atualizar sua revisão e as auditorias pertinentes antes de ativá-lo.

A publicação deve incluir a conferência das relações Tudo com Tudo e da disponibilidade desses registros nos mecanismos de busca/indexação do site. Isso é uma etapa distinta da gravação dos rascunhos; não se deve usar uma reconciliação global como atalho para ativação.

Não há publicação efetuada por este pacote de preparação, conforme `published_by_this_release: 0` no manifesto. O comprovante da atualização no banco e o suplemento Claude estão incluídos no pacote final.

## Suplemento Claude — penicilina benzatina

Os 7 registros adicionais foram corrigidos e preparados com status `revisado` e `published: false`: 4 novos e 3 atualizações, em `claude-benzatina-supplement/`. Foram conferidos 28 vínculos, 13 fontes e 3 diagramas Mermaid adicionais, sem erros de análise. O suplemento conserva os originais, as versões corrigidas e o registro das decisões de revisão. Ele ainda não foi importado para o banco; as atualizações de registros existentes devem ser incorporadas durante a publicação, sem desativar versões publicadas incidentalmente.

O arquivo `checksums.json` permite conferir a integridade dos arquivos deste pacote. Nenhum teste de CI backend foi executado.
