# Verbete novo — Torsades de pointes e QT longo adquirido — 29/08/2026

## Contexto e escopo

Rafael pediu um verbete novo cobrindo especificamente a forma **ADQUIRIDA**
(induzida por fármaco/distúrbio eletrolítico) de QT longo e torsades de
pointes — distinta de duas fichas irmãs que já existiam:

- `canalopatias-cardiacas-hereditarias` — a canalopatia CONGÊNITA (mutação
  em gene de canal iônico, presente desde o nascimento, estratificada por
  escore de Schwartz/genótipo);
- `qt-longo-terapia-oncologica` — o prolongamento de QT por terapia
  oncológica dirigida (inibidores de tirosina-quinase, trióxido de arsênio,
  inibidores de CDK4/6 e outros antineoplásicos), criada na mesma data.

Ambas usam `category="arritmia"`; este verbete segue a mesma convenção.

Criado via `doencas/fragmentos/torsades-de-pointes-qt-longo-adquirido.json`
— **não** via edição direta de `doencas/metadados.json` — para minimizar
colisão com outras frentes de produção concorrentes, mesmo padrão da PR
#698 (`cardiomiopatia-de-takotsubo`).

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: dados de Tisdale et al. (incidência de QTc prolongado por
  estrato de risco: ~15%/37%/73%), das duas coortes de Ray et al. sobre
  antipsicótico e morte súbita cardíaca (dose-dependência, ausência de
  proteção do "atípico"), e do documento de consenso AHA/ACCF (limiares de
  QTc por percentil 99, com assimetria por sexo).
- `presentation` (10), `diagnostic_approach` (dict aninhado com 5 eixos:
  mecanismo fisiopatológico do bloqueio de hERG, causas farmacológicas
  comuns descritas qualitativamente — sem dose, distúrbios eletrolíticos
  predisponentes, escore de Tisdale completo, reconhecimento eletrocardiográfico
  da torsades), `differentials` (8, incluindo diferenciação explícita das
  duas fichas irmãs, CPVT, Brugada, TV bidirecional por digoxina e síndrome
  de Andersen-Tawil), `tests` (8), `red_flags` (10).
- `treatment_summary`: sequência de choque não sincronizado imediato na TV
  polimórfica sustentada (AHA 2025), remoção do substrato reversível,
  magnésio IV como prevenção de recorrência (não substituto do choque),
  distinção de TV polimórfica sem QT longo, pacing/isoproterenol em
  recorrência pausa-dependente, papel exclusivamente de estratificação de
  risco do escore de Tisdale, e sinalização de investigação de canalopatia
  congênita quando o QT persiste após remoção do fator adquirido — tudo sem
  nenhuma dose de fármaco.
- `ambulatory_flow` (10), `emergency_flow` (10), `monitoring` (8).
- `special_populations` (7): paciente psiquiátrico em antipsicótico,
  paciente hospitalizado com múltiplos fatores de Tisdale, sexo feminino,
  idoso polimedicado, insuficiência renal/hepática, predisposição a
  hipocalemia, e portador de variante genética latente exposto a fármaco
  pró-QT (sobreposição "dois fatores" com a canalopatia congênita).
- `assistant_questions` (15), `assistant_rules` (12, priority 97 para TV
  polimórfica sustentada — a regra de maior risco clínico).
- `related_document_slugs` (5, verificados individualmente).
- `patient_material_slug` preenchido:
  `qt-longo-o-que-significa-e-cuidados-com-medicamentos`.

## Verificação dos related_document_slugs (Tudo com Tudo)

Seis candidatos foram mapeados na missão original. **Três vivem em
`content/Farmacologia/` e foram deliberadamente excluídos**, por instrução
explícita desta rodada, mesmo sendo tematicamente relevantes:

1. `metadona-e-prolongamento-do-intervalo-qt`
2. `hipocalcemia-grave-e-prolongamento-do-qt-mecanismo-de-fase-2-e-reversao-rapida-com-calcio`
3. `sulfato-de-magnesio-em-cardiologia-torsades-de-pointes-e-adjuvante-no-controle-de-frequencia-da-fa`

Os três foram **lidos como apoio de conteúdo** para o texto desta ficha
(mecanismo de bloqueio de hERG pela metadona, hipocalcemia de fase 2, papel
do magnésio na torsades), mas não entram como link estrutural — nenhum
candidato final resolve para `content/Farmacologia/`, `content/
Calculadoras/` ou `content/Exames/`.

Isso deixava apenas 3 candidatos válidos (exatamente o piso da regra Tudo
com Tudo). Busquei ativamente 1-2 alternativas via
`grep -ril "torsades\|QT longo adquirido\|prolongamento do QT" content/`
fora de Farmacologia/Calculadoras/Exames, e **incluí 2** para dar folga:

Lista final (5, cada um **lido por completo** nesta sessão, confirmando
discussão CENTRAL do tema):

1. `torsades-de-pointes-e-qt-longo-adquirido-escore-de-tisdale-e-manejo-agudo`
   — documento central homônimo, em `content/Arritmias/`.
2. `fluxograma-torsades-de-pointes-e-qt-longo-adquirido` — fluxograma
   central homônimo, em `content/Arritmias/`.
3. `antipsicoticos-e-prolongamento-de-qt-risco-de-morte-subita-cardiaca` —
   em `content/Saúde_mental_e_cardiologia/`, documento inteiro dedicado ao
   risco de QT/torsades por antipsicótico.
