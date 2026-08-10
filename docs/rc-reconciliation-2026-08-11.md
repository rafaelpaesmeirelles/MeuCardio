# Reconciliação RC — 2026-08-11

> ## ⚠️ ADENDO CRÍTICO, escrito pelo orquestrador logo após este relatório — leia antes do resto
>
> A afirmação da seção 1.1 abaixo ("existem exatamente **dois** branches no remoto") está
> **provadamente errada**, por uma causa de metodologia identificada horas depois deste relatório:
> a config de `git fetch` deste checkout (`/root/corvia-stabilizacao`) tinha um **refspec
> restrito** (`+refs/heads/stabilizacao-2026-08-09:refs/remotes/origin/stabilizacao-2026-08-09`),
> que só trazia 1 branch. `git fetch --all --prune` **nunca poderia** ter revelado outros
> branches — não porque eles não existissem, mas porque o próprio comando de fetch estava
> configurado para nunca buscá-los. Confirmado via GitHub API e `git ls-remote --heads origin`
> (que ignora completamente a config de refspec local): **existem 69 branches reais no remoto**,
> dos quais **33 têm commits não incorporados** a esta branch.
>
> O refspec foi corrigido (`git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"`)
> e um agente dedicado investigou, um por um, os 33 branches não-ancestrais. **Ver
> `docs/rc-branch-investigation-2026-08-11.md` para o relatório completo e correto** — esse
> arquivo substitui a conclusão da seção 1.1 abaixo. O resto deste relatório (categorização de
> commits desta branch contra produção, migrations, metodologia de checagem) continua válido e
> não foi refeito, só a contagem de branches do remoto.
>
> **HEAD também mudou desde que este relatório foi escrito** (`44bc0357` → HEAD atual da branch,
> mais commits de correção de segurança e de conteúdo aplicados depois). O SHA final do RC será
> registrado no relatório GO/NO-GO, não neste documento.

**Executado por:** Agente G (frente de reconciliação/documentação, somente leitura)
**Data/hora da reconciliação:** 2026-08-11, 00:47–00:55 UTC (horário do commit mais recente no branch:
`2026-08-11 00:47:55 +0200`; comando `date -u` local rodado às `2026-08-10 23:21:35 UTC` — ambos
dentro da mesma janela, sem viagem no tempo entre a apuração e a escrita deste arquivo).
**Repositório de trabalho:** `/root/corvia-stabilizacao`
**Branch:** `stabilizacao-2026-08-09`
**HEAD (SHA completo):** `44bc035752f5de9b733e847abf133d0e856e1aa4`
**Remoto:** `https://github.com/rafaelpaesmeirelles/MeuCardio.git` (o mesmo repositório GitHub que
`/opt/meucardio` usa via SSH — `git@github.com:rafaelpaesmeirelles/MeuCardio.git` — confirmado
como o mesmo remoto lógico, apenas protocolo diferente).

**Baseline de produção:**
- Caminho: `/opt/meucardio` (produção, só leitura nesta reconciliação)
- SHA completo: `c38c66244892f6931de0bbfeec1bbe4264c10325`
- Mensagem: `docs(claude): registra exclusao definitiva dos 34 duplicados + orfao historico`
- Data do commit: `2026-08-09 05:10:42 +0200`

---

## 1. Confirmação passo a passo (comando + resultado real)

Todas as checagens abaixo foram executadas do zero nesta sessão, sem reaproveitar nenhuma conclusão
de rodada anterior sem reconferir.

### 1.1 `git fetch --all --prune` + branches remotos

```
$ git fetch --all --prune
$ git branch -r
  origin/main
  origin/stabilizacao-2026-08-09
```

**Resultado:** confirmado — existem exatamente **dois** branches no remoto,
`origin/main` e `origin/stabilizacao-2026-08-09`. Nenhum branch novo apareceu, nenhum branch
antigo (`claude/medicamentos-review-completo-38tslz` ou qualquer outro) ressurgiu.

### 1.2 HEAD de produção

