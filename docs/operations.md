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
