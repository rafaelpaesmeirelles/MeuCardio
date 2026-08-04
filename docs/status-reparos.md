# Status dos reparos — MeuCardio

Última atualização: 04/08/2026 00:03 (BRT)

## Estado geral

A `main` contém as correções de segurança, corpus, Painel, CorvIA Mail, CorvIA Chat e PDFs clínicos, sem warnings conhecidos. O PR #37 endurece o deploy, backup, restauração e reconciliação antes de aplicar essas versões no servidor real.

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

### Publicações recentes

- `2209d1e3` — PR #34: bcrypt direto; CI `30870119043`, 174 testes;
- `54ccee76` — PR #35: acervo, Mail e Chat; CI `30870366597`, 182 testes;
- `1bea10cf` — PR #36: ReportLab; CI `30870752333`, **186 testes e zero warnings**.

## Em andamento — PR #37: deploy certificado

Branch: `agent/deploy-certifica-corpus`

### Proteções implementadas

1. validação de variáveis críticas, ferramentas do host, SHA Git completo e checkout limpo;
2. `.dockerignore` nos contextos frontend/backend para excluir artefatos locais ignorados;
3. detecção fail-closed de banco persistente por container ativo/parado ou volume `pgdata`;
4. erro de Docker/Compose nunca é interpretado como “primeiro deploy”;
5. início exclusivo do PostgreSQL antes do backup, sem backend ou migrations;
6. backup custom com arquivo temporário, compressão nativa, `pg_restore --list`, permissões `0600` e SHA-256;
7. restaurador compatível com `.dump` atual e `.sql.gz` legado;
8. checksum vinculado ao nome e conteúdo do dump selecionado;
9. checksum e catálogo validados antes de qualquer operação destrutiva;
10. confirmação destrutiva em duas etapas;
11. backend existente deve ser parado com sucesso antes de `dropdb`;
12. falha de restauração mantém o backend parado;
13. readiness obrigatório após a restauração;
14. build com remoção de serviços órfãos;
15. readiness interno obrigatório antes de migrations e reconciliação;
16. migrations idempotentes explícitas;
17. execução obrigatória de:

   ```bash
   python -m app.commands.reconcile_content --publish-reviewed
   ```

18. ausência do importador parcial e de `--allow-partial` no deploy;
19. reconciliador fail-closed para falhas, duplicados, avisos, recusados, ausências e Markdown vazio;
20. diagnósticos bloqueantes pesquisados recursivamente;
21. mínimos individuais das 11 coleções;
22. `/api/version` com somente o SHA implantado;
23. comparação do SHA público com o commit local;
24. handler `ERR` para estado e logs em qualquer falha pós-start;
25. testes de sintaxe Bash, deploy, backup, restauração, Docker contexts, conteúdo e endpoint de versão.

### Certificações já obtidas nesta branch

- reconciliação real fail-closed aprovada com **4.936 registros** nas 11 coleções;
- CI `30873219782` aprovada com **216 testes**, auditorias, migrations, smoke HTTP, frontend e backup/restauração;
- após essa CI, a detecção de banco persistente foi endurecida para não ocultar erro do Docker; uma certificação final foi disparada no mesmo PR.

### Revisão automática

Todos os riscos apontados até aqui foram tratados:

- checkout sujo certificado como SHA conhecido;
- artefatos locais ignorados entrando na imagem;
- falha pós-start sem diagnóstico;
- banco persistente parado sem backup;
- restaurador incompatível com dump custom;
- backend não parado antes da restauração;
- checksum pertencente a outro dump;
- arquivos ignorados ou Markdown vazio mascarados por registros históricos.

## Bloqueio externo atual

O ambiente desta sessão não resolve `corvia.med.br`, e o IP anteriormente informado (`169.58.78.100`) não aceitou conexões nas portas 22, 80 ou 443. Portanto ainda não foi possível:

- atualizar o checkout real;
- criar o backup real;
- reconstruir os containers;
- reconciliar o PostgreSQL real;
- confirmar o SHA em `/api/version`;
- validar com login o Painel, Biblioteca, CorvIA Mail, CorvIA Chat e WebSocket;
- aplicar `vm.overcommit_memory=1` no host.

As credenciais fornecidas para validação não foram usadas, porque o host permaneceu inacessível.

## Próximos marcos

1. concluir a certificação final do PR #37;
2. resolver as threads de revisão já corrigidas;
3. publicar o PR #37 na `main`;
4. reexecutar inventário científico após o merge;
5. aplicar a `main` e validar a produção assim que a rede/SSH voltar;
6. retomar upgrades maiores em PRs isolados.

## Estado de publicação

- PRs #34, #35 e #36 publicados na `main`;
- PR #37 aberto e em certificação final;
- nenhum arquivo científico removido;
- nenhuma senha armazenada alterada;
- nenhum dado do servidor real alterado nesta sessão.
