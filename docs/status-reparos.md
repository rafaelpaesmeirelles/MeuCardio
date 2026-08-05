# Status dos reparos — CorvIA / MeuCardio

Última atualização: 04/08/2026 19:20 (BRT)

## Resumo executivo

A produção está sincronizada com a `main` no merge do PR #45:

```text
be3a73a9028cd00f1d57c82d9dc338eeb943c22b
```

Após o deploy, foram confirmados:

- `/api/health` saudável;
- `/api/ready` com PostgreSQL e Redis disponíveis;
- `/api/version` retornando o mesmo SHA publicado;
- deploy concluído com código de retorno zero;
- testes autenticados e validação funcional executados;
- parâmetro operacional do Redis verificado;
- senha administrativa compartilhada durante a intervenção rotacionada;
- checkout do servidor alinhado à `main`.

O PR #46 está em desenvolvimento isolado e **não foi mesclado nem publicado em produção**.

## Estado de produção

| Item | Estado |
|---|---|
| Branch publicada | `main` |
| SHA publicado | `be3a73a9028cd00f1d57c82d9dc338eeb943c22b` |
| PostgreSQL | saudável |
| Redis | saudável |
| Backend | saudável |
| Caddy/HTTPS | ativo |
| Revisão Alembic consolidada | `d63a0cc83807` |
| Corpus científico | 4.936 registros preservados |
| Senha administrativa da intervenção | rotacionada |

## Publicações concluídas

### PRs #34–#40 — recuperação e consolidação operacional

Esse ciclo entregou, entre outros itens:

- migração para bcrypt direto;
- Painel e Biblioteca baseados no inventário canônico;
- CorvIA Mail e CorvIA Chat;
- atualização do ReportLab;
- deploy determinístico com rollback;
- reconciliação do corpus científico;
- unificação da cadeia Alembic da produção;
- backup e restauração certificados.

A cadeia Alembic consolidada permanece em:

```text
d63a0cc83807
```

### PR #42

Correções posteriores de interface e operação incorporadas à `main`.

### PR #43

Correções posteriores de segurança e consistência incorporadas à `main`.

### PR #44

Ajustes adicionais certificados e incorporados à `main`.

### PR #45 — árvores SVG do Modo Emergência

- corrigiu a renderização Mermaid das árvores do Modo Emergência;
- eliminou a remoção prematura do SVG montado;
- passou a validar o SVG antes da exibição;
- CI concluída com sucesso;
- merge e deploy confirmados em produção.

Merge publicado:

```text
be3a73a9028cd00f1d57c82d9dc338eeb943c22b
```

## Incidente de produção em 04/08/2026

### Estado inicial

O checkout em `/opt/meucardio` estava divergente da `main`, com histórico local e arquivos modificados. Antes de qualquer alinhamento foram preservados:

- branch local de resgate;
- commit de resgate;
- bundle independente;
- patch das alterações rastreadas;
- inventário dos arquivos não rastreados;
- cópia protegida do `.env`;
- checksums SHA-256.

### Backup do PostgreSQL

Foi criado e validado um dump custom do PostgreSQL, com catálogo conferido por `pg_restore --list` e checksum aprovado.

### Cadeia Alembic

O banco registrava uma revisão que não existia integralmente na `main` daquele momento. As migrations históricas necessárias foram restauradas e unificadas pela revisão:

```text
d63a0cc83807
```

A migração operacional concluiu com sucesso; o backend atingiu readiness antes da reabertura do proxy público.

### `.env`

O `.env` de produção permanece fora do controle de versão e não foi copiado para commits, PRs ou documentação.

Durante a recuperação foi corrigida localmente uma declaração com sintaxe inadequada. A documentação registra apenas que a validação passou, sem reproduzir valores, remetentes, senhas, tokens ou demais segredos:

```text
bash -n .env: aprovado
docker compose config: aprovado
```

## Garantias preservadas

- nenhum volume PostgreSQL removido;
- nenhuma restauração destrutiva executada;
- backup validado antes das alterações críticas;
- branch e bundle de resgate preservados;
- nenhum arquivo científico removido;
- nenhuma senha armazenada de usuário alterada;
- corpus de 4.936 registros preservado;
- credenciais e segredos mantidos fora do Git;
- produção alinhada ao SHA publicado na `main`.

## PR #46 — correções em desenvolvimento

Título:

```text
Corrige RCE, medicamentos comerciais, históricos e atalho de emergência
```

Branch:

```text
agent/corrige-rce-historicos-emergencia-docs
```

Estado: **rascunho, sem merge e sem deploy**.

Escopo:

1. paginação explícita da Receita de Controle Especial, sem truncar medicamentos ou observações;
2. validação completa de conselho, número e UF do registro profissional;
3. manutenção do bloqueio de primeiro acesso enquanto o perfil profissional estiver incompleto;
4. apresentação legível de erros estruturados da API;
5. pesquisa em todo o acervo cifrado do usuário antes da paginação de históricos;
6. remoção da regra CSS duplicada do atalho de Emergência, mantendo o botão textual;
7. preservação exata do produto e da apresentação comercial escolhidos;
8. atualização desta documentação e dos testes de regressão.

### Regra para medicamentos comerciais

Quando o prescritor escolher uma apresentação comercial, o nome e a apresentação selecionados devem permanecer exatamente iguais na prévia, persistência, revisão, PDF, histórico e recriação.

Exemplo:

```text
Benicar 20 mg
```

não pode ser substituído visualmente por:

```text
olmesartana 20 mg
```

A substância genérica continua armazenada separadamente para classificação regulatória, interações e regras de receituário.

### Regra para históricos

A busca por paciente não cria índice em texto claro. O backend:

1. restringe a consulta aos registros pertencentes ao usuário autenticado;
2. decifra somente os nomes desse acervo;
3. aplica busca parcial e filtro por tipo;
4. pagina o resultado já filtrado;
5. devolve `page`, `page_size`, `has_more` e `total`.

Essa estratégia prioriza confidencialidade e correção. O custo de varrer o acervo cifrado deverá ser acompanhado por métricas antes de qualquer otimização futura.

## Critérios para concluir o PR #46

O PR somente poderá sair de rascunho após:

- testes de regressão do escopo aprovados;
- suíte backend integral aprovada;
- build frontend aprovado;
- migrations e reconciliação aprovadas;
- smoke HTTP aprovado;
- backup/restauração aprovado;
- revisão do diff sem pendências críticas;
- confirmação de que nenhuma alteração destrutiva de banco foi introduzida.

O merge e o deploy exigem decisão separada após a certificação. O documento não orienta mais o servidor a retornar ao commit obsoleto `a0b24f34`.

## Retenção e limpeza operacional

Os artefatos de resgate e o backup do incidente devem permanecer retidos até existir política formal de expiração e um backup posterior validado. A remoção não faz parte do PR #46.
