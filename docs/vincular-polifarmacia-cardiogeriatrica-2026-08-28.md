# Vincular Tudo com Tudo — Polifarmácia e desprescrição cardiovascular — 28/08/2026

## Contexto

Ficha `polifarmacia-e-desprecricao-cardiovascular` (área `cardiogeriatria`,
categoria `sindrome_geriatrica`, `prevalence_rank: 1`) já era
`completeness: completo`, mas tinha apenas 1 `related_document_slug` —
abaixo do piso mínimo de 3. Lote apenas de vínculo — nenhum conteúdo
clínico pré-existente foi reescrito.

## Vínculos adicionados (3)

- `desprescricao-de-medicamentos-cardiovasculares-na-polifarmacia-consenso-cientifico-aha-2026`
- `fluxograma-desprescricao-cardiovascular-no-idoso-polifarmacia-e-fim-de-vida`
- `polifarmacia-anti-hipertensiva-e-adesao-no-idoso-desprescrever-simplificar-ou-manter`

Total final: 4.

## Verificação feita na montagem

O agente de pesquisa avaliou e descartou corretamente 7 outros candidatos
por menção lateral (polifarmácia citada apenas como item de lista em
documentos sobre outros temas centrais — quedas, fragilidade, delirium,
reconciliação medicamentosa). Confirmei os 3 aceitos por leitura direta.

Overlaps legítimos e pré-existentes:
- `fluxograma-desprescricao-...` também em `hipotensao-ortostatica-no-idoso`.
- O vínculo original `polifarmacia-cardiovascular-no-idoso-cascata-de-
  prescricao-e-desprescricao` também em `insuficiencia-cardiaca-no-idoso`,
  `risco-quedas-cardiogeriatria` e `anticoagulacao-idoso`.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_polifarmacia_cardiogeriatrica.py`: 6 testes
  (1 correção durante desenvolvimento, para documentar overlap
  pré-existente descoberto pelo próprio teste).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando.
- `app.main` importa sem erro.
- Total: 12 testes executados, 12 passando.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhum conteúdo clínico pré-existente foi alterado, apenas o vínculo.
