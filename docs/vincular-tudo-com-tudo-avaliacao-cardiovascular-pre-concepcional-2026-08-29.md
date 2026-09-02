# Vincular Tudo com Tudo — Avaliação cardiovascular pré-concepcional — 29/08/2026

## Contexto

Ficha `avaliacao-cardiovascular-pre-concepcional` (área `gravidez`,
categoria `planejamento_reprodutivo`) já era `completeness: completo` na
base `doencas/metadados.json`, mas tinha **0 `related_document_slugs`**
— abaixo do piso mínimo de 3, inconsistência do dataset apontada na
tarefa. Lote apenas de vínculo — nenhum conteúdo clínico pré-existente
foi reescrito, e `review_status`/`completeness` não foram alterados.

## Vínculos adicionados (4)

- `escores-de-risco-materno-carpreg-carpreg-ii-e-zahara`
- `anticoncepcao-na-mulher-com-cardiopatia-criterios-de-elegibilidade-da-oms-posicionamento-sbc-2020`
- `fluxograma-doenca-cardiovascular-e-gravidez-esc-2025`
- `preditores-de-recuperacao-ventricular-e-aconselhamento-pre-concepcional-na-cardiomiopatia-periparto`

Total final: 4.

## Candidatos avaliados e descarte justificado

Dos 5 candidatos levantados na tarefa, 1 foi descartado por rigor:

- **`doenca-cardiovascular-na-gravidez-estratificacao-de-risco-e-manejo-esc-2018-sbc-2020`
  — descartado.** Lido na íntegra (55 linhas): documento é majoritariamente
  sobre manejo **intra-gestacional** já estabelecido — limiares de
  anti-hipertensivo, prevenção de pré-eclâmpsia, substituição de
  varfarina por heparina, tratamento de cardiomiopatia periparto com
  bromocriptina, via de parto. A única menção a "avaliação pré-
  concepção" é um único item de bullet list ("classe II a IV: Avaliação
  pré-concepção obrigatória por pregnancy heart team multidisciplinar"),
  sem seção substantiva dedicada ao tema — não atende ao padrão de
  discussão central pedido pela tarefa. Também é a diretriz ESC **2018**,
  já superada pela ESC 2025 na própria pasta. Coberto por teste dedicado
  (`test_candidato_estratificacao_esc_2018_foi_corretamente_descartado`).

Os outros 4 foram lidos na íntegra e confirmados com discussão central
ou seção dedicada ao aconselhamento/avaliação pré-concepcional:

- `escores-de-risco-materno-carpreg-carpreg-ii-e-zahara`: seção "Como
  usar na prática" liga explicitamente o 10º preditor do CARPREG II
  ("avaliação tardia na gestação") ao aconselhamento pré-concepcional
  como variável mensurável, não recomendação genérica.
- `anticoncepcao-na-mulher-com-cardiopatia-criterios-de-elegibilidade-
  da-oms-posicionamento-sbc-2020`: documento inteiro é sobre
  planejamento familiar/contracepção em cardiopata — parte central do
  aconselhamento pré-concepcional, mesmo sem usar o termo literal em
  todas as seções.
- `fluxograma-doenca-cardiovascular-e-gravidez-esc-2025`: a própria
  árvore de decisão começa em "Avaliação de risco materno antes da
  concepção pela classificação mWHO 2.0" e tem seção dedicada ao
  Pregnancy Heart Team/aconselhamento pré-concepcional.
- `preditores-de-recuperacao-ventricular-e-aconselhamento-pre-
  concepcional-na-cardiomiopatia-periparto`: título e conteúdo
  inteiramente dedicados ao aconselhamento pré-concepcional na
  cardiomiopatia periparto prévia, com seção "Síntese prática para o
  aconselhamento pré-concepcional".

Nenhum candidato resolve para `content/Farmacologia/`,
`content/Calculadoras/` ou `content/Exames/` — todos os 4 aceitos estão
em `content/Gravidez/`.

## Overlaps legítimos e pré-existentes

- `escores-de-risco-materno-carpreg-carpreg-ii-e-zahara` também em
  `cardiopatia-congenita-gravidez`.
