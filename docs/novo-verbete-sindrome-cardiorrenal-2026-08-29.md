# Verbete novo — Síndrome cardiorrenal — 29/08/2026

## Contexto

Rodada de reconhecimento sistêmico identificou que **síndrome cardiorrenal**
— tema central e recorrente na prática de insuficiência cardíaca, presente
implicitamente em múltiplos documentos do corpus (inclusive citada de
passagem, sem nunca ter sido definida, em
`estrategia-diuretica-na-insuficiencia-cardiaca-aguda-descompensada.md`) —
não tinha ficha própria em `doencas/metadados.json`, apesar de corpus já
rico e existente: classificação em cinco tipos, manejo no idoso, diretriz
ESC 2026 de doença cardiovascular/doença renal crônica, resistência
diurética, estratégia diurética na ICAD e a diretriz mais recente sobre
síndrome cardiovascular-renal-metabólica (CKM).

Criado via `doencas/fragmentos/sindrome-cardiorrenal.json` — **não** via
edição direta do arquivo `doencas/metadados.json` — para minimizar colisão
com outras frentes de produção concorrentes (mecanismo já utilizado por
outros verbetes-hub recentes do sistema, ex. cardiomiopatia hipertrófica em
28/08/2026).

## Conteúdo produzido (verbete completo, do zero)

- `summary`/`epidemiology`: síndrome cardiorrenal como interdependência
  hemodinâmica, neuro-hormonal e inflamatória bidirecional entre coração e
  rim; classificação de Ronco em cinco tipos (tipo 1: cardiorrenal agudo;
  tipo 2: cardiorrenal crônico; tipo 3: renocardíaco agudo; tipo 4:
  renocardíaco crônico; tipo 5: secundário a doença sistêmica).
- Foco clínico central do verbete: a **distinção entre piora renal
  verdadeira e hemoconcentração/ajuste hemodinâmico esperado** durante a
  descongestão ativa da insuficiência cardíaca aguda descompensada — para
  não subtratar a congestão por receio infundado de "piorar o rim" quando a
  elevação de creatinina é transitória e acompanha descongestão eficaz.
- `presentation` (8), `diagnostic_approach` (5 eixos — classificação por
  subtipo, diferenciação piora renal verdadeira vs. hemoconcentração,
  avaliação hemodinâmica/volêmica, exames complementares, avaliação de
  resistência diurética), `differentials` (8), `tests` (8), `red_flags`
  (6).
- `treatment_summary`: não subtratar congestão por elevação isolada e
  transitória de creatinina durante descongestão eficaz; estratégia guiada
  pelo estado volêmico (congestão venosa renal vs. hipoperfusão);
  investigação sistemática de resistência diurética antes de escalar;
  bloqueio sequencial do néfron; terapias com benefício cardiovascular e
  renal simultâneo (iSGLT2, antagonistas mineralocorticoides não
  esteroidais) no contexto do continuum cardiovascular-renal-metabólico;
  ultrafiltração/terapia renal substitutiva em congestão refratária. Sem
  doses específicas em nenhum campo.
- `ambulatory_flow` (6), `emergency_flow` (5), `monitoring` (6).
- `special_populations` (5).
- `assistant_questions` (13), `assistant_rules` (8, priority 90 para
  oligúria persistente com congestão em curso).
- `related_document_slugs` (6, do zero).
- `patient_material_slug`: deixado `null` — nenhuma correspondência
  encontrada em `material-paciente/metadados.json` (confirmado por busca
  textual por "cardiorrenal"/"cardiorenal"/"cardio-renal" sem resultado);
  registrado como possível oportunidade futura de produção, não como
  omissão.

## Verificação de citações

Os 9 PMIDs desta rodada foram verificados individualmente via NCBI e-utils
antes da montagem: os dois artigos fundadores da classificação de Ronco
(Eur Heart J 2010, PMID 20037146; JACC 2008, PMID 19007588), o scientific
statement da AHA sobre GFR em IC (Circulation 2019, PMID 30852913), o
estudo de Testani sobre descongestão agressiva e hemoconcentração
(Circulation 2010, PMID 20606118), a position statement da HFA-ESC sobre
diuréticos na IC congestiva (Eur J Heart Fail 2019, PMID 30600580), o
ensaio CLOROTIC (Eur J Heart Fail 2022, PMID 36423214), o ensaio ADVOR
(NEJM 2022, PMID 36027559) e os ensaios FIDELIO-DKD (NEJM 2020, PMID
33264825) e FIGARO-DKD (NEJM 2021, PMID 34449181) de finerenona.

## Verificações feitas na montagem

