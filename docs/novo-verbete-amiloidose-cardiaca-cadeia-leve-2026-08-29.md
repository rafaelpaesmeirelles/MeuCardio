# Verbete novo: Amiloidose cardíaca por cadeia leve (AL) — 29/08/2026

## Decisão editorial em destaque

**Esta é uma decisão de escopo/taxonomia que merece atenção humana confirmatória
antes do merge**, dado o risco de sobreposição percebido com a ficha já publicada
`amiloidose-cardiaca-idoso`. Por isso o registro novo foi salvo com
`review_status="pendente_revisao"` — deliberadamente, não por descuido — e os
gates de status editorial foram deixados falhar, documentados, em vez de
contornados por allowlist. Ver seção "Gates" abaixo.

## Fase 1 — Investigação (por que este verbete foi criado)

### 1. A ficha existente é genuinamente focada em ATTR

Lido o registro completo de `amiloidose-cardiaca-idoso` em `doencas/metadados.json`:

- **Aliases**: `["ATTR cardíaca", "cardiomiopatia amiloide"]` — nenhum menciona AL/cadeia leve.
- **Tags**: `amiloidose, ATTR, insuficiência cardíaca, idoso, cardiomiopatia
  infiltrativa, tafamidis, transtirretina selvagem, cintilografia óssea,
  fibrilação atrial, amiloidose hereditária` — todas específicas de ATTR.
- **Summary/epidemiology/diagnostic_approach**: descrevem o algoritmo de
  diagnóstico não invasivo da ATTR (cintilografia + exclusão de clonalidade),
  a genotipagem do TTR, ATTRwt vs. ATTRv. A amiloidose AL aparece **apenas**
  como: (a) critério de exclusão obrigatório antes de fechar ATTR, (b) um
  parágrafo de contraste na epidemiologia, (c) uma entrada explícita em
  `differentials` afirmando que AL é "doença hematológica com tratamento e
  prognóstico completamente diferentes do ATTR" e deve ser "excluída antes de
  fechar diagnóstico de ATTR, nunca assumida como a mesma condição".
- **treatment_summary** contém a frase mais reveladora: ao chegar em AL, o
  texto diz "ver conteúdo específico já publicado no acervo sobre o ensaio
  ANDROMEDA (daratumumabe) para essa via, **sem duplicação aqui**" — a própria
  ficha ATTR já sinalizava que o conteúdo de AL pertence a outro registro.

Conclusão: a ficha `amiloidose-cardiaca-idoso` **não** cobre AL de forma
substantiva — trata-a apenas como diagnóstico diferencial/critério de
exclusão, corretamente, mas isso não é o mesmo que ter conteúdo próprio sobre
epidemiologia, apresentação, estadiamento e tratamento de AL.

### 2. O corpus já discute AL com rigor, só que disperso sem ficha organizadora

Lido por completo `content/Cardiomiopatias/diagnostico-e-tratamento-da-amiloidose-cardiaca.md`:
confirma discussão lado a lado de "attr ca" e "al amiloidose" nos "Principais
subtipos", e o algoritmo diagnóstico não invasivo (Gillmore et al. 2016)
depende de excluir proteína monoclonal (AL) antes de aceitar cintilografia
como diagnóstica de ATTR — exatamente como descrito na missão.

Além disso, o corpus já tinha conteúdo **centralmente** sobre AL, espalhado
em três pastas sem um registro de doença que os organizasse:
- `content/Cardio-oncologia/amiloidose-cardiaca-por-cadeia-leve-al-e-o-ensaio-andromeda-daratumumabe.md`
  — documento inteiro sobre o ensaio ANDROMEDA (daratumumabe), fisiopatologia
  de AL, segurança e mortalidade.
- `content/Calculadoras/al-iss-estadiamento-internacional-da-amiloidose-al-cardiaca-2026.md`
  — estadiamento prognóstico validado, exclusivo de AL (não se aplica a ATTR).
- `content/Cardiomiopatias/fluxograma-amiloidose-cardiaca-diagnostico-nao-invasivo.md`
  — tem ramos de decisão explícitos que terminam em "hipótese de amiloidose AL.
  Encaminhar ao hematologista sem retardar".

Isso é o oposto de "corpus sem rigor suficiente": há conteúdo rico,
PMID-verificável, sobre AL — só faltava o registro de doença.

### 3. AL e ATTR são clinicamente distintas