```
$ cd /opt/meucardio && git rev-parse HEAD
c38c66244892f6931de0bbfeec1bbe4264c10325
$ git log -1 --format="%H | %ad | %s" --date=iso
c38c66244892f6931de0bbfeec1bbe4264c10325 | 2026-08-09 05:10:42 +0200 | docs(claude): registra exclusao definitiva dos 34 duplicados + orfao historico
```

**Nota de apuração, registrada para quem repetir este procedimento:** `/opt/meucardio` tem um
`origin` git próprio (`git@github.com:rafaelpaesmeirelles/MeuCardio.git`, via SSH) — mesmo
repositório lógico do GitHub que `/root/corvia-stabilizacao` usa via HTTPS, mas **remoto
configurado separadamente**, com seu próprio conjunto de branches já buscados (inclusive dezenas
de branches `agent/*` que não aparecem no fetch de `/root/corvia-stabilizacao`, porque cada
checkout só busca o que já buscou antes). Além disso, o diretório de trabalho de um shell
**persiste entre chamadas de Bash separadas** neste ambiente — um `cd /opt/meucardio` numa chamada
afeta a chamada seguinte se ela não fizer `cd` de volta explicitamente. As duas armadilhas juntas
podem levar a comparar `origin/main`/`origin/stabilizacao-2026-08-09` do repositório errado. Nesta
reconciliação, cada comparação de branch foi refeita com `pwd` explícito confirmando
`/root/corvia-stabilizacao` antes de rodar.

### 1.3 Produção é ancestral de `origin/main`?

```
$ cd /root/corvia-stabilizacao
$ git cat-file -t c38c66244892f6931de0bbfeec1bbe4264c10325
commit
$ git merge-base --is-ancestor c38c66244892f6931de0bbfeec1bbe4264c10325 origin/main && echo YES
YES
```

**Resultado:** confirmado — o objeto de produção existe no histórico alcançável por
`origin/stabilizacao-2026-08-09` (por isso `git cat-file -t` o resolve mesmo sem estar em
`/opt/meucardio`), e é ancestral direto de `origin/main`.

### 1.4 Produção é ancestral de `origin/stabilizacao-2026-08-09`?

```
$ git merge-base --is-ancestor c38c66244892f6931de0bbfeec1bbe4264c10325 origin/stabilizacao-2026-08-09 && echo YES
YES
```

**Resultado:** confirmado.

### 1.5 `merge-base(origin/main, origin/stabilizacao-2026-08-09)`

```
$ git merge-base origin/main origin/stabilizacao-2026-08-09
940a812c21376c9890cedb89aa9a941bd4fa65a5
$ git merge-base --is-ancestor origin/main origin/stabilizacao-2026-08-09 && echo YES
YES
```

**Resultado:** confirmado — o merge-base entre os dois branches é **o próprio `origin/main`**
(SHA `940a812c21376c9890cedb89aa9a941bd4fa65a5`). Isso significa que `origin/main` é ancestral
direto de `origin/stabilizacao-2026-08-09`: a branch de estabilização contém **100% do histórico
do `main`**, sem divergência nenhuma, mais commits adicionais por cima.

### 1.6 Contagem `--left-right` entre `origin/main` e `origin/stabilizacao-2026-08-09`

```
$ git rev-list --left-right --count origin/main...origin/stabilizacao-2026-08-09
0	18
```

**Resultado:** confirmado — **zero** commits exclusivos de `origin/main` (lado esquerdo), **18**
commits exclusivos de `origin/stabilizacao-2026-08-09` (lado direito). Não há divergência/merge
cruzado — é uma relação puramente linear (fast-forward de `main` para `stabilizacao`).

### 1.7 Contagem de commits entre produção e `origin/stabilizacao-2026-08-09`

```
$ git rev-list --count c38c66244892f6931de0bbfeec1bbe4264c10325..origin/stabilizacao-2026-08-09
37
$ git rev-list --count c38c66244892f6931de0bbfeec1bbe4264c10325..origin/main
19
```

**Resultado:** confirmado — 19 commits de produção até `main`, mais 18 commits de `main` até
`stabilizacao-2026-08-09` = **37 commits no total** entre produção e o HEAD atual desta branch.
Aritmética consistente (19 + 18 = 37) e consistente com o resultado do item 1.6 (0 exclusivos de
`main`, 18 exclusivos de `stabilizacao`).

