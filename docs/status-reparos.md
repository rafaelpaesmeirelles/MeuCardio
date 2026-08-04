# Status dos reparos — CorvIA / MeuCardio

Última atualização: 04/08/2026 00:28 (BRT)

## Resumo executivo

A `main` já contém os PRs #34, #35, #36 e #37. O PR #37 foi integrado no commit:

```text
d7a4589d2135e368dbcf1743369f60a1a8fa4acd
```

Esse merge publicou o deploy certificado, backup/restauração endurecidos, rollback automático, identificação pública do commit e reconciliação científica fail-closed.

Após o merge, a revisão Codex encontrou um último caso-limite isolado: Markdown que declara explicitamente `slug` vazio, nulo, falso ou numérico ainda podia receber fallback pelo título. A correção foi reaplicada numa branch limpa baseada na `main`:

```text
agent/reconcile-slug-explicito
```

Nenhuma credencial, senha ou dado do servidor foi gravado no repositório, documentação, commits, PRs ou logs produzidos neste trabalho.

## Publicado na `main`

### PR #34 — bcrypt direto

Commit publicado:

```text
2209d1e3
```

Resultado:

- Passlib removido;
- bcrypt direto compatível com hashes `$2a$`, `$2b$` e `$2y$`;
- hashes truncados ou malformados bloqueados antes do binding nativo;
- nenhuma senha armazenada alterada;
- CI verde com **174 testes backend**.

### PR #35 — acervo, CorvIA Mail e CorvIA Chat

Commit publicado:

```text
54ccee76
```

Resultado:

- Painel usa o inventário integral das 11 coleções;
- separação entre registros preservados e conteúdo publicado;
- mínimos individuais impedem que excesso numa coleção esconda déficit em outra;
- alertas de integridade no Painel e na Biblioteca;
- CorvIA Mail visível no Painel e menu;
- CorvIA Chat visível em cartão e widget, com HTTP, WebSocket, histórico, busca e não lidas;
- CI verde com **182 testes backend**.

### PR #36 — ReportLab e Python 3.14

Commit publicado:

```text
1bea10cf
```

Resultado:

- ReportLab atualizado para 4.4.10, permanecendo na linha 4.x;
- warning de `ast.NameConstant` eliminado;
- receituário e documento clínico protegidos por geração real de PDF;
- CI verde com **186 testes backend e zero warnings**.

### PR #37 — deploy, corpus e commit publicado

Commit de merge:

```text
d7a4589d2135e368dbcf1743369f60a1a8fa4acd
```

Head certificado antes do merge:

```text
4b0e1359eb637ba4989b6baa5e619d310e94139c
```

Certificação:

- CI #204 — run `30875803741`;
- **233 testes backend aprovados em 74,40 s**;
- frontend integralmente aprovado;
- auditorias Python e Node sem vulnerabilidades conhecidas;
- migrations completas e idempotentes;
- bootstrap administrativo aprovado;
- smoke HTTP aprovado: health, readiness, sessão HttpOnly e logout;
- backup/restauração PostgreSQL aprovados com preservação da identidade do registro de prova;
- Corpus database reconciliation #80 — run `30875803765`;
- **4.936 registros científicos** confirmados nas 11 coleções.

## Garantias operacionais publicadas pelo PR #37

### Build determinístico

- lock exclusivo com `flock` impede deploys concorrentes;
- `HEAD`, árvore Git e checkout limpo são revalidados durante o processo;
- `.dockerignore` exclui artefatos locais ignorados;
- frontend usa `package-lock.json` e `npm ci`;
- imagens são construídas antes da indisponibilidade;
- `/api/version` expõe somente o SHA injetado;
- o deploy compara o SHA público com o commit local antes de declarar sucesso.

### Deploy em duas fases

1. valida host, `.env`, Git e Docker;
2. adquire lock e confirma checkout imutável;
3. constrói as imagens sem interromper o site atual;
4. fecha Caddy e backend antigo antes do snapshot usado no rollback;
5. detecta banco por container ou volume `pgdata`, inclusive sem labels;
6. cria e valida o backup pré-deploy sem escritores ativos;
7. arma rollback antes de iniciar o novo backend e suas migrations automáticas;
8. executa migrations, reconciliação e eventual indexação;
9. exige readiness interno e revalidação do checkout;
10. abre o Caddy somente após os gates privados;
11. valida HTTPS, readiness e SHA público.

### Backup e restauração

- dump custom e comprimido do PostgreSQL;
- arquivo temporário e publicação atômica;
- validação por `pg_restore --list`;
- SHA-256 vinculado ao nome e conteúdo do dump selecionado;
- permissões restritas;
- restaurador compatível com `.dump` atual e `.sql.gz` legado;
- checksum e catálogo validados antes do `dropdb`;
- confirmação destrutiva em duas etapas no uso manual;
- backend e proxy permanecem fora do tráfego durante restauração;
- restauração usa `pg_restore --exit-on-error`;
- falha durante a fase mutável aciona rollback automático;
- após rollback, backend e Caddy permanecem parados até intervenção.

### Reconciliação científica fail-closed

Comando oficial:

```bash
python -m app.commands.reconcile_content --publish-reviewed
```

Garantias:

- o deploy não usa `--allow-partial`;
- falhas, avisos, recusados, duplicados ignorados, ausências e Markdown vazio bloqueiam a certificação;
- diagnósticos são pesquisados recursivamente;
- manifestos JSON devem ser listas de objetos com `slug` válido e único;
- slugs com espaços externos são rejeitados antes dos loaders/upserts;
- conjunto canônico de slugs é inventariado por commit;
- somente itens revisados e presentes na fonte atual são publicados;
- slugs removidos ou renomeados são despublicados, preservando histórico no banco;
- mínimos individuais das 11 coleções permanecem obrigatórios;
- excesso numa coleção não mascara déficit em outra.

## Correção complementar em andamento

Branch:

```text
agent/reconcile-slug-explicito
```

Problema residual:

- em Markdown, `slug: ""`, `slug: null`, `slug: false` ou `slug: 0` era interpretado como se a chave não existisse;
- o reconciliador então gerava um slug pelo título, certificando o arquivo sob identificador diferente do explicitamente declarado.

Correção implementada:

- fallback por título ocorre somente quando a chave `slug` está realmente ausente;
- qualquer `slug` declarado deve ser string não vazia;
- espaços nas extremidades continuam bloqueados;
- valores vazio, nulo, falso e numérico são rejeitados antes de qualquer carregador ou upsert;
- arquivo sem chave `slug` continua recebendo fallback legítimo pelo título.

Testes adicionados:

- fallback legítimo quando a chave é omitida;
- rejeição de `slug: ""`;
- rejeição de `slug: null`;
- rejeição de `slug: false`;
- rejeição de `slug: 0`.

## Bloqueio externo de produção

O deploy real não foi executado nesta sessão.

O ambiente utilizado não conseguiu resolver ou alcançar `corvia.med.br`. O host anteriormente informado também não aceitou as conexões tentadas. Portanto não foi possível:

- confirmar o SHA atualmente implantado;
- criar o backup real;
- atualizar `/opt/meucardio`;
- executar o novo `deploy.sh`;
- reconciliar o PostgreSQL real;
- validar login, Painel, Biblioteca, CorvIA Mail e CorvIA Chat;
- testar mensagens em duas sessões e WebSocket `wss://`;
- testar envio/recebimento do CorvIA Mail;
- aplicar `vm.overcommit_memory=1` no host.

As credenciais fornecidas pelo proprietário não foram usadas porque o domínio permaneceu inacessível e não foram persistidas em nenhum artefato. Recomenda-se rotacionar a senha após a validação, pois ela foi compartilhada em texto na conversa.

## Trabalho pendente imediato

1. abrir PR complementar da branch `agent/reconcile-slug-explicito`;
2. executar CI completa e reconciliação independente;
3. solicitar revisão Codex no SHA final;
4. corrigir qualquer novo P1/P2 material;
5. integrar somente com CI, corpus e revisão verdes;
6. atualizar este arquivo com o número do PR, runs, quantidade final de testes e commit de merge.

## Trabalho pendente no servidor

Quando o acesso ao host for restabelecido:

1. aplicar no host:

   ```bash
   sudo sysctl -w vm.overcommit_memory=1
   echo 'vm.overcommit_memory=1' | sudo tee /etc/sysctl.d/99-corvia-redis.conf
   ```

2. acessar `/opt/meucardio`;
3. confirmar que `.env` permanece preservado;
4. executar backup manual independente;
5. atualizar a `main` com `git pull --ff-only`;
6. confirmar checkout limpo;
7. executar presencialmente:

   ```bash
   bash ./deploy.sh
   ```

8. confirmar:
   - `/api/health`;
   - `/api/ready`;
   - `/api/version` com o SHA correto;
   - 4.936 registros e mínimos individuais das 11 coleções;
   - ausência de erros em backend, PostgreSQL, Redis, Caddy e frontend.

## Validação autenticada após o deploy

- login principal;
- Painel e inventário integral;
- Biblioteca, paginação e buscas;
- CorvIA Chat por cartão e botão flutuante;
- envio/recebimento entre duas sessões ou abas;
- WebSocket `wss://`;
- CorvIA Mail, ativação/acesso da caixa e webmail;
- envio e recebimento de e-mail;
- receituário e PDFs clínicos;
- links públicos de documentos;
- logout e revogação de sessão.

## Ponto exato para a próxima sessão

1. consultar a branch `agent/reconcile-slug-explicito`;
2. localizar o PR complementar aberto para essa branch;
3. confirmar o último SHA;
4. conferir CI, reconciliação e revisão Codex;
5. integrar o PR se não houver apontamento material;
6. depois retomar o acesso ao servidor e o deploy real.

## Estado de publicação

- PRs #34, #35, #36 e #37: publicados na `main`;
- correção de slug explícito inválido: implementada em branch complementar;
- deploy real: não executado;
- credenciais persistidas: nenhuma;
- arquivos científicos removidos: nenhum;
- senhas armazenadas alteradas: nenhuma;
- dados do servidor real alterados nesta sessão: nenhum.
