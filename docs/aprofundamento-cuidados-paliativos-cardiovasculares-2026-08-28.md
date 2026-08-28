# Aprofundamento Tudo com Tudo — Cuidados paliativos cardiovasculares — 28/08/2026

## Contexto

Décimo lote de aprofundamento do dia (após `doenca-coronariana-idoso`,
PR #603; `valva-aortica-bicuspide-pediatrica`, PR #604; `hipotensao-
ortostatica-no-idoso`, PR #606; `sopros-na-infancia`, PR #608;
`hipertensao-arterial-pediatrica`, PR #609; `dor-toracica-pediatrica`,
PR #610; `dislipidemias-pediatricas`, PR #611; `arritmias-pediatricas`,
PR #612; `avaliacao-multidimensional-cardiogeriatrica`, PR #613).
Diferente de uma doença, a ficha `cuidados-paliativos-cardiovasculares`
(área `cardiogeriatria`, categoria `cuidado_centrado_pessoa`,
`prevalence_rank: 14`) é um **framework de cuidado paliativo aplicado em
paralelo** ao tratamento cardiovascular ativo — não é sinônimo de fim de
vida nem de suspensão de terapia — e tinha apenas metadados de
catalogação e 2 `related_document_slugs`.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (subutilização
   sistemática de cuidados paliativos em cardiologia vs. oncologia,
   evidência dos ensaios PAL-HF, ENABLE CHF-PC e SWAP-HF — nenhuma
   diferença em mortalidade, melhora consistente de qualidade de vida),
   `presentation` (12 cenários de decisão clínica, não sintomas),
   `diagnostic_approach` (4 subtópicos: triagem para encaminhamento —
   "surprise question", NYHA III-IV persistente —, avaliação estruturada
   de sintomas — ESAS, KCCQ —, avaliação de compreensão de prognóstico,
   cuidados paliativos primários vs. especializados), `differentials` (7
   distinções conceituais — ex. "paliativo ≠ hospice", "desativar CDI ≠
   eutanásia"), `tests` (7 instrumentos), `red_flags` (8), `source_refs`
   (12).
2. **Conduta e assistente** — `treatment_summary` (controle de sintomas
   por classe terapêutica sem posologia, processo estruturado de
   desativação de dispositivo distinguindo eticamente choque de CDI vs.
   estimulação de marca-passo-dependente, planejamento antecipado,
   critérios de hospice), `ambulatory_flow` (8), `emergency_flow` (5),
   `monitoring` (7), `assistant_questions` (12), `assistant_rules` (10,
   priority 90 para sintoma refratário + ≥2 internações + inotrópico
   contínuo).
3. **Populações especiais e conexões** — `special_populations` (6:
   LVAD de destino, oncológico com prognóstico duplo, idoso muito
   frágil, CDI ativo em fim de vida, valvopatia inoperável, cuidador
   sobrecarregado), `related_document_slugs` (7, o máximo permitido —
   5 novos escolhidos entre 8 candidatos avaliados com critério).

## Correções feitas na montagem

- Todos os 7 `related_document_slugs` verificados individualmente —
  confirmada menção explícita a cuidados paliativos/fim de vida/hospice
  no texto de cada um.
- **Sobreposição pré-existente descoberta pelo teste, não pelos agentes**:
  os 2 documentos já vinculados antes deste lote (`marca-passo-e-cdi-no-
  muito-idoso-...` e `cuidados-paliativos-e-transicao-de-cuidado-na-
  insuficiencia-cardiaca-terminal-do-muito-idoso`) também estão em
  `insuficiencia-cardiaca-no-idoso` — mantidos por serem genuína e
  centralmente relevantes também aqui (paliação terminal em IC).
- O agente da parte 3 descartou 3 dos 8 candidatos por menção apenas de
  passagem a cuidados paliativos (comunicação de prognóstico em geral,
  protocolo SPIKES, desprescrição no fim de vida) — disciplina de
  vínculo direto central aplicada consistentemente.

Nenhuma dose de fármaco em nenhum campo — opioides, benzodiazepínicos,
ISRS e anti-inflamatórios mencionados apenas por classe terapêutica.
Estrutura de perguntas e regras validada com o motor de regras real
antes da montagem.

## Nota operacional (não relacionada a este lote)

Durante o rebase deste PR, `origin/main` recebeu um commit do próprio
Rafael (`e7c8df3e`, "ops: emergency unlock stale production worktree
and deploy") adicionando um workflow de GitHub Actions
(`.github/workflows/emergency-unlock-deploy.yml`). É uma operação de
infraestrutura/deploy do próprio Rafael, sem relação com conteúdo —
absorvida pelo rebase sem conflito, mencionada aqui apenas por
transparência.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

12 referências novas, com PMID verificado, incluindo o AHA Scientific
Statement de 2025 (Graven et al., Circulation), o ensaio PAL-HF (Rogers
et al., JACC 2017) e o consenso HRS 2010 sobre desativação de CIED em
fim de vida (Lampert et al., Heart Rhythm).

## Coordenação com Codex

Nenhum dos 36 PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `cuidados-paliativos-cardiovasculares`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug` (já existente,
  `conversar-sobre-o-futuro-do-tratamento-planejamento-antecipado-de-
  cuidados`) reconfirmado.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_cuidados_paliativos_cardiovasculares.py`:
  12 testes, 1 falha na primeira rodada (sobreposição pré-existente não
  documentada, corrigida) e 12/12 na segunda.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist unificada).
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-cuidados-paliativos-cardiovasculares-20260828`,
rebaseada em `origin/main` sem drift no momento do commit.
