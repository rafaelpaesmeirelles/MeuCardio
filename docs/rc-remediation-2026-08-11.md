# Release Candidate — remediação pós-falha de deploy (issue #52)

> Este documento cobre especificamente a remediação do incidente de deploy do
> RC anterior (`27d240895490ace26a30c01f5bf1b813e6d5187c`). O inventário
> funcional completo, a distância produção→RC e a reconciliação de branches
> continuam válidos como registrados em `docs/rc-final-2026-08-11.md` — nada
> no conjunto de funcionalidades mudou nesta rodada, só a causa raiz da falha
> de deploy foi corrigida, testada e endurecida contra repetição.
>
> Um bug real de entitlement (médico convidado barrado por cobrança
> indevida) foi diagnosticado durante esta remediação, com duas soluções
> possíveis avaliadas — mas **por decisão humana explícita, nenhuma das duas
> entra neste RC**. Fica registrado como pendência pré-lançamento (seção 6),
> com o trabalho parcial isolado em `docs/wip/`, fora do escopo funcional
> deste release.

## 1. O que falhou, e por quê (resumo — detalhe completo no issue #52)

O deploy do RC anterior falhou em produção durante
`reconcile_content --publish-reviewed`, dentro do `deploy.sh` certificado.
O rollback automático do próprio script disparou corretamente, mas restaurou
um backup que já estava contaminado — uma migration do RC havia sido
aplicada manualmente contra o backend antigo, ainda em execução, **antes**
de `deploy.sh` ter sido chamado (possível porque `migrations/` é bind mount
no container). Produção ficou fora do ar por um período e foi restaurada
manualmente para o baseline seguro, com uma janela reconhecida de possível
perda de até ~40 minutos de gravações (já registrada no issue #52).

Reproduzindo localmente, contra conteúdo real, o mesmo comando exato que
falhou em produção revelou **três bugs reais em sequência** — cada um só
apareceu depois de corrigir o anterior:

1. **`TypeError: 'review_note' is an invalid keyword argument for Drug`** —
   `carregar_drugs.py`/`popular_drugs.py` construíam o registro novo via
   `Drug(**d)` sem filtrar o JSON pelas colunas reais do modelo. `review_note`
   é convenção de documentação já usada em `documents`/`evidencias`; nunca
   deveria derrubar a carga.
2. **`StringDataRightTruncation`** em `drugs.duration_of_action_source`
   (varchar 500) e `drugs.drug_class` (varchar 120) — os dois guardam texto
   de prosa/citação completa, não rótulo curto; dois registros reais do RC
   excediam os limites (530/728 e 143 caracteres).
3. **Ordem de carga em `reconcile_content.py`**: `trilhas` era processada
   antes de `casos_clinicos`, e a validação de referência de etapa consulta
   o banco, não o arquivo de origem — 6 trilhas reais, com referência
   genuinamente existente, eram rejeitadas como "referência inexistente" só
   por ordem de carga.

## 2. Correções aplicadas

### 2.1 — Os três bugs, corrigidos na causa raiz

- `backend/app/services/carregar_drugs.py` e `popular_drugs.py`: filtram o
  dict do JSON pelas colunas reais de `Drug.__table__.columns` antes de
  construir ou atualizar um registro — campo desconhecido é ignorado
  silenciosamente, nos dois ramos (criação e atualização), nunca derruba a
  carga.
- `backend/app/models/drug.py` + migração nova `72abcfc8df81`:
  `duration_of_action_source` e `drug_class` viram `Text` (sem limite),
  mesmo padrão do resto do modelo e do precedente `f2b8c41d7a93`
  (`audit_logs.entity_id`). Downgrade é no-op de propósito (encurtar de
  volta truncaria conteúdo já gravado).
- `backend/app/commands/reconcile_content.py`: `casos_clinicos` movida para
  antes de `trilhas` em `FRONTS`, resolvendo a dependência real de
  referência sem tocar em mais nada da ordem.

### 2.2 — Auditoria estrutural das 13 frentes de `reconcile_content`

Toda frente que constrói o modelo ORM a partir do JSON foi inspecionada
individualmente em busca do mesmo padrão (`Model(**item)` sem filtro):

| Frente | Estado encontrado | Ação |
|---|---|---|
| `medicamentos` (Drug) | Vulnerável — foi o bug real | Corrigido (ver 2.1) |
| `galeria` (GalleryImage) | Vulnerável, sem mismatch atual no conteúdo real | Corrigido preventivamente |
| `exames` (LabTest) | Vulnerável, sem mismatch atual | Corrigido preventivamente |
| `evidencias` (EvidenceRecord) | Vulnerável, sem mismatch atual | Corrigido preventivamente |
| `estudos` (ScientificStudy) | Vulnerável, sem mismatch atual | Corrigido preventivamente |
| `checklists` (DischargeChecklist) | Já defendido (`CAMPOS` allowlist) | Nenhuma |
| `casos_clinicos` (ClinicalCase) | Já defendido (`CAMPOS` allowlist) | Nenhuma |
| `trilhas` (StudyTrack) | Já defendido (`CAMPOS` allowlist) | Nenhuma (bug de ordem corrigido à parte) |
| `doencas_especializadas` (SpecialtyDisease) | Já defendido (`CAMPOS` allowlist) | Nenhuma |
| `triagem_sintomas` (SymptomTriageGuide) | Já defendido (`CAMPOS` allowlist) | Nenhuma |
| `material_paciente` (PatientMaterial) | Imune por construção (atribuição campo a campo, nunca `Model(**item)`) | Nenhuma |
| `emergencia` (EmergencyProtocol) | Imune por construção (idem) | Nenhuma |
| `documentos` (Document, via `importer.py`) | Imune por construção (campos lidos individualmente do front matter, nunca repassados em bloco) | Nenhuma |

Verificado antes de decidir: nenhuma das 4 frentes corrigidas preventivamente
tinha, no conteúdo real do repositório, qualquer chave fora das colunas do
modelo no momento da correção — o risco era estrutural (idêntico ao que já
havia derrubado `drugs`), não um bug já disparado nelas.

### 2.3 — Endurecimento do procedimento de deploy

Causa raiz operacional: migration aplicada manualmente, fora da sequência
certificada, possível porque `migrations/` é bind mount e o comando de
migração não tem modo dry-run.

- **`deploy.sh`**: nova função `validar_migrations_nao_adiantadas()`,
  chamada logo após o build da imagem nova e antes de qualquer mutação
  (parar caddy/backend, backup). **Redesenhada uma vez, depois de revisão
  adversarial dedicada encontrar um bug real de lógica na primeira versão**:
  a versão inicial comparava `alembic_version` contra o head ABSOLUTO das
  migrations do RC — o que abortaria (falso positivo) qualquer deploy cujo
  commit não trouxesse migration nova (a maioria) e deixaria passar (falso
  negativo) o caso de só parte das migrations novas terem sido aplicadas
  fora de ordem. A versão corrigida compara contra o head que o **commit
  ATUALMENTE em execução** esperava — lido do próprio `DEPLOY_COMMIT` do
  container backend ainda rodando (não depende do checkout do host, que já
  está no commit novo neste ponto do script), com o head daquele commit
  antigo recalculado via AST do Python (stdlib, sem alembic, sem tocar em
  banco/container) — uma tentativa inicial com regex simples já se mostrou
  ambígua contra merge migrations reais deste projeto (5 candidatas a head
  em vez de 1) antes desta versão ser adotada. Função inteira roda sob
  `set +e` local — qualquer falha de leitura (container indisponível, git
  show falhando, banco inacessível) é um *graceful-skip* logado, nunca um
  abort — o guard é defensivo, não pode ele mesmo travar um deploy legítimo
  por falta de diagnóstico. Validado por três testes standalone (commit
  baseline real reproduz o head já confirmado independentemente; commit do
  próprio RC anterior reproduz o head correto; SHA inexistente não crasha,
  faz skip gracioso) — não por agente adversarial dedicado numa segunda
  rodada, dado o tempo já investido nesta remediação.
- **`DEPLOY.md`**: seção "Migrations" reescrita com um aviso explícito no
  topo, citando o incidente inteiro, explicando por que a idempotência do
  comando não protege contra rodá-lo fora de ordem, e apontando os
  comandos somente-leitura (`alembic current`/`alembic heads`) para quem
  só precisa inspecionar.
- Lista numerada "O que `deploy.sh` garante" atualizada para incluir o
  passo novo na posição real (depois do build, antes do backup).
- **Achado à parte, corrigido**: o próprio texto dos comentários novos em
  `deploy.sh` continha a substring literal `python -m app.commands.migrate`
  (dentro de prosa explicando o incidente), o que colidia com
  `tests/test_deploy_contract.py` — uma suíte de "contrato" já existente que
  valida a ORDEM de comandos no script por posição de substring no arquivo.
  Meus comentários, posicionados antes da invocação real no arquivo,
  faziam o teste encontrar o comentário em vez do comando de verdade,
  derrubando 2 dos 20 testes daquele arquivo. Reescrito para não conter a
  substring exata, preservando o sentido — 20/20 passam agora.

## 3. Verificação

- `reconcile_content --publish-reviewed --allow-partial` — o comando exato
  que falhou em produção — roda limpo contra conteúdo real, todas as 13
  frentes acima do mínimo, zero rejeição. Coberto por teste automatizado
  novo (`test_reconcile_content_full_run.py`), não só verificação manual.
- Migrations: `alembic upgrade head` idempotente (rerun sem `Running
  upgrade`), `alembic heads` com head único, ciclo
  `downgrade -1` → `upgrade head` correto.
- `deploy.sh`: sintaxe validada (`bash -n`); a chamada Python do novo guard
  (`ScriptDirectory.from_config(...).get_current_head()`) verificada
  isoladamente contra o repositório real, resolve para o head correto
  (`72abcfc8df81`) sem tocar em nenhum banco.
- Frontend: `tsc --noEmit` limpo (Node 22) — nenhuma mudança de frontend
  nesta rodada, verificado para confirmar ausência de regressão incidental.
- `scripts/feature_inventory.py`: íntegro, mesmas contagens de sempre (61
  rotas React, 38 destinos de menu, 49 routers FastAPI) — sem drift.
- Backup/restore: **verificado ao vivo, não só em teste** — a restauração
  real de produção durante a recuperação do incidente usou exatamente
  `infra/backup/restaurar.sh`, o mesmo script que este RC continua usando;
  funcionou sob pressão real, não é hipotético.
- **Revisão adversarial dedicada, dois agentes independentes, escopos sem
  sobreposição**: um revisou os fixes de `reconcile_content`/loaders/
  migração de schema (achados reais: `carregar_galeria.py` usava lista de
  campos mantida à mão em vez do padrão auto-derivado dos outros 4 loaders
  — corrigido; teste de reconciliação completa é sensível a contenção do
  banco de teste compartilhado — documentado, não é regressão de código);
  outro revisou especificamente o guard novo de `deploy.sh` e encontrou o
  bug real de falso positivo/negativo já descrito na seção 2.3, que motivou
  o redesenho.
- Suíte completa do backend: ver resultado abaixo.

## 4. Resultado da suíte completa

<!-- preenchido após a rodada final -->

## 5. Produção — confirmado no baseline seguro, intocada

`GET /api/version` → `c38c66244892f6931de0bbfeec1bbe4264c10325` (mesmo
baseline restaurado após o incidente) · `GET /api/ready` → `database: ok,
redis: ok` · `/opt/meucardio`: `git status` limpo, nenhuma mutação. Apenas
inspeção read-only foi feita em produção durante esta remediação.

## 6. Pendências mantidas — pré-lançamento comercial (não bloqueiam este RC)

- **Entitlement de médico convidado — bug real, diagnosticado, NÃO corrigido
  neste RC por decisão humana explícita.** `assinante_ativo()`
  (`backend/app/core/security.py`, o gate central aplicado a quase toda
  rota) só verifica `Subscription.status` — nunca lê `User.convidado`. O
  bypass de cobrança do convidado vive inteiramente dentro de
  `criar_checkout()` (`billing.py`), que só executa quando o usuário visita
  a tela de Assinatura e clica "Assinar". Sem esse clique, um convidado
  marcado pelo admin é barrado com 402 como um visitante sem conta — foi o
  que aconteceu com a conta real `drmarciopeixoto@corvia.med.br`. **Duas
  opções levantadas e avaliadas** (correção mínima sem migration em
  `assinante_ativo()`, vs. arquitetura `access_grants` completa e
  extensível) — decisão humana foi adiar as duas para frente própria
  pós-RC, com revisão dedicada. **Contorno imediato, sem depender deste
  RC**: a pessoa afetada logar e clicar "Assinar" em `/assinatura` uma vez
  já funciona hoje, no baseline em produção (grava acesso liberado sem
  cobrar, auditado) — não resolve o problema estrutural, mas destrava o
  caso concreto sem nenhuma mudança de código.
- **Entitlement de conta demonstrativa para investidores — não definido nem
  implementado.** Regras de acesso, duração, permissões, revogação,
  auditoria e isolamento de dados (nunca paciente real, nunca dado
  administrativo) ficam para a mesma frente futura acima, junto com
  convidado — são a mesma decisão de arquitetura de entitlement,
  deliberadamente não separadas.
- Um rascunho de arquitetura unificada (`AccessGrant`, tabela nova +
  serviço central de decisão) foi iniciado e **explicitamente isolado, fora
  do RC**: `docs/wip/access-grants-pendente/` (arquivos `.wip`, fora de
  `app/models/` e `migrations/versions/`, nunca aplicados a nenhum banco,
  nenhuma referência residual no código ativo — confirmado por `grep` e por
  `alembic heads` continuando em `72abcfc8df81`, o head real deste RC).
  Preservado só como ponto de partida para quem retomar a frente, não
  como parte deste release.
- **Kairos** — inteligência de mercado, pendente de acesso/licenciamento
  comercial. Sem bypass de Cloudflare, sem scraping. Arquitetura preparada,
  desativada.
- **Data Market/Cnova** — provedor de preço de varejo avaliado (POC), sem
  categoria farmacêutica suficiente para ativar; não é fonte válida hoje.
- **CliqueFarma** — potencial integração B2B documentada, sem API pública
  disponível; não implementado.
- **Auditoria quantitativa de volume/completude/conectividade do conteúdo
  após o backfill do Knowledge Graph** — o backfill em si roda e é
  idempotente (testado), mas uma auditoria quantitativa dedicada (contagem
  real de entidades/relações por tema, cobertura por front, ausência de nó
  privado) ainda não foi executada nesta rodada — fica registrada como
  pendência explícita, não escondida.

Nenhuma dessas pendências bloqueia este RC tecnicamente — bloqueiam a
declaração de lançamento comercial definitivo, não o deploy técnico.

## 7. Veredito

<!-- preenchido após a rodada final -->

## 8. Plano de deploy — preparado, NÃO executado

Idêntico ao plano já certificado em `docs/rc-final-2026-08-11.md` seção 8,
com um passo novo entre "build" e "backup": a validação automática de
migrations não adiantadas (`validar_migrations_nao_adiantadas`), já
embutida no próprio `deploy.sh` — não é um passo manual extra a lembrar, o
script certificado já faz isso sozinho.

**Regra que fica valendo a partir deste incidente, sem exceção**: nenhuma
migration roda manualmente contra produção fora de `./deploy.sh`, nunca
como passo isolado de "verificação". Para inspecionar sem aplicar, usar
`alembic current`/`alembic heads` (somente leitura).

## 9. Hostinger

Fora do escopo desta remediação — não tocado.

---

**NENHUM DEPLOY FOI EXECUTADO NESTA REMEDIAÇÃO.** Aguardando nova
autorização humana explícita, no formato `AUTORIZO O DEPLOY DO RC <SHA>`.
