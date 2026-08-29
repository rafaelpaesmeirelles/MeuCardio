# Vincular Tudo com Tudo — Parada cardiorrespiratória e morte súbita abortada — 29/08/2026

## Contexto

A ficha `parada-cardiorrespiratoria-e-morte-subita-abortada` já estava
clinicamente completa e revisada, mas tinha apenas 4
`related_document_slugs`. O PR Claude #705 propôs ampliar exclusivamente
as conexões com o corpus pós-parada; nenhuma recomendação, tratamento,
fluxo ou campo clínico pré-existente foi reescrito.

## Vínculos incorporados após auditoria

- `neuroprognostico-multimodal-pos-parada-cardiorrespiratoria-algoritmo-erc-esicm-2021-e-a-atualizacao-aha-2025` — cobre o eixo de neuroprognóstico multimodal e prevenção de prognóstico prematuro pós-ROSC.
- `coronariografia-imediata-apos-parada-cardiaca-sem-supra-de-st-coact-e-tomahawk` — cobre a decisão individualizada de estratégia coronariana após parada sem supra de ST.
- `rcp-extracorporea-ecpr-na-parada-refrataria-arrest-e-inception` — cobre o cenário distinto de parada refratária e seleção para ECPR.

A ficha passa de 4 para 7 vínculos, preservando o teto editorial usado
nesta frente Tudo com Tudo.

## Candidatos revisados e não incorporados

O lote também avaliou documentos de cuidado pós-parada geral, metas de
pressão/oxigenação, HYPERION, via aérea pré-hospitalar e um fluxograma de
coronariografia. Eles foram mantidos fora desta ficha por redundância com
links já existentes ou menor centralidade quando havia uma fonte mais
específica para o mesmo eixo. A decisão preserva diversidade temática sem
inflar a malha com referências equivalentes.

## Governança

A alteração é materializada por uma correção canônica versionada em
`doencas/correcoes/`, para evitar regravar o manifesto inteiro durante o
release consolidado. `review_status` e `completeness` permanecem
inalterados. O `review_note` registra a origem Claude #705 e a revisão da
auditoria consolidada de 29/08/2026.
