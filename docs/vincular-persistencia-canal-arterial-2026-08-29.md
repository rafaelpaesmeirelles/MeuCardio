# Vincular Tudo com Tudo — Persistência do canal arterial — 29/08/2026

## Contexto

Ficha `persistencia-canal-arterial` (área `cardiopediatria`) já era
`completeness: completo`, mas tinha apenas 1 `related_document_slug` —
abaixo do piso mínimo de 3. Confirmado via `gh pr list --search` que
nenhuma PR aberta tocava este slug. Lote apenas de vínculo — nenhum
conteúdo clínico pré-existente foi reescrito.

## Vínculos adicionados (5)

- `persistencia-do-canal-arterial-no-adulto-criterios-hemodinamicos-de-fechamento-esc-2020`
- `fluxograma-comunicacao-interatrial-e-shunt-esquerda-direita-no-adulto-esc-2020`
- `colapso-neonatal-por-cardiopatia-congenita-critica-canal-dependente`
- `fluxograma-colapso-neonatal-por-cardiopatia-congenita-critica-canal-dependente`
- `cianose-no-recem-nascido-diagnostico-diferencial-e-conduta-inicial`

Total final: 6.

## Verificação feita na montagem

O agente de pesquisa avaliou ~35 candidatos e descartou corretamente 18
por menção lateral ou padrão de negação de conexão (destaque:
`janela-aortopulmonar-...` cita PCA repetidamente só para dizer "não
confundir com"). Os 5 aceitos foram confirmados por leitura direta.

Overlaps legítimos e pré-existentes: `fluxograma-comunicacao-
interatrial-...` também em `comunicacao-interventricular`;
`cianose-no-recem-nascido-...` também em `tetralogia-de-fallot`,
`transposicao-das-grandes-arterias`, `sopros-na-infancia`,
`transposicao-grandes-arterias-fetal`; `colapso-neonatal-...` também em
`transposicao-das-grandes-arterias`, `transposicao-grandes-arterias-
fetal`; `persistencia-do-canal-arterial-no-adulto-...` também em
`cardiopatia-congenita-do-adulto`.

## ⚠️ Mesma mudança de gate documentada em outras PRs de hoje

Ver `docs/aprofundamento-atresia-tricuspide-2026-08-29.md` (PR #678) para
detalhes: o gate `test_manifestos_canonicos_so_tem_pendencias_
explicitamente_aprovadas_para_rc` falha intencionalmente para esta PR,
pois `review_status` permanece `pendente_revisao` (não autoaprovado) e a
política atual exige `revisado` sem exceção via allowlist. Todos os
demais gates passam.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_persistencia_canal_arterial.py`: 6 testes.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `backend/tests/test_canonical_content_review_status.py`: 1 falha
  esperada (mesma natureza documentada acima).
- `app.main` importa sem erro.
