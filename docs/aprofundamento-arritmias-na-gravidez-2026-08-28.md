# Aprofundamento Tudo com Tudo — Arritmias na gravidez — 28/08/2026

## Contexto

A ficha `arritmias-na-gravidez` (área `gravidez`, categoria `arritmia`,
`prevalence_rank: 6`) estava `completeness: intermediario`, zero
`related_document_slugs`, zero `patient_material_slug`.

## Conteúdo produzido

- `epidemiology`: palpitações como queixa comum na gestação, TSV
  paroxística como arritmia sustentada mais relevante, alterações
  fisiológicas gestacionais predisponentes.
- `presentation` (12), `diagnostic_approach` (6 eixos — ECG, monitorização
  ambulatorial, ecocardiograma, avaliação de gatilhos, avaliação fetal),
  `differentials` (8), `tests` (8), `red_flags` (9).
- `treatment_summary`: conduta conservadora inicial, escolha de
  antiarrítmico priorizando segurança gestacional (sem doses), cardioversão
  elétrica segura em qualquer trimestre, encaminhamento a cardiologia
  obstétrica, plano de parto individualizado.
- `ambulatory_flow` (10), `emergency_flow` (7), `monitoring` (8).
- `special_populations` (6).
- `assistant_questions` (13), `assistant_rules` (10, priority 100 para
  instabilidade hemodinâmica).
- `related_document_slugs` criado do zero: 7.
- `patient_material_slug` preenchido: `arritmia-na-gravidez-remedios-
  seguros-para-o-coracao`.

## Verificação de citações

Todos os 7 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem (Adamson & Nelson-Piercy Heart 2007, Silversides
et al. Am J Cardiol 2006, Enriquez et al. Circ Arrhythm Electrophysiol
2014, Li et al. Clin Cardiol 2008, Joglar & Page Curr Opin Cardiol 2014,
ESC Guidelines 2018, ACC/AHA/HRS SVT Guideline 2015).

## Verificações feitas na montagem

- Os 7 `related_document_slugs` foram encontrados do zero e cada um
  verificado por mim, de forma independente do agente de pesquisa, por
  leitura direta do arquivo — incluindo o candidato mais limítrofe
  (pré-eclâmpsia/HELLP), cujo título e conteúdo dedicam seção substancial
  ao manejo de TSV aguda na gestante, confirmando centralidade real, não
  apenas menção lateral.
- `patient_material_slug` confirmado por correspondência exata em
  `material-paciente/metadados.json`.
- **Overlap pré-existente e legítimo**: `taquiarritmia-na-gestacao-com-
  instabilidade-hemodinamica` também vinculado por `medicamentos-
  cardiovasculares-gestacao-lactacao` (ficha processada mais cedo hoje) —
  documentado no teste dedicado.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `prevalence_rank` originais
preservados sem alteração.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap parcial mas documentado com `medicamentos-cardiovasculares-
  gestacao-lactacao`.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_arritmias_na_gravidez.py`: 11
  testes.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando, 6 testes.
- `app.main` importa sem erro.
- Total: 17 testes executados, 17 passando.

## Branch e PR

Branch `claude/aprofundar-arritmias-na-gravidez-20260828`, baseada em
`origin/main` sem drift no momento do commit.
