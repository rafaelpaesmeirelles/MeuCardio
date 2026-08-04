# Publicação certificada da Corvia

Este guia descreve o deploy de produção em `corvia.med.br`, usando o diretório histórico `/opt/meucardio`, Docker Compose, PostgreSQL/pgvector, Redis e Caddy.

> O nome `meucardio` ainda aparece em caminhos, usuário e banco porque são identificadores operacionais existentes. Renomeá-los exige migração própria; não faça substituição textual durante um deploy.

## O que `deploy.sh` garante

O script só declara sucesso depois de:

1. validar as variáveis críticas do `.env`;
2. identificar um SHA Git completo;
3. verificar DNS;
4. criar backup pré-deploy se o banco já estiver em execução;
5. reconstruir e subir os serviços;
6. aguardar `/api/ready` no backend;
7. confirmar as migrations de forma idempotente;
8. reconciliar as 11 coleções científicas;
9. publicar somente conteúdo com `review_status=revisado`;
10. falhar se qualquer coleção permanecer abaixo do mínimo versionado;
11. reindexar a IA quando `AI_ENABLED=true`;
12. confirmar `/api/ready` pelo domínio HTTPS público;
13. confirmar em `/api/version` que o domínio serve exatamente o commit solicitado.

O importador parcial antigo não é mais usado no deploy.

## 1. Pré-requisitos do servidor

- DNS `A` de `corvia.med.br` apontando para o IP do servidor;
- portas TCP 80 e 443 liberadas;
- Docker Engine e Docker Compose v2;
- checkout do repositório em `/opt/meucardio`;
- arquivo `/opt/meucardio/.env` preservado fora do Git;
- acesso administrativo ao host para o ajuste do Redis:

  ```bash
  sudo sysctl -w vm.overcommit_memory=1
  echo 'vm.overcommit_memory=1' | sudo tee /etc/sysctl.d/99-corvia-redis.conf
  ```

## 2. Variáveis mínimas

No diretório do projeto:

```bash
cd /opt/meucardio
cp .env.example .env  # somente no primeiro deploy
nano .env
```

Preencha ao menos:

| Variável | Finalidade |
|---|---|
| `DOMAIN` | `corvia.med.br` |
| `POSTGRES_USER` | usuário existente do banco |
| `POSTGRES_PASSWORD` | senha forte do banco |
| `POSTGRES_DB` | banco existente |
| `JWT_SECRET` | `openssl rand -hex 32` no primeiro deploy |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | bootstrap inicial; troque a senha após entrar |
| `AI_ENABLED` | `true` somente quando a indexação estiver configurada |
| `OPENAI_API_KEY` | necessária quando a IA estiver habilitada |

Nunca recrie ou substitua o `.env` durante uma atualização comum.

## 3. Atualizar o código

```bash
cd /opt/meucardio
git fetch origin
git checkout main
git pull --ff-only origin main
git status --short
git log -1 --oneline
```

`git status --short` deve ficar vazio. O SHA mostrado será injetado no backend e confirmado publicamente no final.

## 4. Executar o deploy

```bash
cd /opt/meucardio
bash ./deploy.sh
```

Não rode o processo em segundo plano. Se alguma etapa falhar, o script mostra o estado dos containers e os logs recentes e termina com código diferente de zero.

## 5. Reconciliação científica

O comando oficial, executado automaticamente pelo deploy, é:

```bash
docker compose -f docker-compose.prod.yml exec -T backend \
  python -m app.commands.reconcile_content --publish-reviewed
```

Ele carrega e valida:

- documentos;
- evidências;
- estudos;
- casos clínicos;
- trilhas;
- galeria;
- exames;
- medicamentos;
- checklists;
- material para pacientes;
- protocolos de emergência;
- listas de controlados.

A operação é idempotente. Registros existentes não são apagados, e somente itens explicitamente revisados são promovidos para publicação. Não use `--allow-partial` em produção.

## 6. Verificações após o deploy

```bash
curl --fail --silent --show-error https://corvia.med.br/api/health
curl --fail --silent --show-error https://corvia.med.br/api/ready
curl --fail --silent --show-error https://corvia.med.br/api/version

docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=200 backend caddy frontend-build
```

O SHA de `/api/version` deve ser idêntico ao de `git rev-parse HEAD`.

Depois de entrar como administrador, confirme:

- o Painel mostra o inventário integral das 11 coleções;
- não há alerta de coleção abaixo do mínimo;
- a Biblioteca diferencia registros preservados de itens publicados;
- CorvIA Mail aparece no Painel e no menu;
- CorvIA Chat abre pelo cartão e pelo botão flutuante;
- envio e recebimento de mensagem funcionam em duas contas/abas;
- o WebSocket usa `wss://` sem erro no navegador.

## Comandos operacionais

### Logs

```bash
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f caddy
docker compose -f docker-compose.prod.yml logs -f redis
```

### Migrations

```bash
docker compose -f docker-compose.prod.yml exec -T backend python -m app.commands.migrate
```

O comando pode ser repetido; a CI exige idempotência.

### Backup manual

```bash
cd /opt/meucardio
PROJETO="$PWD" bash ./infra/backup/backup.sh
```

O backup é um dump custom do PostgreSQL (`.dump`), comprimido internamente pelo `pg_dump`. Antes de ser publicado, seu catálogo é validado por `pg_restore --list`. O script usa arquivo temporário, permissões `0600` e cria um SHA-256 portátil no mesmo diretório.

### Backup automático

```bash
crontab -e
```

Adicione:

```cron
0 3 * * * PROJETO=/opt/meucardio bash /opt/meucardio/infra/backup/backup.sh >> /opt/meucardio/infra/backup/backup.log 2>&1
```

A retenção padrão é de 14 dias e pode ser alterada com `BACKUP_RETENCAO_DIAS`.

## Falhas comuns

### Backend não atinge readiness

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=300 backend db redis
```

O deploy não executa reconciliação enquanto o backend estiver indisponível.

### Corpus abaixo do mínimo

O reconciliador informa exatamente quais coleções estão incompletas. Verifique se todos os diretórios versionados foram recebidos pelo checkout e se os volumes somente-leitura estão montados no backend. Não contorne com `--allow-partial`.

### HTTPS não responde ou commit diverge

```bash
dig +short corvia.med.br
curl -fsS https://corvia.med.br/api/version
git rev-parse HEAD
docker compose -f docker-compose.prod.yml logs --tail=300 caddy backend
```

O IP retornado pelo DNS deve ser o IP público do servidor. Se `/api/version` divergir, o backend antigo ainda está atendendo ou o container não foi recriado.

### Redis alerta sobre memory overcommit

Aplique `vm.overcommit_memory=1` no host. Essa configuração não pode ser feita de dentro do container ou do repositório.

## Rollback

Antes de cada atualização, o deploy cria um dump custom quando o banco já está em execução. Para voltar apenas o código:

```bash
cd /opt/meucardio
git log --oneline -10
git checkout <commit-anterior-certificado>
bash ./deploy.sh
```

Não execute downgrade manual de migrations. Restauração de banco é operação destrutiva e deve usar o dump, seu SHA-256 e um banco-alvo explicitamente confirmado.

## Limitações externas

O repositório não consegue, sozinho:

- abrir a porta SSH do provedor;
- alterar firewall ou DNS;
- aplicar `sysctl` no host;
- executar o deploy sem acesso administrativo ao servidor;
- validar credenciais reais de e-mail, Stripe ou provedores de IA.
