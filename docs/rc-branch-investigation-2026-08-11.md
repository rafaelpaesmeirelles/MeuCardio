# Investigação dos 33 branches remotos não incorporados — 2026-08-11

Corrige a seção 1.1 de `docs/rc-reconciliation-2026-08-11.md`, que concluiu (erroneamente, por
causa de um refspec de fetch restrito no checkout local) que só existiam 2 branches no remoto.

**Metodologia real**: `git ls-remote --heads origin` (ignora config local) e a API do GitHub
confirmaram, de forma independente e concordante, **69 branches no remoto**. `git merge-base
--is-ancestor` contra `origin/stabilizacao-2026-08-09` classificou 36 como já contidos
(ancestrais) e **33 como não-ancestrais** — potencialmente com trabalho não incorporado. Um
agente dedicado (Opus, esforço alto) investigou os 33 um a um, comparando não só ancestralidade
de commit mas **conteúdo real** (o que main/stabilizacao têm hoje resolve o que o branch tentava
resolver, mesmo que por um caminho de implementação diferente — squash-merge quebra ancestralidade
sem significar perda de conteúdo).

Duas confirmações de segurança, antes de qualquer outra coisa: **produção (`c38c6624`) é
ancestral estrito do RC** — produção não tem nada que o RC não tenha. **Nenhum branch é mais
recente que o RC** — todos datados ≤ 2026-08-10.

## Categorias

- **(A) Já incorporado** — o que o branch fazia já está presente hoje (por outro commit).
- **(B) Obsoleto/superado** — resolvia algo que não é mais relevante.
- **(C) Conteúdo científico duplicado/descartado** — já avaliado e rejeitado por duplicata.
- **(D) Possivelmente faltando** — precisa de decisão humana.

## Tabela completa

| Branch | Categoria | Evidência |
|---|---|---|
| agent/chatgpt-grupo-b | C+D | 19/22 tópicos já no corpus; 2 arquivos *encolheriam* docs de Cardio-oncologia já publicados; 3 tópicos genuinamente novos (ver D1) |
| agent/chatgpt-grupo-b-20260808 | C | 4/4 tópicos cobertos (ferro IV, DAP, rastreio IC/DM, HP grupo 2) |
| agent/chatgpt-grupo-b-conteudo | C | Clone de #1 sob outros slugs; 21/22 já cobertos, 4 itens de Perioperatório duplicados; CLAUDE.md já rejeitou este padrão AHA/ACC-2024 duas vezes |
| agent/chatgpt-preoperatorio-continuacao | A | `perioperative_calculators_{geriatria,sort,mortalidade}.py` já presentes |
| agent/chatgpt-preoperatorio-v2 | A+D | Backends presentes; só falta `CalculadorasPreOperatoriasAvancadas.tsx` + testes unitários |
| agent/chatgpt-preoperatorio-v3 | A+D | Mesma lacuna de v2 |
| agent/corrige-painel-acervo-comunicacao | A | `inventory_total` + integridade por coleção já em `library.py`, com testes de contrato |
| agent/corvia-pdf-build | B | Deck de slides de marketing, não é código de produto |
| agent/corvia-pdf-final | B | Mesmo trabalho de corvia-pdf-build, só chunks regenerados |
| agent/dependency-security-audit | B | `docs/dependency-security.md` do RC já registra esta PR e a decisão de portar só o gate |
| agent/deploy-certifica-corpus | A | `deploy.sh` já tem snapshot/rollback/readiness/traffic-gating + 4 testes de contrato |
| agent/frontend-code-splitting | A | `check-route-splitting.mjs` + `check-bundle-budget.mjs` já presentes e no CI |
| agent/frontend-rendering-security | A | `check-rendering-security.mjs` + docs já presentes e no CI |
| agent/reconcile-slug-explicito | A | `_resolve_markdown_slug()` já centralizado em `importer.py`, usado por `reconcile_content.py` |
| agent/reportlab-python314-compat | A | `reportlab==4.4.10` idêntico; teste de compatibilidade presente |
| agent/security-headers-csp | A+D | Headers já em Caddy/nginx, CSP mais forte que o branch propunha; ver D5 |
| agent/status-pos-pr38 | B | Snapshot de doc que termina no PR 38; RC já está em PR 45/46 |
| agent/structured-request-logging | A | `observability.py` já é superset; teste presente |
| agent/substitui-passlib-bcrypt | A | `bcrypt==4.0.1`, sem passlib, testes de compatibilidade presentes |
| claude/biblioteca-30-07-morning-orcq0g | A | Código presente, RC é superset (email.py +778 linhas) |
| claude/biblioteca-session-recovery-gnft29 | A+D | Metade pré-operatório é inferior ao RC (branch recusa calcular Gupta); metade de templates genuinamente ausente — ver D4 |
| claude/medicamentos-review-completo-38tslz | A | Já integrada por cherry-pick nesta mesma fase — 176/176 slugs presentes |
| claude/novo-usuario-corvia-mail-t3wb3p | B | As 3 operações já existem via API+UI; script do branch está obsoleto (422 sem local_part) |
| 10× dependabot | D-lite | Todos de 10/08/2026 — propostas de upgrade em aberto, não trabalho perdido |

**Contagem: A=13 · B=5 · C=3 (uma com resíduo D) · D=2 puros + 4 parciais · dependabot=10 decisões pendentes.**

