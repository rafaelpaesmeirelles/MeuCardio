# Status dos reparos — MeuCardio

Última atualização: 03/08/2026 23:05 (BRT)

## Visão geral

O trabalho de correção, consolidação e publicação do MeuCardio segue em andamento contínuo. Este arquivo registra apenas avanços verificáveis, resultados de CI, publicações e bloqueios externos.

## Concluído e publicado na `main`

### Corpus científico e biblioteca

- Inventário certificado de **4.936 registros científicos**.
- Preservação certificada de **1.327 arquivos físicos**.
- Paginação da biblioteca implementada.
- Catálogo consolidado das 11 frentes científicas.
- Reconciliação idempotente do corpus com PostgreSQL.
- Proteções automáticas contra redução silenciosa.
- Total do Painel corrigido para o inventário integral das 11 coleções.
- Separação explícita entre registros preservados e conteúdo publicado.
- Integridade verificada pelos mínimos individuais de cada coleção.
- Excedente numa frente não mascara déficit em outra.
- Alertas de integridade publicados no Painel administrativo e na Biblioteca.

### Painel e comunicação

- CorvIA Mail publicado em rota, navegação e cartão explícito no Painel.
- CorvIA Chat publicado com cartão acionável no Painel, widget flutuante, mensagens HTTP, WebSocket, histórico, busca de usuários e não lidas.
- Grupo **Comunicação profissional** publicado no Painel.

### Segurança e compatibilidade

- Sessão de navegador via cookie HttpOnly.
- Revogação de sessões após troca de senha.
- Separação dos escopos da aplicação e do CorvIA Mail.
- Migração para PyJWT.
- Passlib removido e substituído por bcrypt direto.
- Compatibilidade preservada com hashes `$2a$`, `$2b$` e `$2y$`.
- Validação estrutural impede que hash bcrypt truncado alcance o binding nativo.
- Warning Passlib/`crypt` eliminado.

### Operação e certificação

- Migrations Alembic completas e idempotentes.
- Bootstrap administrativo testado.
- Smoke HTTP de health, readiness, sessão HttpOnly e logout.
- Backup e restauração PostgreSQL comprovados em CI.
- Auditorias Python e Node sem vulnerabilidades conhecidas.
- Build, divisão por rota, segurança de renderização e orçamentos PWA certificados.

### Publicações recentes

- `2209d1e3`: substituição segura do Passlib por bcrypt direto — PR #34.
- `54ccee76`: total canônico do acervo e acessos de comunicação — PR #35.

### Certificação do PR #35

- CI `30870366597` integralmente verde.
- **182 testes backend aprovados**.
- `pip-audit` sem vulnerabilidades conhecidas.
- migrations e idempotência aprovadas.
- bootstrap administrativo aprovado.
- smoke HTTP aprovado.
- backup e restauração aprovados.
- frontend integralmente aprovado.
- único warning remanescente após essa publicação: ReportLab/`ast.NameConstant`.

## Em andamento

### Compatibilidade ReportLab com Python 3.14

Branch: `agent/reportlab-python314-compat`

Objetivo:

- eliminar o último warning da suíte;
- manter a geração de receituário, atestado e laudo;
- evitar o salto major para ReportLab 5;
- preservar a stack Python pura e os layouts clínicos existentes.

Implementado:

- `reportlab==4.2.5` atualizado para `reportlab==4.4.10`;
- permanência na linha 4.x;
- versão escolhida declara suporte a Python 3.14;
- teste em processo Python limpo transforma `DeprecationWarning` em erro e importa `reportlab.lib.rl_safe_eval`;
- teste exige versão exata 4.4.10;
- teste gera receituário comum real e valida assinatura estrutural do PDF;
- teste gera documento genérico real e valida assinatura estrutural do PDF.

Commits atuais:

- `cb66e511`: atualização da dependência;
- `426bc1c7`: testes de compatibilidade e geração de PDFs.

Próximos marcos:

1. abrir PR da atualização;
2. executar CI integral;
3. confirmar ausência completa de warnings;
4. tratar eventual revisão automática;
5. publicar na `main` após certificação verde.

## Dependências externas ao repositório

As seguintes ações continuam exigindo acesso administrativo ao servidor real ou à plataforma de deploy:

- identificar o commit efetivamente implantado;
- atualizar o checkout para a `main` certificada;
- reconstruir containers e bundle frontend;
- executar migrations;
- executar:

  ```bash
  python -m app.commands.reconcile_content --publish-reviewed
  ```

- reiniciar serviços;
- confirmar pelo menos 4.936 registros e os mínimos individuais das 11 coleções;
- validar visualmente CorvIA Mail, CorvIA Chat e o total do Painel;
- validar WebSocket, domínio e TLS;
- aplicar `vm.overcommit_memory=1` no host.

O host anteriormente informado, `169.58.78.100`, recusou conexão na porta 22 nesta sessão. Nenhuma alteração do PostgreSQL real ou deploy do servidor foi executada.

## Pendências após o ReportLab

1. Reexecutar inventário científico após o merge.
2. Revisar documentação operacional final de deploy.
3. Tratar upgrades maiores em PRs isolados, começando pelos de menor risco e maior benefício.
4. Manter CI integral obrigatória para cada alteração.

## Estado de publicação

- PRs #34 e #35 publicados na `main`.
- Atualização do ReportLab em branch isolada, ainda sem merge.
- Nenhum arquivo científico foi removido.
- Nenhuma senha armazenada foi alterada.
- A produção real ainda precisa receber e validar a `main` certificada.
