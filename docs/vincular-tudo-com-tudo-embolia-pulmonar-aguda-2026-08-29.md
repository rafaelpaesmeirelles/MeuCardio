# Vincular Tudo com Tudo (enriquecimento) — Embolia pulmonar aguda — 29/08/2026

## Contexto

Ficha `embolia-pulmonar-aguda` (área geral, categoria `tromboembolismo`)
já era `completeness: completo` com apenas 2 `related_document_slugs` —
abaixo do piso técnico mínimo de 3 exigido pela regra Tudo com Tudo —
apesar de existir corpus rico de TEP grave/maciça-submaciça em
`content/Tromboembolismo/` ainda não vinculado. Lote de enriquecimento
apenas de vínculo. Nenhum conteúdo clínico pré-existente foi reescrito, e
nem `review_status` nem `completeness` foram alterados (decisão explícita
desta tarefa).

## Verificação prévia: a lacuna era real?

Antes de agir, foi verificada a composição real do registro via
`load_disease_records()` (não apenas o catálogo-base), incluindo qualquer
patch em `doencas/correcoes/*.json`. Não há nenhuma correção que aponte
para o slug `embolia-pulmonar-aguda` em `doencas/correcoes/` — a única
correção que menciona TEP no arquivo (`zz-release36h-pr574-
tromboembolismo-venoso.json`) altera o registro **`tromboembolismo-
venoso`**, uma ficha irmã distinta, não `embolia-pulmonar-aguda`. A
composição real confirmou exatamente 2 `related_document_slugs`:

- `aha-acc-2026-tep-agudo-categorias-clinicas-anticoagulacao-e-terapias-avancadas`
- `tratamento-farmacologico-do-tep-diretriz-brasileira-sbpt-2025-grade`

A lacuna era real — o lote prosseguiu.

## PR #544 (aberto) — por que não resolveu isto

O PR #544 (`feat: aprofundar embolia pulmonar aguda`,
`codex/condicoes-profundas-adulto-lote3-embolia-20260827`) foi checado
antes de agir. Seu diff contra `origin/main` atual mostra apenas 331
arquivos alterados quase todos por estar **muito desatualizado** frente
ao histórico recente do repositório (branch aberta em 27/08, sem rebase
desde então) — comparado ao seu próprio merge-base com `main`, o diff
efetivo em `doencas/metadados.json` e `doencas/relacoes-explicitas.json`
é **vazio**: o registro `embolia-pulmonar-aguda` já existia idêntico no
merge-base, e o PR nunca chegou a alterar `related_document_slugs`. O PR
está obsoleto/superado por outros merges e não interfere neste lote.

## Vínculos adicionados (5)

- `fluxograma-tep-agudo-estratificacao-de-risco-e-decisao-de-trombolise`
  (estratificação de risco)
- `trombolise-sistemica-em-dose-reduzida-no-tep-de-risco-intermediario-o-ensaio-mopett`
  (trombólise sistêmica, ensaio MOPETT)
- `trombectomia-mecanica-versus-anticoagulacao-isolada-no-tep-de-risco-intermediario-alto-storm-pe`
  (trombectomia mecânica, ensaio STORM-PE)
- `terapia-dirigida-por-cateter-no-tep-peerless-e-o-que-ainda-nao-esta-respondido`
  (terapia dirigida por cateter, PEERLESS/HI-PEITHO)
- `filtro-de-veia-cava-inferior-recuperavel-no-tep-agudo-o-ensaio-prepic2`
  (filtro de veia cava, ensaio PREPIC2)

Total final: 7 (piso técnico de 3, teto de 7 — fechado no máximo
permitido, priorizando diversidade).

## Verificação feita na montagem

Todos os 5 lidos por inteiro (não apenas o frontmatter) antes de incluir,
confirmando: (1) `theme: "Tromboembolismo"` e `kind` em
`estudo`/`fluxograma`/`protocolo` — nunca resolvendo para
`content/Farmacologia`, `content/Calculadoras` ou `content/Exames`; (2)
discussão central (não incidental) de TEP agudo grave/maciça-submaciça —
cada um é o documento-hub do próprio ensaio ou fluxograma citado; (3)
nenhuma duplicata de slug já vinculado por outra ficha de doença (checado
por varredura de todo `doencas/metadados.json`, sem sobreposição
encontrada).

Um 6º candidato mapeado pela tarefa,
`tromboembolismo-pulmonar-agudo-diagnostico-e-manejo-escers-2019.md`
(protocolo ESC/ERS 2019, diagnóstico e manejo), foi **descartado** por
redundância: seu escopo de estratificação/categorização já é coberto de
forma mais atual pelo documento AHA/ACC 2026 já vinculado e pelo novo
fluxograma de estratificação de risco, ambos citando o próprio ESC 2019
como fonte histórica. Incluí-lo levaria o total além do teto útil de
diversidade sem agregar uma frente clínica nova.

As 4 frentes de diversidade pedidas na tarefa (estratificação de risco,
trombólise sistêmica, trombectomia/terapia dirigida por cateter, filtro
de veia cava) estão todas cobertas — a frente de trombectomia/cateter
recebeu 2 documentos (STORM-PE testa trombectomia mecânica vs.
anticoagulação isolada; PEERLESS/HI-PEITHO cobre a via por cateter, com
lítico e sem lítico) por serem desenhos de ensaio distintos e
complementares, não redundantes entre si.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `SpecialtyDisease.related_document_slugs`
  1098/1098 resolvidos, sem `broken_references`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vincular_tudo_com_tudo_embolia_pulmonar_aguda.py`:
  10 testes, todos passando.
- `backend/tests/test_disease_fragments_canonical.py` e
  `test_canonical_content_review_status.py`: passando — sem necessidade
  de allowlist, já que `review_status` permaneceu `revisado` (não houve
  mudança para `pendente_revisao`, ao contrário do padrão usual de outros
  lotes desta frente).
- `app.main` importa sem erro.

## Riscos e limitações

- Registro permanece `review_status: revisado` e `completeness: completo`
  — publicado, por decisão explícita desta tarefa de não alterar esses
  dois campos. Diferente do padrão usual de outros lotes "vincular Tudo
  com Tudo" do dia (que rebaixam para `pendente_revisao` por prudência
  editorial ao tocar campo estrutural em ficha publicada) — aqui a
  mudança fica visível imediatamente, sob responsabilidade de quem
  autorizou esta exceção.
- Nenhum conteúdo clínico pré-existente foi alterado, apenas o vínculo.
- PR #544 permanece aberto e obsoleto; não foi fechado nem tocado por
  este lote (fora de escopo desta tarefa).
