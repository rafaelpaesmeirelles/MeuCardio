# Sintoma novo na Triagem — Distensão abdominal/ascite com suspeita de congestão cardíaca direita — 29/08/2026

## Contexto

Rodada de reconhecimento identificou que **distensão abdominal/ascite com
suspeita de congestão cardíaca direita** não tinha registro próprio em
`triagem-sintomas/metadados.json`, apesar de corpus já rico e existente na
biblioteca:

- `hepatopatia-congestiva-cronica-na-insuficiencia-cardiaca-direita-de-longa-data-reconhecimento-e-prognostico.md`
- `insuficiencia-cardiaca-direita-isolada-por-doenca-tricuspide-fisiopatologia-da-congestao-e-manejo-clinico.md`
- `falencia-aguda-do-ventriculo-direito-na-uco-pre-carga-pos-carga-e-intubacao.md`
- `fluxograma-edema-bilateral-membros-inferiores-diferencial-cardiaco.md`

Os 4 documentos-fonte foram lidos por completo antes da montagem das
perguntas e regras. Este registro cobre a Triagem de Sintomas
(`triagem-sintomas/metadados.json`), schema distinto do Guia de Doenças
(`doencas/metadados.json`): usa `questions`/`rules` validados por
`validate_question_definitions`/`validate_rule_definitions` e avaliados por
`evaluate_rules` do `clinical_rule_engine`, em vez dos campos de ficha de
doença.

Retomada de trabalho de um agente anterior que parou por contenção no
Postgres de teste compartilhado, sem commitar nem abrir PR. Nesta sessão de
conclusão: JSON e schema revalidados do zero, testes executados, verificação
de drift contra `origin/main`, escrita deste relatório, commit, push e
abertura do PR.

## Conteúdo produzido (registro novo, do zero)

- `areas`: `geral` e `cardiogeriatria`.
- `aliases` (4): "barriga inchada", "ascite", "distensão abdominal",
  "abdômen inchado".
- `questions` (13): 4 red flags obrigatórias (febre/dor abdominal
  importante, dispneia aguda/hipóxia, instabilidade hemodinâmica, ganho de
  peso rápido/redução da diurese), história cardíaca (IC/doença tricúspide
  conhecida, edema de MMII, dispneia aos esforços, turgência jugular,
  hepatomegalia dolorosa), padrão evolutivo (`select` agudo vs. crônico
  progressivo + `number` de semanas de evolução, com `min`/`max`/`unit`) e
  causas não cardíacas de ascite (doença hepática conhecida, uso de
  álcool, perda de peso com sinais de alarme oncológico).
- `rules` (9, priority 100→25): infecção/peritonite (emergência),
  instabilidade hemodinâmica ou dispneia aguda/hipóxia (emergência), ganho
  de peso rápido (urgente), sinal de alarme oncológico (urgente, diferencial
  neoplásico), padrão clássico de congestão direita descompensada
  (prioritário), hepatopatia primária sem contexto cardíaco (diferencial
  hepatológico), uso de álcool sem contexto cardíaco (diferencial),
  contexto crônico progressivo (mensagem orientadora) e duração
  prolongada sem etiologia definida (mensagem orientadora).
- `default_tests` (3), `differentials` (6), `red_flags` (5),
  `ambulatory_flow` (4), `emergency_flow` (4), `tags` (6).
- `source_refs`/`source_urls` (5 PMIDs/PubMed).

## Verificação de citações

Os 5 PMIDs citados em `source_refs` (29650544, 19215833, 42154163, 23939641,
26995592) foram verificados individualmente via NCBI E-utilities
(`esummary`) — título, autoria, journal, volume, páginas e DOI conferidos
contra o texto usado nos documentos-fonte já revisados da biblioteca, sem
divergência.

## Verificações feitas na montagem

- JSON completo de `triagem-sintomas/metadados.json` revalidado por
  `json.load` (19 registros, slugs únicos, nenhum erro de sintaxe).
- Schema revalidado campo a campo contra o loader
  (`backend/app/services/carregar_triagem_sintomas.py`): `slug`, `name`,
  `aliases`, `areas` ⊂ `{geral, cardiopediatria, cardiogeriatria,
  cardiooncologia, gravidez}`, `summary`, `questions`, `rules`,
  `default_tests`, `differentials`, `red_flags`, `ambulatory_flow` (não
  vazio), `emergency_flow` (não vazio), `tags`, `source_refs` (não vazio),
  `source_urls`, `review_status="pendente_revisao"`, `review_note`,
  `version=1` — todos presentes e corretos.