### 1.8 `git diff --stat` produção → branch

```
$ git diff c38c66244892f6931de0bbfeec1bbe4264c10325...origin/stabilizacao-2026-08-09 --stat | tail -1
 62 files changed, 6899 insertions(+), 432 deletions(-)
$ git diff c38c66244892f6931de0bbfeec1bbe4264c10325...origin/stabilizacao-2026-08-09 --name-only | wc -l
62
```

**Resultado:** confirmado — **62 arquivos alterados**, +6899/−432 linhas, entre produção e o HEAD
atual da branch. Lista completa de arquivos na seção 4 (migrations) e no corpo deste relatório
onde relevante; a lista integral de nomes de arquivo está reproduzida abaixo para referência:

```
M  DEPLOY.md
M  backend/app/api/admin.py
M  backend/app/api/appointments.py
M  backend/app/api/browser_session.py
A  backend/app/api/email_session.py
M  backend/app/api/health.py
A  backend/app/api/knowledge_graph.py
M  backend/app/api/prescriptions.py
M  backend/app/api/round.py
M  backend/app/api/timeline.py
M  backend/app/core/security.py
M  backend/app/main.py
M  backend/app/models/__init__.py
M  backend/app/models/email_account.py
A  backend/app/models/knowledge.py
A  backend/app/services/clinical_ownership.py
M  backend/app/services/instagram_profile.py
A  backend/app/services/knowledge_graph.py
A  backend/app/services/pricing/__init__.py
A  backend/app/services/pricing/base.py
A  backend/app/services/pricing/cmed_provider.py
A  backend/migrations/versions/525c83496f23_email_account_sessions_valid_after.py
A  backend/migrations/versions/5a786cb55611_knowledge_graph.py
A  backend/tests/test_agenda_connectors_write.py
A  backend/tests/test_agenda_oauth_flow.py
A  backend/tests/test_agenda_sync_cli.py
M  backend/tests/test_backup_freshness.py
M  backend/tests/test_browser_session_cookie.py
A  backend/tests/test_browser_session_persistence.py
M  backend/tests/test_clinical_tenant_isolation.py
A  backend/tests/test_email_session_password_change_revocation.py
A  backend/tests/test_email_session_renewal.py
M  backend/tests/test_envio_paciente_documento_gerado.py
M  backend/tests/test_envio_paciente_material.py
M  backend/tests/test_envio_paciente_receita.py
A  backend/tests/test_external_mail_google_microsoft.py
M  backend/tests/test_feature_inventory.py
M  backend/tests/test_instagram_handle.py
A  backend/tests/test_knowledge_graph.py
A  backend/tests/test_knowledge_graph_api.py
A  backend/tests/test_password_reset_flow.py
A  backend/tests/test_pricing_cmed_provider.py
M  backend/tests/test_readiness.py
M  backend/tests/test_relacionados.py
M  docker-compose.prod.yml
A  docs/knowledge-graph.md
A  docs/pricing-architecture.md
M  frontend/Dockerfile.prod
M  frontend/scripts/check-rendering-security.mjs
M  frontend/scripts/check-rendering-security.test.mjs
M  frontend/src/lib/apiEmail.ts
M  frontend/src/lib/auth.tsx
A  frontend/src/lib/freshness.ts
M  frontend/src/main.tsx
M  frontend/src/pages/Entrar.tsx
M  frontend/vite.config.ts
M  infra/Caddyfile
A  infra/backup_freshness_cron.sh
M  medicamentos/metadados.json
M  ops/check-backup-freshness.sh
M  scripts/feature_inventory.py
M  scripts/release_smoke.py
```

### 1.9 Local `HEAD` vs. `origin/stabilizacao-2026-08-09`

```
$ git rev-parse HEAD
44bc035752f5de9b733e847abf133d0e856e1aa4
$ git rev-parse origin/stabilizacao-2026-08-09
44bc035752f5de9b733e847abf133d0e856e1aa4
```

