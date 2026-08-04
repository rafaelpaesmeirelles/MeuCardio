# Operação do backend Corvia

## Princípios

A importação de `app.main` não cria tabelas, extensões, índices, triggers ou
usuários. O processo HTTP apenas valida a configuração e registra as rotas.

Mudanças de banco pertencem ao fluxo Alembic. A criação do primeiro
administrador é uma ação explícita do operador e nunca redefine uma conta já
existente.

## Subida local

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend python -m app.commands.create_admin
```

O serviço `backend` executa `python -m app.commands.migrate` antes do Uvicorn.
Esse comando:

1. garante as extensões `vector`, `pg_trgm` e `unaccent`, necessárias antes da
   migration-base;
2. aplica `alembic upgrade head`;
3. termina antes de o servidor HTTP começar a aceitar tráfego.

Executar o comando novamente é seguro e não reaplica migrations concluídas.

## Subida em produção

Antes do Compose, execute o preflight no próprio host Linux:

```bash
bash ops/check-redis-host.sh
```

O comando é somente leitura e termina com:

- código `0` quando `vm.overcommit_memory=1`;
- código `2` quando o host não está apto para operações de background do Redis;
- código `3` quando o valor não pode ser lido ou é inválido.

Quando o preflight retornar código `2`, aplique e persista a configuração como
administrador do host:

```bash
sudo sysctl -w vm.overcommit_memory=1
printf 'vm.overcommit_memory = 1\n' | \
  sudo tee /etc/sysctl.d/99-corvia-redis.conf
sudo sysctl --system
bash ops/check-redis-host.sh
```

A configuração pertence ao kernel do host, não ao container. O script nunca
executa `sudo`, não modifica `/proc` e não apresenta o requisito como corrigido
até conseguir ler o valor `1`.

Depois do preflight aprovado:

```bash
cp .env.example .env
# preencher todas as variáveis críticas
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend \
  python -m app.commands.create_admin
```

O comando de administrador usa `ADMIN_EMAIL` e `ADMIN_PASSWORD` do `.env` por
padrão. Também aceita parâmetros explícitos:

```bash
docker compose -f docker-compose.prod.yml exec backend \
  python -m app.commands.create_admin \
  --email admin@dominio.com.br \
  --password 'senha-longa-e-exclusiva' \
  --name 'Administrador Corvia'
```

Se o e-mail já existir, a operação encerra com sucesso sem trocar nome, papel ou
senha. Alterações de credencial devem usar um fluxo administrativo separado e
auditável.

## Probes

- `GET /api/health`: liveness; confirma que o processo HTTP responde.
- `GET /api/ready`: readiness; exige PostgreSQL e Redis disponíveis.

O proxy de produção aguarda o backend ficar `healthy`, baseado em `/api/ready`,
antes de encaminhar tráfego.

## Migração manual

Para aplicar migrations sem reiniciar o serviço:

```bash
docker compose -f docker-compose.prod.yml exec backend \
  python -m app.commands.migrate
```

Não execute `Base.metadata.create_all()` em produção e não adicione DDL ao
startup da API. Novas colunas, constraints, índices, triggers e backfills devem
ser implementados como revisões Alembic.

## Rollback

Antes de downgrade, faça backup do PostgreSQL. Em seguida, identifique a revisão
alvo e execute o Alembic conscientemente dentro do backend. Extensões não são
removidas automaticamente por downgrade porque podem ser compartilhadas por
outros objetos do banco.
