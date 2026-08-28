# Aprofundamento Tudo com Tudo — Medicamentos cardiovasculares na gestação e lactação — 28/08/2026

## Contexto

Décimo quarto lote de conteúdo do dia (após `doenca-coronariana-idoso`,
PR #603; `valva-aortica-bicuspide-pediatrica`, PR #604;
`hipotensao-ortostatica-no-idoso`, PR #606; `sopros-na-infancia`,
PR #608; `hipertensao-arterial-pediatrica`, PR #609;
`dor-toracica-pediatrica`, PR #610; `dislipidemias-pediatricas`,
PR #611; `arritmias-pediatricas`, PR #612;
`avaliacao-multidimensional-cardiogeriatrica`, PR #613;
`cuidados-paliativos-cardiovasculares`, PR #615;
`cardiopatia-congenita-gravidez`, PR #616;
`hipertensao-pulmonar-gravidez`, PR #621;
`cardiotoxicidade-bcr-abl`, PR #624). A ficha
`medicamentos-cardiovasculares-gestacao-lactacao` (área `gravidez`,
categoria `farmacologia`, `prevalence_rank: 14`) tinha apenas
metadados de catalogação — zero campos clínicos, zero
`related_document_slugs`, sem `patient_material_slug`.

Diferente de todas as fichas anteriores do dia, esta não trata de uma
única doença: é um guia transversal de decisão farmacológica sobre
segurança de classes de fármacos cardiovasculares na gestação e na
lactação.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (lacuna estrutural
   de evidência por exclusão sistemática de gestantes de ensaios
   clínicos, princípio de decisão individualizada risco-benefício),
   `presentation` (11 cenários de decisão, não sintomas de doença),
   `diagnostic_approach` (7 subtópicos por classe farmacológica:
   inibidores do sistema renina-angiotensina, antagonistas de vitamina
   K/heparinas, beta-bloqueadores, diuréticos, amiodarona, estatinas,
   anticoagulantes orais diretos), `differentials` (6, categorias de
   decisão farmacológica), `tests` (8), `red_flags` (8), `source_refs`
   (7, com PMIDs verificados).
2. **Conduta e assistente** — `treatment_summary` (contraindicações
   absolutas, troca planejada pré-concepcional, manejo de
   anticoagulação em prótese mecânica, avaliação separada de
   segurança gestacional vs. compatibilidade com lactação),
   `ambulatory_flow` (11), `emergency_flow` (7), `monitoring` (9),
   `assistant_questions` (13), `assistant_rules` (10, priority 98
   para uso confirmado de IECA/BRA em gestação em curso).
3. **Populações especiais e conexões** — `special_populations` (6:
   prótese valvar mecânica, IECA/BRA inadvertido, amiodarona em
   arritmia refratária, estatina em dislipidemia familiar grave,
   puérpera lactante, insuficiência cardíaca com diurético),
   `related_document_slugs` (7, o máximo permitido).

## Verificações feitas na montagem

- Todos os 7 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo (fora de
  Farmacologia/Calculadoras/Exames) e à menção de classe/fármaco
  cardiovascular relevante no texto.
- **4 dos 7 compartilhados** com fichas de gravidez já publicadas ou
  aprofundadas: `ropac-iii-anticoagulacao-em-protese-valvar-mecanica-
  na-gestacao-dados-atualizados-de-risco` e `trombose-de-protese-
  valvar-mecanica-na-gestacao` (também em `protese-mecanica-na-
  gravidez` e `valvopatias-na-gravidez`); `anti-hipertensivos-na-
  gestacao-o-que-a-bula-registrada-diz-de-cada-um` (também em
  `hipertensao-cronica-gravidez`); `anticoagulantes-na-gestacao-e-
  lactacao-o-que-diz-a-bula-registrada` (também em `protese-mecanica-
  na-gravidez` e `tromboembolismo-gravidez`) — overlap esperado e
  legítimo, dado o caráter transversal do tema desta ficha (segurança
  farmacológica atravessa múltiplas fichas de doença específica),
  documentado explicitamente no teste dedicado.
- O agente da Parte 3 documentou explicitamente que não encontrou
  documento publicado com foco farmacológico dedicado a "diurético na
  insuficiência cardíaca gestacional" (apenas menções de protocolo
  genérico dentro de fichas de doença de base) — não incluído como
  link por não satisfazer o critério de centralidade do documento ao
  tema.
- `patient_material_slug` (`medicamentos-cardiovasculares-gestacao-
  lactacao`, mesmo slug da própria ficha) confirmado como existente
  em `material-paciente/metadados.json`, já vinculado a um dos
  documentos técnicos incluídos.

Nenhuma dose de fármaco em nenhum campo — verificação reforçada por
ser tema farmacológico (maior risco de menção inadvertida de
posologia), checado programaticamente com os mesmos 4 padrões de
regex das rodadas anteriores. Classes e nomes de fármacos citados
apenas por classificação de segurança (contraindicado/preferido/
compatível com amamentação), nunca por dose. Estrutura de perguntas e
regras validada com o motor de regras real — todos os operadores
usados pertencem ao conjunto permitido, nenhum uso de "includes".

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

7 referências com PMID verificado, incluindo a diretriz ESC 2025 de
doença cardiovascular na gravidez, o estudo clássico de malformações
por IECA no primeiro trimestre (Cooper et al. 2006), a revisão
sistemática de anticoagulação em prótese mecânica (D'Souza et al.
2017) e o estudo de atenolol e restrição de crescimento fetal
(Lydakis et al. 1999).

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `medicamentos-cardiovasculares-gestacao-
lactacao`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada — verificação reforçada por ser
  tema farmacológico.
- Overlap de 4 documentos com outras fichas de gravidez, documentado
  e esperado (tema transversal).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_medicamentos_cardiovasculares_gestacao_lactacao.py`:
  11 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 17 testes executados, 17 passando.

## Branch e PR

Branch `claude/aprofundar-medicamentos-cardiovasculares-gestacao-
lactacao-20260828`, baseada em `origin/main` sem drift no momento do
commit.
