# Status dos reparos — CorvIA / MeuCardio

Última atualização: 04/08/2026 00:27 (BRT)

## Resumo executivo

A `main` permanece no commit `1bea10cf2f168abf069f721ec0d5017573c05528`, com os PRs #34, #35 e #36 publicados. O PR #37 está **aberto, mergeável e ainda não integrado**, no head:

```text
f2217ee44972b287c0a3a79c3ac29840df9ae05c
```

O head final do PR #37 está certificado por CI e reconciliação independentes. O único bloqueio antes do merge é concluir a revisão Codex final, tratar qualquer nova observação e encerrar as threads já corrigidas.

Nenhuma credencial, senha ou dado do servidor foi gravado neste arquivo ou no repositório.

## Publicado na `main`

- inventário certificado de **4.936 registros científicos** e **1.327 arquivos físicos**;
- catálogo das 11 coleções, total integral no Painel e alertas por coleção;
- CorvIA Mail em rota, menu e Painel;
- CorvIA Chat em cartão, widget, HTTP e WebSocket;
- sessão HttpOnly, PyJWT e revogação após troca de senha;
- Passlib substituído por bcrypt direto compatível com hashes existentes;
- ReportLab 4.4.10 e geração real de PDFs clínicos.

### Publicações recentes

- `2209d1e3` — PR #34: bcrypt direto; 174 testes;
- `54ccee76` — PR #35: acervo, Mail e Chat; 182 testes;
- `1bea10cf` — PR #36: ReportLab; 186 testes.

## Trabalho realizado no PR #37

### 1. Deploy em duas fases

O deploy agora separa construção e publicação:

1. valida ambiente, commit e checkout;
2. detecta banco persistente e cria dump pré-deploy;
3. constrói as imagens sem interromper o site atual;
4. fecha o Caddy antes da fase que pode alterar banco ou corpus;
5. sobe backend, banco, Redis e frontend sem reabrir tráfego;
6. exige readiness interno;
7. executa migrations e reconciliação;
8. reabre o Caddy somente após sucesso integral;
9. confirma HTTPS, readiness e commit em `/api/version`.

### 2. Proteção contra falso commit publicado

- exige SHA Git completo;
- exige checkout limpo, incluindo arquivos não rastreados;
- exclui artefatos locais ignorados dos contextos Docker;
- frontend usa `package-lock.json` com `npm ci`;
- usa lock com `flock` para impedir dois deploys simultâneos;
- registra a árvore Git inicial;
- revalida `HEAD`, árvore e estado do checkout antes e depois do build e antes da certificação pública;
- injeta `DEPLOY_COMMIT` no backend;
- compara o SHA público com o commit local antes de declarar sucesso.

### 3. Banco persistente e backup pré-deploy

A detecção de banco cobre:

- container `db` ativo;
- container `db` parado;
- volume `pgdata` rotulado pelo Compose;
- volume determinístico `${projeto}_pgdata` sem labels;
- erro de Docker/Compose tratado como falha, nunca como primeiro deploy.

O backup pré-deploy:

- ocorre antes da inicialização do novo backend;
- usa dump custom do PostgreSQL;
- grava primeiro em arquivo temporário;
- valida o catálogo com `pg_restore --list`;
- aplica permissão restrita;
- publica checksum SHA-256 vinculado ao nome e conteúdo do dump.

### 4. Rollback automático

O rollback é armado **antes** do `docker compose up` que inicia o novo backend, pois o entrypoint do backend também pode executar migrations.

Se houver falha desde a inicialização do novo backend até o fim de migrations, reconciliação ou indexação:

- Caddy e backend são parados;
- o dump pré-deploy é restaurado automaticamente;
- a restauração roda em modo não interativo controlado;
- backend e proxy não são religados automaticamente;
- o tráfego permanece fechado caso o rollback falhe;
- o deploy termina com erro e exibe estado e logs.

No primeiro deploy, sem banco anterior, uma falha mantém a aplicação parada e não simula um rollback inexistente.

### 5. Restaurador endurecido

- aceita `.dump` custom atual e `.sql.gz` legado;
- valida checksum, nome registrado e hash real antes do `dropdb`;
- valida o catálogo custom antes da etapa destrutiva;
- exige confirmação manual em duas etapas no uso normal;
- aceita modo automático apenas quando explicitamente habilitado pelo deploy;
- exige que o backend seja parado antes de recriar o banco;
- usa `dropdb --force`, `createdb` e `pg_restore --exit-on-error`;
- pode restaurar sem religar backend ou tráfego;
- se uma religação manual não atingir readiness, tenta parar o backend novamente.

### 6. Reconciliação científica fail-closed

Comando oficial:

```bash
python -m app.commands.reconcile_content --publish-reviewed
```

Garantias adicionadas:

- ausência de `--allow-partial` no deploy;
- bloqueio para falhas, avisos, duplicados, recusados, ausências e arquivos vazios;
- diagnósticos pesquisados recursivamente;
- Markdown vazio passa a ser reportado;
- manifestos JSON devem ser listas de objetos com `slug` válido;
- slugs duplicados são rejeitados antes de qualquer upsert;
- quantidade de itens-fonte fica observável no resultado;
- mínimos individuais das 11 coleções continuam obrigatórios;
- listas de controlados seguem a mesma política fail-closed.

## Certificação do head final

### CI

Execução:

```text
CI #193 — run 30874577322
```

Resultado:

- frontend build: aprovado;
- auditoria de dependências frontend: aprovada;
- políticas de sessão, renderização segura e code splitting: aprovadas;
- sintaxe dos scripts operacionais: aprovada;
- auditoria Python: **nenhuma vulnerabilidade conhecida**;
- migrations: aprovadas e idempotentes;
- bootstrap explícito de administrador: aprovado;
- compilação Python: aprovada;
- pytest: **226 testes aprovados em 93,38 s**;
- release smoke: health, readiness, sessão HttpOnly e logout aprovados;
- backup/restauração PostgreSQL: aprovados, com identidade do registro preservada.

### Reconciliação do corpus

Execução:

```text
Corpus database reconciliation #69 — run 30874577320
```

Resultado:

- migrations aprovadas;
- reconciliação e publicação do corpus aprovadas;
- inventário mínimo integral de **4.936 registros científicos** confirmado.

## Revisão automática

O comentário de revisão final foi solicitado para o SHA certificado `f2217ee44972b287c0a3a79c3ac29840df9ae05c`, com foco em:

- deploy em duas fases;
- rollback armado antes do backend;
- fechamento do Caddy;
- restauração sem reabrir tráfego;
- volume `pgdata` sem labels;
- alteração concorrente do checkout;
- caminhos residuais de falso sucesso, perda de dados ou banco parcialmente exposto.

No momento desta atualização, a resposta final do Codex ainda não havia sido publicada.

Threads já resolvidas nesta sessão incluem:

- checkout sujo;
- diagnóstico de falhas pós-start;
- restaurador compatível com dump custom;
- banco persistente parado;
- conteúdo recusado ou ignorado na reconciliação.

Outras threads antigas permanecem visíveis no PR e devem ser resolvidas somente após conferir que o head final realmente contém a correção correspondente.

## Bloqueio externo de produção

O ambiente desta sessão não conseguiu resolver ou alcançar `corvia.med.br` nem o IP anteriormente informado nas portas 22, 80 ou 443. Por isso não foi possível executar login real ou testes autenticados.

As credenciais fornecidas pelo proprietário:

- não foram usadas;
- não foram copiadas para código, documentação, comentários ou logs;
- não devem ser registradas em futuras atualizações.

Recomenda-se rotacionar a senha após a validação em produção, pois ela foi compartilhada em texto na conversa.

## Trabalho pendente para a próxima sessão

### Antes do merge

1. consultar a revisão Codex final solicitada no head `f2217ee4`;
2. corrigir qualquer novo P1/P2 material;
3. repetir CI e reconciliação caso o código seja alterado;
4. conferir e resolver todas as threads antigas realmente corrigidas;
5. atualizar a descrição do PR #37 para incluir:
   - deploy em duas fases;
   - rollback automático;
   - lock/revalidação do checkout;
   - detecção de volume sem labels;
   - CI com 226 testes;
   - runs `30874577322` e `30874577320`;
6. integrar o PR #37 somente com head esperado e revisão final limpa.

### Depois do merge

1. confirmar CI e reconciliação na `main`;
2. confirmar o novo SHA da `main`;
3. no servidor, executar backup manual independente antes do primeiro uso do novo fluxo;
4. aplicar `vm.overcommit_memory=1` no host;
5. atualizar `/opt/meucardio` com `git pull --ff-only`;
6. executar `bash ./deploy.sh` presencialmente, sem segundo deploy concorrente;
7. confirmar:
   - `/api/health`;
   - `/api/ready`;
   - `/api/version` com o SHA correto;
   - containers e logs sem erro;
   - inventário das 11 coleções no Painel.

### Validação autenticada de produção

Após o deploy:

- login principal;
- Painel e inventário;
- Biblioteca e buscas;
- CorvIA Chat por cartão e botão flutuante;
- envio e recebimento entre duas sessões/abas;
- WebSocket em `wss://`;
- CorvIA Mail;
- criação/acesso da caixa usando a autenticação principal prevista;
- envio e recebimento de e-mail;
- PDFs clínicos, receituário e links públicos;
- logout e revogação de sessão.

## Estado de publicação

- PRs #34, #35 e #36: publicados;
- PR #37: aberto, mergeável, CI verde e corpus verde;
- head certificado: `f2217ee44972b287c0a3a79c3ac29840df9ae05c`;
- merge do PR #37: **não realizado**;
- deploy em produção: **não realizado**;
- credenciais persistidas: **nenhuma**;
- dados do servidor real alterados nesta sessão: **nenhum**.
