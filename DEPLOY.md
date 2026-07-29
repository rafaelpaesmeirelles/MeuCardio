# Colocar a Corvia no ar

Guia para o seu servidor já contratado, com o domínio já registrado.

> **Sobre o nome `meucardio` que aparece adiante neste arquivo.** Ele sobrou do
> nome anterior do produto em lugares onde **não é texto de marca, e sim
> identificador real em uso**: o diretório do projeto no servidor
> (`/opt/meucardio`), o usuário e o banco do PostgreSQL (`POSTGRES_USER` e
> `POSTGRES_DB`) e o prefixo dos dumps gerados por `infra/backup/backup.sh`.
> **Trocar esses valores aqui quebra os comandos** — renomear o banco é migração
> de dado, não edição de documentação. Estão listados como resíduo conhecido no
> `CLAUDE.md`; enquanto não forem migrados de fato, este arquivo tem de
> descrevê-los como são.

## 1. Antes de começar

- **DNS**: crie um registro **A** apontando seu domínio (ou subdomínio, ex.
  `corvia.med.br`) para o **IP do servidor**. Sem isso o
  Caddy não consegue emitir o certificado HTTPS.
- **Portas 80 e 443 liberadas** no firewall do servidor/provedor.
- **Chave da OpenAI** em mãos, se for ligar a IA clínica agora.

## 2. Colocar o projeto no servidor

Envie a pasta do projeto (via `scp`, `rsync` ou `git clone` se você versionar
em algum repositório privado). Exemplo com `scp` a partir do seu computador:

    scp -r meucardio usuario@SEU_SERVIDOR:/opt/

## 3. Configurar o ambiente

No servidor, dentro da pasta do projeto:

    cp .env.example .env
    nano .env

Preencha, no mínimo:

| Variável | O que colocar |
|---|---|
| `DOMAIN` | o domínio/subdomínio que você apontou no DNS |
| `POSTGRES_PASSWORD` | uma senha forte, só sua |
| `JWT_SECRET` | gere com `openssl rand -hex 32` |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | seu login inicial — troque a senha depois de entrar |
| `OPENAI_API_KEY` | se for usar o assistente clínico agora; senão deixe `AI_ENABLED=false` |

## 4. Subir

    ./deploy.sh

O script confere se as senhas de exemplo foram trocadas, verifica se o
Docker está instalado, sobe os serviços, importa o conteúdo científico e
indexa para a IA (se ligada). Leva alguns minutos na primeira vez, porque
o Postgres com pgvector e o build do frontend rodam do zero.

## 5. Conferir

- `https://SEU_DOMINIO` deve abrir a tela de login.
- `https://SEU_DOMINIO/api/docs` mostra a documentação da API.
- Entre com o `ADMIN_EMAIL`/`ADMIN_PASSWORD` do `.env` e **troque a senha**.

## Comandos do dia a dia

    # ver logs
    docker compose -f docker-compose.prod.yml logs -f backend

    # reiniciar depois de mudar código
    docker compose -f docker-compose.prod.yml up -d --build

    # importar conteúdo novo (depois de colocar .md em content/<tema>/)
    docker compose -f docker-compose.prod.yml exec backend python -m app.services.importer
    docker compose -f docker-compose.prod.yml exec backend python -m app.services.indexar

    # backup do banco
    docker compose -f docker-compose.prod.yml exec db pg_dump -U meucardio meucardio > backup.sql

    # parar tudo
    docker compose -f docker-compose.prod.yml down

## Se o certificado HTTPS não sair

Confira `docker compose -f docker-compose.prod.yml logs caddy`. A causa mais
comum é o DNS ainda não ter propagado — pode levar de minutos a algumas
horas dependendo do provedor. Teste com `dig SEU_DOMINIO` até o IP bater
com o do servidor, então rode `docker compose -f docker-compose.prod.yml
restart caddy`.

## Backup automático

    scp -r infra/backup root@SEU_SERVIDOR:/opt/meucardio/infra/
    ssh root@SEU_SERVIDOR
    chmod +x /opt/meucardio/infra/backup/*.sh
    crontab -e
    # adicionar:
    0 3 * * * /opt/meucardio/infra/backup/backup.sh >> /opt/meucardio/infra/backup/backup.log 2>&1

Backup diário às 3h, compactado, com 14 dias de retenção automática. Os arquivos ficam em
`infra/backup/dumps/`. Para restaurar:

    ./infra/backup/restaurar.sh infra/backup/dumps/meucardio_AAAA-MM-DD_HHMM.sql.gz

O script pede confirmação explícita antes de apagar o banco atual — não é destrutivo por acidente.

## Migração de banco (Alembic)

O esquema do banco agora é versionado. Depois de aplicar o pacote que traz `backend/migrations/`,
rode **uma vez**:

    ./migrations_setup.sh

Isso gera a migração de linha de base a partir do banco real e marca como já aplicada — não
recria nem altera nenhuma tabela existente.

Daqui pra frente, mudança de esquema (nova coluna, nova tabela) é:

    # 1. editar o modelo em backend/app/models/
    docker compose -f docker-compose.prod.yml exec backend alembic revision --autogenerate -m "descricao"
    # 2. revisar o arquivo gerado em backend/migrations/versions/
    docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

Sem mais `ALTER TABLE` manual.

## O que este deploy NÃO cobre ainda

- Alertas de monitoramento/uptime.
- Ambiente de homologação separado do de produção.

Para um piloto com poucos usuários da equipe, o que está aqui é suficiente.
Antes de abrir para todo o serviço, vale revisar esses dois pontos.
