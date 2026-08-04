# Status dos reparos — MeuCardio

Última atualização: 03/08/2026 22:19 (BRT)

## Visão geral

O trabalho de correção, consolidação e publicação do MeuCardio está em andamento contínuo. Este arquivo registra o estado real do repositório, o que já foi concluído e o que ainda falta executar.

## Concluído e publicado na `main`

### Biblioteca científica e preservação de conteúdo

- Inventário completo do corpus científico.
- Preservação confirmada de **4.936 registros científicos**.
- Preservação confirmada de **1.327 arquivos físicos**.
- Correção da biblioteca que mostrava apenas os primeiros 50 documentos.
- Paginação da biblioteca implementada.
- Catálogo consolidado das 11 frentes científicas implementado.
- Reconciliação do corpus científico com PostgreSQL validada.
- Proteções automáticas para impedir redução silenciosa do corpus.

### Funcionalidades e arquitetura

- Auditoria funcional das rotas e recursos publicados.
- Preservação de **48 páginas frontend**.
- Preservação de **31 destinos de navegação**.
- Preservação de **38 routers FastAPI**.
- Carregamento lazy por rota implementado.
- Orçamento de bundle e cache PWA implementado.
- Renderização segura de Mermaid, snippets de busca e conteúdo externo de e-mail.

### Segurança e autenticação

- Sessão via cookie HttpOnly implementada para navegador.
- Revogação de sessões após troca de senha implementada.
- Separação de escopos de token entre aplicação e CorvIA Mail.
- Validação de origem e rate limiting com Redis.
- Migração para PyJWT.
- Auditorias automáticas de dependências Python e Node.

### Operação, banco e infraestrutura

- Migrations Alembic consolidadas e idempotentes.
- Smoke test HTTP de release implementado.
- Backup e restauração PostgreSQL comprovados em CI.
- GitHub Actions atualizadas para versões v7.
- Preflight de host Redis publicado.
- Validação de `vm.overcommit_memory=1` documentada e testada.
- Script do Redis é somente leitura e não executa `sudo`.

### Compatibilidade técnica

- Migração de `Settings.Config` para `SettingsConfigDict`.
- Compatibilidade do TestClient com HTTPX2 somente em ambiente de testes.
- Gate AST que impede retorno de configuração Pydantic class-based.
- Warning legado do Pydantic eliminado.
- Warning legado do TestClient Starlette/HTTPX eliminado.
- Suíte atual certificada com **168 testes backend aprovados**.

### Commits publicados mais recentes

- `4856db20`: preflight Redis e documentação operacional.
- `55c363da`: compatibilidade Pydantic e HTTPX2.
- `114fd965`: criação deste acompanhamento contínuo dos reparos.

## Em andamento

### Substituição segura do Passlib

Objetivo atual: eliminar a dependência do `passlib`, que importa o módulo `crypt`, previsto para remoção no Python 3.13.

Requisitos obrigatórios desta etapa:

- manter compatibilidade com todos os hashes bcrypt já armazenados;
- não invalidar senhas existentes;
- preservar `hash_password()` e `verify_password()` como contrato interno;
- criar testes com hashes antigos e novos;
- executar auditoria, migrations, 168+ testes, smoke HTTP e backup/restauração;
- publicar somente após CI integralmente verde.

Estado atual:

- execução iniciada em 03/08/2026 às 22:19 BRT;
- branch isolada criada: `agent/substitui-passlib-bcrypt`;
- código atual localizado em `backend/app/core/security.py`;
- uso atual confirmado: `CryptContext(schemes=["bcrypt"], deprecated="auto")`;
- dependências atuais confirmadas: `passlib[bcrypt]==1.7.4` e `bcrypt==4.0.1`;
- estratégia em validação: usar diretamente a biblioteca `bcrypt`, sem regravar hashes existentes;
- implementação e testes ainda não publicados em PR;
- nenhuma alteração de senha ou banco realizada.

## Pendente

### Prioridade alta

1. Substituir Passlib mantendo compatibilidade com bcrypt existente.
2. Eliminar warning do ReportLab relacionado a `ast.NameConstant` e Python 3.14.
3. Reexecutar certificação funcional completa após cada mudança.
4. Confirmar novamente inventário científico após novos merges.

### Prioridade média

5. Revisar atualizações maiores de dependências que foram adiadas por risco:
   - React Router 7;
   - React 19;
   - vite-plugin-pwa major;
   - Stripe major;
   - ReportLab major;
   - bcrypt major;
   - Capacitor major;
   - markdown-it major.
6. Tratar cada upgrade em PR isolado com testes específicos.
7. Revisar documentação operacional final de deploy.

### Dependência externa ao repositório

- Aplicar `vm.overcommit_memory=1` no servidor real exige acesso administrativo ao host Linux.
- O repositório já contém verificação e instruções seguras, mas o servidor real não foi alterado por este processo.

## Estado de publicação

- Correções funcionais publicadas na `main` até `55c363da`.
- Acompanhamento documental publicado na `main` até `114fd965`.
- A correção do Passlib está em branch isolada e ainda não foi integrada.
- Nenhum deploy adicional ao servidor foi executado nesta etapa.
- Nenhum arquivo científico foi removido nas correções recentes.
- O acompanhamento continuará sendo atualizado neste arquivo a cada etapa relevante.
