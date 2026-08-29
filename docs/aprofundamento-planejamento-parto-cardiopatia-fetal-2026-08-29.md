# Aprofundamento Tudo com Tudo — Planejamento do parto na cardiopatia fetal — 29/08/2026

## Contexto

Ficha `planejamento-parto-cardiopatia-fetal` (área `cardiopediatria`,
categoria `cardiologia_fetal`, `prevalence_rank: 41`) estava
`completeness: basico`, só catalogação (1 `source_ref`: AHA Scientific
Statement), zero campos clínicos. Confirmei via `gh pr list --search`
que nenhuma PR aberta recente tocava este slug (a PR antiga #564,
travada desde 27/08, não toca este slug especificamente).

## Conteúdo produzido

- `epidemiology`: taxa de detecção pré-natal de cardiopatia crítica
  (30-70% conforme sistema), impacto do planejamento antecipado na
  redução de morbimortalidade neonatal.
- `presentation` (11), `diagnostic_approach` (3 eixos — categorização de
  risco perinatal, definição de local do parto, definição de intervenção
  imediata), `differentials` (7), `tests` (8), `red_flags` (8).
- `treatment_summary`: estratificação de risco perinatal por lesão,
  definição do local do parto conforme categoria, plano de contingência
  formal, via de parto majoritariamente obstétrica, comunicação
  estruturada entre equipes, sem doses.
- `ambulatory_flow` (10), `emergency_flow` (6), `monitoring` (8).
- `special_populations` (7).
- `assistant_questions` (14), `assistant_rules` (11, priority 95 para
  septo restritivo em lesão dependente de mistura).
- `related_document_slugs` expandido de 1 para 5.

## Verificação de citações

Todos os 6 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem (Moray et al. JAHA 2024, Donofrio et al.
Circulation 2014, Divanović et al. J Thorac Cardiovasc Surg 2011, Punn &
Silverman JASE 2011, Seale et al. Ultrasound Obstet Gynecol 2012, Buca
et al. J Matern Fetal Neonatal Med 2022).

## Verificações feitas na montagem

- Os 4 novos `related_document_slugs` verificados individual e
  programaticamente quanto à resolução e à menção explícita ao tema —
  todos lidos por completo antes da inclusão.
- **Descartados explicitamente 4 candidatos** que tratam de cardiopatia
  MATERNA na gestação (eclâmpsia/HAS grave, TEP na gestação, SCA na
  gestação/puerpério, CMH-LVOTO descompensada) — tema irmão mas
  distinto: nesses, "planejamento do parto" é decidido pela doença da
  mãe, não do feto. O próprio corpus confirma essa distinção
  explicitamente.
- Overlaps legítimos e pré-existentes documentados com 6 fichas irmãs de
  cardiologia fetal (tetralogia de Fallot, TSV fetal, flutter atrial
  fetal, TGA fetal, RVPA fetal).

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente.

## ⚠️ Mesma mudança de gate documentada em outras PRs de hoje

Ver PR #678 (atresia-tricúspide) para detalhes completos. O gate
`test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
falha intencionalmente para esta PR, pois `review_status` permanece
`pendente_revisao`. Todos os demais gates passam.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_planejamento_parto_cardiopatia_fetal.py`:
  11 testes, todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `backend/tests/test_canonical_content_review_status.py`: 1 falha
  esperada, documentada acima.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-planejamento-parto-cardiopatia-fetal-20260829`.
