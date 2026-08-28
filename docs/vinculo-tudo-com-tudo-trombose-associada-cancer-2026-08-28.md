# Fechamento de lacuna Tudo com Tudo — Trombose associada ao câncer — 28/08/2026

## Contexto

Vigésimo nono lote de conteúdo do dia, terceiro desta natureza (após
`doenca-de-kawasaki`, PR #642, e `estenose-aortica-tavi-idoso`, PR
#643). A ficha `trombose-associada-cancer` (área `cardiooncologia`,
`prevalence_rank: 13`) já estava `completeness: completo`, com
`treatment_summary`/`presentation`/`differentials` íntegros e
`review_status: revisado`, mas `related_document_slugs` e
`patient_material_slug` estavam `None`.

## O que este lote NÃO faz

Não altera nenhum campo de conteúdo clínico pré-existente.

## O que este lote faz

Adiciona 5 `related_document_slugs` e 1 `patient_material_slug`,
verificados por leitura real de cada documento candidato:

- `trombose-associada-ao-cancer-escore-de-khorana-e-escolha-de-anticoagulante` — provável documento-hub (11 menções).
- `trombose-associada-a-cateter-venoso-central-em-pacientes-oncologicos` — apresentação central listada na própria ficha (10 menções).
- `fluxograma-tromboembolismo-pulmonar-agudo-associado-ao-cancer-e-trombocitopenia` — complicação central (7 menções).
- `anticoagulacao-no-tromboembolismo-venoso-oncologico-com-trombocitopenia` — conduta central (6 menções).
- `anticoagulacao-estendida-em-dose-reduzida-no-tev-do-cancer-o-ensaio-api-cat` — evidência de conduta específica (9 menções).

`patient_material_slug` definido como `cancer-e-trombose-por-que-o-
anticoagulante-muda`, material educativo já existente e correspondente
exato ao tema.

## Candidato descartado (nota de escopo)

`rastreio-de-neoplasia-oculta-apos-tev-nao-provocado-os-ensaios-somit-
e-some` teve 28 menções ao termo de busca, mas cobre a relação
**inversa**: TEV sem causa aparente como achado que leva à investigação
de câncer oculto — fora do escopo desta ficha, que é sobre trombose
**em paciente com câncer já conhecido** (confirmado por leitura do
`name`/`aliases`/`presentation` originais da ficha antes da seleção).
Descartado por não ser central ao tema, apesar da alta contagem de
menções — critério de centralidade prevalece sobre contagem bruta.

## Verificações feitas na montagem

- Os 5 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  de câncer/oncologia no texto.
- Nenhuma sobreposição com outra ficha do corpus encontrada.
- `patient_material_slug` verificado como existente em
  `material-paciente/metadados.json`.
- Nenhuma dose de fármaco foi introduzida.

## Catalogação e conteúdo clínico preservados

`name`, `aliases`, `area`, `category`, `prevalence_rank`,
`treatment_summary`, `presentation`, `differentials` originais
preservados sem qualquer alteração — verificado pelo teste dedicado.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Coordenação com Codex

Nenhum PR aberto (busca por título/branch) toca
`trombose-associada-cancer` em `doencas/metadados.json`.

## Riscos e limitações

- Registro volta a `review_status: pendente_revisao` por prudência
  editorial.
- Nenhuma dose de fármaco é citada ou alterada.
- Ainda restam 4 fichas na mesma situação para lotes futuros:
  `miocardite-pediatrica` (colisão com PR #568 descartada, confirmado
  via gh pr diff — livre para o próximo ciclo), `avaliacao-basal-
  cardiooncologica` (corpus raso, requer vetting cuidadoso),
  `avaliacao-cardiovascular-pre-concepcional` (corpus com muito ruído
  de falso positivo, requer leitura individual cuidadosa),
  `hipertensao-arterial-pediatrica` (precisa confirmação se PR #609
  já resolveu isto e o checkout local está desatualizado).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vinculo_tudo_com_tudo_trombose_associada_cancer.py`:
  7 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 13 testes executados, 13 passando.

## Branch e PR

Branch `claude/vincular-tudo-com-tudo-trombose-associada-cancer-20260828`,
baseada em `origin/main` sem drift no momento do commit.
