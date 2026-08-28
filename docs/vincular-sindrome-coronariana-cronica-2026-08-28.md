# Vincular Tudo com Tudo — Síndrome coronariana crônica — 28/08/2026

## Contexto

Ficha `sindrome-coronariana-cronica` (área `geral`, categoria
`doenca_coronariana`, `prevalence_rank: 4`) já era `completeness:
completo`, mas tinha apenas 2 `related_document_slugs` — abaixo do piso
mínimo de 3. Lote apenas de vínculo. Nenhum conteúdo clínico
pré-existente foi reescrito.

## Vínculos adicionados (5)

- `orbita-2-pci-versus-placebo-angina-estavel`
- `fluxograma-angina-estavel-refrataria-manejo-escalonado`
- `anoca-inoca-angina-e-isquemia-sem-obstrucao-coronariana-esc-2024`
- `ischemia-estrategia-invasiva-vs-conservadora-na-dac-estavel`
- `avaliacao-funcional-da-lesao-coronariana-ffr-e-ifr-o-ensaio-fame-2-e-o-define-flair`

Total final: 7 (teto máximo da regra).

## Verificação feita na montagem

Todos os 5 confirmados por leitura direta do documento completo antes da
inclusão. O agente de pesquisa avaliou 9 candidatos adicionais e
descartou-os corretamente por redundância temática com os já
selecionados, por serem calculadoras/farmacologia (fora do escopo
permitido), ou por serem tangenciais (avaliação pré-operatória). Sem
overlap com nenhuma outra ficha.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_sindrome_coronariana_cronica.py`: 6 testes.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando.
- `app.main` importa sem erro.
- Total: 12 testes executados, 12 passando.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhum conteúdo clínico pré-existente foi alterado, apenas o vínculo.
