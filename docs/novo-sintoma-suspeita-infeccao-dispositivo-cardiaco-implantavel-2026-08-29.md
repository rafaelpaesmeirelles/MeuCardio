# Triagem de sintomas nova — Suspeita de infecção de dispositivo cardíaco implantável — 29/08/2026

## Contexto

A função **Triagem de Sintomas** (`triagem-sintomas/metadados.json`) não
tinha fluxo próprio para reconhecer **sinais locais na loja do gerador**
(marca-passo, CDI ou ressincronizador) — eritema, dor, drenagem purulenta,
deiscência de sutura, erosão com exposição do dispositivo — apesar de o
tema já estar coberto em profundidade em `content/Dispositivos/` e
`content/Endocardite/`. Este é um manifesto e schema diferentes do Guia de
Doenças (`doencas/metadados.json`); a função aqui é o assistente
determinístico de triagem (perguntas → regras → risco/fluxo), não a ficha
enciclopédica de uma condição.

Registro novo: `suspeita-infeccao-dispositivo-cardiaco-implantavel`,
adicionado ao **final** do array em `triagem-sintomas/metadados.json`.

## Fontes usadas (verificadas)

As duas fontes mapeadas na missão, mais duas adicionais localizadas por
busca (`grep -ril "infeccao.*dispositivo\|CIED\|erosao.*gerador\|bolsa.*marca-passo" content/`):

1. `content/Dispositivos/infeccao-de-dispositivo-cardiaco-extracao-de-eletrodo-e-envelope-antibiotico.md`
   — Scientific Statement AHA 2024 (PMID 38047353): reconhecimento de
   bolsa infectada, erosão como infecção presumida, remoção completa do
   sistema, WRAP-IT.
2. `content/Dispositivos/fluxograma-suspeita-infeccao-cied-extracao-reimplante-aha-2023.md`
   — mesmo Scientific Statement, fluxograma de decisão diagnóstica e de
   reimplante.
3. `content/Dispositivos/complicacoes-de-bolso-do-gerador-hematoma-infeccao-erosao-fatores-de-risco-e-prevencao.md`
   — meta-análise de fatores de risco de infecção de CIED (PMID 25926473)
   e elo quantificado entre hematoma e infecção (WRAP-IT, PMID 30883056).
4. `content/Dispositivos/fluxograma-infeccao-de-bolsa-de-gerador-conduta.md`
   — consenso HRS 2017 (PMID 28919379): erosão = infecção do sistema
   mesmo sem febre/hemocultura; hematoma estéril não deve ser aspirado.

Os 4 PMIDs citados em `source_refs` (38047353, 28919379, 30883056,
25926473) foram verificados individualmente nesta sessão via NCBI
E-utilities (`esummary`, porque o PubMed direto retornou apenas o aviso
de cookies ao WebFetch) — título, revista, ano, volume/páginas e DOI
conferidos contra o registro oficial e batem com os já citados nos quatro
documentos-fonte acima.

## Conteúdo produzido

- **11 perguntas**: tipo de dispositivo (`select`), dias desde o
  implante/procedimento mais recente (`number`, 0–3650 dias), erosão com
  exposição, drenagem purulenta, deiscência de sutura, eritema/calor
  local, hematoma isolado sem flogose, febre, sinais de sepse, hemocultura
  prévia positiva, vegetação prévia em eletrodo/válvula ao ecocardiograma.
