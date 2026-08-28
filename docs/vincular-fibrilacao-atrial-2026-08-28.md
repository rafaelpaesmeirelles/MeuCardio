# Vincular Tudo com Tudo (enriquecimento) — Fibrilação atrial — 28/08/2026

## Contexto

Ficha `fibrilacao-atrial` (a ficha geral da arritmia mais prevalente da
prática clínica) já era `completeness: completo` com exatamente 3
`related_document_slugs` — atendendo o piso técnico mínimo, mas
desproporcionalmente rasa: ~59 arquivos em `content/**` mencionam
fibrilação atrial. Lote de enriquecimento apenas de vínculo. Nenhum
conteúdo clínico pré-existente foi reescrito.

## Vínculos adicionados (2)

- `controle-de-ritmo-vs-frequencia-na-fibrilacao-atrial-affirm-east-afnet-4-e-castle-af`
- `ablacao-por-cateter-em-fibrilacao-atrial-indicacoes-e-tecnica`

Total final: 5.

## Verificação feita na montagem

Ambos confirmados por leitura direta do documento completo, cuidando para
não duplicar escopo já coberto pelas fichas irmãs específicas
(`fibrilacao-atrial-no-idoso`, `fibrilacao-atrial-de-inicio-na-gestacao`).
**Descartei um 3º candidato proposto pelo agente** (`cha2ds2-va`) por
resolver para `content/Calculadoras`, pasta explicitamente fora do
escopo permitido pela regra Tudo com Tudo.

Overlap legítimo e pré-existente: `controle-de-ritmo-vs-frequencia-...`
também vinculado por `fibrilacao-atrial-no-idoso`.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_fibrilacao_atrial.py`: 6 testes.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando.
- `app.main` importa sem erro.
- Total: 12 testes executados, 12 passando.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhum conteúdo clínico pré-existente foi alterado, apenas o vínculo.
