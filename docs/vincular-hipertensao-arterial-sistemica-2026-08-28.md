# Vincular Tudo com Tudo (enriquecimento) — Hipertensão arterial sistêmica — 28/08/2026

## Contexto

Ficha `hipertensao-arterial-sistemica` (a ficha geral da doença
cardiovascular mais prevalente) já era `completeness: completo` com
exatamente 3 `related_document_slugs` — atendendo o piso técnico, mas
desproporcionalmente rasa frente ao corpus disponível em
`content/Hipertensão/`. Lote de enriquecimento apenas de vínculo. Nenhum
conteúdo clínico pré-existente foi reescrito.

## Vínculos adicionados (4)

- `escolha-do-anti-hipertensivo-de-primeira-linha-allhat-ascot-bpla-e-accomplish`
- `fluxograma-hipertensao-escalonamento-farmacologico-combinacao-inicial-aos-tres-passos-esc-2024`
- `hipertensao-resistente-verdadeira-versus-pseudorresistente-tecnica-adesao-avental-branco`
- `hipertensao-do-jaleco-branco-e-mascarada-mapa-mrpa-prevalencia-e-decisao-terapeutica`

Total final: 7 (teto máximo da regra).

## Verificação feita na montagem

Todos os 4 confirmados por leitura direta do documento completo — os dois
últimos espelham diretamente trechos do `treatment_summary`/
`diagnostic_approach` já existentes da própria ficha (pseudorresistência
e MAPA/MRPA), reforçando a centralidade. O agente descartou corretamente
4 candidatos adicionais por redundância com vínculos já existentes/
escolhidos ou por ultrapassarem o teto de 7. Sem overlap com nenhuma
outra ficha.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_hipertensao_arterial_sistemica.py`: 6 testes.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando.
- `app.main` importa sem erro.
- Total: 12 testes executados, 12 passando.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhum conteúdo clínico pré-existente foi alterado, apenas o vínculo.
