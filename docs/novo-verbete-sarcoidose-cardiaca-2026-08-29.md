# Verbete novo — Sarcoidose cardíaca — 29/08/2026

## Fase 1 — Investigação e decisão

O fragmento pendente `miocardite` (hub IMPS,
`doencas/fragmentos/zz-release36h-miocardite.json`, `review_status: revisado`)
cita "sarcoidose cardíaca" **14 vezes** ao longo de `summary`, `epidemiology`,
`diagnostic_approach`, `differentials`, `tests`, `red_flags`,
`assistant_questions` e `related_document_slugs` — mas em nenhum momento
reproduz:

- os critérios diagnósticos da Japanese Circulation Society (SJC), reproduzidos
  pela diretriz SBC 2022 (dois maiores, ou um maior + dois menores);
- o protocolo/papel do PET-FDG (ou cintilografia com gálio-67) como critério
  maior isolado;
- os pré-requisitos da forma **isolada** (sarcoidose cardíaca sem doença
  extracardíaca detectável);
- a classe de recomendação específica de imunossupressão da sarcoidose
  cardíaca (Classe IIa, Nível B para prednisona — distinta da Classe I da
  miocardite de células gigantes, seu diferencial mais próximo).

Todas as 14 menções seguem o mesmo padrão: sarcoidose cardíaca como
**etiologia imunomediada** e como **diagnóstico diferencial histológico** da
miocardite de células gigantes, sempre no contexto de "as duas podem ser
indistinguíveis clinicamente, exigem biópsia". O documento-fonte dedicado
desta biblioteca —
`sarcoidose-cardiaca-criterios-diagnosticos-e-tratamento-sbc-2022.md`, que
contém todo o conteúdo acima — **nem consta** no `related_document_slugs` do
hub de miocardite.

**Decisão**: sarcoidose cardíaca é tratada apenas superficialmente no hub
`miocardite` (menção de etiologia/diferencial, não abordagem diagnóstica e
terapêutica própria). A entidade tem fisiopatologia granulomatosa distinta
(doença sistêmica multiorgânica, não infecciosa/pós-viral como a maioria das
miocardites do hub), abordagem diagnóstica própria (critérios SJC, PET-FDG,
forma isolada) e força de recomendação terapêutica distinta da miocardite de
células gigantes — critérios suficientes para justificar ficha própria.
Prosseguiu-se para a Fase 2.

## Conteúdo produzido (verbete completo, do zero)

Criado via `doencas/fragmentos/sarcoidose-cardiaca.json` — não por edição
direta de `doencas/metadados.json` — para reduzir colisão com outras frentes
de produção concorrentes no mesmo dia.

- `epidemiology`: subdiagnóstico por apresentação inespecífica, discrepância
  entre acometimento clínico aparente e histológico/por imagem, diferencial
  histológico com miocardite de células gigantes (GCM) e a hipótese de
  sobreposição fenotípica não estabelecida nem refutada, classificação sob o
  guarda-chuva IMPS (ESC 2025).
- `diagnostic_approach` (dict aninhado com 8 eixos: critérios SJC — visão
  geral, maiores, menores —, grupo histológico vs. clínico, forma isolada com
  pré-requisitos, papel e limitações do PET-FDG/cintilografia, limitações da
  biópsia, diferenciação com células gigantes, indicação individualizada de
  CDI).
- `presentation` (10), `differentials` (8, incluindo explicitamente
  miocardite de células gigantes como diferencial mais próximo, com nota de
  indistinguibilidade clínica/histológica e de força de recomendação
  terapêutica diferente), `tests` (8), `red_flags` (6).
- `treatment_summary`: contraste de força de recomendação entre sarcoidose
  cardíaca (imunossupressão Classe IIa) e miocardite de células gigantes
  (Classe I, com transplante Classe I); indicação individualizada de CDI
  conforme ESC 2022 de arritmias ventriculares/morte súbita — nenhuma dose de
  fármaco em nenhum campo.
- `ambulatory_flow` (7), `emergency_flow` (4), `monitoring` (5),
  `special_populations` (5).
