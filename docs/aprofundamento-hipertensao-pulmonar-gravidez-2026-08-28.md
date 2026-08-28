# Aprofundamento Tudo com Tudo — Hipertensão pulmonar na gravidez — 28/08/2026

## Contexto

Décimo terceiro lote de aprofundamento do dia (após `doenca-
coronariana-idoso`, PR #603; `valva-aortica-bicuspide-pediatrica`,
PR #604; `hipotensao-ortostatica-no-idoso`, PR #606; `sopros-na-
infancia`, PR #608; `hipertensao-arterial-pediatrica`, PR #609;
`dor-toracica-pediatrica`, PR #610; `dislipidemias-pediatricas`,
PR #611; `arritmias-pediatricas`, PR #612; `avaliacao-multidimensional-
cardiogeriatrica`, PR #613; `cuidados-paliativos-cardiovasculares`,
PR #615; `cardiopatia-congenita-gravidez`, PR #616). A ficha
`hipertensao-pulmonar-gravidez` (área `gravidez`, categoria
`circulacao_pulmonar`, `prevalence_rank: 11`) já tinha `summary`,
`tags`, 1 `source_ref` de catalogação, 2 `related_document_slugs` e 1
`patient_material_slug` — aprofundamento "completo" nos campos
clínicos, "pontual" nos vínculos (ampliados, não recriados do zero).

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (mortalidade
   materna histórica de até ~56% pré-terapias-alvo, hoje ainda entre
   3% e 12% mesmo em centros de referência, segundo Weiss et al. e
   registro ROPAC), `presentation` (10 itens), `diagnostic_approach`
   (5 subtópicos: classificação de risco materno, avaliação
   ecocardiográfica, cateterismo cardíaco direito, biomarcadores,
   classificação etiológica em 5 grupos clínicos), `differentials` (7
   grupos clínicos de hipertensão pulmonar), `tests` (8), `red_flags`
   (8), `source_refs` (8, incluindo ESC 2025, ESC/ERS 2022 e os
   estudos de coorte/registro ROPAC).
2. **Conduta e assistente** — `treatment_summary` (contraindicação
   absoluta, aconselhamento pré-concepcional, Pregnancy Heart Team,
   classes terapêuticas vasodilatadoras pulmonares sem posologia,
   plano de parto, puerpério como período de maior risco),
   `ambulatory_flow` (9), `emergency_flow` (9), `monitoring` (7),
   `assistant_questions` (12), `assistant_rules` (10, priority 100
   para HAP confirmada + síndrome de Eisenmenger).
3. **Populações especiais e conexões** — `special_populations` (7:
   Eisenmenger, HAP idiopática/hereditária, associada a doença do
   tecido conjuntivo, tromboembólica crônica, puerpério imediato,
   diagnóstico tardio, prole), `related_document_slugs` (união dos 2
   já existentes com 3 novos propostos = 5 no total).

## Correção de compliance feita na montagem

O texto de `special_populations` produzido pelo agente de pesquisa
usava a sigla "mWHO IV" (duas ocorrências) para a classificação de
risco materno da OMS/ESC — contém a substring banida. Reescrito por
extenso ("categoria de maior risco/contraindicação formal da
classificação de risco materno da OMS/ESC") mantendo o conteúdo
clínico intacto — mesmo precedente já aplicado em
`cardiopatia-congenita-gravidez` (PR #616). Também descoberto e
corrigido durante a montagem: o próprio texto do `review_note` que eu
estava escrevendo, ao *descrever* essa correção, citava a sigla
banida entre aspas — reescrito para descrever a correção sem repetir
a sigla, e o `assemble.py` falhou corretamente na primeira execução
até esse ajuste (evidência de que a checagem programática funciona).

## Verificações feitas na montagem

- Os 5 `related_document_slugs` finais (2 já existentes + 3 novos)
  verificados individualmente quanto à resolução e ao escopo — todos
  fora de Farmacologia/Calculadoras/Exames.
- Menção temática verificada com termo ampliado: o documento
  `fluxograma-hipertensao-pulmonar-descompensada-na-gestacao-e-
  puerperio` (um dos 2 já existentes antes deste lote) não escreve a
  frase "hipertensão pulmonar" por extenso em nenhum ponto do texto —
  usa as siglas "HAP"/"HP" ao longo de todo o documento (título:
  "Fluxograma: HAP descompensada na gestação e no puerpério").
  Confirmado manualmente, por leitura completa do arquivo, que o
  documento é central e legitimamente sobre hipertensão pulmonar na
  gestação. O teste dedicado usa um conjunto de termos ampliado (frase
  completa OU sigla HAP/HP com word boundary) para não gerar falso
  negativo.
- Dois candidatos propostos pelo agente foram descartados por não
  satisfazerem o critério de menção explícita, já sendo reivindicados
  por `cardiopatia-congenita-gravidez` (PR #616):
  `sindrome-de-eisenmenger-contraindicacao-absoluta-a-gestacao-
  mecanismo-mwho-iv` (nunca usa a frase "hipertensão pulmonar",
  apenas "resistência vascular pulmonar") e `escores-de-risco-
  materno-carpreg-carpreg-ii-e-zahara` (menção de HAP é apenas 1 de
  10 preditores de risco em uma lista, não central ao documento).
- Nenhuma sobreposição de `related_document_slugs` detectada com
  outras fichas *nesta branch* (baseada em `origin/main` antes do
  merge do PR #616). Uma sobreposição é esperada e já documentada
  preventivamente no teste dedicado: `sindrome-de-eisenmenger-e-
  gestacao-mortalidade-materna-do-registro-britanico-ao-ropac` também
  está em `related_document_slugs` de `cardiopatia-congenita-
  gravidez` (PR #616, ainda não mesclado) — legítimo, ambas as fichas
  tratam centralmente do mesmo tema clínico sob ângulos diferentes
  (cardiopatia congênita geral vs. hipertensão pulmonar
  especificamente).
- `patient_material_slug` original (`hipertensao-pulmonar-e-gravidez-
  por-que-planejar-com-antecedencia`) preservado sem alteração —
  reconfirmado como existente em `material-paciente/metadados.json`.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente (incluindo o padrão `j/kg` de energia de choque de
dispositivo, adicionado no lote de `arritmias-pediatricas`/PR #612).
Classes terapêuticas vasodilatadoras pulmonares citadas por nome
(antagonistas de receptor de endotelina, inibidores da
fosfodiesterase-5, estimuladores da guanilato-ciclase solúvel,
prostanoides) sem posologia. Estrutura de perguntas e regras validada
com o motor de regras real antes da montagem — todos os operadores
usados pertencem ao conjunto permitido (`eq`, `in`, `contains`, `gte`,
`lt`), nenhum uso de "includes".

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

8 referências, com PMID verificado, incluindo a diretriz ESC 2025 de
doença cardiovascular na gravidez, a diretriz ESC/ERS 2022 de
hipertensão pulmonar, a revisão sistemática histórica de Weiss et al.
(1998) e os estudos de coorte/registro ROPAC (Sliwa et al. 2016,
Roos-Hesselink et al. 2019).

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `hipertensao-pulmonar-gravidez`, além do
overlap documentado acima com `cardiopatia-congenita-gravidez`
(PR #616), que não edita esta ficha diretamente.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap de um documento com `cardiopatia-congenita-gravidez`
  (PR #616) documentado, mas só ficará visível ao gate combinado
  depois que ambos os PRs forem mesclados — sinalizado aqui
  preventivamente para o revisor.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_hipertensao_pulmonar_gravidez.py`:
  11 testes, todos passando de primeira (após a correção do
  `review_note`).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 17 testes executados, 17 passando.

## Branch e PR

Branch `claude/aprofundar-hipertensao-pulmonar-gravidez-20260828`,
baseada em `origin/main` sem drift no momento do commit.
