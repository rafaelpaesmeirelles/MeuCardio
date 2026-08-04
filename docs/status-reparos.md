# Status dos reparos — CorvIA / MeuCardio

Última atualização: 04/08/2026 (BRT)

## Resumo executivo

As correções planejadas no repositório foram concluídas e publicadas na `main` pelos PRs #34, #35, #36, #37 e #38.

A `main` atual contém:

- autenticação bcrypt sem Passlib;
- biblioteca e Painel com inventário canônico das 11 coleções;
- CorvIA Mail e CorvIA Chat expostos no Painel;
- ReportLab compatível com Python 3.14 e suíte sem warnings conhecidos;
- deploy determinístico em duas fases;
- backup, restauração e rollback automático;
- identificação pública do commit implantado;
- reconciliação científica fail-closed;
- uma única regra de slug usada pelo importador direto e pelo reconciliador.

O trabalho pendente agora depende do acesso ao servidor real: implantar a `main`, reconciliar o PostgreSQL de produção e validar o site autenticado.

Nenhuma credencial, senha ou dado do servidor foi gravado no repositório, em commits, PRs, documentação ou logs criados neste trabalho.

## Publicações concluídas

### PR #34 — bcrypt direto

Commit:

```text
2209d1e3
```

- Passlib removido;
- compatibilidade preservada com hashes `$2a$`, `$2b$` e `$2y$`;
- hashes truncados ou malformados rejeitados antes do binding nativo;
- nenhuma senha armazenada alterada;
- CI verde com **174 testes backend**.

### PR #35 — acervo, CorvIA Mail e CorvIA Chat

Commit:

```text
54ccee76
```

- Painel passou a usar o inventário integral das 11 coleções;
- registros preservados e conteúdo publicado são apresentados separadamente;
- mínimos individuais impedem que excedente numa coleção esconda déficit em outra;
- alertas de integridade publicados no Painel e na Biblioteca;
- CorvIA Mail publicado em rota, menu e Painel;
- CorvIA Chat publicado em cartão, widget, HTTP e WebSocket;
- CI verde com **182 testes backend**.

### PR #36 — ReportLab e Python 3.14

Commit:

```text
1bea10cf
```

- ReportLab atualizado para 4.4.10, sem salto para a linha major 5;
- warning de `ast.NameConstant` eliminado;
- receituário e documento clínico protegidos por geração real de PDF;
- CI verde com **186 testes backend e zero warnings**.

### PR #37 — deploy, corpus e commit publicado

Commit de merge:

```text
d7a4589d2135e368dbcf1743369f60a1a8fa4acd
```

Certificação funcional principal:

- CI #204 — run `30875803741`;
- **233 testes backend aprovados**;
- Corpus database reconciliation #80 — run `30875803765`;
- **4.936 registros científicos** confirmados nas 11 coleções;
- frontend, auditorias, migrations, bootstrap, smoke HTTP e backup/restauração aprovados.

Correções finais incorporadas antes do merge:

- build determinístico com lockfile e `.dockerignore`;
- lock exclusivo de deploy;
- revalidação de `HEAD`, árvore e checkout durante o processo;
- snapshot somente depois de bloquear Caddy e backend antigo;
- rollback armado antes do novo backend executar migrations;
- janela de rollback mantida até readiness interno e checkout privado serem aprovados;
- restauração automática sem reabrir backend ou proxy;
- detecção de `pgdata` por container, labels ou nome determinístico;
- despublicação de slugs ausentes da fonte canônica, preservando histórico;
- bloqueio de slugs ausentes, duplicados, vazios ou com espaços externos.

### PR #38 — slug Markdown explicitamente inválido

Commit de merge:

```text
955047999ab7b4015c9a29f8c86368e13d4b0576
```

Head certificado:

```text
af492b697436747b0da275b0975fbc5b213ef498
```

Certificação:

- CI #209 — run `30876684232`;
- **242 testes backend aprovados em 76,29 s**;
- Corpus database reconciliation #84 — run `30876684227`;
- **4.936 registros científicos** confirmados nas 11 coleções;
- frontend integralmente aprovado;
- `pip-audit` sem vulnerabilidades conhecidas;
- migrations completas e idempotentes;
- bootstrap administrativo aprovado;
- smoke HTTP aprovado;
- backup/restauração PostgreSQL aprovados com preservação do registro de prova;
- revisão Codex final: nenhum problema relevante encontrado.

Correção publicada:

- `_resolve_markdown_slug` centraliza a resolução do identificador;
- `import_directory` e o reconciliador usam exatamente a mesma regra;
- fallback pelo título ocorre somente quando a chave `slug` não existe;
- `slug: ""`, `slug: null`, `slug: false` e `slug: 0` são rejeitados;
- espaços nas extremidades continuam bloqueados;
- quatro testes executam o importador diretamente e confirmam que nenhum registro inválido é gravado.

## Garantias operacionais atuais

### Deploy determinístico em duas fases

