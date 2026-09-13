# Auditoria rápida do CorVIA — 13/09/2026

Varredura de erros de programação, visuais e de funcionalidade em todo o sistema.
Base auditada: `main` em `524528b` (branch `claude/corveia-audit-yda469`).
Frontend 37,4k linhas (TS/TSX) · backend 85,5k linhas (Python) · 517 rotas de API · 93 declarações de rota de tela.

**Método — medido, não inferido.** Postgres 16 + pgvector instalado localmente,
`alembic upgrade head` aplicado, dependências instaladas em venv limpo, `npm ci`
real. Todos os números abaixo vêm de execução ou de varredura por AST/script, não
de leitura superficial. Cada hipótese foi confirmada antes de virar achado — e três
suspeitas iniciais foram **descartadas** por verificação (registradas no fim).

---

## 🔴 1. 76% das suítes de contrato do frontend nunca são executadas — e 18 asserções estão vermelhas há um dia

O achado mais importante da auditoria, porque explica todos os outros.

**O repositório tem 54 suítes `scripts/check-*.test.mjs`. Só 13 rodam** — 8 citadas
nominalmente em `.github/workflows/ci.yml` e 5 alcançadas por `npm run` na CI ou pelo
`prebuild`. **41 nunca executam**, nem na CI, nem no build, nem em nenhum workflow.

A CI lista arquivo por arquivo (`run: node --test scripts/check-rendering-security.test.mjs`)
em vez de usar um glob — então toda suíte nova nasce fora da CI por padrão.

Entre as 41 que nunca rodam estão garantias sensíveis:
`check-patient-timeline-isolation`, `check-prontuario-context-isolation`,
`check-clinical-cache-safety`, `check-commercial-plans`, `check-heart-team-budget`,
`check-search-flow`.

**Consequência já materializada.** Rodando as 54 localmente: **435 passam, 18 falham**.
As 18 falhas têm uma causa única e datada:

O commit **`d1f28d6`** — *"fix: publish audited CorVIA corrections **[skip ci]** [code-only-deploy]"*,
12/09/2026 — criou `frontend/src/lib/loginReturn.ts` e acrescentou
`import { clearLoginReturn, saveLoginReturn } from "./loginReturn"` em `src/lib/api.ts`.
Quatro suítes montam `api.ts` dentro de um `vm` com stub manual de `require`, e nenhuma
foi atualizada para conhecer o módulo novo:

| Suíte | Falhas | Erro |
|---|---:|---|
| `check-research-loading-recovery.test.mjs` | 10 (arquivo inteiro) | `MODULE_NOT_FOUND: './loginReturn'` |
| `check-password-recovery.test.mjs` | 4 | idem |
| `check-clinical-cache-safety.test.mjs` | 3 | stub genérico devolve o módulo errado → `clearLoginReturn is not a function` |
| `check-guidelines-radar-isolation.test.mjs` | 1 (arquivo inteiro) | fixture gravada em `/tmp/…` resolve `../lib/api` para `/tmp/lib/api` |

O código de produção está **correto** — `tsc --noEmit` passa, `clearLoginReturn` existe e
é exportado, `api.logout()` funciona. O que quebrou foi o andaime de teste. Mas o efeito
prático é que estas garantias deixaram de ser verificadas:

- logout limpa o cache clínico **mesmo com a rede falhando**;
- falha do Cache Storage **não impede** o logout local;
- link de ativação preserva token/query/hash e não dispara reset sem token;
- deadline de GET aborta o transporte; resposta atrasada não repovoa a tela errada.

**20 dos últimos 200 commits carregam `[skip ci]`** (10%) — inclusive o que quebrou isto.

**Correção sugerida (ordem de valor):**
1. Trocar a lista nominal do `ci.yml` por `node --test scripts/*.test.mjs` (ou um job que
   varra o diretório), para que suíte nova entre na CI sozinha.
2. Ensinar os 4 stubs a resolver `./loginReturn` (3 linhas cada).
3. Restringir `[skip ci]` a commits que só tocam conteúdo — este tocou 40+ arquivos de código.

---

## 🔴 2. Elementos renderizados sem nenhuma regra de CSS — inclusive no menu lateral do desktop

