# Fechamento de lacuna Tudo com Tudo — Miocardite pediátrica — 28/08/2026

## Contexto

Trigésimo lote de conteúdo do dia, quarto desta natureza (após
`doenca-de-kawasaki` PR #642, `estenose-aortica-tavi-idoso` PR #643 e
`trombose-associada-cancer` PR #644). A ficha `miocardite-pediatrica`
(área `cardiopediatria`, `prevalence_rank: 3`) já estava
`completeness: completo`, com `treatment_summary`/`assistant_rules`
íntegros e `review_status: revisado`, mas `related_document_slugs` e
`patient_material_slug` estavam `None`.

## O que este lote NÃO faz

Não altera nenhum campo de conteúdo clínico pré-existente.

## O que este lote faz

Adiciona 4 `related_document_slugs` e 1 `patient_material_slug`,
verificados por leitura real:

- `miocardite-aguda-pediatrica-diagnostico-suporte-hemodinamico-e-ecmo` — documento-hub (11 menções).
- `miocardite-fulminante-pediatrica-e-choque-cardiogenico` — complicação central (12 menções).
- `fluxograma-miocardite-fulminante-pediatrica-e-choque-cardiogenico` — fluxograma companheiro (6 menções).
- `miocardite-pos-vacina-de-mrna-em-adolescentes-incidencia-comparacao-com-covid-19-e-vigilancia-atual` — subtipo/etiologia central (18 menções).

`patient_material_slug` definido como `miocardite-inflamacao-do-
musculo-do-coracao-e-recuperacao`, material educativo geral já
existente.

## Candidatos descartados

`mis-c-com-disfuncao-miocardica-e-choque` (2 menções),
`cardiomiopatia-pediatrica-dilatada-e-hipertrofica-...` (1 menção) e
`insuficiencia-cardiaca-pediatrica-...` (2 menções) — todos com menção
apenas de passagem, não centrais ao tema miocardite pediátrica.

## Verificação de colisão

Uma suspeita inicial de colisão com a PR #568 ("novo verbete-hub de
Miocardite geral") foi descartada via `gh pr diff 568 | grep '"slug":
"miocardite-pediatrica"'`, que retornou 0 ocorrências do slug exato —
a PR #568 cria uma ficha-hub geral distinta, não toca esta ficha
pediátrica.

## Verificações feitas na montagem

- Os 4 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  de miocardite no texto.
- Nenhuma sobreposição com outra ficha do corpus encontrada.
- `patient_material_slug` verificado como existente.
- Nenhuma dose de fármaco foi introduzida.

## Catalogação e conteúdo clínico preservados

`name`, `aliases`, `area`, `category`, `prevalence_rank`,
`treatment_summary`, `assistant_rules` originais preservados sem
qualquer alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Riscos e limitações

- Registro volta a `review_status: pendente_revisao` por prudência
  editorial.
- Nenhuma dose de fármaco é citada ou alterada.
- Ainda restam 3 fichas na mesma situação para lotes futuros:
  `avaliacao-basal-cardiooncologica`, `avaliacao-cardiovascular-pre-
  concepcional` (corpus mais delicado, requer leitura individual
  cuidadosa), `hipertensao-arterial-pediatrica` (precisa confirmação de
  estado real, possivelmente já resolvido em PR #609 não refletido
  neste checkout).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vinculo_tudo_com_tudo_miocardite_pediatrica.py`:
  7 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 13 testes executados, 13 passando.

## Branch e PR

Branch `claude/vincular-tudo-com-tudo-miocardite-pediatrica-20260828`,
baseada em `origin/main` sem drift no momento do commit.