- `assistant_questions` (8), `assistant_rules` (7).
- `related_document_slugs` (3, cada um verificado individualmente).
- `patient_material_slug`: nulo — não existe material educativo dedicado à
  sarcoidose cardíaca no corpus atual (conferido em
  `material-paciente/metadados.json`); não foi inventado um slug.

## Verificação do related_document_slugs (Tudo com Tudo)

Dos 3 documentos originalmente mapeados para esta rodada, apenas 2 discutem
sarcoidose cardíaca de forma central:

1. `sarcoidose-cardiaca-criterios-diagnosticos-e-tratamento-sbc-2022` —
   documento inteiro dedicado ao tema (critérios SJC, forma isolada,
   tratamento, comparação com GCM).
2. `miocardite-de-celulas-gigantes-diagnostico-diferencial-com-sarcoidose-cardiaca-e-terapia-imunossupressora` —
   diferencial obrigatório com sarcoidose cardíaca é parte central do próprio
   título e do corpo do documento.

O terceiro documento originalmente mapeado,
`sindromes-inflamatorias-miocardicas-e-pericardicas-imps-framework-unificado-esc-2025`,
foi lido por completo e **não menciona "sarcoidose" nenhuma vez** — foi usado
apenas como contexto de fundo (classificação IMPS) e excluído do
`related_document_slugs` por não discutir o tema de forma central.

Busca ativa adicional via `grep -ril sarcoidose content/` encontrou mais 11
documentos citando o termo. Cada um foi lido por completo. Dez foram
descartados por menção superficial (item de lista/diferencial entre muitos,
sem discussão dedicada):
`arritmias-ventriculares-e-prevencao-de-morte-subita-cardiaca-esc-2022`,
`cardiomiopatia-pediatrica-dilatada-e-hipertrofica-etiologia-genetica-versus-adquirida-e-transplante`,
`cardiomiopatia-hipertrofica-diagnostico-estratificacao-de-risco-e-tratamento-esc-2023-versao-completa`,
`fluxograma-miocardite-aguda-esc-2025`,
`miocardite-chagasica-aguda-e-miocardites-tropicais-sbc-2022`,
`cardiodesfibrilador-implantavel-fundamentos-prevencao-secundaria` (sarcoidose
aparece 6 vezes, mas sempre como item avulso em listas/checklists ao longo de
um módulo genérico de CDI, sem seção dedicada),
`doenca-veno-oclusiva-pulmonar-pvod-diagnostico-diferencial-e-risco-de-edema-com-vasodilatador`,
`esc-2026-insuficiencia-cardiaca-mudancas-chave-e-recomendacoes` (uma única
recomendação IIa C sobre PET-FDG — usada como apoio textual no
`diagnostic_approach`, sem citação formal em `source_refs` por não ter PMID
verificável nesta sessão, mas não elevada a `related_document_slugs`),
`doenca-pericardica-induzida-por-radioterapia-pericardite-aguda-e-constricao-tardia`,
e `miocardite-diagnostico-estratificacao-de-risco-e-biopsia-endomiocardica-esc-2025`
(lista o padrão histológico da sarcoidose numa tabela comparativa, mas
declara explicitamente que "manejo específico de subtipos raros (sarcoidose
cardíaca...) têm corpo de evidência próprio, não reproduzido aqui" — a própria
fonte confirma que não é discussão central ali).

Um documento adicional passou no crivo de discussão central e foi incluído:

3. `hipertensao-pulmonar-associada-a-sarcoidose-mecanismos-multiplos-e-tratamento-individualizado` —
   dedica um mecanismo inteiro (item 4 de 5, com parágrafo próprio) à
   disfunção de ventrículo esquerdo por **sarcoidose cardíaca concomitante**
   como causa de hipertensão pulmonar pós-capilar (Grupo 2) em 5-20% dos casos
   de SAPH — conexão clinicamente verdadeira e específica, não mera
   proximidade temática (15 menções ao termo "sarcoidose" no arquivo).

Não foi possível justificar uma quarta conexão sem forçar uma menção
superficial a passar por discussão central. **3 entradas** ficou dentro do
intervalo permitido (3-7); cada uma foi lida por completo e confirmada.

