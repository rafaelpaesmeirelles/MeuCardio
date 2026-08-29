# Vincular Tudo com Tudo — Parada cardiorrespiratória e morte súbita abortada — 29/08/2026

## Contexto

Ficha `parada-cardiorrespiratoria-e-morte-subita-abortada` (área `geral`,
`completeness: completo`) tinha apenas 4 `related_document_slugs`, apesar
de existir corpus rico de cuidados pós-parada em `content/Terapia_intensiva/`
não vinculado. Lote apenas de vínculo — nenhum conteúdo clínico
pré-existente foi reescrito; `review_status` e `completeness` não foram
alterados.

## Vínculos adicionados (3)

- `neuroprognostico-multimodal-pos-parada-cardiorrespiratoria-algoritmo-erc-esicm-2021-e-a-atualizacao-aha-2025`
- `coronariografia-imediata-apos-parada-cardiaca-sem-supra-de-st-coact-e-tomahawk`
- `rcp-extracorporea-ecpr-na-parada-refrataria-arrest-e-inception`

Total final: 7 (teto da regra Tudo com Tudo).

## Verificação feita na montagem

Os 8 candidatos mapeados em `content/Terapia_intensiva/` foram lidos
integralmente:

1. `cuidados-pos-parada-cardiaca-na-uco-aha-2025-oxigenacao-pressao-temperatura-neuroprognostico` — central, mas protocolo "guarda-chuva" que recobre temperatura, coronariografia e neuroprognóstico já representados de forma mais específica pelos documentos escolhidos; descartado por redundância temática, priorizando diversidade sobre volume.
2. `neuroprognostico-multimodal-pos-parada-cardiorrespiratoria-algoritmo-erc-esicm-2021-e-a-atualizacao-aha-2025` — **escolhido**. O próprio verbete já cita "Evitar neuroprognóstico prematuro e usar avaliação multimodal no momento apropriado" (`diagnostic_approach.apos_retorno_da_circulacao`); tema totalmente ausente dos 4 vínculos originais.
3. `metas-de-pressao-arterial-e-de-oxigenacao-pos-parada-cardiorrespiratoria-o-ensaio-box` — descartado por redundância temática com o vínculo já existente de controle de temperatura pós-parada (mesmo eixo de "metas fisiológicas pós-ROSC").
4. `hipotermia-terapeutica-em-ritmo-nao-chocavel-pos-parada-o-ensaio-hyperion` — descartado pelo mesmo motivo (redundante com `controle-de-temperatura-pos-parada-cardiorrespiratoria-ttm-e-ttm2`, já vinculado).
5. `coronariografia-imediata-apos-parada-cardiaca-sem-supra-de-st-coact-e-tomahawk` — **escolhido**. O próprio verbete já cita "avaliação coronariana individualizada" em `emergency_flow`; tema ausente dos 4 vínculos originais.
6. `rcp-extracorporea-ecpr-na-parada-refrataria-arrest-e-inception` — **escolhido**. Cobre o cenário de parada refratária, ausente dos 4 vínculos originais e distinto tematicamente dos demais.
7. `via-aerea-na-parada-extra-hospitalar-airways-2-e-part-e-o-que-o-paramedic2-mediu` — descartado por menor centralidade ao escopo específico desta ficha (técnica de via aérea/adrenalina pré-hospitalar, já coberto em essência pelo vínculo existente de suporte avançado SBC 2019 e pelo DEA/cadeia de sobrevivência).
8. `fluxograma-cuidado-pos-parada-e-coronariografia` — descartado por redundância com o documento de evidência COACT/TOMAHAWK escolhido (mesmo tema, formato fluxograma em vez de estudo).

Todos os 8 candidatos foram confirmados como discussão central de parada
cardiorrespiratória/cuidados pós-parada (nenhum resolve para
Farmacologia/Calculadoras/Exames). Os 3 escolhidos priorizam diversidade
temática (neuroprognóstico, coronariografia, ECPR) sobre volume, conforme
a regra "Rafael prioriza descoberta sobre volume", e têm ancoragem textual
direta em campos já existentes do próprio verbete (`diagnostic_approach`,
`emergency_flow`).

Nenhuma outra ficha do catálogo referenciava os 3 documentos escolhidos
antes deste lote (verificado por varredura em `doencas/metadados.json`) —
não há sobreposição não documentada a registrar.

## Achado sobre o gate de review_status

Diferente de outros lotes desta frente (ex.: atresia-pulmonar), não existe
patch em `doencas/correcoes/` sobrescrevendo
`parada-cardiorrespiratoria-e-morte-subita-abortada`. O `review_status`
permaneceu `"revisado"` (não alterado por este lote, apenas
`related_document_slugs`, `review_note` e `version`), e
`test_canonical_content_review_status.py` passou sem nenhuma falha
preexistente a documentar para este slug.

## Gates

- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `backend/tests/test_vincular_tudo_com_tudo_parada_cardiorrespiratoria_e_morte_subita_abortada.py`: 9 testes, todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes, passando.
- `backend/tests/test_canonical_content_review_status.py`: 3 testes, passando (sem falha preexistente para este slug).
- `app.main` importa sem erro.
- `DATABASE_URL="postgresql+psycopg://meucardio_test:test@localhost:5432/meucardio_test"` (container `corvia-test-pg`).
- Total: 15 testes pytest executados, 15 passando.

Observação operacional: a primeira tentativa de rodar os testes de banco
sofreu `psycopg.errors.DeadlockDetected` no `TRUNCATE ... RESTART IDENTITY
CASCADE` do fixture `_banco_limpo` — o container `corvia-test-pg` estava
com ~15 processos pytest concorrentes de outras sessões/branches paralelas
desta mesma frente de trabalho no momento da execução. Repetição da suíte
(sem alteração de código) passou sem erro em 356s. Não é uma falha deste
lote.
