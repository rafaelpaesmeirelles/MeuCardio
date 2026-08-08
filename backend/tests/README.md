# Testes automatizados — backend

Exigem um Postgres 16 real com a extensão `pgvector` e o esquema em dia
(`alembic upgrade head`) — não usam `create_all` de propósito, para testar
contra o mesmo schema que a migração real produz. `test_readiness.py`
também precisa de um Redis real (só ele — os outros ~760 testes não).

**Se este servidor já roda o `docker-compose.prod.yml` de produção**, o
Postgres/Redis de produção já ocupam as portas padrão (5432/6379) via
`docker-proxy` em `127.0.0.1`. Não tente reusá-los para teste — o cluster
local de teste abaixo nasce em portas diferentes (`postgresql-common`
resolve isso sozinho pro Postgres; para o Redis, a porta alternativa é
explícita no comando). **Nunca aponte os testes para o banco/Redis de
produção** — `_banco_limpo` faz `TRUNCATE ... CASCADE` antes de cada teste.

## Banco e Redis locais, uma vez

```bash
apt-get install -y postgresql-16-pgvector redis-server
service postgresql start
sudo -u postgres psql -c "CREATE USER meucardio_test WITH PASSWORD 'test' SUPERUSER;"
sudo -u postgres psql -c "CREATE DATABASE meucardio_test OWNER meucardio_test;"
sudo -u postgres psql -d meucardio_test -c "CREATE EXTENSION IF NOT EXISTS vector;"
pg_lsclusters   # confirme a porta real do cluster novo (5433 se 5432 já estiver ocupado)

redis-server --port 6380 --daemonize yes --bind 127.0.0.1 --logfile /var/log/redis-test.log
```

## Rodar

```bash
cd backend
pip install -r requirements-dev.txt
POSTGRES_HOST=localhost POSTGRES_PORT=5433 POSTGRES_USER=meucardio_test POSTGRES_PASSWORD=test \
POSTGRES_DB=meucardio_test REDIS_URL=redis://127.0.0.1:6380/0 \
STORAGE_ENCRYPTION_KEY=$(python3 -c "import os,base64;print(base64.b64encode(os.urandom(32)).decode())") \
alembic upgrade head

POSTGRES_HOST=localhost POSTGRES_PORT=5433 POSTGRES_USER=meucardio_test POSTGRES_PASSWORD=test \
POSTGRES_DB=meucardio_test REDIS_URL=redis://127.0.0.1:6380/0 \
python3 -m pytest tests/ -v
```

Ajuste `POSTGRES_PORT` para o que `pg_lsclusters` mostrou (5433 é o valor
observado nesta sessão, 08/08/2026, com produção ocupando 5432). Sem
`REDIS_URL` explícito, `test_readiness.py::test_readiness_checks_database_and_redis`
falha sozinho (Redis indisponível) — os demais ~760 testes não dependem
dele e passam normalmente mesmo sem essa variável.

`tests/conftest.py` já define o resto das variáveis de ambiente necessárias
(Mail360, Stripe, JWT) com valores dublê — nenhum teste sai para a rede;
`app/services/mail360.py` é sempre mockado via a fixture `monkeypatch_mail360`.
Cada teste roda contra o banco real acima, com `TRUNCATE ... CASCADE` nas
tabelas tocadas antes de cada teste (ver `_banco_limpo` em `conftest.py`).

## O que está coberto hoje

- `tests/test_corvia_mail.py` — CorvIA Mail (Tarefa 28/29): ativação da
  caixa, isolamento entre o token da conta Corvia e o token da "sessão
  email" (`scope`), login/senha própria da caixa, o fluxo completo de
  "esqueci a senha" reaproveitando `PasswordResetToken.alvo`, pastas/
  mensagens/anexos com o Mail360 mockado, sincronização assinatura → caixa
  no webhook (incluindo o caso de evento atrasado) e o checkout do add-on
  recusando com 409 enquanto o preço não está definido.

## O que ainda não está coberto

Registrar aqui em vez de deixar implícito — mesma régua do resto do projeto:

- Fluxo de e-mail/receituário da Tarefa 29 (`documentos_publicos.py`,
  `document_share_links`, envio por link seguro).
- Verificação de assinatura HTTP real do webhook do Stripe (os testes de
  sincronização chamam `_aplicar_evento` diretamente, não via
  `POST /api/billing/webhook` com assinatura HMAC) — cobre a lógica de
  roteamento por `metadata.tipo`, não a validação de assinatura em si.
- Chamada real contra a API do Mail360 (sem credencial de parceiro — ver
  ressalva no topo de `app/services/mail360.py`).