Etiologia (discrasia de plasmócitos vs. desdobramento de transtirretina
ligado à idade), via diagnóstica (biópsia de gordura/medula com tipagem por
espectrometria de massa vs. cintilografia óssea não invasiva), tratamento
(quimioterapia dirigida ao clone plasmocitário, incluindo daratumumabe, vs.
estabilizadores do tetrâmero de TTR como tafamidis) e faixa etária/prognóstico
(AL mais agressiva, pode acometer adultos jovens; ATTRwt essencialmente
restrita a idosos) não têm equivalência entre as duas doenças.

**Decisão: nenhuma das duas condições de aborto se aplicou — prossegui para a Fase 2.**

## Fase 2 — O que foi criado

- `doencas/fragmentos/amiloidose-cardiaca-cadeia-leve.json` — registro novo,
  slug `amiloidose-cardiaca-cadeia-leve`, `category="cardiomiopatia"` (mesma
  da ficha ATTR, por consistência taxonômica), `area="geral"`,
  `subtype="infiltrativa"`, `completeness="completo"`,
  `review_status="pendente_revisao"`, `version=1`, `fonte_producao="claude"`.
- `backend/tests/test_novo_verbete_amiloidose_cardiaca_cadeia_leve.py` — 15
  testes dedicados cobrindo existência, não colisão de slug, marcação
  editorial, catalogação, profundidade mínima, acentuação, diferencial
  explícito de ATTR, assistente determinístico seguro (incluindo regra de
  segurança AL↔ATTR), ausência de dose de fármaco, vínculos Tudo com Tudo
  (resolução + escopo + narrativa), sobreposição documentada com
  `amiloidose-cardiaca-idoso` **e** com o hub `cardiomiopatias`, resolução do
  `patient_material_slug` reaproveitado, e presença dos 4 PMIDs em
  `source_refs`.
- A ficha `amiloidose-cardiaca-idoso` **não foi alterada** — nenhum campo
  dela foi editado nesta rodada.

### PMIDs verificados individualmente (NCBI e-utils, 29/08/2026)

| PMID | Verificação | Uso |
|---|---|---|
| 34192431 | esummary — título/periódico/ano conferidos (Kastritis et al., NEJM 2021, ANDROMEDA) | evidência pivotal de tratamento (dara-CyBorD) |
| 41353737 | esummary — título/periódico/ano conferidos (Khwaja et al., J Clin Oncol 2026, AL-ISS) | estadiamento de risco cardíaco |
| 36697326 | esummary — título/periódico/ano conferidos (Kittleson et al., 2023 ACC ECDP) | via de consenso multidisciplinar (mesma referência já usada, de forma independente, em `amiloidose-cardiaca-idoso`; reverificada aqui) |
| 38095141 | esummary + efetch (abstract lido) — Gertz, Am J Hematol 2024 | epidemiologia, diagnóstico (biópsia/tipagem), estadiamento de Mayo, tratamento de 1ª/2ª linha |

Nenhuma correção foi necessária em nenhuma das quatro referências.

### related_document_slugs (3 de 3-7 — mínimo da regra, por rigor de "central AL")

Cada candidato listado pela recognição prévia foi lido por completo e avaliado
individualmente quanto a discutir **AL cardíaca especificamente de forma
central** (não amiloidose em geral, não apenas ATTR):

| Documento | Incluído? | Motivo |
|---|---|---|
| `amiloidose-cardiaca-por-cadeia-leve-al-e-o-ensaio-andromeda-daratumumabe` (Cardio-oncologia) | **Sim** | Documento inteiro sobre AL (ANDROMEDA) |
| `al-iss-estadiamento-internacional-da-amiloidose-al-cardiaca-2026` (Calculadoras) | **Não** — regra de pasta | Central sobre AL, mas Calculadoras é fora de escopo por regra explícita; PMID usado em `source_refs` normalmente |
| `diagnostico-e-tratamento-da-amiloidose-cardiaca` (Cardiomiopatias) | **Sim** | Algoritmo de exclusão de AL antes de ATTR, subtipos lado a lado |
| `fluxograma-amiloidose-cardiaca-diagnostico-nao-invasivo` (Cardiomiopatias) | **Sim** | Ramos de decisão explícitos terminando em diagnóstico/encaminhamento de AL |
| `amiloidose-cardiaca-attr-hereditaria-versus-selvagem-diferenciacao-clinica-e-teste-genetico` (Insuficiência cardíaca) | **Não** | Puramente ATTRv vs. ATTRwt; AL citada uma única vez, lateralmente (estatística de erro de classificação) |
| `fibrilacao-atrial-e-amiloidose-cardiaca-prevalencia-e-implicacao-terapeutica` (Fibrilação atrial) | **Não** | Trata "amiloidose cardíaca" (AL+ATTR combinadas) sem foco específico em AL |