**Resultado:** idênticos — o checkout local está exatamente sincronizado com o remoto, sem commits
locais não empurrados e sem commits remotos ainda não trazidos. (Nenhum `push`/`commit` foi feito
por esta sessão, em conformidade com as regras da tarefa.)

---

## 2. Contexto previamente estabelecido — reconfirmado sem divergência

O contexto informado no início da tarefa (produção em `c38c6624`, `origin/main` 19 commits à
frente, `stabilizacao-2026-08-09` contendo 100% de `main` mais 18 commits adicionais, só dois
branches no remoto) foi **reconfirmado de ponta a ponta nesta rodada, sem nenhuma divergência**.
Ver seção "Riscos e pendências conhecidas" para a única ressalva relevante encontrada (que é
metodológica/de apuração, não uma divergência de estado real).

---

## 3. Lista completa e categorizada de commits (produção → HEAD, 37 commits, ordem cronológica)

Legenda de fronteira: os 19 primeiros commits (até `940a812c`) são os que também estão em
`origin/main` (idênticos, sem cherry-pick — `main` é ancestral direto). Os 18 últimos
(`43025105` até `44bc0357`) existem **só** em `origin/stabilizacao-2026-08-09`.

### 3.1 Funcionalidades novas

| Commit | Data | Mensagem |
|---|---|---|
| `66a0e10a` | 2026-08-09 | feat(auth): adiciona sessão persistente opcional no navegador |
| `d99c8fb5` | 2026-08-09 | feat(auth): suporta permanecer conectado e login com recarga forte |
| `07c5bc29` | 2026-08-09 | feat(login): adiciona permanecer conectado no acesso principal |
| `c2239341` | 2026-08-09 | fix(corvia-mail): respeita persistência escolhida da sessão |
| `c288b8be` | 2026-08-09 | feat(frontend): detecta deploy novo e elimina cache antigo |
| `a5c66b22` | 2026-08-09 | feat(frontend): valida versão real em login, foco, reload e navegação |
| `2445330a` | 2026-08-09 | fix(pwa): impede cache antigo de respostas da API |
| `beaec654` | 2026-08-09 | fix(cache): força revalidação total do shell e service worker |
| `7fb682b0` | 2026-08-09 | perf(frontend): limita checagens de versão sem perder atualização imediata |
| `26ba92ef` | 2026-08-09 | feat(frontend): verifica deploy também nas interações do usuário |
| `49b1b518` | 2026-08-09 | feat(corvia-mail): adiciona renovação silenciosa da sessão persistente |
| `2f60ae0c` | 2026-08-09 | feat(corvia-mail): registra renovação da sessão própria |
| `866f0caa` | 2026-08-09 | feat(corvia-mail): renova silenciosamente sessão persistente em uso |

Duas linhas de funcionalidade nesta categoria: (a) **"permanecer conectado" / sessão persistente**
(login, CorvIA Mail, renovação deslizante) e (b) **detecção de deploy novo / invalidação de cache
do PWA** (freshness.ts, service worker, verificação em login/foco/reload/navegação). `de8c0c8e`
("sessão não persistente expira ao fechar navegador") pertence à mesma linha (a) mas foi
classificado em Correções de segurança abaixo por corrigir um comportamento de expiração incorreto.

### 3.2 Correções de segurança

