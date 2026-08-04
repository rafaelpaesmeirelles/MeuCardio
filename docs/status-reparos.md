# Status dos reparos — MeuCardio

Última atualização: 04/08/2026 00:12 (BRT)

## Estado geral

A `main` contém as correções de segurança, corpus, Painel, CorvIA Mail, CorvIA Chat e PDFs clínicos, sem warnings conhecidos. O PR #37 torna o deploy, backup, restauração, build e reconciliação verificáveis antes da publicação no servidor real.

## Concluído e publicado na `main`

- inventário certificado de **4.936 registros científicos** e **1.327 arquivos físicos**;
- catálogo das 11 coleções, total integral no Painel e alertas por coleção;
- CorvIA Mail em rota, menu e Painel;
- CorvIA Chat em cartão, widget, HTTP e WebSocket;
- sessão HttpOnly, PyJWT e revogação após troca de senha;
- Passlib substituído por bcrypt direto compatível com hashes existentes;
- ReportLab 4.4.10 e geração real de PDFs clínicos.

### Publicações recentes

- `2209d1e3` — PR #34: bcrypt direto; 174 testes;
- `54ccee76` — PR #35: acervo, Mail e Chat; 182 testes;
- `1bea10cf` — PR #36: ReportLab; 186 testes e zero warnings.

## Em andamento — PR #37: operação certificada

### Deploy e identificação

- valida variáveis, ferramentas, SHA completo e checkout limpo;
- exclui artefatos locais ignorados dos contextos Docker;
- frontend copia `package-lock.json` e usa `npm ci`;
- mesmo commit produz o mesmo grafo de dependências frontend;
- detecta banco persistente por container ou volume `pgdata`;
- erro de Docker/Compose nunca é reinterpretado como primeiro deploy;
- cria backup antes de migrations ou subida do backend;
- exige readiness, migrations idempotentes, reconciliação e HTTPS;
- publica `/api/version` e compara o SHA público com o commit local;
- mostra estado e logs para qualquer falha pós-start.

### Backup e restauração

- dump custom, temporário/atômico, validado por `pg_restore --list`;
- SHA-256 vinculado ao nome e conteúdo do dump escolhido;
- compatibilidade com `.sql.gz` legado;
- confirmação destrutiva em duas etapas;
- backend existente deve parar antes de `dropdb`;
- se o backend for religado e não atingir readiness, o handler tenta pará-lo novamente;
- falha de restauração não é declarada como sucesso e exige intervenção operacional.

### Reconciliação científica

- comando obrigatório: `python -m app.commands.reconcile_content --publish-reviewed`;
- ausência de `--allow-partial` no deploy;
- fail-closed para falhas, avisos, duplicados, recusados, ausências e Markdown vazio;
- diagnósticos pesquisados recursivamente;
- manifestos JSON devem ser listas de objetos com slug válido;
- slugs duplicados bloqueiam antes de qualquer upsert;
- quantidade de itens-fonte fica visível no resultado;
- mínimos individuais das 11 coleções permanecem obrigatórios.

### Certificações já obtidas na branch

- reconciliação real aprovada repetidamente com **4.936 registros**;
- CI anterior aprovada com **216 testes**, auditorias, migrations, smoke HTTP, frontend e backup/restauração;
- as últimas proteções de determinismo e fail-closed estão em nova certificação.

### Revisão automática

Foram tratados todos os riscos apontados até o momento, incluindo:

- checkout sujo e artefatos ignorados certificados como SHA conhecido;
- dependências frontend resolvidas sem lockfile;
- banco persistente parado sem backup;
- erro de Docker mascarado como primeiro deploy;
- backend ativo durante restauração ou não pronto após religamento;
- checksum de outro dump;
- restaurador incompatível com dump custom;
- conteúdo recusado, vazio ou com slug duplicado certificado pelo total histórico.

## Bloqueio externo atual

O ambiente desta sessão não resolve `corvia.med.br`, e o IP anteriormente informado (`169.58.78.100`) não aceitou conexões nas portas 22, 80 ou 443. As credenciais fornecidas para validação não foram usadas.

Ainda dependem do acesso ao host:

- backup e deploy reais;
- reconciliação do PostgreSQL real;
- confirmação de `/api/version`;
- validação autenticada do Painel, Biblioteca, CorvIA Mail, CorvIA Chat e WebSocket;
- aplicação de `vm.overcommit_memory=1`.

## Próximos marcos

1. concluir CI, reconciliação e revisão do head final;
2. resolver as threads corrigidas e publicar o PR #37 na `main`;
3. reexecutar inventário após o merge;
4. aplicar e validar a `main` assim que o host voltar acessível;
5. retomar upgrades maiores em PRs isolados.

## Estado de publicação

- PRs #34, #35 e #36 publicados;
- PR #37 em certificação final;
- nenhum arquivo científico removido;
- nenhuma senha armazenada alterada;
- nenhum dado do servidor real alterado nesta sessão.
