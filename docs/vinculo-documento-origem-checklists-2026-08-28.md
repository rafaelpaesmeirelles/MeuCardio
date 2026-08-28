# Fechamento de lacuna — documento_origem em 5 checklists — 28/08/2026

## Contexto

Trigésimo quarto lote de conteúdo do dia, primeiro em `checklists/metadados.json`
(fora de `doencas/`). Ao mapear onde a regra "Tudo com Tudo" (que na
prática só é formalmente testada em `doencas/metadados.json`) poderia
ser aplicada por analogia em outros manifestos do sistema, encontrei
`checklists/metadados.json` com 8 dos 366 registros com `documento_origem`
vazio — campo que deveria apontar para o documento narrativo em
`content/**/*.md` que serve de fonte clínica ao checklist.

## O que este lote faz

Para 5 dos 8 checklists vazios, confirmei por leitura real do documento
candidato (não apenas nome de arquivo) que ele trata centralmente do
mesmo tema clínico do checklist, com as mesmas referências primárias:

- `avaliacao-cardiovascular-do-usuario-recreativo-de-esteroides-anabolizantes-androgenicos` → `esteroides-anabolizantes-androgenicos-e-risco-cardiovascular` (mesmas 2 referências primárias do checklist).
- `manejo-agudo-de-fibrilacao-atrial-induzida-por-alcool-holiday-heart-syndrome` → `sindrome-do-coracao-em-ferias-e-fibrilacao-atrial-induzida-por-alcool` (correspondência quase literal de tema, referência compartilhada).
- `controle-da-hipertensao-sistolica-isolada-no-muito-idoso-com-vigilancia-de-hipotensao-ortostatica-iatrogenica` → `hipertensao-sistolica-isolada-e-meta-pressorica-no-muito-idoso-hyvet-sprint-e-step` (mesmos ensaios HYVET/SPRINT citados).
- `decisao-entre-valvuloplastia-por-balao-percutanea-e-cirurgia-na-estenose-mitral-reumatica-cronica-grave` → `estenose-mitral-diagnostico-e-manejo-esc-eacts-2025` (mesma diretriz ESC/EACTS 2025, mesmo eixo de decisão CMP vs. cirurgia).
- `envolvimento-cardiaco-na-sindrome-inflamatoria-multissistemica-pediatrica-mis-c-avaliacao-e-seguimento` → `mis-c-com-disfuncao-miocardica-e-choque` (mesma referência ACR central, mesmo cronograma de eco de seguimento).

## O que este lote NÃO faz (transparência)

Os outros 3 checklists vazios permanecem **sem** `documento_origem`,
deliberadamente:

- `aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca` — nenhum documento do corpus trata centralmente de STOP-Bang/triagem de apneia pré-operatória em cirurgia cardíaca.
- `manejo-da-abstinencia-alcoolica-aguda-com-risco-de-tempestade-autonomica-e-arritmia` — nenhum documento trata centralmente de abstinência alcoólica aguda (os 2 candidatos mais próximos tratam de outra substância ou de outro aspecto do tema).
- `diagnostico-e-tratamento-da-trombose-de-esforco-sindrome-de-paget-schroetter` — o único candidato relacionado (`trombose-venosa-de-membro-superior-associada-a-cateter`) é sobre o cenário **oposto** (TVP secundária a cateter) e diz explicitamente no próprio texto que não cobre a síndrome de Paget-Schroetter.

Achado interessante: duas PRs anteriores fechadas (#460, #465) já haviam
tentado preencher esses `documento_origem` (incluindo os 3 acima),
apontando para arquivos que **nunca chegaram a existir** em nenhuma
branch do repositório — referências quebradas, provável motivo do
fechamento dessas PRs e da lacuna persistir até hoje. Não fabriquei
vínculo para preencher essa lacuna; ela requer a escrita de documento
narrativo novo, fora do escopo deste lote (que é só de vínculo).

## Verificações feitas

- Os 5 `documento_origem` verificados individual e programaticamente
  quanto à resolução, ao escopo (fora de Farmacologia/Calculadoras/
  Exames) e à menção explícita do tema central no texto.
- Nenhum PR aberto toca qualquer um dos 8 checklists (confirmado por
  busca exaustiva contra as branches abertas).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_vinculo_documento_origem_checklists_28_08.py`: 5
  testes, todos passando de primeira.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/vincular-documento-origem-checklists-20260828`, baseada
em `origin/main` sem drift no momento do commit.
