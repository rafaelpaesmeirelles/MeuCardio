# Aprofundamento Tudo com Tudo — Plano de alta cardiogeriátrico — 28/08/2026

## Contexto

Quadragésimo lote de conteúdo do dia. A ficha `plano-alta-cardiogeriatria`
(área `cardiogeriatria`, categoria `transicao_cuidado`, `prevalence_rank: 15`)
estava `completeness: basico`, só catalogação (1 `source_ref`: AHA
Scientific Statement sobre idosos na UTI cardiológica), zero campos
clínicos, mas já tinha 3 `related_document_slugs` pré-existentes
(atendendo o piso mínimo da regra Tudo com Tudo) e `review_status: revisado`
herdado de uma revisão anterior que cobria apenas a catalogação. Quarta
ficha desbloqueada hoje pela reavaliação de escopo da PR #551.

## Conteúdo produzido

- `epidemiology`: readmissão em 30 dias no idoso cardiopata (~20% geral,
  ~25% pós-IC), fatores de risco (polifarmácia, fragilidade, isolamento
  social, transição de cuidado malfeita), evidência de modelos
  estruturados (Care Transitions Intervention, Transitional Care Model).
- `presentation` (11), `diagnostic_approach` (7 etapas — estratificação de
  risco, reconciliação medicamentosa, suporte social, rastreio cognitivo/
  funcional, educação, seguimento precoce, comunicação com atenção
  primária), `differentials` (7), `tests` (8), `red_flags` (8).
- `treatment_summary`: os 3 pilares (reconciliação medicamentosa completa
  sem doses, educação estruturada com teach-back, retorno ambulatorial
  precoce de 7-14 dias) mais telessaúde/reabilitação cardíaca, suporte
  social e comunicação estruturada com a atenção primária.
- `ambulatory_flow` (11), `emergency_flow` (6), `monitoring` (8).
- `special_populations` (6).
- `assistant_questions` (14), `assistant_rules` (12, priority 95 para
  dependência sem suporte social, 92 para congestão residual na alta).
- `related_document_slugs` mantido em 3 (piso mínimo, reconfirmado).

## Verificação de citações

Todos os 6 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem (Jencks et al. NEJM 2009, Coleman et al. Arch
Intern Med 2006, Naylor et al. J Am Geriatr Soc 2004, van Walraven et al.
CMAJ 2010, Kansagara et al. JAMA 2011, Donzé et al. JAMA Intern Med 2013).
O agente de pesquisa havia inicialmente proposto PMIDs incorretos para
Coleman 2006 e Naylor 2004, corrigidos pelo próprio agente após verificação
e reconfirmados por mim de forma independente antes da montagem.

## Verificações feitas na montagem

- Os 3 `related_document_slugs` pré-existentes (PACT-HF, telessaúde/
  monitoramento remoto na IC do idoso, reabilitação cardíaca no muito
  idoso) foram reconfirmados por leitura direta dos documentos — todos
  centrais ao tema de plano de alta/transição de cuidado.
- Um grep amplo em `content/Cardiologia_geriátrica` não encontrou nenhum
  candidato adicional genuinamente central: os demais resultados usavam
  "reinternação"/"transição de cuidado" apenas como desfecho lateral
  (válvula, iSGLT2, delirium, anemia, desprescrição) ou em outro sentido
  (cuidados paliativos usa "transição de cuidado" para mudança de objetivo
  terapêutico curativo→paliativo, não plano de alta hospitalar). Total
  mantido em 3 — nenhum vínculo fabricado.
- `patient_material_slug` permanece vazio: busca programática por
  "alta"+idoso/cardíaco/hospital em `material-paciente/metadados.json` não
  retornou correspondência inequívoca.
- **Overlap pré-existente e legítimo**: `reabilitacao-cardiaca-no-muito-
  idoso-...` também vinculado por `fragilidade-pre-procedimento-
  cardiovascular` e `doenca-coronariana-idoso` — documentado no teste
  dedicado.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração. `source_refs`/`source_urls`
originais preservados e complementados (1 → 7).

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — revertido do
  `revisado` herdado, porque todo o conteúdo clínico novo ainda não
  passou por revisão humana; não publica até revisão.
- Nenhuma dose de fármaco é citada.
- Overlap parcial mas documentado com 2 outras fichas de cardiogeriatria.
- `patient_material_slug` permanece não preenchido por falta de
  correspondência confiável — decisão consciente de não fabricar vínculo.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_plano_alta_cardiogeriatria.py`: 12
  testes, todos passando (1 correção durante desenvolvimento, para
  documentar overlap pré-existente descoberto pelo próprio teste).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando, 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-plano-alta-cardiogeriatria-20260828`, baseada em
`origin/main` sem drift no momento do commit.
