# Aplicação da rodada 2 para a release integrada

Worktree: `/tmp/corvia-prevalentes-release-20260909`.
Base: PR #915, commit `d7f51132d0c1e343e75ff0e85c69211adbf2daa3`.
Branch local: `codex/prevalentes-round2-release-20260909`.

O pacote original `handoff/corvia-prevalentes-rodada2.patch.xz` foi conferido:
81.444 bytes; SHA256 `ddd7a8915dc4c0a27155cff439ba3d357dfbc3c61c9f5688c559d5b8261b26bf`.
A descompactação produziu 389.140 bytes. O pacote não foi modificado.

## Reconciliação exata de duas terminações de arquivo

O primeiro `git apply --check` apontou divergências em dois documentos. A comparação linha a linha demonstrou que cada arquivo do PR estava sem uma linha vazia final presente na base original do patch. Nenhum texto clínico divergia.

Foi acrescentado somente um LF ao final de cada arquivo. Antes de aplicar, o hash Git passou a coincidir exatamente com a base declarada no patch:

| Documento | Blob base reconstruído | Blob final aplicado |
|---|---|---|
| DAPT, `sindrome-coronariana-aguda-duracao-de-dapt-complemento-final.md` | `5a10e0ed3064c9efbd0605000d4890e2adc38fe3` | `9a807f54f89e42e412b79348621381f82b341b58` |
| HAS resistente/pseudorresistente | `2dcde12158a1a6860092605ed4a1c959401260be` | `9807ab385f892d65194608e93036665d04fae617` |

Depois dessa normalização, `git apply --check` e `git apply --index` concluíram sem erro. Não foi usado `--reject`, merge aproximado ou substituição de catálogo por outra versão. **Todos os 43 blobs finais reproduzem exatamente os hashes de destino declarados no patch.**

O `git diff --cached --check` registra uma linha vazia no EOF do documento de HAS, que faz parte do blob final revisado. Ela foi preservada deliberadamente para manter a reprodução exata do pacote; não há marcador de conflito.

## Verificação limitada à aplicação e aos contratos do lote

Resultado em `docs/prevalentes-round2-release-validation-20260909.json`, sem erros:

- JSON e frontmatter dos arquivos alterados válidos.
- 24 recursos novos localizados, com ida e volta em 14 documentos; doenças de referência verificadas também nos fragmentos canônicos.
- 24 relações novas e 3.135 relações anteriores preservadas.
- Oito trilhas progressivas, 67 etapas, ordem e tipos válidos.
- Catálogos finais: 927 casos, 479 checklists e 454 materiais.
- 914 casos, 471 checklists e 446 materiais não envolvidos nas correções preservados sem mudança de valor.
- Oito materiais novos/corrigidos passaram pelo detector de posologia e pela simulação do overlay extraídos por AST do carregador real, sem importar aplicação ou conectar banco.

A auditoria de 431 links e a revisão científica pertencem ao pacote autoral; não foram apresentadas como nova revisão clínica nesta integração. Não houve nova produção científica.

## Autorização e publicação

A autorização operacional para incluir o PR #915 e aplicar a segunda rodada foi recebida pelo coordenador da release. Isso não foi convertido em declaração de revisão humana: os registros continuam identificando revisão assistida por IA.

O manifesto histórico `editorial-approvals/full-corpus-release-20260907.json`, que referencia 11.581 itens, permanece inalterado. O coordenador deve vincular a autorização aplicável ao snapshot final integrado, preservando os gates e estados editoriais existentes. Esta worktree não promoveu, publicou, importou nem alterou quarentena.

Ler também `docs/HANDOFF-producao-prevalentes-20260909.md`. Usar os carregadores e a promoção editorial existentes na release conjunta, reconciliar grafo/índices e verificar os percursos autenticados após publicação. Não iniciar novo lote.