- **10 regras**, cobrindo as quatro disciplinas exigidas pela missão:
  - `erosao-exposicao` (priority 100, `emergencia`) — erosão com
    exposição do gerador/eletrodo, red flag de bacteremia/endocardite
    relacionada a dispositivo.
  - `sepse-sistemica` (100, `emergencia`) e `vegetacao-eletrodo-previa`
    (95, `emergencia`) — sinais de sepse e vegetação prévia ao eco.
  - `febre-com-sinais-locais` (90, `urgente`) — febre + qualquer sinal
    local (eritema, drenagem, deiscência, erosão).
  - `drenagem-purulenta` (88, `urgente`) — dispara **mesmo sem febre**,
    conforme o consenso HRS 2017 ("erosão/drenagem = infecção do
    sistema" independe de sinal sistêmico).
  - `deiscencia-sutura` (82, `urgente`).
  - `hemocultura-previa-positiva` (65, `prioritario`).
  - `eritema-tardio-sem-outros-sinais` (55, `prioritario`) — eritema
    isolado fora da janela pós-operatória imediata (>14 dias).
  - `hematoma-sem-inflamacao` (40, `rotina`) — hematoma isolado sem
    eritema/calor/drenagem/febre; usa `opposing`, não `red_flags`.
  - `eritema-leve-pos-procedimento-recente` (30, `rotina`) — eritema
    leve isolado, ≤14 dias do procedimento, reação inflamatória benigna
    possível, mas ainda com reavaliação recomendada.

  **Cuidado deliberado de engenharia**: o motor de regras
  (`clinical_rule_engine.evaluate_rules`) escala automaticamente o risco
  para pelo menos `urgente` sempre que qualquer regra adiciona algo a
  `red_flags`. As duas regras "benignas" (hematoma isolado, eritema leve
  recente) usam `supporting`/`opposing` em vez de `red_flags`, para não
  disparar essa escalada indevida — confirmado por teste dedicado e por
  execução manual do motor com os 4 cenários da missão antes de escrever
  o teste.

- `default_tests`, `differentials`, `red_flags` (nível de registro),
  `ambulatory_flow` e `emergency_flow` não vazios, com ênfase em: nunca
  aspirar a bolsa para diagnóstico, extração completa do sistema (gerador
  + todos os eletrodos, incluindo abandonados) como conduta definidora
  diante de erosão/infecção de bolsa confirmada, hemoculturas antes do
  antimicrobiano quando a condição permitir.
- `areas`: `["geral", "cardiogeriatria"]`, conforme exigido.
- Nenhuma dose de fármaco em nenhum campo — checado por regex dedicada no
  teste (`test_nenhuma_dose_de_farmaco_em_nenhum_campo_de_texto`).

## Validações feitas

- JSON válido (`json.load`).
- `validate_question_definitions` / `validate_rule_definitions`
  (`app.services.clinical_rule_engine`): sem erros. IDs de pergunta e de
  regra únicos. Nenhum operador `includes` usado — apenas os operadores
  válidos do motor (`eq, neq, in, not_in, gt, gte, lt, lte, truthy, falsy,
  contains, exists, missing`).
- `evaluate_rules` executado manualmente para os cenários centrais:
  erosão → `emergencia`; sepse → `emergencia`; drenagem purulenta sem
  febre → `urgente` com red flag; febre + eritema → `urgente`; eritema
  leve recente (dia 3) → `rotina`, sem red flag; eritema tardio (dia 30)
  → `prioritario`; hematoma isolado → `rotina`; nenhum sinal →
  `informativo`; campo obrigatório ausente → reportado em
  `missing_information`.
- Loader `app.services.carregar_triagem_sintomas.carregar` executado
  contra `corvia-test-pg`
  (`DATABASE_URL=postgresql+psycopg://meucardio_test:test@localhost:5432/meucardio_test`):
  `{"novos": 19, "atualizados": 0}`, sem erros — os 19 registros do
  manifesto (18 existentes + o novo) foram inseridos. Uma primeira
  tentativa sofreu `DeadlockDetected` por concorrência real de outros
  agentes gravando na mesma base de teste compartilhada nesta sessão; a
  segunda tentativa (retry simples) teve sucesso.

## Gates

- `backend/tests/test_novo_sintoma_suspeita_infeccao_dispositivo_cardiaco_implantavel.py`
  (teste dedicado, novo): cobre existência/posição do registro, campos
  obrigatórios do schema, validade de perguntas/regras, presença das
  perguntas clínicas exigidas pela missão, os 8 cenários de risco acima e
  a ausência de dose de fármaco.
- `backend/tests/test_specialty_guides.py::test_triage_manifest_has_two_flows_and_special_populations`
  — continua passando com o registro novo (≥15 itens, `ambulatory_flow`/
  `emergency_flow`/`source_refs` não vazios em todos, URLs válidas).
- `backend/tests/test_canonical_content_review_status.py` — **falha
  esperada e documentada**, não é bug e não foi contornada:
  `test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  falha porque o novo registro tem `review_status="pendente_revisao"` e
  as allowlists do gate (`PENDENTES_MEDICAMENTOS_RC`,
  `PENDENTES_LOTES_TUDO_COM_TUDO`) foram deliberadamente deixadas vazias
  em 28/08/2026 ("qualquer novo status diferente de `revisado` quebra o
  gate e exige decisão editorial explícita") — mesmo padrão de comentário
  usado na PR #698 (branch
  `claude/novo-verbete-cardiomiopatia-de-takotsubo-20260829`), que também
  documentou essa falha esperada em vez de adicionar o próprio slug a
  uma allowlist. Publicar este conteúdo (`review_status: "revisado"`)
  fica para revisão médica humana.
- `import app.main` — sem erro.

## Risco de colisão sinalizado

`triagem-sintomas/metadados.json` é um arquivo único compartilhado por
várias frentes de produção em branches paralelas nesta mesma sessão
multiagente (confirmado: processos de pytest concorrentes de pelo menos
uma dezena de outros worktrees rodando ao mesmo tempo, inclusive contra a
mesma base `corvia-test-pg`, causando um deadlock transitório já
resolvido por retry). O registro novo foi adicionado ao **final** do
array, mas a branch pode divergir de `origin/main` até o momento do merge
— resolução de conflito e novo `git diff` contra a base atual são
necessários antes de qualquer merge.

## Não incluído neste PR

Merge e deploy — aguardando revisão humana.
