# Status dos reparos — MeuCardio

Última atualização: 03/08/2026 22:58 (BRT)

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
- Passlib removido e substituído por bcrypt direto, preservando hashes existentes `$2a$`, `$2b$` e `$2y$`.
- Validação estrutural impede que hash bcrypt truncado alcance o binding nativo.
- Migrations Alembic consolidadas e idempotentes.
- Smoke test HTTP de release implementado.
- Backup e restauração PostgreSQL comprovados em CI.
- GitHub Actions atualizadas para versões v7.
- Suíte publicada certificada com **174 testes backend aprovados**.

### Commits publicados mais recentes

- `55c363da`: compatibilidade Pydantic e HTTPX2.
- `114fd965`: criação deste acompanhamento contínuo.
- `2209d1e3`: substituição segura do Passlib por bcrypt direto — PR #34.

### Certificação do PR #34

- CI `30870119043` integralmente verde;
- 174 testes backend aprovados;
- `pip-audit` sem vulnerabilidades conhecidas;
- migrations completas e idempotentes;
- bootstrap administrativo aprovado;
- smoke HTTP de health, readiness, sessão HttpOnly e logout aprovado;
- backup e restauração PostgreSQL aprovados;
- frontend, segurança, divisão por rota, build e orçamentos PWA aprovados;
- warning Passlib/`crypt` eliminado;
- único warning atual: ReportLab/`ast.NameConstant`.

## Em andamento

### PR #35 — painel, acervo e comunicação

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
- `total` representa o inventário integral preservado nas 11 coleções;
- `published_total` informa separadamente o conteúdo liberado aos assinantes;
- itens em revisão permanecem preservados e não são publicados indevidamente;
- integridade é calculada com registros armazenados, não somente publicados;
- cada coleção é comparada ao seu mínimo oficial do reconciliador;
- excedente numa coleção não pode mascarar déficit em outra;
- API expõe baseline de **4.936**, expectativa de **1.327 arquivos físicos**, déficit total e frentes abaixo do mínimo;
- Painel e Biblioteca exibem alerta quando o corpus está incompleto;
- novo grupo **Comunicação profissional** no Painel;
- cartão acionável para abrir o CorvIA Chat;
- cartão explícito para CorvIA Mail;
- gates automatizados impedem retorno da soma parcial por temas ou ocultação de Mail/Chat;
- testes cobrem 3 publicados + 1 preservado em revisão;
- teste específico comprova que excedente em documentos não mascara falta em emergência.

Revisão automática:

- P1 sobre integridade calculada apenas com publicados: corrigido;
- P1 sobre validação apenas pelo agregado: corrigido com mínimos individuais por coleção;
- nova CI foi disparada após o merge do PR #34 para certificar a combinação real da `main` sem Passlib.

Próximo marco:

- concluir CI integral do PR #35;
- resolver os threads obsoletos do Codex;
- publicar na `main` após certificação verde;
- retomar a frente ReportLab/Python 3.14.

## Pendências organizadas

### Prioridade crítica

1. Finalizar CI e revisão do PR #35.
2. Confirmar qual commit está implantado no servidor real.
3. Recriar frontend e reiniciar a aplicação com a `main` certificada.
4. Executar no servidor real:

   ```bash
   python -m app.commands.reconcile_content --publish-reviewed
   ```

5. Confirmar na produção inventário de pelo menos 4.936 registros e os mínimos de cada coleção.
6. Confirmar visualmente CorvIA Mail, CorvIA Chat e o novo total do acervo.

### Prioridade alta

7. Eliminar warning do ReportLab relacionado a `ast.NameConstant` e Python 3.14.
8. Reexecutar inventário científico após cada merge relevante.
9. Manter smoke HTTP, backup/restauração e testes integrais obrigatórios.

### Prioridade média

10. Revisar upgrades maiores isoladamente: React Router, React, PWA, Stripe, ReportLab, bcrypt, Capacitor e markdown-it.
11. Revisar documentação operacional final do deploy.

## Dependências externas ao repositório

As seguintes ações exigem acesso administrativo ao host ou à plataforma de deploy:

- identificar o commit efetivamente implantado;
- executar checkout da `main` certificada;
- reconstruir containers ou bundle frontend;
- executar a reconciliação contra o PostgreSQL real;
- reiniciar serviços;
- aplicar `vm.overcommit_memory=1` no host;
- validar domínio, TLS, WebSocket e CorvIA Mail em produção.

O host anteriormente informado, `169.58.78.100`, recusou conexão na porta 22 nesta sessão. Nenhuma alteração do banco real ou deploy do servidor foi executada.

## Estado de publicação

- PR #34 publicado na `main` como `2209d1e3`.
- PR #35 aberto e em certificação sobre a nova `main`.
- Nenhum arquivo científico foi removido.
- Nenhuma senha armazenada foi alterada.
- A produção ainda precisa ser confrontada com os commits certificados e reconciliada no servidor real.