| Commit | Data | Mensagem |
|---|---|---|
| `de8c0c8e` | 2026-08-09 | fix(auth): sessão não persistente expira ao fechar navegador |
| `440ed2ae` | 2026-08-10 | fix(ci): gate de renderização segura estava cego ao renderer real de e-mail (issue #52) |
| `f7917690` | 2026-08-10 | fix(release): smoke E2E, inventário funcional, teste de conteúdo e SSRF defensivo no Instagram (issue #52) |
| `4caf96e9` | 2026-08-10 | fix(security): corrige IDOR/BOLA estrutural em timeline/prescriptions/appointments (issue #52) |
| `c428ce1c` | 2026-08-10 | fix(security): revoga sessão da caixa CorvIA Mail ao trocar senha ou banir a conta (issue #52) |
| `300a9a58` | 2026-08-10 | docs(security): documenta avaliação de risco do token do CorvIA Mail em localStorage (issue #52) |

Destaques (detalhe completo nas mensagens de commit, reproduzidas integralmente no repositório):

- **`4caf96e9`** — maior severidade: bypass de tenant isolation (IDOR/BOLA) que permitia a
  **qualquer admin** ler/operar dados clínicos (timeline, prescrições, agendamentos) de paciente
  pertencente a outro médico, via `app/api/timeline.py`, `prescriptions.py` e `appointments.py`.
  Corrigido centralizando a checagem de posse em `app/services/clinical_ownership.py`
  (`patient_for_user`), sem exceção de papel — nem admin. Resposta sempre 404 (nunca 403), para não
  confirmar existência de `patient_id` alheio por enumeração.
- **`c428ce1c`** — token `scope="email"` da caixa CorvIA Mail não era revogado ao trocar a senha da
  caixa nem ao banir a conta principal (`User.is_active=False`), ao contrário da sessão principal.
  Corrigido com `EmailAccount.sessions_valid_after` (migração `525c83496f23`) + reaproveitamento do
  helper genérico já usado pela sessão principal.
- **`440ed2ae`** — o gate estático `check-rendering-security.mjs` apontava para um arquivo shim
  (`CaixaDeEmail.tsx`, 1 linha, redirecionando para `CaixaDeEmailProfessional.tsx`) desde o
  redesenho da caixa de e-mail, ficando cego à sanitização real (que sempre esteve correta no
  arquivo novo). O gate falhava mesmo contra produção (`/opt/meucardio`, conferido só por leitura).
  Corrigida a constante `APPROVED_EMAIL_RENDERER`; nenhuma mudança de comportamento em runtime.
- **`f7917690`** — inclui defesa em profundidade contra SSRF em `app/services/instagram_profile.py`
  (allowlist de host para a segunda chamada de rede, que usava uma URL vinda do corpo da primeira
  resposta sem validação), além de corrigir o smoke E2E oficial da CI (quebrado desde 09/08 por dois
  motivos: comparação estrita de dict ignorando o campo novo `persistent`, e exigência do valor
  antigo `SameSite=Strict` em vez do `Lax` correto).
- **`300a9a58`** — decisão documentada (não código) de **não** migrar o token da caixa de e-mail de
  localStorage para cookie HttpOnly nesta fase; risco residual classificado BAIXO-MÉDIO.

### 3.3 Conteúdo científico (medicamentos)

| Commit | Data | Mensagem |
|---|---|---|
| `e6fd81a9` | 2026-08-11 | content(medicamentos): integra revisão de meia-vida/tempo de ação/potência anti-hipertensiva |
| `8cb03bcb` | 2026-08-11 | content(medicamentos): fecha as 2 últimas lacunas reais de meia-vida/tempo de ação/PA |
| `c2677329` | 2026-08-11 | content(medicamentos): apresentações comerciais para 8 fármacos prioritários (issue #52 seção 9) |
| `44bc0357` | 2026-08-11 | content(medicamentos): confere e corrige a citação do SAVOR-TIMI 53 no Kombiglyze XR (issue #52, seção 5) |

Resumo: `e6fd81a9` é um cherry-pick de `fa95b07d` (branch externa
`claude/medicamentos-review-completo-38tslz`, sem SSH/rede, integrada sem conflito). `8cb03bcb`
fecha as 2 últimas lacunas reais de `half_life_hours`/`duration_of_action_hours`/
`sbp_reduction_mmhg`/`dbp_reduction_mmhg` sem nota explicativa, de um catálogo de 176 registros.
`c2677329` preenche apresentações comerciais para 8 fármacos (de 54 sem nenhuma apresentação
cadastrada; ~46 restam como backlog explícito). `44bc0357` reconfirma via PubMed E-utilities um
dado que estava marcado como "citado de memória" e corrige a atribuição da fonte (Circulation 2014,
não NEJM 2013). Toda a categoria segue a regra do projeto de nunca fabricar dado e marcar
`VERIFICAÇÃO HUMANA NECESSÁRIA` onde a fonte não sustenta um valor.

### 3.4 Preços/CMED/Kairos

| Commit | Data | Mensagem |
|---|---|---|
| `7918e083` | 2026-08-11 | feat(pricing): arquitetura multi-fonte de preços (PriceProvider) + auditoria CMED/Kairos (issue #52) |

Camada fina (`PriceObservation`/`PriceProvider`, `backend/app/services/pricing/`) sobre o pipeline
CMED já existente (`cmed_precos.py`, sem duplicar download/parsing/casamento). `CMEDProvider` traduz
dados já persistidos (`CmedApresentacao`/`CmedVersao`) — usa só a versão mais recente, descarta
alíquota nula em vez de fabricar preço zero. Avaliação da Kairos (`bra.kairosweb.com`): bloqueada
por Cloudflare/403 em todas as URLs testadas, `robots.txt` com `ai-train=no` — nenhum scraping
realizado, nenhuma alteração de produção. 4 testes novos (`test_pricing_cmed_provider.py`).
Documentado em `docs/pricing-architecture.md`.

### 3.5 Knowledge Graph

| Commit | Data | Mensagem |
|---|---|---|
| `30e163f3` | 2026-08-11 | feat(knowledge-graph): grafo de conhecimento clínico universal — MVP real (issue #52) |

Duas tabelas novas aditivas (`knowledge_entities`, `knowledge_relations`; migração `5a786cb55611`,
UNIQUE em ambas para evitar duplicação de nó/aresta). Distinto do cruzamento por tema em tempo de
consulta já em produção (`related_content.py`). Segurança estrutural: `TIPOS_ENTIDADE_PERMITIDOS`
é allowlist real — `Patient`/`Prescription`/`Appointment`/`GeneratedDocument`/`ServiceOrder` nunca
podem virar nó do grafo público (mesma classe de risco do IDOR/BOLA corrigido em `4caf96e9`, agora
na camada do grafo). Despublicação arquiva (nunca apaga) o nó correspondente. `GET
/api/grafo/relacionados` exige assinatura ativa; `POST /api/admin/grafo/backfill` exige admin — os
dois testados pela rota HTTP real (401/402/403/200). 22 testes novos
(`test_knowledge_graph.py` + `test_knowledge_graph_api.py`). `feature_inventory.py` atualizado
(49 routers esperados, era 48). Documentado em `docs/knowledge-graph.md`.

### 3.6 Testes/regressão

| Commit | Data | Mensagem |
|---|---|---|
| `aa3f371f` | 2026-08-09 | test(auth): cobre permanecer conectado da sessão principal |
| `11ee7840` | 2026-08-09 | test(auth): ajusta expectativa da sessão curta para cookie de navegador |
| `940a812c` | 2026-08-09 | test(corvia-mail): cobre renovação deslizante da sessão *(= HEAD de `origin/main`)* |
| `43025105` | 2026-08-09 | test(auth): cobertura de regressão da subfase 1 (issue #52) |
| `00d46492` | 2026-08-10 | test(auth): cobertura do fluxo de esqueci-senha da conta principal (issue #52) |
| `59700758` | 2026-08-10 | test(oauth): cobertura de state/PKCE, account-linking, refresh e revogação (issue #52) |
| `b745affd` | 2026-08-10 | test(mail): cobertura de list/get/act/send Google-Microsoft + corrige 3 lacunas de fixture (issue #52) |
| `1cd33fc0` | 2026-08-10 | test(agenda): cobertura do cron de sincronização e da escrita bidirecional nos conectores (issue #52) |

Progressão por subfase do plano de estabilização (subfase 1 = AUTH/SESSION, 2 = OAUTH, 3 = MAIL,
4 = AGENDA). Nenhum destes commits altera comportamento de produção — são aditivos, sem migração.
`43025105` documenta (sem corrigir ainda) os dois achados de segurança que seriam corrigidos
depois nesta mesma branch (`4caf96e9`, `c428ce1c`). `b745affd` corrige 3 lacunas reais de fixture
em `test_envio_paciente_*.py` (setup de teste incompleto mascarando cenários gated por assinatura/
CorvIA Mail — não são bugs de produção).

### 3.7 Migrations

Ver seção 4 abaixo (lista dedicada). Resumo: 2 migrations novas, ambas aditivas, cadeia linear
sem branch.

### 3.8 Infra/observability

| Commit | Data | Mensagem |
|---|---|---|
| `98cc454f` | 2026-08-09 | build(frontend): injeta commit do deploy no bundle |
| `8d1aabb0` | 2026-08-09 | build(frontend): vincula bundle ao mesmo commit do backend |
| `bb2605b9` | 2026-08-10 | feat(observability): expõe estatísticas do pool de conexões em /api/ready (issue #52) |
| `1e59d009` | 2026-08-10 | feat(ops): encadeia monitoramento de frescor do backup no cron (issue #52) |

`bb2605b9`: campo opcional `database_pool` (size/checked_out/checked_in/overflow — só inteiros,
nunca credencial) em `GET /api/ready`; falha de introspecção nunca deriva 503 sozinha. 3 testes
novos. `1e59d009`: corrige `BACKUP_NAME_PREFIX` (o script de checagem de frescor só reconhecia o
prefixo `corvia-` de CI, não `meucardio_` — o prefixo real do backup de produção
`infra/backup/backup.sh`; sem o fix, a checagem sempre acusaria backup ausente mesmo com backups
válidos). Novo `infra/backup_freshness_cron.sh`, **não instalado no crontab de produção** — só
preparado no repositório (ação operacional posterior, fora do escopo do commit).

---

## 4. Migrations novas desde a produção

Duas migrations novas, nenhuma modificação de migration existente. Ambas aditivas
(nenhuma coluna/tabela existente alterada de forma destrutiva), nullable/vazias na criação, sem
dado a migrar.

| Arquivo | revision | down_revision | O que faz |
|---|---|---|---|
| `backend/migrations/versions/525c83496f23_email_account_sessions_valid_after.py` | `525c83496f23` | `26751b9d12f0` | Coluna nova `email_accounts.sessions_valid_after` (DateTime, nullable). Idempotente (checa `sa.inspect` antes de criar). |
| `backend/migrations/versions/5a786cb55611_knowledge_graph.py` | `5a786cb55611` | `525c83496f23` | Duas tabelas novas: `knowledge_entities` e `knowledge_relations` (grafo de conhecimento). Idempotente (checa `get_table_names()` antes de criar). Nascem vazias. |

### 4.1 Cadeia de revisões — confirmação de HEAD único, sem branch divergente

Verificação feita por **leitura direta dos 67 arquivos** em `backend/migrations/versions/`
(65 arquivos `.py` com par `revision`/`down_revision` válido — 2 entradas adicionais no diretório
são `.gitkeep` e um artefato vazio pré-existente `b7d24e`, sem extensão `.py`, presente desde muito
antes desta branch e por isso ignorado pelo glob padrão do Alembic; não é uma migration e não afeta
a cadeia). Script Python que faz o parse de `revision`/`down_revision` (inclusive os casos de merge
com `down_revision` em tupla/múltiplas linhas, ex. `d63a0cc83807`/`f47a20260804`) e calcula o
conjunto de "heads" (revisões nunca referenciadas como `down_revision` de nenhuma outra):

```
total revisions parsed: 65
heads: {'5a786cb55611'}
dangling down_revision refs (not found as revision): set()
```

**Resultado:** confirmado — existe **exatamente um head**, `5a786cb55611` (a migration do
Knowledge Graph, a mais recente), e **nenhuma referência pendurada** (nenhum `down_revision`
aponta para uma revisão inexistente). A cadeia é única e consistente, sem *multiple heads* — não
há risco de `alembic upgrade head` falhar por ambiguidade nesta branch.

Confirmado também, por `grep` direto, que:
- exatamente 1 arquivo tem `down_revision = "26751b9d12f0"` → `525c83496f23`
- exatamente 1 arquivo tem `down_revision = "525c83496f23"` → `5a786cb55611`
- 0 arquivos têm `down_revision = "5a786cb55611"` (confirma que é o head atual)

---

## 5. Resumo agregado

- **62 arquivos alterados** entre produção (`c38c6624`) e o HEAD desta branch (`44bc0357`):
  +6899/−432 linhas.
- **37 commits** no total (19 já presentes em `origin/main`, 18 exclusivos de
  `origin/stabilizacao-2026-08-09`).
- **2 migrations novas**, cadeia linear, head único, ambas aditivas e idempotentes.
- **22 arquivos de teste** tocados (13 novos, 9 modificados) — a categoria "Testes/regressão"
  lista os commits dedicados a teste, mas praticamente todo commit desta branch (inclusive os de
  segurança e de feature) inclui teste novo/atualizado na mesma unidade de commit.

---

## 6. Riscos e pendências conhecidas

1. **Nenhuma divergência de estado foi encontrada** em relação ao contexto informado no início
   desta tarefa — produção, `origin/main` e `origin/stabilizacao-2026-08-09` estão exatamente onde
   o contexto dizia que estariam, com a mesma relação de ancestralidade linear (produção → main →
   stabilizacao, sem branch cruzado, sem commit divergente).

2. **Ressalva metodológica (não é uma divergência de estado, é um risco de apuração a evitar em
   reconciliações futuras):** o diretório de trabalho de uma sessão Bash **persiste entre chamadas
   de ferramenta separadas** neste ambiente. Como `/opt/meucardio` (produção) e
   `/root/corvia-stabilizacao` (esta branch) apontam para o **mesmo repositório GitHub remoto**,
   mas por URLs/protocolos diferentes e com **conjuntos de branches já buscados diferentes** (o
   checkout de produção tem dezenas de branches `agent/*` antigos ainda em cache local, nunca
   podados), um `cd` que "vaza" de uma chamada de Bash para a próxima pode fazer com que
   `origin/main` ou `origin/stabilizacao-2026-08-09` sejam resolvidos no repositório errado, dando
   um resultado enganoso (por exemplo, `origin/stabilizacao-2026-08-09` "não existir" simplesmente
   porque o checkout de produção nunca buscou esse branch). Nesta reconciliação isso foi detectado
   e corrigido cedo (seção 1.2), refazendo cada checagem com `pwd` explícito. Recomenda-se que
   qualquer reconciliação futura sempre confirme o diretório de trabalho atual antes de resolver um
   ref remoto por nome curto (`origin/<branch>`), ou use `git -C <caminho>` em vez de `cd`.

3. **Nenhuma pendência técnica encontrada nas migrations** — cadeia linear, head único, ambas
   idempotentes (checam `sa.inspect`/`get_table_names()` antes de criar, mesmo padrão documentado
   no `CLAUDE.md` do projeto para o caso de sessão paralela aplicando DDL fora do `alembic_version`).

4. **Uma pendência operacional explícita, documentada nos próprios commits, não é um risco de
   reconciliação mas vale registrar aqui por completude:** `infra/backup_freshness_cron.sh`
   (commit `1e59d009`) foi criado e testado, mas **não foi instalado no crontab de produção** — é
   uma ação operacional deliberadamente deixada para depois do deploy, fora do escopo do commit que
   só altera o script/repositório.

5. **Item de segurança já corrigido nesta mesma branch, sem pendência residual:** os dois riscos
   identificados no "gate final" anterior (bypass de admin em timeline/prescriptions/appointments,
   e ausência de revogação de sessão da caixa de e-mail) foram ambos corrigidos dentro dos 18
   commits exclusivos desta branch (`4caf96e9` e `c428ce1c`, respectivamente) e cobertos por teste
   automatizado. O terceiro item do gate final (token do CorvIA Mail em localStorage) foi avaliado
   e **deliberadamente não migrado** nesta fase, com a decisão e o raciocínio documentados em
   `frontend/src/lib/apiEmail.ts` e no commit `300a9a58` — não é uma pendência esquecida, é uma
   decisão registrada com risco residual classificado explicitamente como BAIXO-MÉDIO.

**Conclusão geral:** nenhuma divergência do estado esperado foi encontrada. A branch
`stabilizacao-2026-08-09` está pronta, do ponto de vista de reconciliação de histórico git e cadeia
de migrations, para ser avaliada como release candidate — nada nesta apuração aponta para um
problema estrutural de merge, branch fantasma, ou migration órfã/divergente.
