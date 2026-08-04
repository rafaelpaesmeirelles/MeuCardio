# Status dos reparos — MeuCardio

Última atualização: 03/08/2026 23:42 (BRT)

## Estado geral

A `main` está sem warnings conhecidos e contém as correções de segurança, corpus, Painel, CorvIA Mail, CorvIA Chat e PDFs clínicos. O trabalho atual endurece o deploy, backup, restauração e reconciliação antes de aplicar essas versões no servidor real.

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
- ReportLab 4.4.10 compatível com Python 3.14;
- receituário e documento genérico protegidos por geração real de PDF.

### Publicações e certificações recentes

- `2209d1e3` — PR #34: bcrypt direto; CI `30870119043`, 174 testes;
- `54ccee76` — PR #35: acervo, Mail e Chat; CI `30870366597`, 182 testes;
- `1bea10cf` — PR #36: ReportLab; CI `30870752333`, **186 testes e zero warnings**.

As certificações incluíram auditoria de dependências, migrations idempotentes, bootstrap, smoke HTTP, build frontend e backup/restauração PostgreSQL.

## Em andamento — PR #37: deploy certificado

Branch: `agent/deploy-certifica-corpus`

### Problemas encontrados no fluxo antigo

- importador parcial em vez do reconciliador das 11 coleções;
- continuação possível sem readiness;
- ausência de verificação HTTPS e do commit publicado;
- backup sem integrar o deploy;
- banco parado podia ser alterado sem backup;
- restaurador não aceitava o novo dump custom;
- reconciliador podia ignorar arquivos e ainda aprovar pelo total histórico;
- falhas pós-start nem sempre exibiam estado e logs.

### Correções implementadas

1. validação de variáveis críticas, ferramentas do host e SHA Git completo;
2. recusa de checkout com modificações ou arquivos não versionados;
3. detecção de banco persistente por container parado **ou** volume `pgdata` preservado;
4. início exclusivo do PostgreSQL antes do backup, sem backend ou migrations;
5. backup custom do PostgreSQL com:
   - arquivo temporário e publicação atômica;
   - compressão nativa do `pg_dump`;
   - `pg_restore --list` antes da publicação;
   - permissões `0600`;
   - SHA-256 portátil;
6. restaurador compatível com `.dump` atual e `.sql.gz` legado;
7. checksum e catálogo validados **antes** de apagar o banco;
8. confirmação destrutiva em duas etapas;
9. restauração custom com `pg_restore --exit-on-error`;
10. backend mantido parado se a restauração falhar;
11. readiness obrigatório após a restauração;
12. build com remoção de serviços órfãos;
13. readiness interno obrigatório antes de migrations e reconciliação;
14. migrations idempotentes explícitas;
15. execução obrigatória de:

   ```bash
   python -m app.commands.reconcile_content --publish-reviewed
   ```

16. remoção do importador parcial e ausência de `--allow-partial` no deploy;
17. reconciliador em modo fail-closed para:
   - `falhas`;
   - `duplicados_ignorados`;
   - `avisos` de itens pulados;
   - recusados, ausências e demais diagnósticos equivalentes;
18. diagnóstico recursivo, inclusive quando o carregador agrupa resultados;
19. verificação dos mínimos individuais das 11 coleções;
20. confirmação final de readiness interno e HTTPS público;
21. `/api/version` com somente o SHA implantado;
22. comparação do SHA público com o commit local;
23. handler `ERR` para mostrar estado e logs em qualquer falha pós-start;
24. testes de sintaxe Bash, contratos operacionais, restauração, diagnósticos do corpus e endpoint de versão.

### Revisão automática

Apontamentos do Codex já tratados:

- checkout sujo certificado como SHA conhecido;
- falha do reconciliador sem diagnóstico;
- restaurador incompatível com dump custom;
- banco persistente parado sem backup;
- arquivos ignorados mascarados por registros históricos.

A CI final será reiniciada sobre essas correções antes do merge.

## Bloqueio externo atual

O host anteriormente informado, `169.58.78.100`, recusou conexão SSH na porta 22 nesta sessão. Portanto ainda não foi possível:

- atualizar o checkout real;
- criar o backup real;
- reconstruir os containers;
- reconciliar o PostgreSQL real;
- confirmar o SHA em `https://corvia.med.br/api/version`;
- validar visualmente Mail, Chat, corpus e WebSocket em produção;
- aplicar `vm.overcommit_memory=1` no host.

A consulta pública automatizada ao domínio também foi inconclusiva; ela não deve ser interpretada como prova de indisponibilidade.

## Próximos marcos

1. concluir CI e revisão do PR #37;
2. publicar o deploy certificado na `main`;
3. reexecutar inventário científico após o merge;
4. aplicar a `main` no servidor assim que o SSH voltar;
5. validar a produção com `/api/version`, catálogo, Mail, Chat e WebSocket;
6. retomar upgrades maiores em PRs isolados.

## Estado de publicação

- PRs #34, #35 e #36 publicados na `main`;
- PR #37 aberto e em nova certificação;
- nenhum arquivo científico removido;
- nenhuma senha armazenada alterada;
- nenhum dado do servidor real alterado nesta sessão.