- Os 6 `related_document_slugs` foram lidos por completo (arquivo real em
  `content/**/*.md`) e verificados individualmente:
  - `sindrome-cardiorrenal-classificacao-em-cinco-tipos-e-manejo-na-insuficiencia-cardiaca`
    (`content/Insuficiência_cardíaca/`) — documento central sobre a
    classificação de Ronco.
  - `sindrome-cardiorrenal-no-idoso-classificacao-e-o-mito-da-piora-renal-durante-a-descongestao`
    (`content/Cardiologia_geriátrica/`) — mesma classificação aplicada ao
    idoso, com o mito da piora renal durante descongestão.
  - `esc-2026-doenca-cardiovascular-e-doenca-renal-cronica-stamp-on-ckd`
    (`content/Cardiorrenal/`) — diretriz ESC 2026 sobre a integração
    DCV/DRC (framework STAMP on CKD).
  - `resistencia-diuretica-na-insuficiencia-cardiaca-aguda-mecanismos-e-bloqueio-sequencial-do-nefron`
    (`content/Insuficiência_cardíaca/`) — mecanismos de resistência
    diurética e bloqueio sequencial do néfron, ensaio CLOROTIC.
  - `estrategia-diuretica-na-insuficiencia-cardiaca-aguda-descompensada`
    (`content/Insuficiência_cardíaca/`) — DOSE-AHF, CARRESS-HF (ensaio de
    ultrafiltração *versus* terapia farmacológica escalonada
    especificamente em síndrome cardiorrenal tipo 1) e ADVOR.
  - `aha-acc-ada-asn-2026-sindrome-cardiovascular-renal-metabolica-ckm`
    (`content/Diabetes_e_cardiologia/`) — diretriz mais recente sobre o
    continuum cardiovascular-renal-metabólico, citado no `treatment_summary`
    do fragmento.
  - Nenhum dos 6 está em `content/Farmacologia/`, `content/Calculadoras/`
    ou `content/Exames/`.
- Um **7º candidato** (`fluxograma-diuretico-resistente-na-sindrome-cardiorrenal`)
  foi **excluído** por resolver para `content/Farmacologia/`, pasta fora do
  escopo permitido pela regra Tudo com Tudo — confirmado por leitura direta
  do caminho do arquivo e coberto por asserção dedicada no teste
  (`test_novo_verbete_sindrome_cardiorrenal.py::test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos`).
- Duas sobreposições de `related_document_slugs` com outras fichas foram
  identificadas e são esperadas/documentadas (mesmo documento legitimamente
  relevante para mais de uma ficha): `sindrome-cardiorrenal-no-idoso-...`
  também aparece em `insuficiencia-cardiaca-no-idoso`, e
  `aha-acc-ada-asn-2026-sindrome-cardiovascular-renal-metabolica-ckm`
  também aparece em `diabetes-mellitus-tipo-2`.
- `patient_material_slug` confirmado `null` por ausência de correspondência
  em `material-paciente/metadados.json`.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente (não `text`).

## Decisão sobre o gate de review-status (1 falha esperada e documentada)

O verbete é publicado com `review_status: "pendente_revisao"` — estado
honesto para um verbete novo ainda não revisado por humano. Sob o padrão de
gate vigente desde 28/08/2026 (PR #606), `PENDENTES_LOTES_TUDO_COM_TUDO` em
`test_canonical_content_review_status.py` **não isenta mais** registros
`pendente_revisao` do teste principal
(`test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`)
— o dicionário hoje só documenta registros **já revisados** que carregam uma
pendência editorial explícita e aprovada. Como o campo continua "pendente
_revisao" para "sindrome-cardiorrenal", a condição de isenção (que exige
`status == "revisado"`) nunca é satisfeita, e o registro cai corretamente em
`invalidos`, causando **exatamente 1 falha esperada** nesse teste.

A entrada em `PENDENTES_LOTES_TUDO_COM_TUDO["doencas/metadados.json"]` foi
revisada e mantida — ela é lida por `test_disease_fragments_canonical.py`
via `PENDENTES_DOENCAS = PENDENTES_LOTES_TUDO_COM_TUDO.get("doencas/metadados.json", set())`,
e é essa allowlist (independente do valor de `review_status`) que permite o
teste `test_catalogo_combinado_tem_slugs_unicos_e_status_editorial_explicito`
aceitar o novo registro `pendente_revisao` sem falhar. A entrada está,
portanto, no dicionário certo e é necessária — apenas não produz (nem
deveria produzir) isenção no gate principal de review-status, que
corretamente continua reportando a pendência editorial em aberto.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_novo_verbete_sindrome_cardiorrenal.py`: 11 testes,
  11 passando.
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes, 3
  passando.
- `backend/tests/test_canonical_content_review_status.py`: 3 testes, **1
  falha esperada e documentada** (`test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  — ver seção acima), 2 passando.
- `app.main` importa sem erro.
- `load_disease_records()` carrega o fragmento sem erro (119 registros
  totais em `doencas/metadados.json` incluindo o novo).

## Branch e PR

Branch `claude/novo-verbete-sindrome-cardiorrenal-20260829`, rebaseada
sobre `origin/main` no momento do commit (sem conflitos — nenhuma das
frentes concorrentes tocou `doencas/fragmentos/sindrome-cardiorrenal.json`,
`backend/tests/test_canonical_content_review_status.py` ou
`backend/tests/test_novo_verbete_sindrome_cardiorrenal.py`).
