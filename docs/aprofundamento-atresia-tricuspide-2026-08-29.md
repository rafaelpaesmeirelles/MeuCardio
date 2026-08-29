# Aprofundamento Tudo com Tudo — Atresia tricúspide — 29/08/2026

## Contexto

Ficha `atresia-tricuspide` (área `cardiopediatria`, categoria
`cardiopatia_congenita`) estava `completeness: basico`, com 1
`related_document_slug` pré-existente e `patient_material_slug` já
preenchido. Confirmei via `gh pr list --search` que nenhuma PR aberta
tocava este slug especificamente (distinto dos 6 slugs congênitos ainda
sob trabalho ativo da frota Codex — DSAV, estenose pulmonar congênita,
RVPA, endocardite pediátrica, HP pediátrica, tronco arterial comum).

## Conteúdo produzido

- `epidemiology`: incidência ~1:10.000, classificação Kuhne/Edwards-
  Burchell (tipos I/II/III conforme relação ventrículo-arterial, cada um
  subdividido conforme grau de fluxo pulmonar).
- `presentation` (10), `diagnostic_approach` (6 eixos — avaliação
  inicial, eco fetal, eco neonatal, dependência ductal, exames
  complementares, cateterismo/imagem avançada), `differentials` (8),
  `tests` (8), `red_flags` (8).
- `treatment_summary`: estadiamento cirúrgico em 3 etapas (derivação
  sistêmico-pulmonar ou banda conforme fluxo pulmonar → Glenn
  bidirecional → Fontan), sem doses, seguimento vitalício pós-Fontan.
- `ambulatory_flow` (10), `emergency_flow` (6), `monitoring` (7).
- `special_populations` (6).
- `assistant_questions` (14), `assistant_rules` (13, priority 98 para
  circulação canal-dependente sem suporte farmacológico documentado).
- `related_document_slugs` expandido de 1 para 6.

## Verificação de citações

Todos os 6 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem (incluindo o artigo histórico de Fontan &
Baudet, Thorax 1971, e a coorte inglesa/galesa de Hadjicosta et al.,
Heart 2022).

## Verificações feitas na montagem

- Os 5 novos `related_document_slugs` verificados individual e
  programaticamente quanto à resolução e à menção explícita ao tema —
  todos lidos por completo antes da inclusão.
- Overlaps legítimos e pré-existentes documentados com 6 fichas irmãs de
  cardiopatia congênita (transposição das grandes artérias, síndrome do
  coração esquerdo hipoplásico fetal, fisiologia de ventrículo único,
  dor torácica pediátrica, cardiopatia congênita na gravidez,
  cardiopatia congênita do adulto) — todas compartilhando documentos
  sobre a circulação de Fontan, tema estruturalmente comum a essas
  fichas.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente.

## ⚠️ Mudança substancial de gate descoberta nesta rodada

O gate `test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
mudou de semântica na integração da noite de 28→29/08: antes, um registro
`pendente_revisao` explicitamente listado em `PENDENTES_LOTES_TUDO_COM_TUDO`
passava o gate (mecanismo usado com sucesso em todas as ~19 PRs deste
lote e do lote anterior). Agora o gate exige `review_status == "revisado"`
diretamente — a allowlist só documenta registros **já revisados**, não
mais concede exceção a `pendente_revisao`. Isso é consistente com o
docstring do próprio arquivo ("Os lotes Tudo com Tudo pendentes foram
revisados em 28/08/2026. As allowlists ficam vazias: qualquer novo status
diferente de revisado quebra o gate e exige decisão editorial explícita").

**Efeito prático**: esta PR (e qualquer PR futura que introduza conteúdo
`pendente_revisao`) **vai falhar esse teste específico intencionalmente**
até que um humano/pipeline de revisão marque o registro como `revisado` —
não tentei contornar isso marcando o registro como `revisado` eu mesmo,
pois isso seria autoaprovar conteúdo clínico sem revisão humana real,
contrariando a diretriz permanente da sessão. Mantive
`review_status: pendente_revisao` e documentei a falha esperada aqui.
Todos os outros gates (auditoria estrutural, inventário, teste dedicado,
`test_disease_fragments_canonical.py`, `app.main`) passam normalmente.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_atresia_tricuspide.py`: 10 testes,
  todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `backend/tests/test_canonical_content_review_status.py`:
  **1 falha esperada** (`test_manifestos_canonicos_...`), documentada
  acima — depende de revisão humana, não de correção de código.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-atresia-tricuspide-20260829`.
