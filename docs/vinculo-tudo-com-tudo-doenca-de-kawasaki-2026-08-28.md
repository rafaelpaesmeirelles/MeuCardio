# Fechamento de lacuna Tudo com Tudo — Doença de Kawasaki — 28/08/2026

## Contexto

Vigésimo sétimo lote de conteúdo do dia, mas de natureza diferente dos
26 anteriores: não é uma aprofundamento de conteúdo clínico. Ao esgotar
o pool de fichas `completeness=basico`/`intermediario` disponíveis para
aprofundamento (todas completadas hoje, em colisão com PR aberta, ou de
corpus insuficiente já confirmado), auditei o corpus completo em busca
de fichas `completeness=completo` com `related_document_slugs` vazio —
uma violação pontual e específica da regra Tudo com Tudo em fichas cujo
conteúdo clínico já está pronto e publicado. Encontrei **7 fichas** nessa
situação; `doenca-de-kawasaki` (área `cardiopediatria`, `prevalence_rank:
2`) é a primeira processada, por ser a de maior relevância clínica entre
as sem colisão de PR confirmada.

## O que este lote NÃO faz

Diferente de todos os 26 lotes anteriores, este **não altera nenhum
campo de conteúdo clínico pré-existente** — `epidemiology`,
`diagnostic_approach`, `treatment_summary`, `assistant_questions`,
`assistant_rules` continuam exatamente como estavam (já completos,
`review_status: revisado`, publicados). O único gap era estrutural:
`related_document_slugs` e `patient_material_slug` estavam `None`.

## O que este lote faz

Adiciona 7 `related_document_slugs` e 1 `patient_material_slug`,
verificados por leitura real de cada documento candidato (contagem de
menções + leitura de contexto, não apenas grep de nome de arquivo):

- `doenca-de-kawasaki-criterios-diagnosticos-estratificacao-de-risco-por-z-score-e-tratamento` — documento-hub da própria doença (9 menções).
- `sindrome-do-choque-da-doenca-de-kawasaki` — complicação central (16 menções).
- `fluxograma-sindrome-do-choque-da-doenca-de-kawasaki` — fluxograma companheiro (10 menções).
- `trombose-coronaria-e-infarto-em-aneurisma-de-kawasaki` — complicação central (12 menções).
- `fluxograma-trombose-coronaria-e-infarto-em-aneurisma-de-kawasaki` — fluxograma companheiro (6 menções).
- `febre-reumatica-aguda-versus-doenca-de-kawasaki-diagnostico-diferencial` — diagnóstico diferencial dedicado (27 menções).
- `dor-toracica-pediatrica-avaliacao-de-sinais-de-alarme-cardiaco-vs-causa-nao-cardiaca` — cita explicitamente história pessoal de Kawasaki como sinal de alarme e referencia de volta os dois documentos centrais desta ficha (5 menções, conexão positiva e explícita).

Dois candidatos adicionais foram lidos e **descartados** por
centralidade insuficiente ou natureza de exclusão: `mis-c-com-
disfuncao-miocardica-e-choque` (3 menções, apenas comparação de
fenótipo) e `pericardite-aguda-na-crianca-e-no-adolescente-...` (8
menções, mas o próprio documento afirma explicitamente que **não**
deve ser usado para derrame pericárdico associado a Kawasaki,
direcionando para o documento-hub — uma redireção, não uma conexão
central).

`patient_material_slug` definido como `doenca-de-kawasaki-o-que-os-
pais-precisam-saber`, material educativo já existente e correspondente
exato ao tema.

## Verificações feitas na montagem

- Os 7 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  de Kawasaki no texto.
- **Overlap pré-existente e legítimo**: `dor-toracica-pediatrica-...`
  também é o documento-hub da própria ficha `dor-toracica-pediatrica`
  (já concluída hoje, PR #610) — overlap natural, documentado no teste
  dedicado.
- `patient_material_slug` verificado como existente em
  `material-paciente/metadados.json`.
- Nenhuma dose de fármaco foi introduzida (o `treatment_summary`
  pré-existente já seguia a convenção de citar tratamento sem
  posologia — verificado, sem necessidade de alteração).

## Catalogação e conteúdo clínico preservados

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`,
`epidemiology`, `diagnostic_approach`, `treatment_summary`,
`assistant_questions`, `assistant_rules` originais preservados sem
qualquer alteração — verificado pelo teste dedicado.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Coordenação com Codex

Nenhum PR aberto (busca por título/branch) toca `doenca-de-kawasaki`
em `doencas/metadados.json`.

## Riscos e limitações

- Registro volta a `review_status: pendente_revisao` por prudência
  editorial — mesmo sem mudança de conteúdo clínico, uma alteração
  estrutural em ficha publicada passa por nova revisão antes de
  republicar.
- Nenhuma dose de fármaco é citada ou alterada.
- Ainda restam 6 fichas na mesma situação (`completeness=completo` com
  `related_document_slugs` vazio) para lotes futuros: `miocardite-
  pediatrica`, `avaliacao-basal-cardiooncologica`, `avaliacao-
  cardiovascular-pre-concepcional`, `estenose-aortica-tavi-idoso`,
  `trombose-associada-cancer`, e `hipertensao-arterial-pediatrica`
  (esta já foi processada em PR #609 anterior a este checkout — precisa
  confirmação de que os vínculos não se perderam antes de reprocessar).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vinculo_tudo_com_tudo_doenca_de_kawasaki.py`: 7
  testes, todos passando (1 correção durante desenvolvimento, para
  documentar overlap pré-existente descoberto pelo próprio teste).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 13 testes executados, 13 passando.

## Branch e PR

Branch `claude/vincular-tudo-com-tudo-doenca-de-kawasaki-20260828`,
baseada em `origin/main` sem drift no momento do commit.