Dois dos três documentos escolhidos também aparecem no `related_document_slugs`
de `amiloidose-cardiaca-idoso` **e** do hub geral `cardiomiopatias` — overlap
de três vias, intencional e documentado no teste dedicado
(`DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS`), no mesmo padrão já usado por
`cardiomiopatia-hipertrofica` em relação ao hub.

### patient_material_slug

Reaproveita `amiloidose-cardiaca` (o mesmo já usado por `amiloidose-cardiaca-idoso`):
o material em linguagem simples já descreve explicitamente os dois tipos
principais de amiloidose cardíaca (transtirretina e cadeia leve). Reúso
intencional, documentado em `review_note`, não um material novo criado nem um
erro de cópia.

## Gates executados

| Gate | Resultado |
|---|---|
| `scripts/audit_tudo_com_tudo.py` | Passou — 100% dos vínculos resolvidos (`SpecialtyDisease.related_document_slugs`: 1096/1096, `SpecialtyDisease.patient_material_slug`: 104/104), `review_status.pendente_revisao: 1` (exatamente este registro) |
| `scripts/content_inventory.py --strict` | Passou — `invalid: []`, `missing: []` |
| `backend/tests/test_novo_verbete_amiloidose_cardiaca_cadeia_leve.py` | **15/15 passaram** |
| `backend/tests/test_disease_fragments_canonical.py` | **3/3 passaram** |
| `backend/tests/test_canonical_content_review_status.py` | **1 falha esperada** (`test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`) |
| `python -c "import app.main"` | Passou |

### Correção: era 1 falha esperada, não 2 (nota de 29/08/2026)

A primeira versão deste relatório registrava **duas** falhas esperadas,
tratando-as como a mesma causa raiz — isso estava incorreto. `PENDENTES_LOTES_TUDO_COM_TUDO`
(definida em `test_canonical_content_review_status.py` e reaproveitada por
`test_disease_fragments_canonical.py` via import, como o mesmo objeto Python)
serve a dois testes com lógicas diferentes:

- Em `test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`,
  a allowlist só é consultada para registros com `status == "revisado"` — ou
  seja, ela nunca isenta um registro `pendente_revisao`. Deixá-la vazia ou
  populada não muda o resultado deste teste para
  `amiloidose-cardiaca-cadeia-leve`: ele **continua falhando**, como deve,
  porque o review_status honesto do registro é `pendente_revisao`. Essa é a
  única falha esperada e correta — não foi contornada.
- Em `test_disease_fragments_canonical.py::test_catalogo_combinado_tem_slugs_unicos_e_status_editorial_explicito`,
  a mesma allowlist é consultada de forma diferente: um slug presente nela é
  aceito como pendência **explicitamente reconhecida** no catálogo combinado,
  independentemente do `review_status`. Deixá-la vazia fazia esse segundo
  teste falhar também — não porque o gate de publicação exigisse isso, mas
  porque a allowlist compartilhada ainda não tinha sido atualizada com o novo
  slug. Essa segunda falha era desnecessária e não intencional.

Seguindo o mesmo padrão já usado com sucesso em
`claude/novo-verbete-cardiomiopatia-de-takotsubo-20260829` (PR #698), foi
adicionada a entrada `"amiloidose-cardiaca-cadeia-leve"` em
`PENDENTES_LOTES_TUDO_COM_TUDO["doencas/metadados.json"]`, com o mesmo
comentário explicativo (adaptado ao slug). Resultado após a correção: **1
falha, não 2** — `test_disease_fragments_canonical.py` agora passa por
completo (3/3), e `test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
continua falhando, sem alteração de comportamento, exatamente como deve.

## Próximo passo

Aval humano explícito do Rafael sobre a decisão de escopo (criar ficha
própria para AL em vez de aprofundar ainda mais a seção de exclusão dentro de
`amiloidose-cardiaca-idoso`) e, se aprovado, mudança de `review_status` para
`revisado` em `doencas/fragmentos/amiloidose-cardiaca-cadeia-leve.json` — via
`doencas/correcoes/*.json` ou edição direta do fragmento, seguindo o padrão
já usado no repositório.