Cruzando toda classe escrita em `className="..."` contra toda regra dos 121 CSS
importados (e depois contra o **bundle já compilado**, para não confiar só na fonte):
**124 elementos em que nenhuma das classes tem qualquer regra**. Descontando os ~85 da
página morta `TourClinicalOS` (item 6), sobram defeitos em superfícies vivas:

**a) Menu lateral do desktop — `components/ClinicalDesktopNav.tsx`, renderizado por
`Shell.tsx:28` em toda página autenticada.** As classes irmãs são bem cuidadas
(`.ccc-nav__item` tem 26 regras, `.ccc-nav__brand` 25, `.ccc-nav__scroll` 3), mas
**cinco não têm nenhuma**:

| Classe | Linha | O que fica sem estilo |
|---|---|---|
| `ccc-nav__space-head` | 210 | cabeçalho "NO ESPAÇO / {espaço}" no topo da barra |
| `ccc-nav__context-actions` | 214 | grupo de ações contextuais do espaço |
| `ccc-nav__catalog` | 216 | o `<details>` "Todas as funções" — abre com o triângulo padrão do navegador |
| `ccc-nav__catalog-panel` | 218 | o painel `role="dialog"` com o catálogo completo — sem posicionamento, sem sobreposição |
| `ccc-nav__catalog-grid` | 220 | a grade de funções — vira pilha vertical crua |
| `ccc-nav__catalog-section` | 174 | cada seção dentro da grade |

Entrou no commit **`9046ee8`** — *"fix: eliminate progressive galaxy loading… **[skip ci]**"*.

**b) `.subtitulo` — 8 páginas roteadas, zero regra em todo o bundle.** Casos clínicos,
Checklists (lista, modelo e alta), Exportar conteúdo, Material do paciente (lista e
detalhe) e Trilha usam `<p className="subtitulo">` para o texto de apoio abaixo do
título; ele renderiza como parágrafo padrão do navegador.

**c) `.tag` — 4 usos em `pages/Assinatura.tsx`** (L78, 79, 80, 103), zero regra. Os selos
de plano da página comercial saem sem forma.

**d) Outros, todos confirmados com 0 regra no bundle:**
`corvia-chat-panel__unread` (contador de não lidas do chat flutuante),
`ia__carregando` (estado de carregamento do Assistente),
`patient-prescription-history` + `__actions` (histórico de prescrição à beira do leito),
`cai-history-detail` (Heart Team Virtual), `cai-admin-ai` (Admin · Operações de IA),
`lista-simples` / `item-lista` / `stack` (ScientificDocumentAI),
`tct-disease-overview`, `cv-section__copy`, `agenda-config-form--mobility`,
`scientific-intelligence-monitor__documents`, `scientific-reading-access__source`,
`scientific-reading-access__coverage`, `cst-at__previous`, `corvia-word-cor`.

Verificação: `grep` da classe em `dist/assets/*.css` depois de `vite build` — nenhuma
delas chega ao CSS publicado. (`.mermaid`/`.fluxograma` aparecem na lista mas são
estilizadas pelo próprio mermaid, não é defeito.)

---

## 🟠 3. Menu "Cursos" visível em duas superfícies, mas a rota é só um redirect

`App.tsx:34-37` declara a intenção explicitamente:

> *"o módulo legado continua conhecido pelo bundle, mas não possui mais ponto de entrada
> no produto. As URLs /cursos* redirecionam para Trilhas abaixo **e os shells não exibem a opção**."*

A segunda metade da frase não é verdade:

| Onde | Linha | O que mostra |
|---|---|---|
| `components/ShellClinicalOSLaunch.tsx` | 69 | `{ to: "/cursos", rotulo: "Cursos", icone: "curso" }` — e o componente é renderizado por `Shell.tsx:30` |
| `pages/PainelClinicalOS.tsx` | 87 | `{ to: "/cursos", label: "Cursos & Atualizações", icon: "curso" }` |
| `pages/Curso.tsx` | 80 | `<Link to="/cursos">← Todos os cursos</Link>` (página que também não tem rota) |

