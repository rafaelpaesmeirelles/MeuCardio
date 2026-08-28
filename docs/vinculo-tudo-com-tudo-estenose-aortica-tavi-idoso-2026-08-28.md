# Fechamento de lacuna Tudo com Tudo — Estenose aórtica e TAVI no idoso — 28/08/2026

## Contexto

Vigésimo oitavo lote de conteúdo do dia, segundo desta natureza (após
`doenca-de-kawasaki`, PR #642). A ficha `estenose-aortica-tavi-idoso`
(área `cardiogeriatria`, `prevalence_rank: 11`) já estava
`completeness: completo` (aprofundada em 12/08/2026, conforme seu
próprio `review_note`), com `treatment_summary` e `assistant_rules`
íntegros e `review_status: revisado`, mas `related_document_slugs` e
`patient_material_slug` estavam `None` — mesma violação estrutural
pontual da regra Tudo com Tudo encontrada em `doenca-de-kawasaki`.

## O que este lote NÃO faz

Não altera nenhum campo de conteúdo clínico pré-existente —
`epidemiology`, `diagnostic_approach`, `treatment_summary`,
`assistant_questions`, `assistant_rules` continuam exatamente como
estavam.

## O que este lote faz

Adiciona 7 `related_document_slugs` e 1 `patient_material_slug`,
verificados por leitura real de cada documento candidato (contagem de
menções centrais):

- `estenose-aortica-grave-no-idoso-fragil-tavi-e-futilidade` — provável documento-hub do tema (24 menções).
- `bloqueio-av-e-disturbio-de-conducao-apos-tavi` — complicação central (18 menções).
- `fluxograma-bloqueio-av-e-disturbio-de-conducao-apos-tavi` — fluxograma companheiro (7 menções).
- `obstrucao-coronaria-aguda-apos-tavi` — complicação central (15 menções).
- `fluxograma-obstrucao-coronaria-aguda-apos-tavi` — fluxograma companheiro (6 menções).
- `estenose-aortica-grave-descompensada-e-choque-no-idoso` — apresentação pré-TAVI (11 menções).
- `fluxograma-estenose-aortica-grave-descompensada-e-choque-no-idoso` — fluxograma companheiro (5 menções).

`patient_material_slug` definido como `o-que-esperar-da-troca-de-
valvula-por-cateter-tavi`, material educativo já existente e
correspondente exato ao tema.

## Verificações feitas na montagem

- Os 7 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  de estenose aórtica/TAVI no texto.
- **Overlap pré-existente e legítimo**: o documento-hub
  `estenose-aortica-grave-no-idoso-fragil-tavi-e-futilidade` também é
  citado por `fragilidade-pre-procedimento-cardiovascular`,
  `avaliacao-multidimensional-cardiogeriatrica` e `valvopatias` —
  overlap natural (mesmo documento central relevante para múltiplas
  fichas geriátricas correlatas), documentado no teste dedicado.
- `patient_material_slug` verificado como existente em
  `material-paciente/metadados.json`.
- Nenhuma dose de fármaco foi introduzida.

## Catalogação e conteúdo clínico preservados

`name`, `aliases`, `area`, `category`, `prevalence_rank`,
`epidemiology`, `diagnostic_approach`, `treatment_summary`,
`assistant_questions`, `assistant_rules` originais preservados sem
qualquer alteração — verificado pelo teste dedicado.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Coordenação com Codex

Nenhum PR aberto (busca por título/branch) toca
`estenose-aortica-tavi-idoso` em `doencas/metadados.json`.

## Riscos e limitações

- Registro volta a `review_status: pendente_revisao` por prudência
  editorial — mesmo sem mudança de conteúdo clínico.
- Nenhuma dose de fármaco é citada ou alterada.
- Ainda restam 5 fichas na mesma situação para lotes futuros:
  `miocardite-pediatrica`, `avaliacao-basal-cardiooncologica`,
  `avaliacao-cardiovascular-pre-concepcional`, `trombose-associada-
  cancer`, `hipertensao-arterial-pediatrica`. As duas primeiras
  mostraram corpus potencialmente raso ou de vetting mais delicado em
  verificação preliminar e devem ser tratadas com cautela extra no
  próximo ciclo.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vinculo_tudo_com_tudo_estenose_aortica_tavi_idoso.py`:
  7 testes, todos passando (1 correção durante desenvolvimento, para
  documentar overlap pré-existente descoberto pelo próprio teste).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 13 testes executados, 13 passando.

## Branch e PR

Branch `claude/vincular-tudo-com-tudo-estenose-aortica-tavi-idoso-20260828`,
baseada em `origin/main` sem drift no momento do commit.
