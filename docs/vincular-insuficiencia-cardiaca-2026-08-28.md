# Vincular Tudo com Tudo — Insuficiência cardíaca — 28/08/2026

## Contexto

Ficha `insuficiencia-cardiaca` (área `geral`, `prevalence_rank: 3`, ficha
flagship muito central no sistema) já era `completeness: completo`, mas
tinha apenas 2 `related_document_slugs` — abaixo do piso mínimo de 3.
Lote apenas de vínculo. Nenhum conteúdo clínico pré-existente foi
reescrito.

## Cuidado especial aplicado

Por ser tema extremamente central no corpus (quase qualquer documento
menciona IC de passagem), apliquei critério deliberadamente rigoroso:
só aceitos documentos cujo tema seja **hub geral/transversal** da própria
síndrome — não subtipos/fenótipos já cobertos por documentos próprios
(ICFEr, ICFEp) nem comorbidades associadas (síndrome cardiorrenal), para
não diluir o vínculo nem duplicar escopo de fichas irmãs específicas.

## Vínculos adicionados (3)

- `segunda-definicao-universal-insuficiencia-cardiaca-2026`
- `estadiamento-e-classificacao-ic-aha-acc-hfsa-2022-versus-esc-e-sbc`
- `atualizacao-focada-2023-das-diretrizes-esc-2021-de-insuficiencia-cardiaca`

Total final: 5.

## Verificação feita na montagem

Todos os 3 confirmados por leitura direta do documento completo. 5
candidatos adicionais foram corretamente descartados pelo agente de
pesquisa (e por mim, na revisão) por serem escopo de fenótipo específico
(ICFEr, ICFEp) ou de comorbidade associada (síndrome cardiorrenal), não
do hub geral da síndrome. Sem overlap com nenhuma outra ficha.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_insuficiencia_cardiaca.py`: 6 testes.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando.
- `app.main` importa sem erro.
- Total: 12 testes executados, 12 passando.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhum conteúdo clínico pré-existente foi alterado, apenas o vínculo.