`App.tsx:259-260`: `<Route path="cursos" element={<Navigate to="/trilhas" replace />} />`.

No launcher, **"Trilhas" e "Cursos" aparecem lado a lado no mesmo grupo "Conhecimento"**,
e os dois levam ao mesmo lugar. É exatamente o "botão que não faz nada" que a régua do
projeto proíbe.

---

## 🟠 4. Duas telas refazem requisição sem cancelar a anterior (resposta atrasada sobrescreve a atual)

Classe de bug que o próprio repositório já cobre em outras telas
(`check-clinical-error-recovery.test.mjs`: *"case detail: changing slug discards delayed content"*),
mas que passou batido nestas duas.

**`pages/AdminAssinantes.tsx:131`** — `useEffect(..., [filtros])`:
```
api.get<ListaResposta>(`/admin/usuarios?${params}`)
  .then(setResposta)
  .catch(...)
  .finally(() => setCarregando(false));
```
Sem `AbortController` nem flag de cancelamento. Há debounce de 400 ms só no campo de
busca; **paginação e os 6 filtros de select disparam direto**. Dois efeitos reais:
uma resposta lenta da página 1 pode sobrescrever a página 2 já renderizada, e o
`.finally()` de um pedido obsoleto apaga o estado "carregando" do pedido em voo.

**`pages/GuiaDoencas.tsx:120`** — `useEffect(..., [area, clinicalDomain, tab])`:
```
api.get<DiseaseFacetsResponse>(`/specialty-guides/disease-facets${search}`)
  .then(setDiseaseFacets)
  .catch(() => setDiseaseFacets({ areas: [], clinical_domains: [], categories: [] }));
```
Trocar de aba rápido pode deixar a aba atual com as facetas da anterior. Pior: o `.catch`
**zera** as facetas — um erro atrasado de um pedido já descartado apaga os filtros
válidos da aba que o médico está vendo.

---

## 🟡 5. Funcionalidades de backend sem porta de entrada na interface

Cruzando as 517 rotas contra todas as chamadas do frontend (descontando admin, webhook,
OAuth e health): **68 rotas de produto sem nenhuma referência na UI** (10 delas do Telediagnóstico, desligado de propósito). As que afetam
diretamente o assinante:

| Rota | O que o usuário não consegue fazer |
|---|---|
| `POST /api/auth/reenviar-ativacao` | pedir novo e-mail de ativação se o primeiro não chegou |
| `POST /api/auth/encerrar-todas-sessoes` | encerrar todas as sessões (segurança de conta) |
| `GET`/`PUT /api/auth/email-recuperacao` | ver ou trocar o e-mail de recuperação |
| `GET /api/diretrizes/meus-alertas` | ver os alertas de atualização de diretriz |
| `GET /api/heart-team/usage` · `GET /api/mail360-status` | consumo do Heart Team, saúde da caixa |
| `GET /api/favorites/types` · `DELETE /api/favorites/by-slug/...` | contrato de favoritos parcialmente ligado |

`/api/diretrizes/meus-alertas` confirma um item que o próprio `CLAUDE.md` já registra como
pendência da Tarefa 9 ("backend pronto, sem tela") — continua assim.

**Telediagnóstico** (10 rotas) está desligado de propósito: `Telediagnostico.tsx` é uma
página de 17 linhas com "Em breve / temporariamente indisponível". Não é bug — mas o
Painel lista o item **duas vezes** ("Telediagnóstico" e "Consultoria / Telediagnóstico"),
as duas levando ao aviso de indisponível.

---

## 🟡 6. Código morto acumulado e fragilidade de cascata no CSS

- **18 arquivos CSS (6.791 linhas) não são importados por nenhum módulo** — entre eles
  `cardiology-spaces-login.css` (2.243 linhas) e mais 4 variantes de login
  (`*-approved-final`, `*-production-approved`, `*-fidelity-20260905`, `*-final-approved-20260904`).
  Verificado que não há `@import` em nenhum CSS e que as classes exclusivas desses arquivos
  não chegam ao bundle.
- **6 componentes sem nenhuma referência**: `LoginGalaxy` (137), `GrafoConstelacao` (134),
  `ClinicalFunctionFigure` (109), `CursoDestaque` (92), `MiniUniverseCanvas` (88),
  `ScientificTimelineCard` (63).
