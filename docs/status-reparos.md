# Status dos reparos — MeuCardio

Última atualização: 03/08/2026 22:42 (BRT)

## Visão geral

O trabalho de correção, consolidação e publicação do MeuCardio está em andamento contínuo. Este arquivo registra o estado verificável do repositório, as correções concluídas, as frentes abertas e o que depende do servidor real.

## Concluído e publicado na `main`

### Biblioteca científica e preservação de conteúdo

- Inventário completo do corpus científico.
- Preservação confirmada de **4.936 registros científicos**.
- Preservação confirmada de **1.327 arquivos físicos**.
- Correção da biblioteca que mostrava apenas os primeiros 50 documentos.
- Paginação da biblioteca implementada.
- Catálogo consolidado das 11 frentes científicas implementado.
- Reconciliação idempotente do corpus com PostgreSQL publicada.
- Proteções automáticas para impedir redução silenciosa do corpus.

### Funcionalidades e arquitetura

- Auditoria funcional das rotas e recursos publicados.
- Preservação de **48 páginas frontend**.
- Preservação de **31 destinos de navegação**.
- Preservação de **38 routers FastAPI**.
- Carregamento lazy por rota implementado.
- Orçamento de bundle e cache PWA implementado.
- CorvIA Mail implementado em rota, menu lateral e painel.
- CorvIA Chat implementado com mensagens HTTP, WebSocket, histórico, não lidas, busca de usuários e widget flutuante.

### Segurança, testes e operação

- Sessão via cookie HttpOnly implementada para navegador.
- Revogação de sessões após troca de senha implementada.
- Separação de escopos de token entre aplicação e CorvIA Mail.
- Migrations Alembic consolidadas e idempotentes.
- Smoke test HTTP de release implementado.
- Backup e restauração PostgreSQL comprovados em CI.
- GitHub Actions atualizadas para versões v7.
- Suíte publicada certificada com **168 testes backend aprovados**.

### Commits publicados mais recentes

- `4856db20`: preflight Redis e documentação operacional.
- `55c363da`: compatibilidade Pydantic e HTTPX2.
- `114fd965`: criação deste acompanhamento contínuo.

## Em andamento

### PR #34 — substituição segura do Passlib

Branch: `agent/substitui-passlib-bcrypt`

Implementado:

- remoção de `passlib[bcrypt]==1.7.4`;
- uso direto de `bcrypt==4.0.1`;
- preservação dos contratos `hash_password()` e `verify_password()`;
- novos hashes com custo 12;
- compatibilidade coberta para `$2a$`, `$2b$` e `$2y$`;
- comportamento histórico de 72 bytes documentado;
- nenhuma senha ou linha do banco alterada;
- gate contra reintrodução da dependência.

Situação:

- PR #34 aberto;
- primeira CI falhou porque o teste encontrou o nome da dependência dentro de um comentário;
- apontamento P1 do Codex corrigido em `f46a9bfa`;
- nova CI pendente/em execução;
- merge somente após certificação integral verde.

### Correção do painel, acervo e comunicação

Branch: `agent/corrige-painel-acervo-comunicacao`

Relato de produção recebido em 03/08/2026:

- número de itens inferior ao inventário real;
- CorvIA Mail não visível no painel publicado;
- mensagens entre usuários sem acesso explícito no painel.

Diagnóstico confirmado:

- o Painel somava `/library/themes`, portanto mostrava somente registros da tabela `Document`;
- `/api/library/catalog` já era a fonte canônica das 11 coleções;
- CorvIA Mail e CorvIA Chat já existem na `main` atual;
- a ausência deles no site indica frontend/build de produção anterior à `main` atual ou ativos não atualizados;
- o banco de produção pode ainda precisar da reconciliação oficial do corpus.

Implementado na branch:

- total principal do Painel passou a usar `/library/catalog`;
- rótulo alterado para **itens científicos**, evitando chamar todas as coleções de documentos;
- API do catálogo agora expõe baseline mínimo de **4.936**, expectativa de **1.327 arquivos físicos**, déficit e estado de integridade;
- Painel exibe alerta administrativo quando o banco está abaixo do baseline;
- Biblioteca exibe alerta de integridade quando o corpus está incompleto;
- novo grupo **Comunicação profissional** no Painel;
- cartão acionável para abrir o CorvIA Chat;
- cartão explícito para CorvIA Mail;
- gates automatizados impedem retorno da soma parcial por temas ou ocultação de Mail/Chat;
- baseline do catálogo testado contra o comando oficial `app.commands.reconcile_content`.

Commits principais desta branch:

- `c587dfe9`: integridade no catálogo;
- `6c7b01bb`: total canônico e comunicação no Painel;
- `6cfade57`: alerta de integridade na Biblioteca;
- `bc37bab9`: alinhamento com o reconciliador;
- `ab927204`: gates de visibilidade e integridade.

Próximo marco:

- abrir PR da correção do painel;
- executar CI integral;
- tratar revisão automática;
- publicar na `main` após certificação verde.

## Pendências organizadas

### Prioridade crítica

1. Finalizar CI e revisão do PR #34.
2. Abrir e certificar o PR do painel/acervo/comunicação.
3. Confirmar qual commit está implantado no servidor real.
4. Recriar frontend e reiniciar a aplicação com a `main` certificada.
5. Executar no servidor real:

   ```bash
   python -m app.commands.reconcile_content --publish-reviewed
   ```

6. Confirmar na produção que o catálogo retorna pelo menos 4.936 itens.
7. Confirmar visualmente CorvIA Mail, CorvIA Chat e o novo total do acervo.

### Prioridade alta

8. Eliminar warning do ReportLab relacionado a `ast.NameConstant` e Python 3.14.
9. Reexecutar inventário científico após cada merge relevante.
10. Manter smoke HTTP, backup/restauração e testes integrais obrigatórios.

### Prioridade média

11. Revisar upgrades maiores isoladamente: React Router, React, PWA, Stripe, ReportLab, bcrypt, Capacitor e markdown-it.
12. Revisar documentação operacional final do deploy.

## Dependências externas ao repositório

As seguintes ações exigem acesso administrativo ao host ou à plataforma de deploy:

- identificar o commit efetivamente implantado;
- executar `git pull`/checkout da `main` certificada;
- reconstruir containers ou bundle frontend;
- executar a reconciliação contra o PostgreSQL real;
- reiniciar serviços;
- aplicar `vm.overcommit_memory=1` no host;
- validar domínio, TLS, WebSocket e CorvIA Mail em produção.

O repositório contém o comando seguro e idempotente de reconciliação, mas nenhuma alteração do banco real ou deploy do servidor foi executada nesta sessão.

## Estado de publicação

- PR #34 aberto e em recertificação.
- Correção do painel/acervo/comunicação implementada em branch isolada e ainda sem merge.
- Nenhum arquivo científico foi removido.
- Nenhuma senha armazenada foi alterada.
- A produção ainda precisa ser confrontada com os commits certificados e reconciliada no servidor real.
