# Verbete novo — Hipertensão pulmonar tromboembólica crônica (CTEPH) — 29/08/2026

## Contexto

A missão pediu a criação de um verbete novo e dedicado para CTEPH (grupo 4
da hipertensão pulmonar), com profundidade que a ficha genérica existente
`hipertensao-pulmonar` não cobre.

Antes de começar, o registro `hipertensao-pulmonar` (revisado, publicado)
foi lido por completo em `doencas/metadados.json`. Confirmação da lacuna:
essa ficha cobre os cinco grupos ESC/ERS 2022 em visão panorâmica e já
menciona CTEPH como grupo 4 (inclusive no `treatment_summary` e nos
`differentials`), mas sem: fisiopatologia da obstrução trombótica
organizada, protocolo de cintilografia V/Q versus angiotomografia,
critérios detalhados de operabilidade e as três funções do heart team, ou
os dados quantitativos de sobrevida operado-versus-não-operado do registro
de Delcroix. Confirmada a lacuna, o verbete `cteph` foi criado via
`doencas/fragmentos/cteph.json` — **não** via edição direta de
`doencas/metadados.json` — para minimizar colisão com outras frentes de
produção concorrentes.

## Convenção de `category` confirmada

`category="circulacao_pulmonar"` — mesma convenção já usada por
`hipertensao-pulmonar`, `hipertensao-pulmonar-pediatrica` e
`hipertensao-pulmonar-gravidez`, confirmada por listagem programática do
manifesto antes de escrever o registro.

## Conteúdo produzido

- `epidemiology`: incidência (3-5 casos/100.000 hab/ano), registro
  internacional prospectivo de Delcroix 2016 (679 pacientes, 27 centros
  europeus, 404 operados vs. 275 não operados, sobrevida 93/91/89% vs.
  88/79/70% em 1/2/3 anos, preditores de mortalidade), mortalidade
  operatória atual (~2%, <3% em centros de referência, <5% mesmo com RVP
  >1.000 dyn·s·cm⁻⁵), proporção de pacientes fora do alcance cirúrgico
  (30-45%) e taxa de doença residual pós-EAP (17-51%, limiar prognóstico
  PAPm ≥38mmHg/RVP ≥5UW).
- `presentation` (10), `diagnostic_approach` (dict aninhado com 3 eixos:
  critérios hemodinâmicos e via diagnóstica; cintilografia V/Q versus
  angiotomografia; avaliação de operabilidade pelo heart team — mais de
  3.000 caracteres, cobrindo exatamente os três pontos de profundidade
  pedidos na missão), `differentials` (7), `tests` (7), `red_flags` (7).
- `treatment_summary` (>2.500 caracteres): anticoagulação vitalícia, heart
  team (composição e três funções), endarterectomia pulmonar (curativa,
  mortalidade ~2%, RVP alta/idade/obesidade/reoperação não são
  contraindicação isolada, operabilidade técnica ≠ decisão de operar),
  doença residual pós-EAP, angioplastia pulmonar por balão (RACE/MR BPA,
  superioridade hemodinâmica com custo procedimental relevante), riociguate
  e macitentana como classes terapêuticas (sem dose), pré-tratamento
  farmacológico antes de BPA com RVP >4UW, e critérios de transplante
  pulmonar para casos refratários.
- `ambulatory_flow` (8), `emergency_flow` (5), `monitoring` (7),
  `special_populations` (7, incluindo o parágrafo dedicado à situação do
  MERIT-1/macitentana).
- `assistant_questions` (8), `assistant_rules` (8, priority 100 para
  falência aguda de VD e 90 para hemoptise significativa).
- `related_document_slugs` (6, verificados individualmente).
- `patient_material_slug`:
  `cteph-hipertensao-pulmonar-por-coagulos-antigos`.

## Verificação dos 6 related_document_slugs (Tudo com Tudo)

Todos os 6 documentos mapeados na missão foram **lidos por completo** nesta
sessão e incluídos, por discutirem CTEPH de forma central (documento
inteiro dedicado ao tema, dentro da faixa 3-7 exigida):

1. `cteph-criterios-de-operabilidade-e-a-decisao-do-heart-team-especializado`
2. `cteph-sobrevida-em-longo-prazo-o-registro-internacional-de-delcroix-2016`
3. `angioplastia-pulmonar-por-balao-na-cteph-inoperavel-race-e-mr-bpa`
4. `macitentana-na-cteph-inoperavel-o-ensaio-merit-1-e-sua-retratacao-republicacao`
5. `hipertensao-pulmonar-tromboembolica-cronica-cteph-e-criterios-de-transplante-pulmonar`
6. `fluxograma-cteph-operabilidade-bpa-riociguate`

Nenhum candidato resolve para `content/Farmacologia/`,
`content/Calculadoras/` ou `content/Exames/`.

### Sobreposição documentada com o hub `hipertensao-pulmonar`

