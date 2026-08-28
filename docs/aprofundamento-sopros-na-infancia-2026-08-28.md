# Aprofundamento Tudo com Tudo — Sopros cardíacos na infância — 28/08/2026

## Contexto

Quarto lote de aprofundamento do dia (após `doenca-coronariana-idoso`,
PR #603; `valva-aortica-bicuspide-pediatrica`, PR #604; `hipotensao-
ortostatica-no-idoso`, PR #606). A ficha `sopros-na-infancia` (área
`cardiopediatria`, categoria `sintoma_e_exame`, `prevalence_rank: 28`) —
um dos achados mais comuns do exame pediátrico — tinha apenas metadados
de catalogação e 1 `related_document_slug`; um agente de auditoria a
escolheu como melhor candidata entre as fichas livres de qualquer um dos
28 PRs abertos que tocam `doencas/metadados.json`, fragmentos ou
correções.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (prevalência de sopro
   inocente até 50-70% das crianças, razão inocente:patológico >10:1),
   `presentation` (10 tipos de sopro por semiologia/faixa etária),
   `diagnostic_approach` (4 subtópicos: características semiológicas
   discriminativas, sinais de alarme, indicação de ecocardiograma, papel
   do pediatra geral vs. cardiologista), `differentials` (8), `tests` (8),
   `red_flags` (9), `source_refs` (10).
2. **Conduta e assistente** — `treatment_summary` (conduta expectante
   para sopro inocente clássico, critérios de ecocardiograma e
   encaminhamento urgente vs. eletivo, comunicação com a família),
   `ambulatory_flow` (8), `emergency_flow` (5), `monitoring` (6),
   `assistant_questions` (12), `assistant_rules` (9, priority até 95 para
   sopro + cianose).
3. **Populações especiais e conexões** — `special_populations` (7:
   recém-nascido nas primeiras 48h, lactente com sinais de alarme,
   síndrome genética, atleta adolescente, ansiedade parental, prematuro
   com PCA, sopro acentuado por febre), `related_document_slugs` (7
   propostos), `patient_material_slug`.

## Correções feitas na montagem

- **2 documentos rejeitados** dos 7 propostos por não serem centralmente
  sobre sopro na infância: `morte-subita-em-atletas-triagem-pre-
  participacao-e-o-debate-do-ecg-obrigatorio` (sopro aparece só como 1
  item de um checklist de 12 elementos; o documento é sobre o debate do
  ECG obrigatório na triagem pré-participação, não sobre semiologia de
  sopro) e `carga-global-febre-reumatica-desigualdade-brasil-2026` (não
  usa a palavra "sopro" em nenhum lugar do texto — discute sensibilidade
  da ausculta cardíaca de 53% para febre reumática, tema distinto).
  Ficaram 5 `related_document_slugs`.
- **3 dos 5 documentos finais compartilhados** com outras fichas:
  `coarctacao-de-aorta-na-crianca-...` (também em `coarctacao-da-aorta` e
  `coarctacao-aorta-fetal`); `triagem-neonatal-de-cardiopatia-congenita-
  critica-por-oximetria-de-pulso` e `cianose-no-recem-nascido-
  diagnostico-diferencial-e-conduta-inicial` (também em `tetralogia-de-
  fallot`; o segundo também em `transposicao-das-grandes-arterias`) —
  mantidos por serem genuína e centralmente relevantes ao exame
  cardiovascular do recém-nascido também nesta ficha.

Nenhuma dose de fármaco em nenhum campo — verificado programaticamente.
Estrutura de perguntas e regras validada com o motor de regras real
antes da montagem (nenhum operador inválido desta vez).

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada, então ainda não tinha a correção de allowlist em
`test_disease_fragments_canonical.py` (novo gate sem exceção para lotes
`pendente_revisao`, introduzido em `64db98f8`). Apliquei aqui a mesma
correção já aprovada pelo Rafael no PR #606 — reaproveitar
`PENDENTES_LOTES_TUDO_COM_TUDO` como fonte única, sem criar uma segunda
allowlist divergente.

## Fontes primárias

10 referências novas, com PMID verificado, incluindo McCrindle et al.
(Arch Pediatr Adolesc Med 1996, critérios semiológicos discriminativos),
Geggel (Pediatrics 2004, motivo mais comum de encaminhamento) e a
diretriz científica AHA/AAP de oximetria de pulso neonatal (2009).

## Coordenação com Codex

Nenhum dos 28 PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `sopros-na-infancia`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug` (já existente, `sopros-na-infancia`)
  reconfirmado.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_sopros_na_infancia.py`: 11 testes,
  todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist unificada).
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-sopros-na-infancia-20260828`, baseada em
`origin/main` (`64db98f8`) sem drift no momento do commit.