- **2 páginas sem rota**: `TourClinicalOS` (313 linhas), `ECGQuickOpinion` (241 linhas).
- **139 arquivos CSS com 7.075 `!important`**, muitos em camadas de sobreposição
  (`*-hotfix`, `*-pending-fixes`, `*-final-approved`, `*-polish`). Não é bug hoje, mas é o
  fator que mais eleva o risco de regressão visual a cada mudança.
- `pages/PainelClinicalOS.tsx`: "Modo apresentação" aparece duas vezes com **rótulo idêntico**
  (L88 e L109). As outras 4 repetições de destino têm rótulos diferentes e parecem
  cross-listing intencional.

---

## ⏳ Suíte backend — execução em andamento quando este arquivo foi commitado

A suíte de 3.912 testes do backend está rodando em banco dedicado (`meucardio_audit`),
sem concorrência. O que já se pode afirmar com segurança:

- **coleta limpa**: 3.912 testes coletados, **0 erro de import** em 75 módulos de API;
- `alembic upgrade head` aplicou as 103 migrações do zero, sem erro;
- **0 drift** entre os modelos e o schema migrado.

O número final de passa/falha será acrescentado aqui quando a corrida terminar. Há um
bloco de erros reincidente por volta de 9% da execução (região de
`test_apresentacao_pptx` / `test_aprofundamento_*`) que **reaparece na corrida limpa** —
ou seja, não é artefato da contaminação descrita na nota de método. Ainda não
diagnosticado; não afirmo causa sem medir.

---

## ✅ O que foi auditado e está saudável (verificado, não presumido)

**Compilação e build**
- `tsc --noEmit`: limpo (0 erro em 37,4k linhas de TS/TSX).
- `vite build`: sucesso; `check-bundle-budget` (entry 307 kB / 96 kB gzip) e
  `check-route-splitting` (80 páginas lazy) aprovados.
- `python -m compileall backend/app`: limpo.

**Segurança e integridade do backend**
- 0 `except:` nu · 0 argumento mutável como default · 0 `datetime.utcnow()` naive
  (todos os `utcnow()` são helpers locais com timezone).
- 0 SQL montado por f-string com entrada do usuário — os f-strings de `catalog_search.py`
  interpolam só nomes de coluna; a consulta do usuário entra por bindparam `:q`.
- **0 sombreamento de rota** no FastAPI (a armadilha `/{slug}` antes de `/timeline`).
- As 7 colisões de rota (`email` × `email_multibox`, `admin` × `account_access_admin`,
  `patient_profiles` × guard multimodal, `agenda_integrada` × `account_sync`,
  `admin_user_management` × `admin_user_delete`) são **overrides documentados**, e a ordem
  de `include_router` em `main.py` confere com a intenção em todos os casos.
- Auditadas as rotas dos routers sem `assinante_ativo`: as 31 sem dependência de auth
  aparente são públicas por desenho (login, reset, webhook, health, documento público por
  token). `POST /api/email/conta` e `/conectar-yahoo` autenticam por
  `bloquear_investidor_em_operacao_real_de_mail`, que embrulha `current_user`.
- **0 endpoint** faz `db.get(Model, id)` em modelo com dono (67 modelos têm
  `owner_id`/`user_id`/`created_by`) sem checagem de propriedade no corpo.

**Banco e migrações**
- 103 migrações, **1 head único** (`c3ca20260910`), grafo íntegro, nenhum
  `down_revision` órfão; `alembic upgrade head` aplicou do zero sem erro.
- **0 drift entre modelos e schema**: 125 tabelas do ORM, 0 tabela faltando,
  0 coluna faltando.

**Frontend**
- **0 link interno quebrado**: todos os `to=` / `href=` / `navigate()` internos batem com
  alguma rota de `App.tsx`. Registro de rotas em paridade exata (78 padrões autenticados).
- 0 `dangerouslySetInnerHTML`/`innerHTML` inseguro; o HTML de e-mail é isolado em iframe
  com CSP `default-src 'none'`. `check-rendering-security` aprovado.
