# Release, homologação e recuperação

Este documento define o mínimo operacional para publicar a Corvia sem depender
de verificações manuais informais. Código, banco e arquivos clínicos são ativos
diferentes e precisam de controles independentes.

## 1. Ordem de release

1. O commit candidato deve estar em PR e com CI concluída.
2. A homologação deve usar host, banco, Redis, domínio e volumes próprios.
3. Aplicar as migrations com o mesmo comando da produção:

   ```bash
   docker compose -f docker-compose.prod.yml run --rm backend \
     python -m app.commands.migrate
   ```

4. Subir o ambiente e aguardar `/api/ready`.
5. Executar o smoke HTTP:

   ```bash
   python scripts/release_smoke.py \
     --base-url https://homolog.corvia.med.br \
     --email release-smoke@corvia.med.br \
     --password 'SENHA_EXCLUSIVA_DE_HOMOLOGACAO' \
     --expect-secure-cookie
   ```

6. Validar manualmente os fluxos clínicos que dependem de PDF, assinatura,
   Stripe, SMTP ou provedores externos.
7. Gerar backup imediatamente antes da publicação.
8. Publicar, repetir o smoke contra produção e acompanhar logs/erros.

A conta de smoke deve existir somente na homologação. Não se deve manter senha
de teste conhecida em produção.

## 2. Isolamento da homologação

Use um host separado sempre que possível. O nome de projeto do Compose impede
que volumes de homologação usem os nomes da produção:

```bash
docker compose \
  --project-name corvia-staging \
  --env-file .env.staging \
  -f docker-compose.prod.yml \
  up -d --build
```

O arquivo `.env.staging` não deve ser versionado e precisa conter segredos
próprios, domínio de homologação, chaves Stripe de teste e banco sem dados reais.
Nunca copie a chave de criptografia nem o banco de produção para um ambiente
menos protegido. Quando a estrutura real for necessária, use dados previamente
anonimizados.

## 3. Backup PostgreSQL

### Dependências do host

- cliente PostgreSQL compatível com o servidor;
- `age` para criptografia;
- destino externo ao servidor para a cópia final.

Gere uma identidade `age` fora do diretório da aplicação:

```bash
install -d -m 700 /root/.config/corvia
age-keygen -o /root/.config/corvia/backup.agekey
```

Guarde a chave privada também em cofre externo. O destinatário público exibido
pelo comando é usado em `BACKUP_AGE_RECIPIENT`.

### Execução

Exporte as variáveis de conexão sem gravá-las na linha de comando ou no log:

```bash
export PGHOST=127.0.0.1
export PGPORT=5432
export PGUSER='USUARIO_DO_BANCO'
export PGPASSWORD='SENHA_DO_BANCO'
export PGDATABASE='BANCO_DA_CORVIA'
export BACKUP_DIR='/var/backups/corvia'
export BACKUP_AGE_RECIPIENT='age1...'

bash ops/backup-postgres.sh
```

O comando:

- produz `pg_dump` no formato custom;
- valida o catálogo com `pg_restore --list`;
- recusa salvar sem criptografia por padrão;
- grava checksum SHA-256 separado;
- aplica permissão `0600`.

`ALLOW_UNENCRYPTED_BACKUP=1` existe exclusivamente para CI ou ambiente isolado.
Não deve ser usado em produção.

## 4. Backup dos arquivos clínicos

O banco não contém todos os binários. Também precisam de backup:

- fotos e logos em `/uploads`;
- exames cifrados em `/exames-pacientes`;
- receitas e documentos em `/documentos-emitidos`;
- materiais de curso em `/materiais-curso`.

Com o backend de produção em execução:

```bash
export COMPOSE_FILE=docker-compose.prod.yml
export BACKUP_DIR='/var/backups/corvia'
export BACKUP_AGE_RECIPIENT='age1...'

bash ops/backup-clinical-volumes.sh
```

O script monta os volumes do backend somente para leitura em um container
efêmero, valida o arquivo `tar.gz`, criptografa e gera checksum.

A chave `STORAGE_ENCRYPTION_KEY` não deve ser incluída no mesmo pacote dos
arquivos cifrados. Ela precisa de cópia em cofre separado; sem essa chave, a
restauração dos volumes não torna os documentos legíveis.

## 5. Cópia externa e retenção

Manter os arquivos somente no mesmo servidor não protege contra perda do host.
Após cada execução, copie backup e checksum para armazenamento externo com
versionamento e controle de acesso.

Política inicial recomendada:

- diário: 14 cópias;
- semanal: 8 cópias;
- mensal: 12 cópias;
- anual: conforme obrigação jurídica e política de retenção aprovada.

A política definitiva deve ser compatível com LGPD, contrato, prontuário e
obrigações profissionais aplicáveis. Expiração do backup deve excluir tanto o
arquivo quanto chaves ou índices associados, conforme a política aprovada.

## 6. Teste de restauração PostgreSQL

Restaure sempre em banco separado. O script recusa usar o mesmo nome de
`PGDATABASE` e exige confirmação textual do destino:

```bash
export PGHOST=127.0.0.1
export PGPORT=5432
export PGUSER='USUARIO_DO_BANCO'
export PGPASSWORD='SENHA_DO_BANCO'
export PGDATABASE='BANCO_DA_CORVIA'
export BACKUP_AGE_IDENTITY='/root/.config/corvia/backup.agekey'

createdb corvia_restore_20260803
TARGET_PGDATABASE=corvia_restore_20260803 \
CONFIRM_RESTORE_TARGET=corvia_restore_20260803 \
  bash ops/restore-postgres.sh /var/backups/corvia/BACKUP.dump.age
```

Depois da restauração:

1. conferir `alembic_version`;
2. executar a aplicação apontando somente para o banco restaurado;
3. rodar `/api/ready` e o smoke HTTP;
4. conferir amostras de contagem sem expor conteúdo clínico em logs;
5. destruir o banco de teste após registrar o resultado.

A CI executa este ciclo automaticamente em banco descartável a cada PR. Isso
prova a mecânica do dump, mas não substitui o exercício periódico com um backup
real criptografado e os volumes clínicos.

## 7. Rollback

Antes do deploy, registre:

- SHA atualmente em produção;
- SHA candidato;
- versão Alembic anterior e nova;
- caminho dos backups pré-deploy;
- responsável pela decisão de rollback.

Se o erro ocorrer antes de migration incompatível, volte a imagem/commit e
reinicie. Se a migration alterar dados ou remover estrutura, não execute
`alembic downgrade` por impulso: interrompa escrita, preserve logs e use o plano
específico da migration ou restaure banco e volumes como conjunto consistente.

## 8. Checklist de saída

- CI verde e PR revisado;
- segredos de produção validados;
- backup de banco e volumes concluído, criptografado e copiado externamente;
- checksum conferido;
- migration testada em banco vazio e em restauração;
- `/api/health` e `/api/ready` aprovados;
- login por cookie HttpOnly e logout aprovados;
- PDFs, uploads e links públicos testados;
- webhooks Stripe e envio de e-mail observados;
- rollback documentado;
- monitoramento acompanhado após publicação.
