# Vincular Tudo com Tudo — Polifarmácia e desprescrição cardiovascular — 29/08/2026

## Contexto

Ficha `polifarmacia-e-desprecricao-cardiovascular` (área `cardiogeriatria`,
categoria `sindrome_geriatrica`, `prevalence_rank: 1`) já era
`completeness: completo`. O registro **base** em `doencas/metadados.json`
tinha apenas 1 `related_document_slug` e `version: 1` — abaixo do piso
mínimo de 3. Lote apenas de vínculo — nenhum conteúdo clínico
pré-existente foi reescrito.

## ⚠️ Achado importante: esta ficha já tinha uma tentativa idêntica, fechada por redundância

Antes de editar qualquer arquivo, a investigação de histórico (`git log
--all`) encontrou a **PR #660**, "vincular Tudo com Tudo em
polifarmacia-e-desprecricao-cardiovascular" (28/08/2026, branch
`claude/vincular-tudo-com-tudo-polifarmacia-cardiogeriatrica-20260828`),
que fazia exatamente esta tarefa e chegou aos mesmos 3 vínculos.
Rafael fechou a PR #660 **sem merge**, comentando:

> "Conteúdo já revisado e integrado em produção via pipeline
> consolidador ('release: integrar e revisar toda produção científica
> das últimas 36h', confirmado em main com review_status=revisado e os
> mesmos valores desta branch). Fechando por redundância, sem merge
> desta PR."