Nenhum candidato resolve para `content/Farmacologia/`, `content/Calculadoras/`
ou `content/Exames/`.

### Overlap documentado

- `miocardite-de-celulas-gigantes-diagnostico-diferencial-com-sarcoidose-cardiaca-e-terapia-imunossupressora`
  também consta no `related_document_slugs` do hub `miocardite` — overlap
  esperado (a diferenciação entre as duas condições é exatamente o motivo do
  link em ambos os registros), coberto por teste dedicado.
- `hipertensao-pulmonar-associada-a-sarcoidose-mecanismos-multiplos-e-tratamento-individualizado`
  também consta no `related_document_slugs` do verbete `hipertensao-pulmonar`
  — overlap igualmente esperado (mecanismo de HP pós-capilar por disfunção de
  VE secundária a sarcoidose cardíaca), coberto pelo mesmo teste dedicado.
- Nenhum outro overlap encontrado ao varrer os 119 registros do catálogo
  combinado.

## Verificação de PMIDs

5 PMIDs verificados individualmente via NCBI E-utilities (`esummary`) em
29/08/2026, conferindo título, periódico e data contra o que os documentos-
fonte já revisados desta biblioteca declaram — sem divergência encontrada em
nenhum dos 5:

- 35830116 — Montera MW et al., Diretriz de Miocardites SBC 2022, Arq Bras
  Cardiol.
- 37456487 — Naseeb MW et al., revisão de terapia imunomoduladora na
  miocardite de células gigantes, Cureus 2023.
- 40878297 — Schulz-Menger J et al., 2025 ESC Guidelines for myocarditis and
  pericarditis, Eur Heart J.
- 37835874 — Kacprzak A et al., fenótipos de hipertensão pulmonar associada à
  sarcoidose, Diagnostics 2023.
- 36017572 — 2022 ESC Guidelines for ventricular arrhythmias and sudden
  cardiac death, Eur Heart J.

Nenhuma correção bibliográfica foi necessária desta vez — os 5 registros
conferiram exatamente com o que os documentos-fonte já revisados descreviam.

## Nota editorial sobre `category`

`doenca_miocardica` segue a mesma convenção já usada para o verbete-irmão
pediátrico `miocardite-pediatrica`. O hub geral `miocardite` usa
`doenca_inflamatoria`, mas esta rodada restringiu explicitamente a escolha a
`doenca_miocardica` ou `pericardio` (convenção confirmada listando as
categorias já usadas no catálogo combinado). Optou-se por `doenca_miocardica`
porque a entidade é fundamentalmente uma miocardiopatia granulomatosa; os
documentos-fonte vivem em `content/Pericárdio/` apenas por organização
histórica da pasta, não por classificação clínica da doença. Essa tensão fica
registrada no `review_note` do próprio registro.

## Falha esperada e documentada no gate de review_status

`review_status` permanece `"pendente_revisao"` — conteúdo novo não revisado
por humano não se autoaprova. Por isso:

- `backend/tests/test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  **FALHA** para `sarcoidose-cardiaca`. Esperado e correto, não um bug: a
  lógica desse teste consome todo registro com `status == "revisado"` no
  primeiro `continue`, antes de qualquer checagem de allowlist — as checagens
  seguintes contra `PENDENTES_LOTES_TUDO_COM_TUDO` só são alcançáveis para
  registros que **já** estão `"revisado"`, nunca para `"pendente_revisao"`. A
  allowlist não isenta este registro, e não foi usada com essa intenção.
- A entrada `"sarcoidose-cardiaca"` foi adicionada a
  `PENDENTES_LOTES_TUDO_COM_TUDO["doencas/metadados.json"]` mesmo assim,
  porque essa mesma allowlist é reaproveitada por importação direta em
  `backend/tests/test_disease_fragments_canonical.py`, onde a checagem contra
  pendências funciona corretamente — mesmo padrão da PR #698
  (`cardiomiopatia-de-takotsubo`).

## Gates executados

(preenchido após execução — ver seção "Resultado dos gates" abaixo)

## Branch e PR

Branch `claude/novo-verbete-sarcoidose-cardiaca-20260829`, baseada em
`origin/main` no momento da criação do worktree.