- `validate_question_definitions`/`validate_rule_definitions` do
  `clinical_rule_engine` executados diretamente contra o registro: nenhum
  erro. Todas as perguntas usam a chave `label` (nunca `text`), tipos
  válidos (`boolean`, `select`, `number`), opções do `select`
  (`onset_pattern`) únicas, e a pergunta `number`
  (`distension_duration_weeks`) tem `min`, `max` e `unit`.
- Nenhuma regra usa o operador `includes` (todas usam operadores da lista
  permitida, majoritariamente `truthy`/`eq`); nenhuma regra adiciona o
  campo `monitoring` (fora de `ALLOWED_ADDITION_FIELDS`); todos os
  `priority` estão no intervalo 0–100; todos os `risk` usados
  (`emergencia`, `urgente`, `prioritario`) são válidos.
- Registro confirmado ao **final** do array (posição 19 de 19), minimizando
  risco de conflito de merge com outras branches paralelas que também
  editam `triagem-sintomas/metadados.json`.
- Nenhuma dose de fármaco em nenhum campo (varredura por padrão de dose
  incluída no teste dedicado).

## Allowlist de `review_status` (test_canonical_content_review_status.py)

Este registro é conteúdo novo, ainda `pendente_revisao`, então
`test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
**falha** para este slug — comportamento esperado e documentado no próprio
`review_note` do registro.

Diferente do padrão usado na PR #698 (`cardiomiopatia-de-takotsubo`) para
`doencas/metadados.json`, **nenhuma entrada foi adicionada** a
`PENDENTES_LOTES_TUDO_COM_TUDO` neste teste: a allowlist só tem efeito
quando `review_status == "revisado"` (ver condição do teste), e este
registro permanece `pendente_revisao` — logo uma entrada na allowlist não
mudaria o resultado do gate. Além disso, ao contrário de
`doencas/metadados.json` (onde `test_disease_fragments_canonical.py`
reaproveita essa mesma allowlist para um segundo gate), não existe teste
equivalente para `triagem-sintomas` que consuma essa allowlist — adicionar
uma entrada aqui não teria efeito em nenhum gate e apenas ampliaria, sem
necessidade, uma allowlist que o próprio comentário do arquivo descreve
como devendo ficar vazia.

## Gates

- `backend/tests/test_novo_sintoma_distensao_abdominal_ascite_congestao_cardiaca.py`:
  suíte dedicada (existência/posição no manifesto, campos obrigatórios,
  áreas, aliases, `source_urls` https, validação de `questions`/`rules`
  pelo motor clínico, cobertura de perguntas por tema, operadores/campos de
  adição permitidos, ausência de doses, cenários clínicos via
  `evaluate_rules` — congestão direita clássica, dispneia aguda/instabili-
  dade, ganho de peso rápido, hepatopatia primária, febre/dor abdominal
  como peritonite, alarme oncológico, resposta obrigatória ausente — e
  integração via `assess_triage`).
- `backend/tests/test_specialty_guides.py`: passando.
- `backend/tests/test_canonical_content_review_status.py`: 1 falha
  esperada e documentada (ver seção acima) — este slug, `pendente_revisao`.
- `python -c "import app.main"`: importa sem erro.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- **Risco de conflito de merge**: múltiplas frentes de produção rodavam em
  paralelo nesta mesma janela (29/08/2026), várias delas também editando
  `triagem-sintomas/metadados.json` em branches próprias a partir do mesmo
  worktree compartilhado (confirmado via processos concorrentes de teste
  observados durante a execução desta tarefa — vários outros
  `test_novo_sintoma_*`/`test_novo_verbete_*` rodando simultaneamente contra
  o mesmo Postgres de teste). O registro foi adicionado ao final do array
  para minimizar a chance de conflito textual, mas como o arquivo é uma
  lista JSON única compartilhada por todos os registros de triagem, um PR
  concorrente que mergear primeiro pode gerar conflito de merge neste PR
  (ou vice-versa) — a resolução, se necessária, deve preservar ambos os
  registros como entradas distintas do array, sem descartar nenhum.
- Nenhuma dose de fármaco é citada em nenhum campo.

## Branch e PR

Branch
`claude/novo-sintoma-distensao-abdominal-ascite-congestao-cardiaca-20260829`,
baseada em `origin/main` sem drift no momento do commit (0 commits de
diferença entre a branch e `origin/main` no merge-base).
