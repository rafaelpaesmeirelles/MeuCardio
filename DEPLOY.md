# Publicação certificada da Corvia

Este guia descreve o deploy de produção em `corvia.med.br`, usando o diretório histórico `/opt/meucardio`, Docker Compose, PostgreSQL/pgvector, Redis e Caddy.

> O nome `meucardio` ainda aparece em caminhos, usuário e banco porque são identificadores operacionais existentes. Renomeá-los exige migração própria; não faça substituição textual durante um deploy.

## Deploy automático da `main`

O workflow `Deploy production` só libera o SHA que ainda é a ponta da `main`
e que concluiu com sucesso `CI`, `RC2 Acceptance`, `Visual QA`,
`Corpus database reconciliation`, `Deep functional inventory` e
`Pre-home visual QA`. Enquanto o Windows estiver registrado como pendente,
`Native installers` permanece manual e não bloqueia a publicação certificada
de web e Android. A conexão usa uma chave SSH forçada: ela
não abre shell nem encaminha portas. A release integrada aceita staging nativo
e deploy apenas quando o SHA é exatamente o `origin/main` do servidor.

Ativação única em produção, depois que os arquivos desta mudança estiverem na
`main`:

```bash
cd /opt/meucardio
git fetch origin main
git checkout main
git pull --ff-only origin main
chmod 0755 ops/remote-deploy-entrypoint.sh ops/install-github-deploy-key.sh
bash ops/install-github-deploy-key.sh 169.58.78.100 22
```

Ao migrar uma chave antiga já instalada, não use o comando `deploy` como
bootstrap: ele alteraria produção. Use uma sessão administrativa e o fluxo sem
checkout descrito em `docs/aplicativos-nativos-1.2.0.md`.
O bootstrap deve ser extraído com `git show SHA:ops/bootstrap-release-entrypoint.sh`;
executar o caminho no checkout antigo não funciona porque o arquivo ainda não existe nele.

Depois da ativação, os deploys aprovados são automáticos. Para reprocessar
manualmente um SHA já certificado:

```bash
gh workflow run deploy-production.yml \
  --repo rafaelpaesmeirelles/MeuCardio \
  -f sha="$(git rev-parse origin/main)"
```

Os workflows históricos `emergency-profile-deploy.yml` e
`emergency-unlock-deploy.yml` foram retirados: ambos publicavam web/APK por
comandos que contornavam staging, assinaturas e gates. Uma urgência usa o mesmo
`Deploy production` acima; acelerar a execução não muda o protocolo nem reduz
as validações.

## O que `deploy.sh` garante

O script só declara sucesso depois de:

1. validar as variáveis críticas do `.env`;
2. identificar um SHA Git completo;
3. verificar DNS;
4. reconstruir as imagens a partir do checkout imutável;
5. **confirmar que o banco NÃO está adiantado em relação às migrations deste
   RC** (issue #52, hardening pós-incidente de 11/08/2026 — ver seção
   "Migrations" abaixo) — aborta antes de tocar em qualquer serviço se
   detectar que uma migration já foi aplicada fora deste script;
6. criar backup pré-deploy se o banco já estiver em execução;
7. subir os serviços com a imagem nova;
8. aguardar `/api/ready` no backend;
9. confirmar as migrations de forma idempotente;
10. reconciliar as 11 coleções científicas;
11. publicar somente conteúdo com `review_status=revisado`;
12. falhar se qualquer coleção permanecer abaixo do mínimo versionado;
13. reindexar a IA quando `AI_ENABLED=true`;
14. confirmar `/api/ready` pelo domínio HTTPS público;
15. confirmar em `/api/version` que o domínio serve exatamente o commit solicitado.

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

