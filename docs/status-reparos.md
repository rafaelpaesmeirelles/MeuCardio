# Status dos reparos — CorvIA / MeuCardio

Última atualização: 04/08/2026 11:18 (BRT)

## Resumo executivo

As correções funcionais e operacionais planejadas foram publicadas na `main` pelos PRs #34 a #40.

A produção em `corvia.med.br` foi acessada e recuperada nesta sessão. O site está respondendo novamente com:

- `/api/health`: sucesso;
- `/api/ready`: `database=ok` e `redis=ok`;
- `/api/version`: commit do hotfix local `46d5cbe928218305f75fd37ac6a2caa1df51a5f2` no momento da recuperação.

O banco de produção está na revisão Alembic consolidada:

```text
d63a0cc83807
```

O PR #40 publicou essa mesma cadeia na `main`, eliminando o risco de o próximo checkout remover migrations já registradas no banco.

Nenhuma credencial, senha ou conteúdo do `.env` foi gravado no repositório, em commits ou em PRs.

## Publicações concluídas

### PR #34 — bcrypt direto

- Passlib removido;
- compatibilidade com hashes `$2a$`, `$2b$` e `$2y$`;
- nenhuma senha armazenada alterada;
- 174 testes backend.

### PR #35 — acervo, CorvIA Mail e CorvIA Chat

- Painel e Biblioteca baseados no inventário canônico das 11 coleções;
- CorvIA Mail publicado em rota, menu e Painel;
- CorvIA Chat publicado em cartão, widget, HTTP e WebSocket;
- 182 testes backend.

### PR #36 — ReportLab e Python 3.14

- ReportLab 4.4.10;
- PDFs clínicos testados por geração real;
- 186 testes backend e zero warnings conhecidos.

### PR #37 — deploy certificado

Merge:

```text
d7a4589d2135e368dbcf1743369f60a1a8fa4acd
```

- deploy determinístico em duas fases;
- lock exclusivo e checkout limpo;
- snapshot após bloquear escritores;
- rollback automático da fase mutável;
- reconciliação fail-closed;
- `/api/version` para confirmar o SHA publicado;
- backup e restauração validados;
- corpus de 4.936 registros certificado.

### PR #38 — slug canônico

Merge:

```text
955047999ab7b4015c9a29f8c86368e13d4b0576
```

- importador direto e reconciliador usam a mesma resolução de slug;
- valores vazios, nulos, booleanos, numéricos e espaços externos são rejeitados;
- 242 testes backend;
- 4.936 registros reconciliados.

### PR #39 — consolidação documental

Merge:

```text
a4b9c8efa8c5becda9efebbbbd7f4a47a62edba0
```

- registrou o estado pré-deploy e o roteiro de acesso ao servidor.

### PR #40 — hotfix da cadeia Alembic de produção

Head certificado:

```text
46d5cbe928218305f75fd37ac6a2caa1df51a5f2
```

Merge na `main`:

```text
a0b24f345ab7ffd48fb6f65502b8dc4220884dd4
```

Arquivos publicados:

```text
backend/migrations/versions/a7c92e4f6b18_subscriptions_periodicidade.py
backend/migrations/versions/b3f8a1d92e64_plano_pretendido_e_onboarding.py
backend/migrations/versions/d63a0cc83807_merge_producao_main.py
```

Cadeia consolidada:

```text
c4a8e6f1b3d7
├── a7c92e4f6b18 → b3f8a1d92e64
└── d5b9f2c7a104 → e6c1a8d4f209 → f7d2b9c4a601 → a4c8e1f2b703

(a4c8e1f2b703, b3f8a1d92e64) → d63a0cc83807
```

Certificação do PR #40:

- CI #213 — run `30917296235`;
- **242 testes backend aprovados em 75,30 s**;
- migrations completas e idempotentes;
- smoke HTTP aprovado;
- backup/restauração PostgreSQL aprovados;
- Corpus database reconciliation #85 — run `30917296311`;
- **4.936 registros científicos** confirmados;
- frontend aprovado;
- `pip-audit` sem vulnerabilidades conhecidas;
- revisão Codex no SHA `46d5cbe928`: nenhum problema relevante.

## Incidente de produção em 04/08/2026

### Estado inicial do servidor

O checkout em `/opt/meucardio` estava na `main` antiga `3d19738`, nove commits locais à frente e com arquivos modificados/não rastreados.

Antes de qualquer reset, foram criados:

- branch local de resgate `rescue/server-20260804T121756Z`;
- commit de resgate `ddf6f5c`;
- bundle independente `/root/corvia-rescue-20260804T121756Z/rescue.bundle` (~110 MB);
- patch das alterações rastreadas;
- arquivo dos untracked;
- backup protegido do `.env`;
- checksums SHA-256.

### Backup real do PostgreSQL

Foi criado e validado o dump:

```text
/root/corvia-backups/meucardio_2026-08-04_143903.dump
```

Características:

- aproximadamente 80 MB;
- dump custom do PostgreSQL;
- checksum SHA-256 aprovado;
- catálogo validado com `pg_restore --list`.

### Correção do `.env`

O arquivo possuía sintaxe Bash inválida em `SMTP_FROM` devido a espaço e caracteres `< >` sem aspas.

Formato corrigido:

```bash
SMTP_FROM='CorvIA <contato@corvia.med.br>'
```

Após a correção:

- `bash -n .env`: código 0;
- `docker compose --env-file .env -f docker-compose.prod.yml config`: código 0.

### Falha do primeiro deploy

O backend entrou em restart loop durante `python -m app.commands.migrate` porque o banco registrava a revisão:

```text
b3f8a1d92e64
```

Essa migration e seu ancestral `a7c92e4f6b18` existiam apenas no histórico local antigo e não na `main` publicada.

Depois de restaurar os dois arquivos, o Alembic encontrou duas heads:

```text
a4c8e1f2b703
b3f8a1d92e64
```

Foi criada a migration de merge `d63a0cc83807`. O comando operacional concluiu com `RC_MIGRATE=0`, o backend atingiu readiness e somente então o Caddy foi religado.

### Produção recuperada

Validações realizadas:

- banco em `d63a0cc83807`;
- backend saudável;
- PostgreSQL saudável;
- Redis saudável;
- Caddy religado após readiness;
- `/api/health`: código 0;
- `/api/ready`: código 0;
- `/api/version`: código 0;
- branch do hotfix enviada ao GitHub;
- PR #40 certificado e integrado à `main`.

## Garantias preservadas

- nenhum volume PostgreSQL removido;
- nenhuma restauração manual destrutiva executada;
- backup real validado antes das alterações;
- branch, bundle e `.env` antigo preservados;
- nenhum arquivo científico removido;
- nenhuma senha armazenada alterada;
- corpus de 4.936 registros preservado;
- 1.327 arquivos físicos preservados conforme inventário anterior.

## Pendências atuais

### 1. Alinhar o checkout do servidor à `main` após o PR #40

O servidor continua na branch local do hotfix, embora o conteúdo já esteja publicado na `main`.

No servidor:

```bash
cd /opt/meucardio
git fetch --prune origin
git switch main
git reset --hard origin/main
git status --short
git log -1 --oneline
```

O commit esperado é:

```text
a0b24f345ab7ffd48fb6f65502b8dc4220884dd4
```

Depois, atualizar somente a identificação pública do backend:

```bash
export DEPLOY_COMMIT="$(git rev-parse HEAD)"
docker compose -f docker-compose.prod.yml up -d --no-deps --force-recreate backend
```

Aguardar readiness, manter o Caddy ativo e confirmar `/api/version` com o SHA da `main`.

### 2. Validação autenticada ainda pendente

- login principal;
- Painel mostrando 4.936 registros e mínimos das 11 coleções;
- Biblioteca, paginação e buscas;
- CorvIA Chat pelo cartão e pelo botão flutuante;
- mensagens entre duas sessões/abas;
- WebSocket `wss://`;
- CorvIA Mail e webmail;
- envio e recebimento de e-mail;
- receituário e PDFs clínicos;
- links públicos de documentos;
- logout e revogação de sessão.

### 3. Segurança operacional

A senha administrativa foi compartilhada em texto na conversa. Após terminar os testes autenticados, rotacioná-la e não reutilizar o valor anterior.

### 4. Limpeza futura, somente após estabilidade confirmada

Não apagar ainda:

- `/root/corvia-rescue-20260804T121756Z`;
- `/root/corvia-backups/meucardio_2026-08-04_143903.dump` e checksum;
- branch local de resgate;
- stashes anteriores.

A limpeza pode ser avaliada somente após validação autenticada e novo backup de retenção.

## Ponto exato de retomada

1. sincronizar o servidor com `origin/main` no commit `a0b24f34`;
2. recriar somente o backend com `DEPLOY_COMMIT` da `main`;
3. confirmar health, readiness e version;
4. executar testes autenticados do Painel, Biblioteca, Chat e Mail;
5. rotacionar a senha compartilhada;
6. registrar resultados e eventuais correções em novo PR isolado.
