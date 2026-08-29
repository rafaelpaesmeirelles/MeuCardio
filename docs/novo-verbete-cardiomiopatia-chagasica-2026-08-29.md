# Novo verbete: Cardiomiopatia chagásica crônica (29/08/2026)

## O que foi criado

`doencas/fragmentos/cardiomiopatia-chagasica.json` — verbete novo e completo
para o Guia de Doenças, slug `cardiomiopatia-chagasica`, `category="cardiomiopatia"`
(mesma convenção de `cardiomiopatia-hipertrofica` e da produção paralela de
`cardiomiopatia-dilatada`). A cardiomiopatia chagásica crônica (CCC) é a
manifestação cardíaca mais comum e mais grave da doença de Chagas — doença
tropical negligenciada endêmica no Brasil — e não tinha ficha própria em
`doencas/metadados.json`, apesar de corpus rico já existente em
`content/Cardiomiopatias/`, `content/Dispositivos/`, `content/Arritmias/` e
`content/Cardiologia_do_Esporte_e_do_Exercício/`.

Criado via `doencas/fragmentos/` (não por edição direta do manifesto base)
para minimizar colisão com outras frentes de produção concorrentes,
incluindo a produção paralela de `cardiomiopatia-dilatada` nesta mesma
sessão.

## Fontes avaliadas e decisão de inclusão

Os 6 documentos-fonte mapeados por um agente de reconhecimento anterior
foram lidos **integralmente** por esta sessão, com avaliação individual de
centralidade ao tema (cardiomiopatia chagásica **crônica**):

**Incluídos em `related_document_slugs` (5, dentro da faixa 3–7 exigida):**

1. `aneurisma-apical-trombo-de-ve-e-avc-cardioembolico-na-cardiomiopatia-chagasica` —
   coorte de 518 pacientes (Heart, 2026); central: mecanismo de AVC
   cardioembólico na CCC.
2. `tratamento-etiologico-da-doenca-de-chagas-cronica-benznidazol-e-nifurtimox` —
   protocolo de tratamento etiológico da doença crônica; central.
3. `cardiopatia-chagasica-cronica-escore-de-rassi-e-indicacao-de-cdi` —
   escore de Rassi e indicação de CDI pela Diretriz Brasileira DCEI 2023;
   central.
4. `ablacao-epicardica-de-taquicardia-ventricular-na-cardiomiopatia-chagasica-e-nao-isquemica` —
   substrato arritmogênico epicárdico e ablação de TV refratária na CCC;
   central (mesmo cobrindo também outras etiologias não isquêmicas).
5. `cardiomiopatia-chagasica-exercicio-e-participacao-esportiva-no-atleta` —
   capacidade funcional, TCPE, elegibilidade esportiva na CCC; central.

**Excluído deliberadamente, com justificativa:**

- `miocardite-chagasica-aguda-e-miocardites-tropicais-sbc-2022` — avaliado
  criticamente conforme pedido na missão. Lido por completo: o documento é
  majoritariamente sobre a fase **aguda** da doença de Chagas (via de
  transmissão oral, diagnóstico parasitológico direto, reativação
  pós-transplante) e sobre miocardites de **outras** doenças tropicais
  (malária, dengue, Chikungunya, Zika, febre amarela). Não há seção
  substantiva sobre a progressão para cardiomiopatia crônica — não atende
  ao critério de discussão central do escopo desta ficha. Tratado como
  diferencial/contexto tangencial, não como link Tudo com Tudo.

**Também avaliados e excluídos, por iniciativa própria (fora da lista da missão):**

- `doenca-de-chagas-congenita-transmissao-vertical-diagnostico-e-tratamento-do-recem-nascido`
  (Cardiologia pediátrica) — foco em transmissão vertical e recém-nascido,
  não na cardiomiopatia crônica do adulto.
- `fluxograma-cardiomiopatia-dilatada-investigacao-etiologica` — a
  cardiomiopatia chagásica é um nó entre vários numa árvore de diagnóstico
  diferencial de CMD geral; documento não é centrado em cardiomiopatia
  chagásica.

## PMIDs verificados

8 PMIDs verificados individualmente via NCBI e-utils (`esummary`/`esearch`)
contra título, periódico, ano e primeiro autor antes da montagem — todos
confirmados sem necessidade de correção:

| PMID | Referência |
|---|---|
| 37377258 | Marin-Neto JA et al. SBC Guideline on Cardiomyopathy of Chagas Disease – 2023. Arq Bras Cardiol. |
| 16928995 | Rassi A Jr et al. Risk score for predicting death in Chagas' heart disease. N Engl J Med. 2006. |
| 26323937 | Morillo CA et al. Randomized Trial of Benznidazole (BENEFIT). N Engl J Med. 2015. |
| 36700596 | Teixeira RA et al. Brazilian Guidelines for Cardiac Implantable Electronic Devices – 2023. Arq Bras Cardiol. |
| 32087356 | Pisani CF et al. RCT ablação endo/epicárdica em Chagas. Heart Rhythm. 2020. |
| 42521491 | Teixeira Tupinambás J et al. Cardioembolic stroke in Chagas cardiomyopathy. Heart. 2026. |
| 41994350 | Kulchetscki RM et al. Outcomes ablação TV Chagas vs. isquêmica/dilatada. Lancet Reg Health Am. 2026. |
| 41172392 | Hasslocher-Moreno AM. Trypanocidal Treatment for Chronic Chagas Disease. Rev Soc Bras Med Trop. 2025. |

## Overlap de related_document_slugs