> ## 🚫 NUNCA rode este comando manualmente contra produção fora de `./deploy.sh`
>
> **Incidente real, 11/08/2026 (issue #52):** este comando foi rodado manualmente
> contra o backend antigo, ainda em execução, como um passo isolado de
> "verificação de schema" — **antes** de `./deploy.sh` ser chamado. `migrations/`
> é bind mount no container, então o backend antigo já enxergava as migrations
> novas do checkout do RC assim que o `git checkout`/`merge` do host trocava de
> commit — mesmo sem nenhum rebuild de imagem. O comando **não tem modo
> dry-run**: rodá-lo "só para conferir" aplica a migração de verdade, para
> sempre, ali mesmo.
>
> Consequência: quando `./deploy.sh` rodou depois, seu próprio backup
> pré-deploy (`criar_backup_pre_deploy`) já capturou um banco **que já estava
> no schema novo** — deixou de representar o estado real anterior à mudança.
> O deploy falhou por outro motivo (bug de conteúdo, não da migration), o
> rollback automático disparou como projetado, mas restaurou um backup já
> contaminado: produção ficou fora do ar, com backend/Caddy parados, exigindo
> intervenção manual para restaurar de um backup anterior, ainda mais antigo,
> localizado à mão comparando o `alembic_version` de vários dumps.
>
> **A idempotência do comando (abaixo) é real, mas não protege contra isto** —
> ela garante que rodar duas vezes SEGUIDAS não aplica nada a mais na segunda
> vez; não protege contra a PRIMEIRA vez ser um passo isolado, fora da
> sequência backup → up → migrate que `./deploy.sh` garante.
>
> **Guarda técnica correspondente**: `deploy.sh` (função
> `validar_migrations_nao_adiantadas`, chamada logo após o build, antes de
> tocar em caddy/backend/backup) aborta o deploy se detectar que o banco já
> está no head das migrations do RC ANTES do próprio script ter feito
> qualquer mudança — é exatamente o sintoma deste incidente, pego cedo.
>
> **Se você precisa mesmo inspecionar o estado das migrations sem aplicar
> nada**, use comandos somente-leitura, que nunca escrevem no banco:
> ```bash
> docker compose -f docker-compose.prod.yml exec -T backend alembic current
> docker compose -f docker-compose.prod.yml exec -T backend alembic heads
> ```

```bash
docker compose -f docker-compose.prod.yml exec -T backend python -m app.commands.migrate
```

Existe só como referência do que `./deploy.sh` executa internamente, na
sequência certificada (depois do backup, antes da reconciliação de
conteúdo) — não é um comando para rodar isoladamente. O comando pode ser
repetido sem efeito adicional (idempotente), mas isso não é o mesmo que ser
seguro para rodar fora de ordem.

### Backup manual

```bash
cd /opt/meucardio
PROJETO="$PWD" bash ./infra/backup/backup.sh
```

O backup é um dump custom do PostgreSQL (`.dump`), comprimido internamente pelo `pg_dump`. Antes de ser publicado, seu catálogo é validado por `pg_restore --list`. O script usa arquivo temporário, permissões `0600` e cria um SHA-256 portátil no mesmo diretório.

**Desde 06/08/2026, o mesmo comando também empacota os quatro volumes sensíveis com arquivo enviado por assinante** (`kycfiles` — selfie e documento pessoal/profissional do KYC; `documentofiles` — PDF de receituário/documento assinado; `certificadosfiles` — certificado digital A1; `examefiles` — exame de telediagnóstico), um `.tar.gz` + `.sha256` por volume, no mesmo diretório e com a mesma retenção do dump do banco. Cada arquivo já está cifrado por dentro pelo cofre (`app/services/cofre.py`) — o backup não decifra nada, só empacota. Restaurar um volume: `infra/backup/restaurar_volume.sh <arquivo.tar.gz>` (destrutivo, pede confirmação, para o backend antes de escrever — mesma cautela do `restaurar.sh` do banco).

**Isto NÃO é disaster recovery contra perda do host inteiro** — os pacotes ficam no mesmo servidor (`infra/backup/dumps/`). Réplica fora do VPS exigiria credencial de armazenamento externo (S3, Backblaze etc.) que este projeto não tem configurada hoje; decisão de contratar isso é do Rafael, não assumida aqui.

### Backup automático

```bash
crontab -e
```

Adicione:

```cron
0 3 * * * PROJETO=/opt/meucardio bash /opt/meucardio/infra/backup/backup.sh >> /opt/meucardio/infra/backup/backup.log 2>&1
```

A retenção padrão é de 14 dias e pode ser alterada com `BACKUP_RETENCAO_DIAS`.

### Monitoramento de frescor do backup (issue #52, hardening pós-gate-final)

O comando acima **cria** o backup diário; o comando abaixo **verifica** que
ele de fato foi criado, tem menos de 30h e passa na checagem de checksum —
sem isso, uma falha silenciosa do cron de backup (disco cheio, permissão,
serviço fora do ar) só seria percebida na hora de precisar restaurar.
Instale junto, com 30 minutos de folga sobre o horário do backup:

```cron
30 3 * * * /opt/meucardio/infra/backup_freshness_cron.sh >> /opt/meucardio/infra/backup_freshness_cron.log 2>&1
```

Este script só verifica e loga — **não envia alerta externo** (e-mail/SMS/
webhook). Não há integração de alerta configurada neste projeto hoje; ler o
log (`infra/backup_freshness_cron.log`) ou encadear a saída não-zero a um
serviço de monitoramento (ex.: healthchecks.io, um cron externo que baixa
esse log) é decisão operacional do Rafael, não implementada aqui.

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
