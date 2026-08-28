# Vincular Tudo com Tudo — Acidente vascular cerebral agudo — 28/08/2026

## Contexto

Ficha `acidente-vascular-cerebral-agudo` (área `geral`, categoria
`emergencia_neurovascular`, `prevalence_rank: 1`) já era `completeness:
completo`, mas tinha apenas 2 `related_document_slugs` — abaixo do piso
mínimo de 3. Lote apenas de vínculo, com foco deliberado na interseção
cardiovascular do AVC (dado que este é um sistema de cardiologia).
Nenhum conteúdo clínico pré-existente foi reescrito.

## Vínculos adicionados (5)

- `timing-cirurgico-apos-avc-na-endocardite-infecciosa-esc-2023`
- `monitor-cardiaco-implantavel-e-deteccao-de-fa-pos-avc-criptogenico-crystal-af`
- `anticoagulacao-empirica-no-avc-criptogenico-sem-fa-documentada-navigate-esus-re-spect-esus-e-arcadia`
- `aneurisma-apical-trombo-de-ve-e-avc-cardioembolico-na-cardiomiopatia-chagasica`
- `disseccao-de-arteria-cervical-carotida-e-vertebral-diagnostico-e-antitrombotico-cadiss`

Total final: 7 (teto máximo da regra).

## Verificação feita na montagem

Todos os 5 confirmados por leitura direta do documento completo antes da
inclusão. O candidato de dissecção de artéria cervical, embora não seja
estritamente "cardioembólico", trata de uma causa relevante de AVC
isquêmico e da escolha antitrombótica — dentro do escopo da própria
ficha (AVC agudo, geral).

Overlap legítimo e pré-existente: `timing-cirurgico-apos-avc-na-
endocardite-...` também em `endocardite-infecciosa`.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_avc_agudo.py`: 6 testes.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando.
- `app.main` importa sem erro.
- Total: 12 testes executados, 12 passando.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhum conteúdo clínico pré-existente foi alterado, apenas o vínculo.