## Categoria (D) — decisão humana

**D1 — OPTIMA-AF 2026 (maior valor).** Zero menção no corpus. Lancet 2026, PMID 42456692, n=1079,
75 centros japoneses, terapia antitrombótica dupla 1 mês vs. 12 meses pós-PCI em FA. Nenhum
documento existente responde a esta pergunta (AUGUSTUS é outro trial). Caminho:
`origin/agent/chatgpt-grupo-b:content/Fibrilação atrial/optima-af-2026-um-mes-terapia-dupla-apos-pci.md`.
**Ainda `review_status: pendente_revisao`** — não passou pela verificação de PMID obrigatória
deste projeto antes de poder ser considerado para publicação.

**D2 — Diretriz CKM 2026.** Único documento cardiorrenal hoje é a síndrome clássica de 5 tipos,
construto diferente dos estágios CKM 0-4. Presente em dois branches; escolher um.

**D3 — Medidas de qualidade PAD ACC/AHA 2026.** Genuinamente ausente, mas é um framework de
métricas de qualidade, não evidência clínica — discutivelmente fora do escopo de conteúdo do
produto.

**D4 — Modelos de documento do sistema.** Genuinamente ausente: `owner_id` ainda não-nullable,
sem coluna `slug_sistema`, migração `a1c8e4f92b6d` não está em `versions/`, sem rotina de seed.
Hoje todo médico começa com lista de templates vazia. Pode ser cherry-picked isoladamente
(`semear_document_templates.py` + migração + a mudança de listagem em `documents.py`) —
**descartar** `preop.py` e os acréscimos de calculadora do mesmo branch, que são estritamente
inferiores ao que já está no RC.

**D5 — Swagger/OpenAPI público em produção.** `documentacao_api_habilitada()` nunca foi portado;
`main.py` fixa `docs_url="/api/docs"`, e o Caddy não tem regra bloqueando. **Avaliado pelo
orquestrador e deliberadamente NÃO alterado nesta fase**: `/api/openapi.json` é usado
extensivamente, em produção, como mecanismo de verificação operacional documentado em todo o
histórico do `CLAUDE.md` deste projeto (múltiplas sessões confirmam rota nova consultando
`curl .../api/openapi.json` direto em produção) — desligar isso quebraria um fluxo de trabalho
estabelecido. Severidade real é baixa (expõe só o schema — todo endpoint continua exigindo sua
própria autenticação). Fica registrado como decisão de produto para o Rafael, não como bug.

**D6 — Cobertura de teste GSCRI/S-MPM.** `test_perioperative_advanced_calculators.py` ausente;
nenhum teste hoje confere a matemática do GSCRI/S-MPM isoladamente. **Nota do orquestrador**: o
GSCRI em si (que este achado citava como "bloqueado") foi investigado a fundo e **corrigido** —
ver commit `d7955c89`: o cálculo já funciona plenamente (confirmado computando um resultado real),
o que estava quebrado era o mapeamento de erro da rota genérica (KeyError virando 404 por engano)
e um texto desatualizado na UI. A lacuna de teste unitário dedicado ao GSCRI/S-MPM isolado
continua real e vale a pena fechar numa iteração futura, mas não é mais um bloqueio de
disponibilidade — a calculadora já é alcançável e testada via `/calculadoras/gscri` (ver
`test_calculators_gerar_documento.py`, testes novos desta fase).

**D7 — 10 bumps do dependabot.** Vários major (React 18→19, TypeScript 5→7, redis 5→8,
react-markdown 9→10). Nenhum indício de urgência: o CI já roda `pip_audit --strict` e
`npm run audit:security` (bloqueante para high/critical) contra as versões atuais.

## Achado incidental do agente, verificado e corrigido pelo orquestrador (não é achado de branch)

O agente notou que `test_calculators_gerar_documento.py` continha uma premissa falsa sobre o
GSCRI estar "deliberadamente fora do catálogo". Investigado a fundo (não só aceito por relato):
confirmado que o GSCRI está implementado e funcional, e que a causa real do teste "passar" era um
bug de mapeamento de exceção (`KeyError` de payload incompleto virando 404 em vez de 422) nas
rotas `/run` e `/gerar-documento` de `app/api/calculators.py`. Corrigido, com 6 testes novos/
reescritos, e o texto da UI (`AvaliacaoPreOperatoria.tsx`) que dizia ao médico que o cálculo
"permanece bloqueado" — commit `d7955c89`.

## Veredito

**Nenhum branch deve ser mergeado por inteiro** — vários regrediriam o RC (branch #1 encolhe dois
documentos já publicados; v2/v3 revertem `AvaliacaoPreOperatoria.tsx` para antes da assinatura
ITI e do envio por e-mail ao paciente; o código pré-operatório do branch de recovery é mais fraco
que o que já está no RC).

**Recomendado antes de fechar o RC** (já executado pelo orquestrador, ver commits citados):
corrigir o teste/UI do GSCRI (feito, `d7955c89`). **Deliberadamente adiado para depois do RC**:
D1-D4, D6 (lacuna de teste unitário) e os 10 bumps do dependabot — D1/D2 ainda devem a verificação
obrigatória de PMID deste projeto antes de qualquer publicação, e nenhum bump do dependabot é
forçado por segurança (confirmado pelo próprio CI já bloqueando high/critical). D5 é decisão de
produto do Rafael, registrada, não uma pendência técnica.