Verificação programática contra o catálogo combinado (119 registros): os 6
`related_document_slugs` desta ficha **já constam integralmente** em
`related_document_slugs` de `hipertensao-pulmonar` (ficha genérica,
revisada e publicada). Isso é overlap **legítimo e esperado** — CTEPH é o
grupo 4 dentro da classificação de cinco grupos que o hub cobre de forma
panorâmica —, exatamente a mesma relação hub/subficha já aceita entre
`cardiomiopatia-de-takotsubo` e o hub `cardiomiopatias` na PR #698 (ainda
não mergeada em main nesta data). Nenhum dos 6 documentos é compartilhado
com nenhuma outra ficha do catálogo além de `hipertensao-pulmonar` — sem
overlap não documentado.

## Verificação de PMIDs

7 PMIDs verificados individualmente via NCBI e-utils (`esummary`) em
29/08/2026, conferindo título, periódico, ano, volume e páginas contra o
registro oficial do PubMed antes de persistir no `source_refs`:

- 39209473 (Kim NH et al., Eur Respir J 2024 — critérios de operabilidade)
- 26826181 (Delcroix M et al., Circulation 2016 — registro internacional)
- 35926542 (Jaïs X et al., RACE, Lancet Respir Med 2022)
- 35926544 (Kawakami T et al., MR BPA, Lancet Respir Med 2022)
- 38548406 (Ghofrani HA et al., MERIT-1, republicação 2024)
- 38552648 (nota de retratação/republicação, Lancet Respir Med 2024)
- 36017548 (Humbert M et al., ESC/ERS 2022 Guidelines)

Todos conferem título/periódico/volume/páginas com o documento-fonte
correspondente; nenhuma correção necessária nesta rodada.

## Situação verificada do PMID do MERIT-1 (atenção especial pedida na missão)

O registro **original** de 2017 (Ghofrani HA et al., Lancet Respir Med.
2017;5(10):785-794, **PMID 28919201**) está hoje marcado
**`Retracted Publication`** no registro oficial do PubMed (confirmado via
e-utils/esummary em 29/08/2026). A cadeia completa nos metadados do PubMed:

- `Retraction in` → PMID **38552648** (nota editorial, Lancet Respir Med.
  2024;12(4):262-263).
- `Retracted and republished in` → PMID **38548406** (republicação com
  dados revisados, Lancet Respir Med. 2024;12(4):e21-e30).

**Motivo da retratação** (apurado no documento-fonte e consistente com os
metadados do PubMed): inspeção de autoridade sanitária levou a uma
verificação rigorosa dos dados-fonte de cateterismo cardíaco direito local,
corrigindo 15 valores de RVP em 13 dos 80 participantes; revisão médica
independente subsequente (dois especialistas cegos à alocação) classificou
como implausíveis os dados de 14 dos 80 participantes (8 no grupo
macitentana, 6 no placebo). **Uma análise de sensibilidade excluindo esses
14 participantes confirmou o resultado positivo original do desfecho
primário de eficácia** — ou seja, retratação por rigor de
integridade/plausibilidade de dados numa fração da amostra, **sem reversão
de conclusão e sem acusação de fraude**.

Esta ficha cita **exclusivamente a versão republicada de 2024 (PMID
38548406)** no `source_refs`, com nota explícita alertando contra o uso
isolado do PMID 28919201, e documenta a situação também em
`special_populations` — coberto por teste dedicado
(`test_merit1_situacao_de_retratacao_documentada`).

## Nenhuma dose de fármaco

Verificado por regex e por leitura direta: riociguate e macitentana
aparecem apenas como classes terapêuticas em todo o registro, nunca com
dose.

## Falha esperada e documentada no gate de `review_status`

`review_status` permanece `"pendente_revisao"` — conteúdo novo não revisado
por humano não se autoaprova. Por isso:

- `backend/tests/test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  **FALHA** para `cteph`. Comportamento esperado e correto, seguindo
  exatamente a mesma lógica já documentada na PR #698: o teste consome todo
  registro `status == "revisado"` no primeiro `continue`, antes de qualquer
  checagem de allowlist — as checagens contra `PENDENTES_LOTES_TUDO_COM_TUDO`
  só são alcançáveis para registros que **já** estão `"revisado"`, nunca
  para `"pendente_revisao"`. A allowlist não isenta este registro e não foi
  usada com essa intenção.
- A entrada `"cteph"` foi adicionada a
  `PENDENTES_LOTES_TUDO_COM_TUDO["doencas/metadados.json"]` mesmo assim,
  porque essa allowlist é **reaproveitada por importação direta** em
  `backend/tests/test_disease_fragments_canonical.py`, onde a checagem
  funciona corretamente e a entrada é necessária ali.

## Gates executados

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`;
  `SpecialtyDisease.related_document_slugs`: 1099/1099 resolvidos;
  `SpecialtyDisease.patient_material_slug`: 104/104 resolvidos;
  `review_status.pendente_revisao: 1` (só este registro); 9.546 registros
  totais.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  9.546 registros totais.
- `backend/tests/test_novo_verbete_cteph.py`: 15 testes.
- `backend/tests/test_canonical_content_review_status.py`: 1 falha
  esperada/documentada, 2 passando.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/novo-verbete-cteph-20260829`, baseada em `origin/main`.
