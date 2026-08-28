# Aprofundamento Tudo com Tudo — Valva aórtica bicúspide na infância — 28/08/2026

## Contexto

Segundo lote de aprofundamento do dia (após `doenca-coronariana-idoso`,
PR #603). O gap-finding de hubs gerais novos segue esgotado (único
candidato restante, cardiopatia reumática crônica do adulto, colide com o
PR aberto `#567` e foi descartado por decisão do Rafael). Um agente
auditou os 22 PRs abertos que tocam `doencas/metadados.json` para excluir
fichas em edição, e escolheu `valva-aortica-bicuspide-pediatrica` — a
cardiopatia congênita mais comum (0,5-2% dos nascidos vivos), com
`completeness: básico`, `prevalence_rank: 15` (ranks 13 e 14 bloqueados
por PRs abertos), apenas catalogação e 1 `related_document_slugs`.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (prevalência,
   herdabilidade de 89%, associação com coartação de aorta e síndrome de
   Turner), `presentation` (10 itens por faixa etária), `diagnostic_approach`
   (estruturado em 6 subtópicos: ecocardiograma, avaliação da aorta
   ascendente por z-score, rastreio de coartação associada, ressonância
   magnética, rastreio familiar, rastreio na síndrome de Turner),
   `differentials` (7), `tests` (8), `red_flags` (8), `source_refs` (11).
2. **Tratamento e assistente** — `treatment_summary` (seguimento seriado
   por gravidade, valvoplastia por balão no neonato crítico, plástica
   valvar/Ross/substituição por idade e anatomia, manejo da aorta
   dilatada, esporte, transição para ACHD), `ambulatory_flow` (8),
   `emergency_flow` (6), `monitoring` (8), `assistant_questions` (12),
   `assistant_rules` (10, priority até 95 para estenose crítica neonatal).
3. **Populações especiais e conexões** — `special_populations` (7:
   neonato ductus-dependente, síndrome de Turner, coartação associada,
   rastreio familiar, atleta, transição ACHD, gestante jovem),
   `related_document_slugs` (9, incluindo o já existente).

## Correções e verificações feitas na montagem

- **Sobreposição com outras fichas**: 5 dos 9 documentos são
  compartilhados com hubs já publicados/abertos —
  `valva-aortica-bicuspide-e-aortopatia-associada-esc-2024` e
  `coarctacao-de-aorta-reparada-e-gestacao-desfechos-do-ropac` (também em
  `aortopatia-na-gravidez`, PR aberto); `coarctacao-de-aorta-na-crianca-...`
  e `sindrome-de-turner-na-crianca-...` (também em `coarctacao-da-aorta`,
  publicada — tríade VAB/coartação/Turner); `estenose-aortica-grave-
  sintomatica-na-gestacao` (também em `valvopatias-na-gravidez`, publicada
  — VAB é causa clássica de estenose aórtica em mulher jovem grávida).
  Todos verificados como genuína e centralmente sobre VAB antes de manter
  — descoberto pelo teste dedicado na primeira rodada de pytest (o agente
  de pesquisa só havia checado 2 das 5 sobreposições) e corrigido.
- **Substring "mwho" em slug legítimo**: `classificacao-de-risco-mwho-
  2-0-na-gravidez-esc-2025` contém "mwho" no próprio nome — não é
  violação de compliance. O gate real do repositório
  (`test_specialty_guides.py`) restringe essa checagem a
  `assistant_rules`, não ao registro inteiro; replicado esse escopo exato
  no teste dedicado e no script de montagem.
- Nenhuma dose de fármaco em nenhum campo — verificado programaticamente.
  Estrutura de perguntas e regras validada com o motor de regras real
  antes da montagem (nenhum operador inválido desta vez).

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `cyanosis_class` e
`prevalence_rank` originais preservados sem alteração.

## Fontes primárias

12 referências (1 original + 11 novas), com PMID verificado, incluindo o
consenso internacional de nomenclatura/classificação de VAB (Michelena et
al. 2021), diretriz ESC 2024 de doença aórtica/periférica, e estudo de
herdabilidade familiar (Cripe et al. 2004).

## Coordenação com Codex

Nenhum dos 22 PRs abertos que tocam `doencas/metadados.json` edita
`valva-aortica-bicuspide-pediatrica`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug` (já existente,
  `valvula-aortica-bicuspide-o-que-significa-esse-diagnostico`) reconfirmado
  como existente em `material-paciente/metadados.json`.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_valva_aortica_bicuspide_pediatrica.py`:
  13 testes, 1 falha na primeira rodada (sobreposição não documentada,
  corrigida) e 13/13 na segunda.
- `backend/tests/test_canonical_content_review_status.py`: passando com
  `valva-aortica-bicuspide-pediatrica` na allowlist
  `PENDENTES_LOTES_TUDO_COM_TUDO`.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-valva-aortica-bicuspide-pediatrica-20260828`,
rebaseada em `origin/main` sem drift no momento do commit (um commit
intermediário — `4a8c0978`, aprofundamento de AAOCA — renomeou
`PENDENTES_MARKDOWN_AVC` para `PENDENTES_MARKDOWN` em
`test_canonical_content_review_status.py`; conflito de rebase resolvido
adotando o novo nome).
