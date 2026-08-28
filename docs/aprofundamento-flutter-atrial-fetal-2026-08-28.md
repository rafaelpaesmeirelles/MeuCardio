# Aprofundamento Tudo com Tudo — Flutter atrial fetal — 28/08/2026

## Contexto

Vigésimo lote de conteúdo do dia, quarto do cluster de cardiologia
fetal (após `doenca-coronariana-idoso`, PR #603;
`valva-aortica-bicuspide-pediatrica`, PR #604;
`hipotensao-ortostatica-no-idoso`, PR #606; `sopros-na-infancia`,
PR #608; `hipertensao-arterial-pediatrica`, PR #609;
`dor-toracica-pediatrica`, PR #610; `dislipidemias-pediatricas`,
PR #611; `arritmias-pediatricas`, PR #612;
`avaliacao-multidimensional-cardiogeriatrica`, PR #613;
`cuidados-paliativos-cardiovasculares`, PR #615;
`cardiopatia-congenita-gravidez`, PR #616;
`hipertensao-pulmonar-gravidez`, PR #621;
`cardiotoxicidade-bcr-abl`, PR #624;
`medicamentos-cardiovasculares-gestacao-lactacao`, PR #625;
`plano-parto-cardiopatia-materna`, PR #626;
`seguimento-cardiovascular-pos-parto`, PR #628;
`indicacoes-ecocardiograma-fetal`, PR #630;
`bloqueio-atrioventricular-fetal`, PR #631;
`hidropisia-fetal-cardiovascular`, PR #632). A ficha
`flutter-atrial-fetal` (área `cardiopediatria`, categoria
`cardiologia_fetal`, `prevalence_rank: 33`) já tinha
`patient_material_slug` e 1 `related_document_slug` preenchidos, mas
zero campos clínicos.

## Correção de citação descoberta durante este ciclo

Ao verificar os PMIDs desta rodada via NCBI e-utils, descobri que o
PMID usado no lote anterior
(`hidropisia-fetal-cardiovascular`/PR #632) para a referência de Krapp
et al. estava incorreto: `12860870` pertence a um artigo diferente
(Duke C et al., sobre redilatação de stent em cardiopatia congênita,
mesmo número da revista *Heart*). O PMID correto é `12860871`.
Corrigido separadamente em um commit próprio no PR #632, já mesclado
ao seu branch. Neste lote, a mesma referência já é citada com o PMID
correto.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (segunda
   taquiarritmia fetal mais comum, tipicamente diagnosticada no
   terceiro trimestre, frequência atrial 300-500 bpm com condução
   variável, sucesso de cardioversão transplacentária 80-90%),
   `presentation` (10 formas), `diagnostic_approach` (5 subtópicos:
   caracterização ecocardiográfica do ritmo, diferenciação de TSV,
   avaliação de repercussão hemodinâmica/hidropisia, escolha do
   primeiro agente conforme hidropisia, seguimento pós-cardioversão),
   `differentials` (6), `tests` (8), `red_flags` (8), `source_refs` (7,
   com todos os PMIDs individualmente verificados via NCBI e-utils
   nesta rodada).
2. **Conduta e assistente** — `treatment_summary` (confirmação
   diagnóstica, avaliação de hidropisia antes de tratar, escolha de
   agente conforme hidropisia — digoxina primeira linha sem
   hidropisia, sotalol/combinação com hidropisia —, monitorização
   materna, conduta em refratário, expectativa neonatal),
   `ambulatory_flow` (10), `emergency_flow` (8), `monitoring` (8),
   `assistant_questions` (12), `assistant_rules` (10, priority 95 para
   hidropisia + refratário + frequência ventricular muito elevada).
3. **Populações especiais e conexões** — `special_populations` (6:
   flutter com hidropisia, com cardiopatia estrutural, diagnosticado
   próximo ao termo, recorrência neonatal, gestante em tratamento
   transplacentário, flutter refratário), `related_document_slugs` (3,
   união do original com 2 novos).

## Verificações feitas na montagem

- Os 3 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção de
  flutter atrial no texto.
- Overlap com 2 fichas irmãs já aprofundadas hoje
  (`bloqueio-atrioventricular-fetal`/PR #631,
  `hidropisia-fetal-cardiovascular`/PR #632) e com
  `taquicardia-supraventricular-fetal` (ainda não aprofundada) —
  legítimo, documentado no teste dedicado.
- `patient_material_slug` original (`flutter-atrial-fetal`) preservado
  sem alteração — reconfirmado como existente.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente; fármacos citados apenas por nome (digoxina,
sotalol, flecainida, amiodarona), sem posologia. Estrutura de
perguntas e regras validada com o motor de regras real — todos os
operadores usados pertencem ao conjunto permitido, nenhum uso de
"includes", nenhuma regra usa a chave `monitoring` (não permitida)
dentro de `add`.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

7 referências com PMID verificado individualmente via NCBI e-utils,
incluindo a diretriz científica da AHA 2014, o estudo comparativo de
Krapp et al. (2003, PMID corrigido), o estudo de Lisowski et al. (2000)
sobre flutter perinatal, o ensaio de Oudijk et al. (2000) sobre
sotalol em disritmias fetais, e o estudo comparativo de Jaeggi et al.
(2011) sobre tratamento transplacentário.

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `flutter-atrial-fetal`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap de 2 documentos com fichas irmãs, documentado.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_flutter_atrial_fetal.py`:
  12 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-flutter-atrial-fetal-20260828`, baseada em
`origin/main` sem drift no momento do commit.
