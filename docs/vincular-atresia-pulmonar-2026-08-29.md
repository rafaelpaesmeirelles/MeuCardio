# Vincular Tudo com Tudo — Atresia pulmonar — 29/08/2026

## Contexto

Ficha `atresia-pulmonar` (área `cardiopediatria`) já era `completeness:
completo` (conteúdo publicado pela PR #577, do Codex, já mesclada), mas
tinha apenas 1 `related_document_slug` — abaixo do piso mínimo de 3.
Lote apenas de vínculo — nenhum conteúdo clínico pré-existente foi
reescrito.

## Vínculos adicionados (5)

- `tetralogia-de-fallot-rastreio-pre-natal-crise-de-hipoxia-e-estrategia-cirurgica`
- `colapso-neonatal-por-cardiopatia-congenita-critica-canal-dependente`
- `triagem-neonatal-de-cardiopatia-congenita-critica-por-oximetria-de-pulso`
- `conduto-ventriculo-direito-arteria-pulmonar-seguimento-reintervencao-e-valva-transcateter`
- `cianose-no-recem-nascido-diagnostico-diferencial-e-conduta-inicial`

Total final: 6.

## Verificação feita na montagem

O agente de pesquisa avaliou 9 candidatos adicionais e descartou-os
corretamente por menção lateral (item de tabela/lista de classificação,
sem discussão substantiva) — inclusive um falso positivo de grep
("planejamento-do-parto-...", onde o trecho encontrado se referia a TGA,
não a atresia pulmonar). Os 5 aceitos foram confirmados por leitura
direta.

Overlaps legítimos e pré-existentes: `atresia-pulmonar-anatomia-
dependencia-coronariana-...` (vínculo original) também em `tetralogia-
de-fallot` e `tetralogia-fallot-fetal`; os demais compartilhados com
`transposicao-das-grandes-arterias`, `transposicao-grandes-arterias-
fetal` e `sopros-na-infancia`.

## ⚠️ Achado sobre mecanismo de correção pré-existente

Diferente das outras PRs de hoje, esta **não** sofre a falha esperada em
`test_canonical_content_review_status.py`: existe um patch em
`doencas/correcoes/zz-release36h-approvals.json` que fixa
`review_status="revisado"` para `atresia-pulmonar` (aprovação de
27-28/08/2026, anterior a este lote). Esse patch tem prioridade sobre o
`pendente_revisao` que escrevi na base do manifesto e **mascara** a
necessidade de nova revisão explícita para os 5 vínculos adicionados
hoje — o registro composto final aparece como já revisado mesmo com
conteúdo novo não verificado por um humano. Sinalizo isso para decisão
editorial: pode ser desejável que o revisor adicione uma nova entrada de
correção específica para este lote, ou trate esse comportamento do
mecanismo de composição como algo a revisar separadamente.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_atresia_pulmonar.py`: 6 testes.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `backend/tests/test_canonical_content_review_status.py`: passando
  (registro já "revisado" via patch pré-existente — ver nota acima).
- `app.main` importa sem erro.
- Total: 12 testes executados, 12 passando.