- 0 hook condicional · 0 `.map()` renderizando lista sem `key` · 0 `console.log` em produção.
- Checagens do próprio repo aprovadas: contraste de formulário, contraste do login,
  ciclo de vida da câmera, armazenamento de sessão sem JWT exposto, ficha do assinante.

---

## 🔍 Três suspeitas levantadas e DESCARTADAS por verificação

Registradas para ninguém refazer o caminho:

1. **"O Modo Emergência perdeu o offline."** `vite.config.ts` de fato passou `/api/` inteiro
   para `NetworkOnly` (decisão correta: dado clínico não pode persistir em cache do
   navegador). Mas `Emergencia.tsx:37-50` mantém cópia própria em `localStorage`, com selo
   "Sem conexão · cópia de {data}" na tela. A garantia continua de pé, por outro mecanismo.
2. **"`GET /api/whatsapp-assistant/metrics` está duplicado e a versão admin é inalcançável."**
   Falso positivo de detector: `metrics` está em `router` (prefixo `/api/whatsapp-assistant`)
   e `admin_metrics` em `admin_router` (prefixo `/api/admin/whatsapp`) — caminhos diferentes.
3. **"O canvas da galáxia do login está sem CSS."** `.login-gateway__galaxy-canvas` é
   definida só em 3 CSS órfãos e não chega ao bundle — mas `LoginGalaxy.tsx` também não é
   renderizado por ninguém. É código morto (item 6), não defeito visível.

---

## Nota sobre o repositório `corviabackup`

É um snapshot parado em **03/08/2026** (`069c464`), ~6 semanas atrás: não tem
`account_sync`, `admin_user_management`, `agenda_clinica`, `agenda_integrada` nem dezenas
de outros módulos hoje em produção. Como backup histórico está coerente; **não deve ser
usado como referência do estado atual** por nenhuma sessão.

---

## Limites desta auditoria — o que NÃO foi coberto

Declarado para que ninguém leia "auditado" onde não foi:

- **Não houve inspeção visual ao vivo.** O repositório tem uma bateria própria e boa para
  isso (`scripts/atelier-route-audit.mjs`: 78 rotas × 2 temas × 2 larguras, medindo
  overflow, texto <12 px, alvo de toque <44 px, imagem quebrada, interativo aninhado),
  mas ela exige `channel: 'chrome'` — Chrome de marca, que não existe neste ambiente (há
  apenas o Chromium do Playwright). **Recomendo rodá-la**: é o caminho certo para
  "erros visuais" de verdade, e cobre o que a análise estática não alcança.
- Os achados visuais aqui são **estáticos, mas conferidos contra o bundle compilado**:
  cruzamento de toda classe de `className` contra toda regra dos CSS importados e depois
  contra `dist/assets/*.css` (item 2), CSS órfão, camadas de `!important`, e as checagens
  de contraste/renderização que o próprio repositório já embute (todas aprovadas). O que
  este método **não** pega: sobreposição, corte, overflow, contraste calculado e alvo de
  toque — só um navegador de verdade mede isso.
- Não foi exercitado nenhum fluxo de ponta a ponta com backend em pé (pagamento Stripe,
  OAuth de agenda/e-mail, envio real de e-mail, assinatura digital de PDF).
- Conteúdo científico (corpus, PMIDs, doses) **não** foi reauditado — é frente separada,
  com método próprio já documentado no `CLAUDE.md`.
- Nenhuma alteração de código foi feita. Este arquivo é o único artefato novo.

**Nota de método, registrada porque quase virou achado falso.** A primeira execução da
suíte backend foi **descartada**: sondagens paralelas minhas rodaram contra o mesmo banco
de teste, e o `TRUNCATE ... CASCADE` por teste do `conftest.py` apagou dados entre a
criação do usuário e a requisição — produzindo 401 que pareciam bug de sessão e não eram.
É exatamente a contenção que o `CLAUDE.md` já documenta entre sessões concorrentes. O
resultado reportado vem de uma corrida única, em banco dedicado (`meucardio_audit`), sem
nenhum outro processo de teste ativo. **Nunca rode duas suítes contra o mesmo banco.**