Confirmado: `origin/main` tem o commit `798bb8d5 "release: integrar e
revisar toda produção científica das últimas 36h"`, que inclui o arquivo
`doencas/correcoes/zz-release36h-pr660-polifarmacia-e-desprecricao-cardiovascular.json`
— um patch de correção que faz `"set"` completo do registro, incluindo
`version: 2`, `review_status: "revisado"` e os **mesmos 4**
`related_document_slugs` que este lote adiciona (texto do `review_note`
do patch também é herdado literalmente da PR #660).

**Consequência prática, verificada via `load_disease_records` (a mesma
função que `app.main` e os gates consomem)**: a visão **canônica**
(base + correções compostas) desta ficha **já estava**, antes deste
lote, em `version=2`, `review_status="revisado"` e com os 4 vínculos —
o patch de correção mascarava (no sentido inverso do achado do lote
`atresia-pulmonar` de hoje: lá o patch mascarava uma pendência de
revisão; aqui o patch mascarava que o enriquecimento de vínculos **já
estava presente** na aplicação, mesmo com o arquivo base desatualizado).

**O que este lote realmente muda**: sincroniza o registro **base** de
`doencas/metadados.json` (que só tinha 1 vínculo e `version: 1`) com o
que o patch de correção já impunha silenciosamente na visão canônica.
Isso não é redundante na fonte-verdade do arquivo — reduz uma dívida
técnica real (arquivo base divergente do que a aplicação de fato
publica) — mas é redundante no comportamento observável da aplicação,
que já mostrava os 4 vínculos antes deste commit.

**Decisão editorial em aberto, sinalizada aqui e não tomada por este
lote**: agora que o registro base tem os mesmos valores do patch, o
arquivo `doencas/correcoes/zz-release36h-pr660-polifarmacia-e-desprecricao-cardiovascular.json`
ficou tecnicamente redundante (mas inofensivo — os dois concordam). Não
o removi porque isso está fora do escopo "só adiciona vínculo" deste
lote e é decisão do revisor humano.

## Verificação independente dos candidatos (sem consultar a PR #660 previamente)

Candidatos fornecidos pelo orquestrador, cada um lido por completo:

| Candidato | Centralidade do tema polifarmácia/desprescrição | Decisão |
|---|---|---|
| `fluxograma-desprescricao-cardiovascular-no-idoso-polifarmacia-e-fim-de-vida` | Documento inteiro é a árvore de decisão de desprescrição cardiovascular no idoso | **Incluído** |
| `fragilidade-como-modificador-de-decisao-cardiovascular` | Polifarmácia citada 1x, apenas como item de lista de síndromes geriátricas que compõem o conceito de futilidade — tema central é fragilidade em TAVI/cirurgia valvar/CABG | Descartado — menção lateral |
| `metas-terapeuticas-cardiovasculares-no-muito-idoso` | Polifarmácia citada 1x, como parte do critério de exclusão de ensaios clínicos (HYVET/SPRINT/PROSPER/ELDERCARE-AF) — tema central é meta de PA/LDL/anticoagulação no 80+ | Descartado — menção lateral |
| `comprometimento-cognitivo-e-demencia-como-modificador-de-decisao-cardiovascular` | Polifarmácia citada 1x, na mesma lista de síndromes geriátricas do documento de fragilidade — tema central é rastreio cognitivo/PA/anticoagulação em FA | Descartado — menção lateral |

Busca adicional por título (`grep` em `content/**/*.md` por
"polifarmácia"/"desprescri" no frontmatter), necessária porque os 4
candidatos fornecidos, sozinhos, não alcançavam o piso de 3 (só 1 dos 4
era central), revelou 2 documentos centrais fora da pasta
`Cardiologia_geriátrica` (mesmos que a PR #660 havia usado,
encontrados de forma independente):

| Documento | Pasta | Centralidade |
|---|---|---|
| `desprescricao-de-medicamentos-cardiovasculares-na-polifarmacia-consenso-cientifico-aha-2026` | `Comunicação_clínica` | Resumo integral do AHA Scientific Statement 2026 sobre desprescrição em polifarmácia cardiovascular — **Incluído** |
| `polifarmacia-anti-hipertensiva-e-adesao-no-idoso-desprescrever-simplificar-ou-manter` | `Hipertensão` | Documento inteiro sobre desprescrever/simplificar/manter anti-hipertensivo em polifarmácia (OPTIMISE, Parati, Tomaszewski) — **Incluído** |

Nenhum candidato resolve para `content/Farmacologia/`,
`content/Calculadoras/` ou `content/Exames/`.

## Vínculos finais (4)

- `polifarmacia-cardiovascular-no-idoso-cascata-de-prescricao-e-desprescricao` (já existente, mantido)
- `fluxograma-desprescricao-cardiovascular-no-idoso-polifarmacia-e-fim-de-vida`
- `desprescricao-de-medicamentos-cardiovasculares-na-polifarmacia-consenso-cientifico-aha-2026`
- `polifarmacia-anti-hipertensiva-e-adesao-no-idoso-desprescrever-simplificar-ou-manter`

## Overlaps legítimos e pré-existentes

- `fluxograma-desprescricao-...` também em `hipotensao-ortostatica-no-idoso`.
- `polifarmacia-cardiovascular-no-idoso-cascata-...` (vínculo original) também em
  `insuficiencia-cardiaca-no-idoso`, `risco-quedas-cardiogeriatria` e
  `anticoagulacao-idoso`.

## review_status e completeness

Nenhum dos dois foi alterado, por instrução explícita. `review_status`
já era `"revisado"` antes deste lote (tanto no patch de correção quanto,
agora, no registro base) — não há falha esperada em
`test_canonical_content_review_status.py` (diferente do lote-irmão
`persistencia-canal-arterial`, que manteve `pendente_revisao` e tem 1
falha esperada e documentada naquele PR).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_polifarmacia_e_desprecricao_cardiovascular.py`: 8 testes, incluindo um dedicado a verificar que o registro base foi sincronizado com o patch de correção pré-existente.
- `backend/tests/test_canonical_content_review_status.py`: 3 testes, passando sem necessidade de allowlist.
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes, passando.
- `app.main` importa sem erro.
- Total: 14 testes pytest executados, 14 passando.

## Riscos e limitações

- Nenhum conteúdo clínico pré-existente foi alterado, apenas o vínculo e a sincronização do registro base com o patch de correção.
- O patch `doencas/correcoes/zz-release36h-pr660-polifarmacia-e-desprecricao-cardiovascular.json` ficou redundante (mas não conflitante) após este lote — decisão sobre removê-lo ou mantê-lo fica para o revisor humano.
