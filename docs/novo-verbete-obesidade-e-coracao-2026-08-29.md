# Verbete novo — Obesidade e risco cardiovascular — 29/08/2026

## Contexto

Rodada de reconhecimento sistêmico identificou que **obesidade como
fator de risco cardiovascular** não tinha ficha própria em
`doencas/metadados.json`, apesar de corpus rico já existente (11
documentos dedicados: SELECT, STEP-HFpEF, SUMMIT, SOS, paradoxo da
obesidade no perioperatório, DOAC em obesidade extrema, estigma de peso
na consulta cardiológica).

Criado via `doencas/fragmentos/obesidade-e-coracao.json` para minimizar
colisão com outras frentes de produção concorrentes.

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: 2/3 do excesso de mortalidade da obesidade é
  cardiovascular (consenso ESC 2024), independência causal parcial
  (SELECT positivo vs. Look AHEAD neutro).
- `presentation` (10), `diagnostic_approach` (4 eixos — IMC,
  circunferência abdominal, obesidade sarcopênica, rastreio de
  comorbidades cardiometabólicas), `differentials` (8), `tests` (9),
  `red_flags` (8).
- `treatment_summary`: estilo de vida como base, agonistas de GLP-1/GIP
  com benefício cardiovascular demonstrado, ajuste técnico de terapias
  em obesidade extrema, cirurgia bariátrica em casos selecionados, sem
  doses.
- `ambulatory_flow` (10), `emergency_flow` (6), `monitoring` (9).
- `special_populations` (6).
- `assistant_questions` (13), `assistant_rules` (10).
- `related_document_slugs` (7, do zero).

## Verificação de citações

Todos os 10 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem (consenso ESC 2024, SELECT, STEP-HFpEF,
STEP-HFpEF DM, SUMMIT, SOS, metabolic surgery JAMA 2019, paradoxo da
obesidade perioperatório, DOAC/ISTH, EWGSOP2).

## Verificações feitas na montagem

- Os 7 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema — todos lidos por completo antes da inclusão.
- `patient_material_slug`: nenhuma correspondência encontrada em
  `material-paciente/metadados.json`, mantido `null`.
- `category='prevencao_e_risco'` já existe na convenção do corpus (área
  geral).
- Overlaps legítimos e pré-existentes documentados com
  `diabetes-mellitus-tipo-2` e `tromboembolismo-venoso` (hubs irmãos).

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Gate `test_canonical_content_review_status.py` falha intencionalmente
  (política vigente desde 28/08/2026 exige `revisado` sem exceção).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_novo_verbete_obesidade_e_coracao.py`: 13 testes,
  todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `backend/tests/test_canonical_content_review_status.py`: 1 falha
  esperada, documentada acima.
- `app.main` importa sem erro.