Verificado contra o catálogo combinado completo (119 registros, via
`load_disease_records`). Cinco pares de sobreposição pré-existente e
legítima foram encontrados e documentados (nenhum problemático):

- `arritmias-ventriculares-e-morte-subita-cardiaca` compartilha a ablação
  epicárdica de TV e o escore de Rassi/CDI — esperado, mesmo cruzamento
  clínico entre as duas fichas.
- `cardiomiopatias` (hub geral, PR #565 ainda não mergeada) compartilha 3
  documentos — esperado, hub cobre todas as etiologias de cardiomiopatia.
- `acidente-vascular-cerebral-agudo` compartilha o documento de
  aneurisma/trombo/AVC — esperado, mesma complicação por outro ângulo.
- `dispositivos-cardiacos-implantaveis` compartilha o documento de escore
  de Rassi/CDI — esperado, mesma indicação por outro ângulo.

**Sem overlap com `cardiomiopatia-dilatada`** (produção paralela desta
mesma sessão) — verificado e coberto por teste dedicado
(`test_sem_overlap_com_cardiomiopatia_dilatada`, que tolera o fragmento
ainda não existir no worktree).

## patient_material_slug

`null`, documentado no `review_note`: não existe material para paciente
específico de cardiomiopatia chagásica em `material-paciente/metadados.json`.
O item mais próximo (`cardiomiopatia-dilatada-por-que-o-coracao-aumenta-de-tamanho`)
não é específico da etiologia chagásica e não foi forçado como
correspondência.

## Teste dedicado

`backend/tests/test_novo_verbete_cardiomiopatia_chagasica.py`, 15 testes,
cobrindo: existência via fragmento, marcação editorial, catalogação,
profundidade mínima, acentuação correta, assistente determinístico seguro
(perguntas com `label`, regras com `op`/`add` válidos, `risk` no enum
correto), ausência de dose de fármaco, vínculos Tudo com Tudo resolvem e
são documentos narrativos (não Farmacologia/Calculadoras/Exames), vínculos
mencionam o tema centralmente, exclusão deliberada do documento de
miocardite aguda, sobreposição documentada com outras fichas, ausência de
overlap com `cardiomiopatia-dilatada`, `patient_material_slug` nulo e
documentado, não colisão de slug com o hub geral/outras cardiomiopatias, e
guarda de regressão sobre a indicação de CDI não depender de FEVE isolada
(particularidade clínica central desta doença).

## Resultado dos gates

| Gate | Resultado |
|---|---|
| Sintaxe JSON | válida |
| `load_disease_records()` | carrega, 119 registros no catálogo combinado |
| `scripts/audit_tudo_com_tudo.py` | exit 0, 100% dos vínculos resolvidos |
| `scripts/content_inventory.py --strict` | exit 0, `invalid: []`, `missing: []` |
| Teste dedicado (15 testes) | **15 passed** |
| `test_disease_fragments_canonical.py` | **3 passed** (nenhuma falha) |
| `test_canonical_content_review_status.py` | **1 falha esperada** (`cardiomiopatia-chagasica` pendente), demais testes do arquivo passam |
| `import app.main` | sucesso |
| Drift contra `origin/main` | nenhum |

## Decisão explícita sobre o gate de review_status

Este registro fica **deliberadamente** com `review_status="pendente_revisao"`.

**Correção de 29/08/2026:** a versão original deste relatório afirmava que
não fora adicionada entrada à allowlist `PENDENTES_LOTES_TUDO_COM_TUDO` em
`backend/tests/test_canonical_content_review_status.py`, sob a premissa de
que isso "contornaria" o gate principal de review-status. Essa premissa
estava incorreta: lendo `test_manifestos_canonicos_so_tem_pendencias_
explicitamente_aprovadas_para_rc`, a allowlist só é consultada para um
registro com `status == "revisado"` — ela existe para permitir uma exceção
nominal de RC a um item já revisado, não para abrir uma exceção a um item
`pendente_revisao`. Como o registro de `cardiomiopatia-chagasica` continua
com `review_status="pendente_revisao"`, adicionar sua entrada à allowlist
**não altera em nada** o resultado desse teste: ele continua — corretamente
— reportando a única falha esperada e honesta, que é o gate reconhecendo
um verbete novo ainda sem revisão humana.

O que a allowlist afeta é `test_disease_fragments_canonical.py`, um teste
diferente que reaproveita essa mesma estrutura (via `PENDENTES_DOENCAS =
PENDENTES_LOTES_TUDO_COM_TUDO.get("doencas/metadados.json", set())`) apenas
para aceitar, no catálogo combinado, que um registro novo com status
diferente de `revisado` é uma pendência editorial explícita e não um erro
de dados. Sem a entrada, esse segundo teste falhava de forma redundante e
não intencional pelo mesmo motivo já coberto pela falha principal — daí a
correção, alinhada ao padrão já usado em `sindrome-cardiorrenal` (commit
`5e107e75`, PR da leva de 29/08/2026): adicionar
`"cardiomiopatia-chagasica"` a `PENDENTES_LOTES_TUDO_COM_TUDO["doencas/
metadados.json"]`. O resultado passou de 2 falhas para exatamente 1, a
falha correta e intencional do gate principal. A promoção a
`review_status="revisado"` continua sendo decisão editorial de Rafael.

## Commit e PR

Branch `claude/novo-verbete-cardiomiopatia-chagasica-20260829`, a partir de
`origin/main`. PR aberta com `gh pr create --base main`. Sem merge, sem
deploy, conforme instrução.