1. valida `.env`, ferramentas, Git e Docker;
2. adquire lock exclusivo;
3. confirma SHA, árvore e checkout limpo;
4. constrói imagens antes de interromper o site existente;
5. fecha Caddy e backend antigo;
6. inicia somente o PostgreSQL quando necessário;
7. cria e valida o snapshot sem escritores ativos;
8. arma rollback antes de iniciar o novo backend;
9. executa migrations, reconciliação e eventual indexação;
10. exige readiness interno e nova validação do checkout;
11. abre o proxy somente após aprovação dos gates privados;
12. confirma HTTPS, readiness e SHA em `/api/version`.

### Backup e restauração

- dump custom e comprimido do PostgreSQL;
- arquivo temporário e publicação atômica;
- validação por `pg_restore --list`;
- SHA-256 vinculado ao dump selecionado;
- permissões restritas;
- compatibilidade controlada com `.sql.gz` legado;
- validação anterior ao `dropdb`;
- confirmação destrutiva em duas etapas no modo manual;
- `pg_restore --exit-on-error`;
- backend e proxy fora do tráfego durante restauração;
- falha da fase mutável aciona rollback automático;
- após rollback, backend e Caddy permanecem parados até intervenção.

### Reconciliação científica fail-closed

Comando oficial:

```bash
python -m app.commands.reconcile_content --publish-reviewed
```

- o deploy não usa `--allow-partial`;
- falhas, avisos, recusados, duplicados ignorados, ausências e Markdown vazio bloqueiam a certificação;
- diagnósticos são pesquisados recursivamente;
- manifestos JSON precisam ser listas de objetos com `slug` válido e único;
- Markdown e importação direta compartilham a mesma validação de slug;
- somente itens revisados e presentes na fonte atual são publicados;
- slugs removidos ou renomeados são despublicados, sem apagar o histórico;
- mínimos individuais das 11 coleções permanecem obrigatórios;
- excesso numa coleção não mascara déficit em outra.

## Bloqueio externo de produção

O deploy real ainda não foi executado.

O ambiente desta sessão não conseguiu resolver ou alcançar `corvia.med.br`, e o host anteriormente informado não aceitou as conexões tentadas. Assim, ainda não foi possível:

- identificar o SHA atualmente implantado;
- criar o backup real do PostgreSQL;
- atualizar `/opt/meucardio` para a `main` atual;
- executar `bash ./deploy.sh` no servidor;
- reconciliar o banco de produção;
- validar login, Painel, Biblioteca, CorvIA Mail e CorvIA Chat;
- testar mensagens entre duas sessões e WebSocket `wss://`;
- testar envio e recebimento no CorvIA Mail;
- aplicar `vm.overcommit_memory=1` no host.

As credenciais fornecidas pelo proprietário não foram usadas nem persistidas. Como foram compartilhadas em texto na conversa, recomenda-se rotacionar a senha depois da validação de produção.

## Próxima sessão — ponto exato de retomada

Não é necessário retomar nenhum PR funcional pendente. Começar pela produção:

1. confirmar acesso SSH ao servidor;
2. entrar em `/opt/meucardio`;
3. preservar e revisar o `.env`, sem substituí-lo;
4. aplicar no host:

   ```bash
   sudo sysctl -w vm.overcommit_memory=1
   echo 'vm.overcommit_memory=1' | sudo tee /etc/sysctl.d/99-corvia-redis.conf
   ```

5. criar um backup manual independente;
6. atualizar o repositório:

   ```bash
   git fetch origin
   git checkout main
   git pull --ff-only origin main
   git status --short
   git log -1 --oneline
   ```

7. confirmar checkout limpo;
8. executar presencialmente:

   ```bash
   bash ./deploy.sh
   ```

9. confirmar:
   - `https://corvia.med.br/api/health`;
   - `https://corvia.med.br/api/ready`;
   - `https://corvia.med.br/api/version` com o SHA da `main`;
   - 4.936 registros e mínimos individuais das 11 coleções;
   - ausência de erros em backend, PostgreSQL, Redis, Caddy e frontend.

## Validação autenticada após o deploy

- login principal;
- Painel mostrando o inventário integral;
- Biblioteca, paginação e buscas;
- CorvIA Chat pelo cartão e pelo botão flutuante;
- envio e recebimento entre duas sessões ou abas;
- WebSocket `wss://`;
- CorvIA Mail, acesso da caixa e webmail;
- envio e recebimento de e-mail;
- receituário e PDFs clínicos;
- links públicos de documentos;
- logout e revogação de sessão.

## Estado final desta sessão

- PRs #34, #35, #36, #37 e #38: publicados na `main`;
- correções funcionais pendentes no GitHub: nenhuma conhecida;
- deploy real: não executado;
- credenciais persistidas: nenhuma;
- arquivos científicos removidos: nenhum;
- senhas armazenadas alteradas: nenhuma;
- dados do servidor real alterados nesta sessão: nenhum.
