# Aprofundamento Tudo com Tudo — Plano de parto na cardiopatia materna — 28/08/2026

## Contexto

Décimo quinto lote de conteúdo do dia (após `doenca-coronariana-idoso`,
PR #603; `valva-aortica-bicuspide-pediatrica`, PR #604;
`hipotensao-ortostatica-no-idoso`, PR #606; `sopros-na-infancia`,
PR #608; `hipertensao-arterial-pediatrica`, PR #609;
`dor-toracica-pediatrica`, PR #610; `dislipidemias-pediatricas`,
PR #611; `arritmias-pediatricas`, PR #612;
`avaliacao-multidimensional-cardiogeriatrica`, PR #613;
`cuidados-paliativos-cardiovasculares`, PR #615;
`cardiopatia-congenita-gravidez`, PR #616;
`hipertensao-pulmonar-gravidez`, PR #621;
`cardiotoxicidade-bcr-abl`, PR #624;
`medicamentos-cardiovasculares-gestacao-lactacao`, PR #625). A ficha
`plano-parto-cardiopatia-materna` (área `gravidez`, categoria
`planejamento`, `prevalence_rank: 15`) tinha apenas metadados de
catalogação — zero campos clínicos, zero `related_document_slugs`,
sem `patient_material_slug`.

Terceira ficha do dia em formato framework/processo (não uma doença
única) — planejamento multidisciplinar do parto em gestante cardiopata
— mesmo padrão de adaptação de campos já usado em
`avaliacao-multidimensional-cardiogeriatrica` (PR #613) e
`cuidados-paliativos-cardiovasculares` (PR #615): `presentation` =
cenários de decisão de planejamento, `differentials` = distinções
conceituais, mantendo o mesmo schema JSON.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Cenários e diagnóstico** — `epidemiology` (cardiopatia como causa
   relevante de mortalidade materna indireta, benefício documentado do
   plano de parto multidisciplinar antecipado vs. parto não
   planejado), `presentation` (11 cenários de decisão), `diagnostic_
   approach` (5 subtópicos: classificação de risco materno, escolha do
   local do parto, definição da via de parto, planejamento de
   analgesia/anestesia, planejamento da anticoagulação periparto),
   `differentials` (7, distinções conceituais), `tests` (8),
   `red_flags` (8), `source_refs` (7, com PMIDs verificados).
2. **Conduta e assistente** — `treatment_summary` (Pregnancy Heart
   Team, local do parto por classificação de risco, via vaginal
   preferida com analgesia peridural precoce, cesariana para indicação
   específica, manejo da segunda fase evitando Valsalva, anticoagulação
   periparto, plano de contingência), `ambulatory_flow` (10),
   `emergency_flow` (8), `monitoring` (8), `assistant_questions` (13),
   `assistant_rules` (9, priority 98 para descompensação em trabalho de
   parto ativo).
3. **Populações especiais e conexões** — `special_populations` (6:
   prótese valvar mecânica, hipertensão pulmonar grave/Eisenmenger,
   dissecção/aneurisma de aorta, Fontan, risco altíssimo sem centro de
   referência, puerpério imediato), `related_document_slugs` (7
   propostos, 6 mantidos após verificação).

## Correção de qualidade feita na montagem

O texto entregue pelo agente da Parte 1 (`epidemiology`, `presentation`,
`diagnostic_approach`, `differentials`, `tests`, `red_flags`) veio sem
acentuação e cedilhas do português (ex.: "congenita", "obstetrica",
"nao" em vez de "congênita", "obstétrica", "não") — provavelmente
efeito colateral da normalização de texto usada pelo agente para
verificar PMIDs via NCBI e-utils. Reescrito por completo restaurando a
ortografia correta do português, preservando o conteúdo clínico e as
referências exatamente como entregues, antes de incorporar ao registro
— nenhum outro lote deste dia teve esse problema.

## Verificações feitas na montagem

- Todos os 7 candidatos de `related_document_slugs` verificados
  individual e programaticamente quanto à resolução, ao escopo e à
  menção de termos de planejamento de parto (via de parto, cesariana,
  periparto, Pregnancy Heart Team etc.) no texto.
- **1 candidato descartado**: `classificacao-de-risco-mwho-2-0-na-
  gravidez-esc-2025` — o documento trata apenas da classificação de
  risco materno em si (classes I a IV), sem qualquer menção específica
  a plano/via de parto, periparto ou local do parto; apesar de
  clinicamente adjacente (a classificação é a base do planejamento),
  não satisfaz o critério de centralidade ao tema desta ficha
  especificamente. Confirmado por leitura completa do documento.
- **3 dos 6 mantidos compartilhados** com outras fichas de gravidez já
  publicadas: `trombose-de-protese-valvar-mecanica-na-gestacao` e
  `anticoagulacao-em-valva-mecanica-e-cardiomiopatia-periparto-na-
  gestacao` (também em `protese-mecanica-na-gravidez`);
  `sindrome-aortica-aguda-na-gestacao-e-puerperio` e `sindrome-de-
  marfan-na-gestacao-risco-de-dissecao-aortica-e-limiares-de-manejo-
  pelo-diametro` (também em `aortopatia-na-gravidez`) — overlap
  legítimo, documentos genuinamente centrais também aqui pela ótica de
  planejamento de parto.
- `patient_material_slug` (`plano-parto-cardiopatia-materna`, mesmo
  slug da própria ficha) confirmado como existente em
  `material-paciente/metadados.json`, já vinculado ao documento técnico
  mais central da lista (`via-de-parto-e-insuficiencia-cardiaca-na-
  gestante-cardiopata-o-registro-ropac`).
- Um documento vinculado (`sindrome-de-eisenmenger-contraindicacao-
  absoluta-a-gestacao-mecanismo-mwho-iv`) contém a sigla "mWHO" em seu
  próprio slug pré-existente — não reescrito, mesmo padrão de PR #604/
  #616 (apenas texto autoral novo é verificado quanto a essa substring).

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

7 referências com PMID verificado (incluindo verificação direta via
NCBI e-utils pelo próprio agente, dado que o orçamento de WebSearch da
sessão estava esgotado), incluindo a diretriz ESC 2025 de doença
cardiovascular na gravidez, o registro ROPAC (Roos-Hesselink et al.
2013), o estudo sobre cesariana planejada em cardiopatia (Ruys et al.
2015) e o estudo CARPREG II (Silversides et al. 2018).

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `plano-parto-cardiopatia-materna`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap de 4 documentos com outras fichas de gravidez, documentado e
  esperado.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_plano_parto_cardiopatia_materna.py`:
  11 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 17 testes executados, 17 passando.

## Branch e PR

Branch `claude/aprofundar-plano-parto-cardiopatia-materna-20260828`,
baseada em `origin/main` sem drift no momento do commit.
