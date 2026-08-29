# Verbete novo — Cardiomiopatia arritmogênica — 29/08/2026

## Contexto

Rodada de reconhecimento sistêmico identificou que **cardiomiopatia
arritmogênica** (ACM), historicamente chamada de displasia/cardiomiopatia
arritmogênica do ventrículo direito (DAVD/ARVC/D), não tinha ficha própria
em `doencas/metadados.json`, apesar de corpus rico e já existente em
`content/Cardiomiopatias/`, `content/Arritmias/`, `content/Cardiologia_do_
Esporte_e_do_Exercício/` e `content/Cardiologia_pediátrica/`.

Criado via `doencas/fragmentos/cardiomiopatia-arritmogenica.json` — **não**
via edição direta de `doencas/metadados.json` — para minimizar colisão com
outras frentes de produção concorrentes. Nesta mesma data, duas frentes
paralelas produziam `cardiomiopatia-hipertrofica` (já integrada, PR #668) e
`cardiomiopatia-de-takotsubo` (branch `claude/novo-verbete-cardiomiopatia-
de-takotsubo-20260829`, PR #698) — confirmado programaticamente, nesta
sessão de retomada, que não há overlap de `related_document_slugs` com
nenhuma das duas.

Este trabalho foi iniciado por uma sessão autônoma anterior, que deixou
pronto (não commitado) o fragmento, o teste dedicado e a entrada de
allowlist. Esta sessão retomou o pipeline: revalidou o schema e o conteúdo
contra os documentos-fonte reais, rodou os gates, resolveu drift contra
`origin/main` e concluiu o commit/PR.

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: sem estimativa de prevalência populacional (nenhuma fonte
  revisada fornece esse número — deliberado, não omissão), coortes de
  derivação/validação da calculadora de risco (Cadrin-Tourigny 2019/2021),
  coorte original da Task Force 2010 (apenas 8% de probandos 12-18 anos),
  coorte pediátrica dedicada (Smedsrud et al. 2022) e revisão sistemática de
  familiares de risco (Sharma et al. 2022).
- `presentation` (10), `diagnostic_approach` (dict aninhado com 6 eixos:
  Task Force revisada 2010, Critérios de Padua 2020, avaliação por imagem,
  teste genético/rastreio em cascata, particularidades diagnósticas na
  criança, estratificação de risco arrítmico pós-diagnóstico — 6.209
  caracteres serializados), `differentials` (8), `tests` (8), `red_flags`
  (9).
- `treatment_summary` (2.024 caracteres): quatro pilares (controle de
  arritmias, manejo de IC, prevenção de morte súbita, rastreio familiar em
  cascata), restrição de exercício como intervenção modificadora da doença
  (não precaução genérica), ressalva de desempenho reduzido da calculadora
  de risco em portador de variante em desmoplaquina — sem nenhuma dose.
- `ambulatory_flow` (9), `emergency_flow` (5), `monitoring` (8).
- `special_populations` (6): atleta de endurance, portador de variante em
  desmoplaquina (DSP), criança/adolescente familiar de primeiro grau,
  genótipo-positivo/fenótipo-negativo, família "gene-elusiva", fenótipo de
  predomínio de VE (ALVC)/biventricular.
- `assistant_questions` (14), `assistant_rules` (10, priority 99 para
  tempestade elétrica e 92 para TV sustentada/síncope de esforço).
- `related_document_slugs` (6, verificados individualmente).
- `patient_material_slug` preenchido:
  `cardiomiopatia-arritmogenica-musculo-do-coracao-trocado-por-gordura-e-
  cicatriz`.

## Verificação dos 6 related_document_slugs (Tudo com Tudo)

Cada um dos 7 documentos mapeados pelo reconhecimento prévio foi **lido por
completo** nesta sessão (confirmando resolução do slug, pasta de origem e
menção central ao tema). 6 foram incluídos, por discutirem a cardiomiopatia
arritmogênica de forma central:

1. `cardiomiopatia-arritmogenica-acm-diagnostico-e-manejo-esc-2023`
   (`content/Cardiomiopatias/`)
2. `cardiomiopatia-arritmogenica-criterios-de-padua-2020-e-task-force-
   revisada-de-2010` (`content/Arritmias/`)
3. `calculadora-de-risco-da-cardiomiopatia-arritmogenica-desempenho-por-
   genotipo` (`content/Arritmias/` — **confirmado explicitamente**: fisicamente
   fora de `content/Calculadoras/`, apesar do `kind: calculadora` no
   frontmatter)
4. `restricao-de-exercicio-na-cardiomiopatia-arritmogenica-de-ventriculo-
   direito-dose-resposta-e-mecanismo` (`content/Arritmias/`)
5. `cardiomiopatia-arritmogenica-no-atleta-exercicio-risco-e-retorno-ao-
   esporte` (`content/Cardiologia_do_Esporte_e_do_Exercício/`)
6. `cardiomiopatia-arritmogenica-na-crianca-penetrancia-idade-dependente-
   rastreio-familiar-e-restricao-de-exercicio` (`content/Cardiologia_
   pediátrica/`)

O 7º candidato mapeado inicialmente,
`reclassificacao-fenotipica-esc-2023-ndlvc-hipertrabeculacao-e-takotsubo-
deixam-de-ser-cardiomiopatia`, foi lido por completo e **deliberadamente
excluído**: discute a reclassificação de NDLVC, hipertrabeculação e
takotsubo como traço/síndrome pela ESC 2023, citando ARVC/ALVC apenas
tangencialmente ao delimitar a categoria NDLVC — sem tratar centralmente a
cardiomiopatia arritmogênica.

Nenhum dos 6 candidatos resolve para `content/Farmacologia/`, `content/
Calculadoras/` ou `content/Exames/` — verificado por leitura direta do
caminho de cada arquivo nesta sessão.

## Overlap com `cardiomiopatia-hipertrofica` e `cardiomiopatia-dilatada`

Verificado programaticamente nesta sessão via `load_disease_records()`
contra o catálogo combinado (119 registros nesta base):

- `cardiomiopatia-hipertrofica` (já integrada): **sem overlap** de
  `related_document_slugs`.
- `cardiomiopatia-dilatada`: **não está presente** nesta base (produzida em
  branch paralela `afeb6a8d`, ainda não integrada a `origin/main`) — sem
  registro carregado, não há overlap a checar nesta composição. Fica
  registrado para nova verificação quando essa branch for integrada.
- Overlap esperado e documentado com o hub `cardiomiopatias` (2 documentos:
  diagnóstico/manejo ESC 2023 e critérios Task Force/Padua) — hubs listam
  amplamente documentos específicos do próprio domínio, comportamento
  esperado e coberto por teste dedicado
  (`test_sobreposicao_de_related_document_slugs_e_explicitamente_
  documentada`).

## Verificação de PMIDs

12 PMIDs citados em `source_refs`/`source_urls`, verificados individualmente
via NCBI E-utilities (`esummary`) nesta sessão de retomada — spot-check
contra o registro oficial do PubMed (título, periódico, ano, volume, páginas,
DOI), sem divergência encontrada nos itens conferidos (20172912, 33296238,
30915475), consistente com a verificação completa dos 12 já documentada no
`review_note` do próprio registro (feita pela sessão autônoma anterior).

## Falha esperada e documentada no gate de review_status

`review_status` permanece `"pendente_revisao"` — conteúdo novo não revisado
por humano não se autoaprova. Por isso:

- `backend/tests/test_canonical_content_review_status.py::
  test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  **FALHA** para `cardiomiopatia-arritmogenica`. Esperado e correto: a lógica
  desse teste consome todo registro com `status == "revisado"` no primeiro
  `continue`, antes de qualquer checagem de allowlist — as checagens
  seguintes contra `PENDENTES_LOTES_TUDO_COM_TUDO` só são alcançáveis para
  registros que **já** estão `"revisado"`, nunca para `"pendente_revisao"`.
  A allowlist não isenta este registro, e não foi usada com essa intenção.
- A entrada `"cardiomiopatia-arritmogenica"` foi adicionada a
  `PENDENTES_LOTES_TUDO_COM_TUDO["doencas/metadados.json"]` — comentário
  idêntico, palavra por palavra, ao padrão usado em
  `claude/novo-verbete-cardiomiopatia-de-takotsubo-20260829` (PR #698) —
  porque essa mesma allowlist é **reaproveitada por importação direta** em
  `backend/tests/test_disease_fragments_canonical.py`, onde a checagem
  contra pendências funciona corretamente.

## Gates executados

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`;
  `SpecialtyDisease.related_document_slugs`: 1099/1099 resolvidos;
  `SpecialtyDisease.patient_material_slug`: 104/104 resolvidos;
  `review_status.pendente_revisao: 1` (só este registro).
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  9.546 registros totais, exit code 0.
- `backend/tests/test_novo_verbete_cardiomiopatia_arritmogenica.py`: GATE_TESTES_DEDICADOS
- `backend/tests/test_disease_fragments_canonical.py`: GATE_FRAGMENTS_CANONICAL
- `backend/tests/test_canonical_content_review_status.py`: GATE_REVIEW_STATUS
- `python -c "import app.main"`: GATE_IMPORT_MAIN
- Verificação manual direta (fora do pytest, nesta sessão): nenhuma dose de
  fármaco (`mg`, `mg/kg`, `mcg`, `J/kg`) em nenhum campo de texto do
  registro; todas as 14 `assistant_questions` usam `label` (nenhuma usa a
  chave legada `text`); todas as 10 `assistant_rules` têm `op`/`field`
  válidos (todo `field` referenciado existe em `assistant_questions`),
  chaves de `add` no conjunto permitido, `priority` 0-100 e `risk` no enum
  permitido; todos os campos mínimos de profundidade (listas e texto
  corrido) acima do limiar usado nesta frente.

## Branch e PR

Branch `claude/novo-verbete-cardiomiopatia-arritmogenica-20260829`. Drift
contra `origin/main` verificado e resolvido nesta sessão antes do commit
(`git log HEAD..origin/main` / `git log origin/main..HEAD` conferidos).
