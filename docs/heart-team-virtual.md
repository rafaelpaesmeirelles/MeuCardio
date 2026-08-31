# CorVIA Heart Team Virtual

O Heart Team é apoio à decisão exclusivo do médico. A feature flag
`HEART_TEAM_ENABLED=false` é o padrão. O recurso não diagnostica o paciente,
não prescreve, não modifica tratamento e não publica nada automaticamente.

## Arquitetura clínica

1. Validação, desidentificação, estruturação, triagem de gravidade e lacunas.
2. Pareceres independentes com cópias profundas e sem respostas dos pares.
3. Reabertura/validação de DOI e PMID e verificação exata de números, doses,
   unidades, N, população, desfecho, direção, data, classe e nível.
4. Red team procura erros, extrapolações, interações e contraindicações.
5. Contestação sem pressão de maioria.
6. Coordenador sintetiza; divergências determinísticas, parecer de evidência e
   objeções do red team não podem ser omitidos.
7. Cada sugestão precisa ser aceita, rejeitada ou editada. Só então o médico
   faz a revisão final com duas confirmações explícitas.

Os agentes obrigatórios são coordenador, evidências e red team. Os agentes
clínicos iniciais cobrem insuficiência cardíaca/cardiomiopatias, arritmias/EP,
imagem, cardiologia intensiva/emergências e farmacologia/segurança. O registro
em `heart_team_agents.py` permite acrescentar especialidades.

Qualquer fonte não revisada, metadado inconsistente, afirmação sem fonte ou
resposta obrigatória insuficiente deixa o caso `unusable`. Resultados parciais
de casos `failed`/`unusable` ficam em auditoria, mas não são exibidos como
parecer. A expressão canônica é **“evidência insuficiente”**.

DOI e PMID informados precisam resolver para a mesma publicação. O resumo é
reaberto por Crossref/PubMed `efetch`; data, população, N, desfecho, direção,
números/unidades, classe e nível alegados são confrontados com a fonte externa.
Título/identificador sem abstract verificável serve apenas como bibliografia e
não autoriza afirmação clínica. O texto editorial local nunca prevalece sobre
um resultado externo divergente.

## Segurança e governança

- LGPD: minimização, confirmação de desidentificação, isolamento por
  `owner_id`, criptografia AES-256-GCM de anexos/cache e leitura auditada.
- Antes de qualquer chamada externa, o snapshot é bloqueado se contiver CPF,
  CNS, RG, telefone, e-mail, CEP, nome/paciente rotulado, nascimento, endereço
  ou número de prontuário; a confirmação do usuário não substitui esse gate.
- Todo PDF, imagem ou texto passa pelo sanitizador clínico fail-closed antes
  da persistência: metadados são removidos, PDF é rasterizado e OCR local
  bloqueia identificadores. Só o binário sanitizado chega ao cofre/provedor;
  hashes de origem e sanitizado são preservados separadamente.
- Trilha append-only com encadeamento SHA-256; triggers PostgreSQL recusam
  UPDATE/DELETE de pareceres, sugestões, revisões, auditoria e ledger.
- Snapshot e hashes original/final são preservados.
- Modelo, pipeline, tokens, custo, fontes, horário e médico revisor são
  registrados.
- Decisão clínica, comunicação, prescrição e assinatura permanecem humanas.
- O acesso exige perfil médico aprovado e CRM; investidor, leitor e
  administrador não médico não podem analisar ou validar pareceres.
- Quando um prontuário autorizado foi importado, sua timeline recebe apenas
  depois da revisão final um artefato de proveniência (modelos, pipeline,
  fontes, horário, revisor, decisão e hash), sem recomendação não aceita.
- ECG/imagem nunca é silenciosamente ignorado: sem extrato multimodal clínico
  homologado, o caso exige laudo textual/PDF associado e falha fechado se ele
  não existir.
- A classificação regulatória, relatório de risco, validação clínica e
  avaliação jurídica para Resolução CFM nº 2.454/2026 precisam ser concluídos
  antes do piloto; este código não equivale a certificação regulatória.

## API

