# Tudo com Tudo — novo verbete-hub de Taquicardia supraventricular (geral) — 27/08/2026

## Lacuna identificada

Auditoria do corpus confirmou que não havia nenhum verbete-hub geral de
**taquicardia supraventricular (TSV) do adulto** no Guia de Doenças —
apenas o hub-irmão `taquicardia-supraventricular-fetal` (área
cardiopediatria). `content/Arritmias/` (54 documentos) reunia 10
documentos que mapeiam quase 1:1 o escopo da diretriz ESC 2019 de TSV
(AVNRT, AVRT/WPW, taquicardia atrial focal e multifocal, taquicardia
juncional/PJRT, SANRT, taquicardia sinusal inapropriada). Este é o décimo
terceiro ciclo Tudo com Tudo do dia, após endocardite infecciosa (PR #553),
pericardite (PR #554), hipertensão pulmonar (PR #555), síncope (PR #560),
valvopatias (PR #563), cardiomiopatias (PR #565), miocardite (PR #568),
dislipidemia (PR #570), diabetes mellitus tipo 2 (PR #572), tromboembolismo
venoso (PR #574), doença arterial periférica de membros (PR #578) e doença
da aorta (PR #580).

## Escopo e cuidado com duplicação

Novo slug `taquicardia-supraventricular`, área `geral`. Fibrilação e
flutter atrial já têm hub próprio (`fibrilacao-atrial`) — citados apenas
como diferencial, não como objeto central deste hub. O verbete-irmão fetal
foi checado e não duplicado.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology`, `presentation` (8
   itens), `diagnostic_approach` (estruturado em dict: diferencial de QRS
   estreito no ECG de 12 derivações, manobras vagais diagnósticas,
   critérios de WPW pré-excitado assintomático, avaliação de risco de
   morte súbita em WPW), `differentials` (6), `tests` (7), `red_flags` (7),
   `source_refs` (9).
2. **Tratamento e fluxos** — `treatment_summary` (3229 caracteres,
   cobrindo manobras vagais/adenosina como primeira linha, ablação vs.
   fármaco por subtipo, manejo de WPW pré-excitado assintomático,
   particularidades da taquicardia sinusal inapropriada e da taquicardia
   atrial multifocal), `ambulatory_flow` (8), `emergency_flow` (6),
   `monitoring` (8), `assistant_questions` (7), `assistant_rules` (8, com
   2 regras de prioridade máxima 100 e 90: instabilidade hemodinâmica e
   fibrilação atrial pré-excitada em WPW).
3. **Populações especiais e conexões** — `special_populations` (5:
   gestante, WPW em atleta competitivo, idoso com taquicardia atrial
   multifocal/DPOC, criança/adolescente com referência ao hub-irmão fetal,
   puérpera/lactante), `related_document_slugs` (12), `patient_material_slug`.

## Correção de compliance feita na montagem

O agente de pesquisa 3 inicialmente incluiu, no item de `special_populations`
sobre criança/adolescente, dose de adenosina em mg/kg e energia de
cardioversão em J/kg. Essas doses foram **removidas e reescritas em termos
qualitativos** ("dose pediátrica ponderal distinta da dose fixa do adulto,
ajustada conforme protocolo pediátrico") antes da montagem final,
respeitando a proibição categórica de doses de fármaco em qualquer campo
do corpus. Um teste dedicado
(`test_nenhuma_dose_de_farmaco_em_nenhum_campo`) varre todo o registro
final por padrões de dose (mg, mg/kg, J/kg) para prevenir recorrência.

## Fontes primárias

9 referências, todas com PMID/DOI verificado via NCBI E-utilities:

- Brugada et al. 2019, ESC Guidelines (TSV) — PMID 31504425
- Page et al. 2015, ACC/AHA/HRS Guideline (TSV) — PMID 26399663
- Gomes et al. 1985, série original de SANRT — PMID 3964808
- Bahar et al. 2025, revisão de caso de SANRT — PMID 40761218
- Pappone et al. 2003, NEJM (ablação profilática em WPW) — PMID 14602878
- Pereira et al. 2021, revisão de morte súbita em WPW — PMID 34840830
- Chhabra et al., StatPearls (WPW) — PMID 32119324
- Kistler et al. 2006, algoritmo de morfologia de onda P — PMID 16949495
- Custer et al., StatPearls (taquicardia atrial multifocal) — PMID 29083603

## Relações Tudo com Tudo

12 `related_document_slugs`: os 10 do núcleo direto de TSV mais 2
encontrados por busca ampla (fluxograma de palpitações e
taquicardiomiopatia induzida por taquicardia). Um 11º candidato
(extrassístole supraventricular e risco de FA futura) foi deliberadamente
excluído por ser sobre risco futuro de FA, não sobre TSV sustentada.

`patient_material_slug`: `taquicardia-supraventricular-crise-o-que-fazer`
(confirmado existente em `material-paciente/metadados.json`).

## Coordenação com Codex

Nenhum dos 30 PRs abertos verificados cria o slug `taquicardia-supraventricular`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não é publicado até
  revisão humana.
- Nenhuma dose de fármaco é citada — verificado programaticamente.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  `total_records: 9497`, `total_files: 2193` (nenhum documento novo criado).
- `backend/tests/test_tudo_com_tudo_taquicardia_supraventricular.py`: 8
  testes, todos passando (inclui varredura dedicada de padrões de dose).
- `backend/tests/test_canonical_content_review_status.py`: passando com
  `taquicardia-supraventricular` na allowlist `PENDENTES_LOTES_TUDO_COM_TUDO`.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-13-20260827`, baseada em `origin/main`
sem drift no momento do commit.
