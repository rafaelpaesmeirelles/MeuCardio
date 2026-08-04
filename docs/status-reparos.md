# Status dos reparos — MeuCardio

Última atualização: 03/08/2026 23:18 (BRT)

## Estado geral

O repositório está sem warnings conhecidos e contém as correções de segurança, corpus, Painel, CorvIA Mail e CorvIA Chat. O trabalho atual é tornar o deploy do servidor tão verificável quanto a CI.

## Concluído e publicado na `main`

### Corpus científico e funções

- inventário certificado de **4.936 registros científicos**;
- preservação certificada de **1.327 arquivos físicos**;
- catálogo das 11 coleções com inventário, publicação e mínimos individuais;
- alertas quando qualquer coleção está abaixo do mínimo;
- total integral publicado no Painel;
- CorvIA Mail publicado em rota, menu e Painel;
- CorvIA Chat publicado em cartão, widget, HTTP e WebSocket.

### Segurança e compatibilidade

- sessão HttpOnly e revogação após troca de senha;
- PyJWT e separação de escopos app/e-mail;
- Passlib removido, bcrypt direto compatível com `$2a$`, `$2b$` e `$2y$`;
- hashes truncados bloqueados antes do binding nativo;
- ReportLab atualizado dentro da linha 4.x para compatibilidade com Python 3.14;
- receituário e documento genérico protegidos por geração real de PDF.

### Publicações e certificações recentes

- `2209d1e3` — PR #34: bcrypt direto; CI `30870119043`, 174 testes;
- `54ccee76` — PR #35: acervo, Mail e Chat; CI `30870366597`, 182 testes;
- `1bea10cf` — PR #36: ReportLab 4.4.10; CI `30870752333`, **186 testes e zero warnings**.

Todas as três certificações incluíram auditoria de dependências, migrations idempotentes, bootstrap, smoke HTTP, build frontend e backup/restauração PostgreSQL.

## Em andamento — deploy certificado

Branch: `agent/deploy-certifica-corpus`

Problemas encontrados no fluxo anterior:

- `deploy.sh` usava `app.services.importer`, que não reconciliava as 11 coleções;
- o script podia continuar mesmo sem o backend atingir readiness;
- não verificava o domínio HTTPS após subir os containers;
- não comprovava qual commit estava efetivamente publicado;
- o backup tinha caminho fixo `/opt/meucardio` e não produzia checksum.

Correções implementadas:

1. validação das variáveis críticas e do commit Git completo;
2. backup pré-deploy quando o banco já está em execução;
3. backup portátil, temporário/atômico, validado por `gzip -t` e acompanhado de SHA-256;
4. build e subida com remoção de serviços órfãos;
5. espera obrigatória por `/api/ready` interno;
6. migrations idempotentes explícitas;
7. execução obrigatória de:

   ```bash
   python -m app.commands.reconcile_content --publish-reviewed
   ```

8. proibição operacional de `--allow-partial` e remoção do importador antigo;
9. falha do deploy se qualquer coleção ficar abaixo do mínimo;
10. confirmação final de readiness interno e HTTPS público;
11. nova rota pública `/api/version`, contendo somente o SHA implantado;
12. injeção de `DEPLOY_COMMIT` pelo Docker Compose;
13. comparação entre `/api/version` e o commit local antes de declarar sucesso;
14. diagnóstico automático com estado e logs se alguma etapa falhar;
15. documentação de deploy e recuperação atualizada;
16. testes de sintaxe Bash, contratos operacionais e endpoint de versão.

Commits principais da branch:

- `c65f6588`: readiness e reconciliação integral;
- `40441e19`: backup portátil e verificável;
- `9d420e2e`: gates do deploy;
- `5f71e89c`: documentação operacional;
- `ef8e22df`: endpoint `/api/version`;
- `4a72f2cf`: SHA injetado no backend;
- `d3c5b0ab`: testes do endpoint de versão;
- `e892fd01`: confirmação pública do commit.

Próximos marcos:

- abrir PR do deploy certificado;
- executar CI integral;
- tratar revisão automática;
- publicar na `main` somente com CI verde.

## Bloqueio externo atual

O host anteriormente informado, `169.58.78.100`, recusou conexão SSH na porta 22 nesta sessão. Portanto ainda não foi possível:

- atualizar o checkout real;
- reconstruir os containers reais;
- reconciliar o PostgreSQL real;
- confirmar o SHA em `https://corvia.med.br/api/version`;
- validar visualmente Mail, Chat, corpus e WebSocket em produção;
- aplicar `vm.overcommit_memory=1` no host.

Nenhum dado do servidor real foi alterado nesta sessão.

## Próximas frentes após o deploy

1. reexecutar inventário científico após o merge;
2. validar a produção assim que o SSH voltar;
3. revisar upgrades maiores em PRs isolados;
4. manter CI integral e atualização deste arquivo após cada avanço verificável.

## Estado de publicação

- PRs #34, #35 e #36 publicados na `main`;
- deploy certificado em branch isolada, ainda sem merge;
- nenhum arquivo científico removido;
- nenhuma senha armazenada alterada;
- produção real ainda aguarda acesso ao servidor para receber a `main` certificada.