4. `hipomagnesemia-risco-arritmico-hipocalemia-refrataria-e-investigacao` —
   em `content/Terapia_intensiva/`, contém seção dedicada "QT longo
   adquirido e torsades de pointes" que já referencia explicitamente os
   dois documentos centrais desta ficha.
5. `hipocalemia-grave-risco-arritmico-e-reposicao-segura` — em
   `content/Terapia_intensiva/`, contém subseção dedicada "QT longo
   adquirido / torsades de pointes" descrevendo hipocalemia como cofator
   clássico.

## Sobreposição de hub documentada

Dois dos cinco `related_document_slugs`
(`torsades-de-pointes-e-qt-longo-adquirido-escore-de-tisdale-e-manejo-agudo`
e `fluxograma-torsades-de-pointes-e-qt-longo-adquirido`) também aparecem em
`related_document_slugs` da ficha-hub `arritmias-ventriculares-e-morte-subita-cardiaca`
(26 vínculos). Verificado programaticamente que essa é a **única**
sobreposição com qualquer outra ficha do catálogo — mesma lógica já aceita
para o hub `cardiomiopatias` na ficha `cardiomiopatia-de-takotsubo` (PR
#698): o verbete específico e o hub geral compartilham legitimamente os
documentos mais centrais do tema.

Confirmado também, sem sobreposição alguma, contra as duas fichas irmãs
`canalopatias-cardiacas-hereditarias` (19 `related_document_slugs`, nenhum
em comum) e `qt-longo-terapia-oncologica` (sem `related_document_slugs`
cadastrados).

## Verificação de PMIDs

8 PMIDs verificados individualmente via NCBI e-utils (`esummary`) em
29/08/2026, conferindo título, periódico, ano, volume, número e páginas
contra o registro oficial do PubMed antes de persistir no `source_refs`:

- 41122884 (Wigginton et al., AHA 2025 ALS Guidelines)
- 36017572 (Zeppenfeld et al., ESC 2022 VA/SCD Guidelines)
- 23716032 (Tisdale et al., escore de risco de QTc, Circ Cardiovasc Qual
  Outcomes 2013)
- 20142454 (Drew et al., AHA/ACCF Scientific Statement sobre prevenção de
  torsades em ambiente hospitalar, Circulation 2010)
- 11735845 (Ray et al., antipsicóticos e morte súbita cardíaca, Arch Gen
  Psychiatry 2001)
- 19144938 (Ray et al., antipsicóticos atípicos e morte súbita cardíaca,
  NEJM 2009)
- 14999113 (Roden, mecanismo de prolongamento de QT induzido por fármaco,
  NEJM 2004)
- 16554806 (Sanguinetti & Tristani-Firouzi, canais hERG e arritmia,
  Nature 2006)

**Nenhuma divergência encontrada** entre os documentos-fonte lidos nesta
sessão e o registro oficial do PubMed (diferente da rodada de takotsubo, em
que 2 PMIDs precisaram de correção).

## Nenhuma dose de fármaco

Nenhum campo de texto desta ficha contém dose, concentração ou velocidade
de infusão de qualquer fármaco — verificado por revisão manual e por regex
dedicado no teste (`test_nenhuma_dose_de_farmaco_em_nenhum_campo`). O
escore de Tisdale foi capturado **qualitativamente** como ferramenta de
estratificação de risco (pontos por variável, faixas de risco), sem
transformar nenhuma de suas variáveis em prescrição.

## Falha esperada e documentada no gate de review_status

`review_status` permanece `"pendente_revisao"` — conteúdo novo não revisado
por humano não se autoaprova. Seguindo o padrão exato da PR #698
(`claude/novo-verbete-cardiomiopatia-de-takotsubo-20260829`):

- `backend/tests/test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  **FALHA** para `torsades-de-pointes-qt-longo-adquirido`. Isso é esperado
  e correto: a lógica desse teste consome todo registro com
  `status == "revisado"` no primeiro `continue`, antes de qualquer checagem
  de allowlist — as checagens seguintes contra `PENDENTES_LOTES_TUDO_COM_TUDO`
  só são alcançáveis para registros que **já** estão `"revisado"`, nunca
  para `"pendente_revisao"`. A allowlist não isenta este registro, e não foi
  usada com essa intenção.
- A entrada `"torsades-de-pointes-qt-longo-adquirido"` foi adicionada a
  `PENDENTES_LOTES_TUDO_COM_TUDO["doencas/metadados.json"]` mesmo assim,
  porque essa mesma allowlist é **reaproveitada por importação direta** em
  `backend/tests/test_disease_fragments_canonical.py::test_catalogo_combinado_tem_slugs_unicos_e_status_editorial_explicito`,
  onde a checagem contra pendências **funciona corretamente**. Ali a
  entrada é necessária e o teste passa.

## Gates executados

- `backend/tests/test_novo_verbete_torsades_de_pointes_qt_longo_adquirido.py`
  — 16 testes dedicados.
- `backend/tests/test_disease_fragments_canonical.py` — passa (allowlist
  compartilhada funciona corretamente).
- `backend/tests/test_canonical_content_review_status.py` — 1 falha
  esperada e documentada (`torsades-de-pointes-qt-longo-adquirido`,
  `review_status=pendente_revisao`), não contornada.
- Demais gates do repositório (auditoria Tudo com Tudo, inventário de
  conteúdo, sanity de import do `app.main`) executados sem regressão nova
  fora da falha já documentada acima.

Nenhum merge nem deploy foi realizado — apenas push da branch e abertura de
PR, conforme instrução.