- `GET /api/heart-team/agents`
- `GET /api/heart-team/usage`
- `GET|POST /api/heart-team/cases`
- `GET|PATCH /api/heart-team/cases/{id}`
- `POST /api/heart-team/cases/{id}/attachments`
- `GET /api/heart-team/cases/{id}/attachments/{position}`
- `POST /api/heart-team/cases/{id}/analyze` — responde `202`, enfileira de
  forma idempotente e fornece `poll_url`.
- `POST /api/heart-team/cases/{id}/suggestions/{sid}/review`
- `POST /api/heart-team/cases/{id}/final-review`
- `GET /api/heart-team/cases/{id}/audit`
- `GET /api/admin/heart-team/metrics`
- `POST /api/admin/heart-team/retention/purge`

O worker durável compartilhado processa `HeartTeamAnalysisJob` iniciado pela
UI e `WhatsAppHeartTeamJob`. Lease perdido antes da análise é recuperável; se
já houver parecer parcial, o job falha fechado e o conteúdo fica em
quarentena. O worker chama a entrada canônica `analyze_case_by_id(...)`; não
duplica a orquestração.

## Tudo com Tudo

`related_content` contém apenas fontes citadas/revisadas e arestas reais,
revisadas e persistidas do grafo canônico. Os links podem apontar para doenças,
medicamentos, exames, calculadoras, diretrizes, evidências, estudos,
fluxogramas, materiais, trilhas e timeline. Sem relação defensável, a lista
fica vazia; nunca há preenchimento por mera semelhança lexical.

## Variáveis

```dotenv
HEART_TEAM_ENABLED=false
HEART_TEAM_FILES_DIR=/heart-team-files
HEART_TEAM_CLINICAL_MODEL=
HEART_TEAM_MAX_OUTPUT_TOKENS=2200
HEART_TEAM_SOURCE_LIMIT=16
HEART_TEAM_CACHE_TTL_SECONDS=3600
HEART_TEAM_MONTHLY_COST_CEILING_MICROS=25000000
HEART_TEAM_DAILY_CASE_LIMIT=10
HEART_TEAM_MONTHLY_CASE_LIMIT=100
HEART_TEAM_INPUT_TOKEN_COST_MICROS=2
HEART_TEAM_OUTPUT_TOKEN_COST_MICROS=12
```

Não há segredo novo no repositório. As chaves do provedor e do cofre continuam
no secret store existente. O volume nomeado `heartteamfiles` preserva anexos
entre substituições de container.

## Retenção

O cache expirado é removido oportunisticamente, pelo endpoint administrativo
auditado ou pelo comando de manutenção:

```bash
python -m app.commands.purge_expired_heart_team_cache          # dry-run
python -m app.commands.purge_expired_heart_team_cache --apply  # exclusão
```

Agendar `--apply` diariamente na rotina operacional. O comando não depende da
criação de novos casos.

## Custos

Reserva atômica por assinante usa advisory lock PostgreSQL antes de cada
chamada e reconcilia o consumo real após a resposta. A próxima chamada é
bloqueada antes de ultrapassar o teto. A chave do cache inclui snapshot,
hashes de origem/sanitizado, tipo/tamanho/extração dos anexos, grafo, agentes,
modelo, pipeline e teto de saída. O payload cifrado inclui pareceres,
contestações, consenso e versões dos modelos; um hit recria linhas imutáveis
após verificar cada hash.

Exemplo conservador com os defaults acima, 13 chamadas por caso, ~1.000 tokens
de entrada e o teto integral de 2.200 tokens de saída por chamada:

| Casos/comandos completos | Unidades estimadas* |
|---:|---:|
| 100 | 36,92 |
| 1.000 | 369,20 |
| 10.000 | 3.692,00 |

\* Unidade depende da moeda configurada pelo operador; estimativa de reserva,
não preço comercial nem fatura do provedor. Substituir os custos por token
pelos valores contratuais homologados antes da ativação.

## Migração e rollback

`f87h20260831` depende de `f86d20260829`; a migração seguinte do WhatsApp
depende de `f87h20260831`. O downgrade remove triggers, tabelas e índices do
Heart Team em ordem reversa. Faça backup antes de qualquer rollback com dados.