- `anticoncepcao-na-mulher-com-cardiopatia-criterios-de-elegibilidade-
  da-oms-posicionamento-sbc-2020` também em `hipertensao-pulmonar-
  gravidez`.
- `preditores-de-recuperacao-ventricular-e-aconselhamento-pre-
  concepcional-na-cardiomiopatia-periparto` também em
  `cardiomiopatia-periparto` e `seguimento-cardiovascular-pos-parto`.
- `fluxograma-doenca-cardiovascular-e-gravidez-esc-2025` não tinha
  overlap prévio com outra ficha na base.

## ⚠️ Achado principal — patch pré-existente já mascarava o vínculo, por outro caminho

Diferente do padrão de `atresia-pulmonar` (onde um patch mascarava
apenas `review_status`), aqui a máscara é sobre o **vínculo inteiro**:

`doencas/correcoes/zz-release36h-pr648-avaliacao-cardiovascular-pre-
concepcional.json` já existe em `origin/main` (chegou via commit
`798bb8d5` "release: integrar e revisar toda produção científica das
últimas 36h", de 28/08/2026) e contém um `"set"` que sobrescreve **o
registro inteiro** desta ficha via `load_disease_records` — incluindo
`epidemiology`, `diagnostic_approach`, `treatment_summary`, `monitoring`,
`special_populations` e `related_document_slugs` com uma lista
**diferente** da deste lote:

```
doenca-cardiovascular-e-gestacao-esc-2025
fluxograma-doenca-cardiovascular-e-gravidez-esc-2025
classificacao-de-risco-mwho-2-0-na-gravidez-esc-2025
```

Esse patch está ligado à **PR #648** (`feat(doencas): aprofundar
avaliação cardiovascular pré-concepcional`), que está **aberta**, tem
base `release/all-science-36h-20260828` (não `main`) e está com
`mergeable: CONFLICTING`. Ou seja: o patch de correção já foi integrado
a `main` de forma independente da PR que o originou, e essa PR nem
sequer teria como ser mesclada limpo hoje.

**Consequência verificada empiricamente** (antes e depois deste lote,
via `load_disease_records`): o registro **efetivo**, servido pelo app e
usado pelos próprios gates (`audit_tudo_com_tudo.py`,
`content_inventory.py`, `test_disease_fragments_canonical.py` — todos
importam `load_disease_records`), **já não tinha 0
`related_document_slugs` antes deste lote** — tinha os 3 do patch. A
premissa "0 vínculos" da tarefa é verdadeira apenas para a base JSON
crua; o registro composto (o que o produto realmente serve) já estava
correto, com vínculos de teor equivalente (2 dos 3 do patch também
tratam da diretriz ESC 2025/mWHO 2.0 pré-concepcional; o terceiro,
`doenca-cardiovascular-e-gestacao-esc-2025`, está em `content/Geral/`,
não `content/Gravidez/`, e não foi verificado por este lote).

Este lote corrige a base por completude, rastreabilidade e para seguir
o padrão desta frente — mas **o vínculo efetivamente ativo em produção
continua sendo o do patch** até decisão editorial reconciliar os dois
(por exemplo, incorporando os 4 vínculos deste lote ao `related_document_slugs`
do patch, ou aposentando o patch em favor de mesclar a PR #648 de
verdade). Coberto por teste de regressão dedicado
(`test_patch_correcoes_pr648_existe_e_mascara_o_vinculo_deste_lote`),
que falha se o patch for removido/alterado sem que a nota seja
atualizada.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_tudo_com_tudo_avaliacao_cardiovascular_pre_concepcional.py`:
  8 testes, todos passando.
- `backend/tests/test_canonical_content_review_status.py`: 3 testes,
  passando — **sem necessidade de allowlist**, porque `review_status`
  não foi alterado (a ficha já era `revisado` e continua `revisado`).
  Nenhuma falha preexistente encontrada neste gate para este slug.
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes,
  passando.
- `app.main` importa sem erro.
- Total: 14 testes pytest executados, 14 passando.
