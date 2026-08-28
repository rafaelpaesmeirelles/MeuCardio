# Vincular Tudo com Tudo — Sangramento relacionado a anticoagulante — 28/08/2026

## Contexto

Ficha `sangramento-relacionado-a-anticoagulante` (área `geral`, categoria
`seguranca_antitrombotica`, `prevalence_rank: 1`) já era `completeness:
completo`, com conteúdo clínico integral, mas tinha apenas 2
`related_document_slugs` — abaixo do piso mínimo de 3 da regra Tudo com
Tudo. Este lote é apenas de vínculo — nenhum conteúdo clínico já existente
foi reescrito.

## Vínculo adicionado

- `reversao-de-anticoagulante-em-sangramento-maior-idarucizumabe-e-andexanet-alfa`
  (comparação dos dois ensaios pivotais RE-VERSE AD e ANNEXA-4).

Total final: 3 (piso mínimo exato).

## Verificação feita na montagem

O agente de pesquisa propôs 4 candidatos. Verifiquei cada um pessoalmente
e descartei 3 por resolverem para `content/Farmacologia` — pasta
explicitamente fora do escopo permitido pela regra Tudo com Tudo (o
fluxograma de reversão emergencial e as monografias de idarucizumabe e
protamina são fichas de fármaco/protocolo farmacológico, não documentos
narrativos clínicos). Apenas o comparativo RE-VERSE AD/ANNEXA-4, que
resolve para `content/Tromboembolismo`, foi aceito — confirmado por
leitura direta do arquivo completo.

Overlap legítimo e pré-existente: o novo vínculo também é usado pela
ficha `anticoagulacao-idoso` (tema clinicamente adjacente).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_sangramento_anticoagulante.py`: 5 testes.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando.
- `app.main` importa sem erro.
- Total: 11 testes executados, 11 passando.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhum conteúdo clínico pré-existente foi alterado, apenas o vínculo.
