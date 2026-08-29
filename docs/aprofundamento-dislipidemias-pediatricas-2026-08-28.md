# Aprofundamento Tudo com Tudo — Dislipidemias pediátricas — 28/08/2026

## Contexto

Sétimo lote de aprofundamento do dia (após `doenca-coronariana-idoso`,
PR #603; `valva-aortica-bicuspide-pediatrica`, PR #604; `hipotensao-
ortostatica-no-idoso`, PR #606; `sopros-na-infancia`, PR #608;
`hipertensao-arterial-pediatrica`, PR #609; `dor-toracica-pediatrica`,
PR #610). A ficha `dislipidemias-pediatricas` (área `cardiopediatria`,
`prevalence_rank: 27`) tinha apenas metadados de catalogação — nenhum
campo clínico, zero `related_document_slugs` (pior caso de violação da
regra Tudo com Tudo entre os candidatos livres de PR, segundo o agente
de busca). É distinta do hub geral `dislipidemia`, voltado ao adulto,
mas a consolidação posterior do corpus demonstrou uma interseção
cientificamente legítima e fechada em três documentos de
hipercolesterolemia familiar, descrita abaixo.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (HF heterozigota
   1:250-1:300, homozigota ~1:160.000-1:300.000, subdiagnóstico
   pediátrico, aterosclerose subclínica já mensurável na infância em HF
   não tratada — Wiegman et al. 2004), `presentation` (10 itens),
   `diagnostic_approach` (5 subtópicos: rastreio universal AAP/NHLBI,
   rastreio seletivo em cascata, critérios de HF heterozigota — LDL-C
   ≥190/160/130 mg/dL conforme contexto —, critérios de HF homozigota —
   LDL-C tipicamente >400 mg/dL, priorizando fenótipo sobre genótipo
   pelo consenso EAS 2023 —, investigação de causas secundárias),
   `differentials` (8), `tests` (8), `red_flags` (8), `source_refs` (11).
2. **Tratamento e assistente** — `treatment_summary` (mudança de estilo
   de vida por 6-12 meses antes de fármaco, critérios objetivos de
   início de estatina, manejo especializado de HF homozigota com
   estatina de alta intensidade + ezetimiba e aférese de LDL, rastreio
   familiar em cascata), `ambulatory_flow` (8), `emergency_flow` (5),
   `monitoring` (7), `assistant_questions` (10), `assistant_rules` (10,
   priority 100 para pancreatite por hipertrigliceridemia grave).
3. **Populações especiais e conexões** — `special_populations` (6: HF
   homozigota, obesidade/síndrome metabólica, diabetes, DRC/síndrome
   nefrótica, parente assintomático em rastreio de cascata,
   hipertrigliceridemia grave), `related_document_slugs` (5 propostos,
   incluindo um sobre evinacumabe com braço pediátrico dedicado do
   ensaio ELIPSE HoFH).

## Correção de compliance feita na montagem

Os limiares diagnósticos de LDL-C (190/160/130 mg/dL para HF
heterozigota, >400 mg/dL para HF homozigota) usam "mg/dL" — unidade de
concentração laboratorial, não posologia de fármaco. O regex de checagem
de dose (`\d+\s*mg\b`) inicialmente marcaria isso como falso-positivo;
ajustado com lookahead negativo (`(?!/d[lL])`) para distinguir "190
mg/dL" (diagnóstico, mantido) de "5 mg" (dose, proibido) — mesma
disciplina já aplicada a "índice cardíaco <2,2 L/min/m²" e "HV ≥70ms" em
ciclos anteriores. Nenhuma dose de fármaco foi incluída; estatina,
ezetimiba e evinacumabe são citados apenas por classe/nome, sem
posologia.

## Verificações feitas na montagem e reconciliação posterior

- Todos os 5 `related_document_slugs` foram verificados individualmente —
  confirmada menção a dislipidemia/colesterol/hipercolesterolemia e a
  contexto pediátrico explícito no texto de cada um.
- Na branch original não havia sobreposição com o hub adulto porque ele
  ainda não estava consolidado. Após a composição canônica dos dois hubs,
  a auditoria identificou **exatamente três documentos compartilhados**, o
  que é clinicamente apropriado porque hipercolesterolemia familiar é uma
  doença genética contínua desde a infância e esses três documentos tratam
  de diagnóstico/manejo de HF, algoritmo DLCN e HF homozigota/ELIPSE HoFH:
  - `hipercolesterolemia-familiar-hf-diagnostico-e-manejo-atualizado-esceas-2025`;
  - `fluxograma-hipercolesterolemia-familiar-diagnostico-dlcn-e-manejo-esc-eas-2025`;
  - `evinacumabe-inibidor-de-angptl3-na-hipercolesterolemia-familiar-homozigota-o-ensaio-elipse-hofh`.
- O contrato de teste foi atualizado para exigir **igualdade exata** com
  esses três slugs. Qualquer quarto documento compartilhado volta a falhar
  até revisão explícita, preservando separação entre escopo pediátrico e hub
  adulto sem negar uma sobreposição transversal real.
- O agente de pesquisa descartou explicitamente candidatos com menção apenas
  de passagem (cardiotoxicidade oncológica pediátrica citando dislipidemia
  como item de checklist; HAS pediátrica citando perfil lipídico como exame
  de rotina; lerodalcibepe/PROGRAM LIBERATE citando "30% pediátricos" apenas
  como dado demográfico sem discussão dedicada).
- `patient_material_slug` permanece `null` — os dois candidatos mais próximos
  são sobre HF em população adulta/geral e sobre obesidade infantil com
  colesterol como apenas um dos temas, nenhum central o suficiente.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Fontes primárias

11 referências novas, com PMID verificado, incluindo o painel NHLBI 2011
(rastreio universal), a meta-análise de prevalência de HF de Beheshti et
al. (JACC 2020, 11 milhões de indivíduos) e o consenso EAS 2023 de HF
homozigota (Cuchel et al.).

## Riscos e limitações

- O conteúdo clínico continua específico da população pediátrica; a
  sobreposição documental acima não transforma a ficha em duplicata do hub
  adulto.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug` permanece `null`.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []` no lote original.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []` no lote original.
- `backend/tests/test_aprofundamento_dislipidemias_pediatricas.py`: contrato
  revisado para validar a interseção canônica exata de três documentos.
- A visão canônica continua carregada por `disease_manifest`, incluindo
  fragmentos/correções e o status de revisão publicado.
