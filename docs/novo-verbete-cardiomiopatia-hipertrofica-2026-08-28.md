# Verbete novo — Cardiomiopatia hipertrófica — 28/08/2026

## Contexto

Rodada de reconhecimento sistêmico identificou que **cardiomiopatia
hipertrófica** — a doença cardíaca genética mais prevalente (~1:500) e
principal causa de morte súbita cardíaca em atletas jovens — não tinha
ficha própria em `doencas/metadados.json`, apesar de corpus já rico e
existente em `content/Cardiomiopatias/` (diretriz brasileira 2024, versão
completa ESC 2023, terapia com inibidores de miosina cardíaca, aficamten
FOREST-HCM/SEQUOIA-HCM, fluxograma ESC 2023, investigação genética
familiar).

Criado via `doencas/fragmentos/cardiomiopatia-hipertrofica.json` — **não**
via edição direta do arquivo `doencas/metadados.json` — para minimizar
colisão com outras frentes de produção concorrentes (mecanismo já
utilizado por outros verbetes-hub recentes do sistema).

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: prevalência ~1:500, herança autossômica dominante
  (MYH7/MYBPC3), penetrância incompleta e variável, principal causa de
  morte súbita cardíaca em jovens/atletas.
- `presentation` (10), `diagnostic_approach` (4 eixos — critérios
  diagnósticos, avaliação por imagem, teste genético/rastreamento
  familiar, estratificação HCM Risk-SCD), `differentials` (9 — incluindo
  fenocópias: amiloidose, Fabry, Danon, coração de atleta), `tests` (8),
  `red_flags` (9).
- `treatment_summary`: escada terapêutica (betabloqueador/BCC →
  inibidores de miosina cardíaca → redução septal invasiva → CDI),
  restrição esportiva individualizada, rastreio familiar em cascata, sem
  doses.
- `ambulatory_flow` (10), `emergency_flow` (5), `monitoring` (8).
- `special_populations` (6).
- `assistant_questions` (16), `assistant_rules` (10, priority 95 para
  síncope + TVNS combinadas).
- `related_document_slugs` (6, do zero).
- `patient_material_slug` preenchido: `cardiomiopatia-hipertrofica`.

## Verificação de citações

Todos os 8 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem, incluindo os dois ensaios pivotais de
inibidores de miosina cardíaca (EXPLORER-HCM/mavacamten Lancet 2020,
SEQUOIA-HCM/aficamten NEJM 2024), o estudo de validação do HCM Risk-SCD
(Eur Heart J 2014), a diretriz ESC 2023 de cardiomiopatias e a diretriz
brasileira 2024.

## Verificações feitas na montagem

- Os 6 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema no texto — todos lidos por completo antes da inclusão.
- `patient_material_slug` confirmado por correspondência exata em
  `material-paciente/metadados.json`.
- Corrigidas 2 entidades HTML (`&lt;`) que apareceram no output bruto do
  agente de pesquisa em labels de `assistant_questions`, substituídas por
  fraseado em português antes da montagem (ex.: "abaixo de 50%").
- **Convenção de `category`**: usei `category: "cardiomiopatia"`, a
  mesma adotada de forma independente por outra frente de produção (PR
  #565, verbete-hub geral "cardiomiopatias", ainda não mergeada) — slugs
  distintos (`cardiomiopatia-hipertrofica` vs. `cardiomiopatias`), sem
  colisão técnica.
- `prevalence_rank` deixado `null`: não pertence ao hub fechado de
  doenças de altíssima prevalência em área "geral" (ranks 1-9); CMH é
  doença rara.
- Sem overlap de `related_document_slugs` com nenhuma outra ficha.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Possível sobreposição conceitual (não técnica) com o verbete-hub geral
  "cardiomiopatias" da PR #565, caso ela venha a ser mergeada — slugs
  distintos, arquitetura já usada no corpus (hub geral + ficha específica
  coexistindo, ex.: fibrilação atrial geral + fibrilação atrial no idoso).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_novo_verbete_cardiomiopatia_hipertrofica.py`: 13
  testes.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando, 5 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/novo-verbete-cardiomiopatia-hipertrofica-20260828`,
baseada em `origin/main` sem drift no momento do commit.
