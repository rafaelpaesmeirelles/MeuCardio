# Aprofundamento Tudo com Tudo — Seguimento cardiovascular pós-parto — 28/08/2026

## Contexto

Décimo sexto e último lote de conteúdo do dia (após `doenca-
coronariana-idoso`, PR #603; `valva-aortica-bicuspide-pediatrica`,
PR #604; `hipotensao-ortostatica-no-idoso`, PR #606; `sopros-na-
infancia`, PR #608; `hipertensao-arterial-pediatrica`, PR #609;
`dor-toracica-pediatrica`, PR #610; `dislipidemias-pediatricas`,
PR #611; `arritmias-pediatricas`, PR #612;
`avaliacao-multidimensional-cardiogeriatrica`, PR #613;
`cuidados-paliativos-cardiovasculares`, PR #615;
`cardiopatia-congenita-gravidez`, PR #616;
`hipertensao-pulmonar-gravidez`, PR #621;
`cardiotoxicidade-bcr-abl`, PR #624;
`medicamentos-cardiovasculares-gestacao-lactacao`, PR #625;
`plano-parto-cardiopatia-materna`, PR #626). A ficha
`seguimento-cardiovascular-pos-parto` (área `gravidez`, categoria
`seguimento`, `prevalence_rank: 16`) tinha apenas metadados de
catalogação — zero campos clínicos, zero `related_document_slugs`,
sem `patient_material_slug`. Fecha o cluster de gravidez pós-parto do
dia (irmã de `medicamentos-cardiovasculares-gestacao-lactacao`/
PR #625 e `plano-parto-cardiopatia-materna`/PR #626, mesmo nível de
raspagem original).

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (janela de risco
   cardiovascular do pós-parto imediato, complicações hipertensivas da
   gestação como marcador de risco cardiovascular de longo prazo — não
   evento isolado —, lacuna assistencial de seguimento estruturado),
   `presentation` (11 cenários), `diagnostic_approach` (6 subtópicos:
   reavaliação cardíaca precoce, reavaliação de cardiomiopatia
   periparto, seguimento de pré-eclâmpsia/hipertensão gestacional,
   transição de anticoagulação em prótese mecânica, rastreio
   metabólico após diabetes gestacional, encaminhamento a atenção
   primária/cardiologia), `differentials` (6), `tests` (8), `red_flags`
   (8), `source_refs` (7, com PMIDs verificados).
2. **Conduta e assistente** — `treatment_summary` (janela de 6 semanas,
   recuperação tardia de função ventricular em cardiomiopatia
   periparto até 6-12 meses, retomada de anticoagulação em prótese
   mecânica, reconciliação medicamentosa com amamentação, seguimento
   de longo prazo pós-pré-eclâmpsia/hipertensão gestacional, rastreio
   metabólico pós-diabetes gestacional, transição organizada de
   cuidado, aconselhamento reprodutivo), `ambulatory_flow` (11),
   `emergency_flow` (7), `monitoring` (8), `assistant_questions` (13),
   `assistant_rules` (10, priority 95 para sinais de descompensação no
   puerpério).
3. **Populações especiais e conexões** — `special_populations` (6:
   cardiomiopatia periparto em reavaliação, pré-eclâmpsia/hipertensão
   gestacional, prótese valvar mecânica, diabetes gestacional,
   puérpera amamentando, planejamento de gestação futura),
   `related_document_slugs` (7, o máximo permitido).

## Correção de qualidade do lote anterior, não repetida aqui

O lote anterior (`plano-parto-cardiopatia-materna`, PR #626) recebeu
texto sem acentuação do português de um dos agentes de pesquisa — este
lote não teve esse problema (texto revisado e confirmado com
acentuação correta antes da montagem), mas o `assemble.py` incluiu uma
checagem preventiva (presença de palavras-chave acentuadas no texto
final) e o teste dedicado espelha essa mesma checagem.

## Verificações feitas na montagem

- Todos os 7 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção de
  pós-parto/puerpério/risco cardiovascular de longo prazo no texto.
- O agente da Parte 3 documentou explicitamente 4 candidatos
  descartados por não satisfazerem o critério de recorte temporal
  específico (pós-parto/seguimento, não apenas a doença de base): um
  documento sobre anticoagulação em valva mecânica que trata apenas do
  período gestacional, sem discutir a retomada pós-parto; e três
  documentos (depressão pós-parto/risco cardiovascular, QT longo no
  puerpério, febre reumática/puerpério) não verificados com
  profundidade suficiente dentro do limite de 7 links.
- **3 dos 7 compartilhados** com fichas já publicadas:
  `hipertensao-gestacional-e-pre-eclampsia-risco-cardiovascular-
  materno-de-longo-prazo` (também em `pre-eclampsia-e-risco-
  cardiovascular`); `cardiomiopatia-periparto-criterios-diagnosticos-
  recuperacao-e-manejo` e `preditores-de-recuperacao-ventricular-e-
  aconselhamento-pre-concepcional-na-cardiomiopatia-periparto` (também
  em `cardiomiopatia-periparto`) — overlap legítimo e esperado, mesma
  lógica de multi-hub já aplicada em todos os lotes anteriores.
- `patient_material_slug` (`cuidado-do-coracao-no-primeiro-ano-depois-
  do-parto`) confirmado como existente em `material-paciente/
  metadados.json`, derivado exatamente do documento técnico mais
  central da lista (`acc-2026-cuidado-cardiovascular-pos-parto-
  primeiro-ano`).

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente. Estrutura de perguntas e regras validada com o
motor de regras real — todos os operadores usados pertencem ao
conjunto permitido, nenhum uso de "includes".

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

7 referências com PMID verificado, incluindo a diretriz ESC 2025 de
doença cardiovascular na gravidez, a metanálise clássica de
pré-eclâmpsia e risco cardiovascular futuro (Bellamy et al. 2007), o
estudo IPAC de cardiomiopatia periparto (McNamara et al. 2015) e a
metanálise de pré-eclâmpsia e saúde cardiovascular futura (Wu et al.
2017).

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `seguimento-cardiovascular-pos-parto`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap de 3 documentos com outras fichas de gravidez, documentado e
  esperado.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_seguimento_cardiovascular_pos_parto.py`:
  12 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-seguimento-cardiovascular-pos-parto-20260828`,
baseada em `origin/main` sem drift no momento do commit.
