# Verbete novo — Cardiotoxicidade por cocaína e estimulantes — 29/08/2026

## Contexto

Reconhecimento sistêmico identificou que **cardiotoxicidade por cocaína e
estimulantes** não tinha ficha própria em `doencas/metadados.json`, apesar de
corpus rico e já existente em `content/Geral/`, `content/Terapia_intensiva/` e
`content/Saúde_mental_e_cardiologia/` (mecanismo do vasoespasmo
alfa-adrenérgico, ensaio randomizado de Lange 1990, protocolo de observação de
Weber 2003, revisão de manejo agudo de Richards 2016, mecanismo
eletrofisiológico de bloqueio de canal de sódio/potássio de O'Leary/Hancox
2010 e manejo da arritmia de Hoffman 2010, infarto na primeira hora e
cardiomiopatia por metanfetamina de Mittleman 1999/Schürer 2017/Sliman
2016/Kevil 2019, e estimulantes prescritos no TDAH de Habel 2011/Holt 2024).

Criado via `doencas/fragmentos/cardiotoxicidade-por-cocaina-e-estimulantes.json`
para minimizar colisão com outras frentes de produção concorrentes.

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: risco de infarto ~24x maior na primeira hora após uso de
  cocaína (Mittleman 1999), protocolo de observação de 9-12h com risco de
  morte cardiovascular em 30 dias próximo de zero (Weber 2003), padrão de
  cardiomiopatia por metanfetamina com recuperação condicionada à abstinência
  (Schürer 2017, Sliman 2016), e o sinal de risco cardiovascular de longo
  prazo (AVC, IC) em uso contínuo de estimulante prescrito no TDAH (Holt
  2024), sem sinal em uso agudo/recente (Habel 2011).
- `presentation` (10), `diagnostic_approach` (fluxo padrão de SCA + leitura
  ativa de QRS/QTc para bloqueio iônico + distinção intoxicação aguda vs. uso
  recente sem intoxicação + ecocardiograma para padrão estrutural crônico),
  `differentials` (10), `tests` (9), `red_flags` (9).
- `treatment_summary`: benzodiazepínico como primeira linha na intoxicação
  aguda, nitrato/bloqueador de canal de cálcio para vasoespasmo, **a
  contraindicação relativa a betabloqueador não seletivo/puro ISOLADO na fase
  aguda** (vasoespasmo sem oposição alfa-adrenérgica, demonstrado em ensaio
  randomizado), beta/alfa-bloqueador combinado como exceção mais documentada
  dentro da classe, bicarbonato de sódio para QRS alargado evitando
  antiarrítmico IA/IC, e manejo padrão de IC com betabloqueador de manutenção
  fora da fase aguda em cardiomiopatia crônica — tudo qualitativo, sem doses.
- `ambulatory_flow` (9), `emergency_flow` (8), `monitoring` (7).
- `special_populations` (6): uso crônico de metanfetamina, cocaetileno
  (álcool + cocaína), TDAH com estimulante prescrito, paciente jovem sem
  fatores de risco clássicos, IC associada a estimulante, uso de drogas
  injetáveis com suspeita de endocardite (cenário distinto, não confundir).
- `assistant_questions` (16), `assistant_rules` (13, priorities 90-100 para
  instabilidade hemodinâmica, QRS alargado, betabloqueador puro na
  intoxicação aguda, supra de ST e persistência de sintomas).
- `related_document_slugs` (6, do zero).

## A regra terapêutica central (item obrigatório da missão)

A contraindicação relativa a **betabloqueador NÃO seletivo/puro isolado** na
intoxicação aguda por cocaína/estimulante (vasoespasmo coronariano sem
oposição alfa-adrenérgica) foi capturada como regra qualitativa em três
lugares, sem nenhuma dose de fármaco:

1. `red_flags`: "Uso de betabloqueador não seletivo/puro isolado durante
   intoxicação aguda... pode piorar o vasoespasmo coronariano...".
2. `treatment_summary`: explicação do mecanismo (bloqueio beta sem bloqueio
   alfa deixa a vasoconstricção sem oposição), com a ressalva de que a
   restrição é **circunscrita à fase aguda de intoxicação**, não ao
   tratamento de manutenção fora desse episódio.
3. `assistant_rules` (regra `betabloqueador_puro_contraindicado_na_intoxicacao_
   aguda`, priority 98): dispara quando há consideração de betabloqueador
   puro **e** sinais de intoxicação aguda em curso, com `red_flags`,
   `opposing` e `messages` — nunca `risk` acima do necessário nem doses.

Testada explicitamente em
`test_regra_contraindicacao_relativa_ao_betabloqueador_puro_no_agudo`.

## Verificação de citações

Todos os **17 PMIDs** desta rodada foram verificados individualmente via NCBI
e-utils (`esummary`) antes da montagem — título, periódico e ano conferidos
contra os `source_refs` dos seis documentos de origem, todos batendo:
Lange 1989 (PMID 2573838), Lange 1990 (1971166), Weber 2003 (12571258),
Richards 2016 (26919414), Anderson/ACCF-AHA 2012 (23639841), StatPearls
Cocaine Toxicity (28613695, fonte terciária), McCord/AHA 2008 (18347214),
O'Leary & Hancox 2010 (20573078), Hoffman 2010 (20573080), Mittleman 1999
(10351966), Schürer 2017 (28571597), Sliman 2016 (26661075), Kevil 2019
(31433698), Habel 2011 (22161946), Holt 2024 (38719367), Amsterdam/AHA-ACC
2014 (25260718), Lo et al. meta-análise 2019 (30562494).

## Verificações feitas na montagem

- As 6 fontes mapeadas (exceto a de Farmacologia) foram lidas **por
  completo** e verificadas individualmente como discussão central do tema —
  nenhuma tangencial.
- **Excluído por regra o 7º candidato mapeado pelo reconhecimento prévio**:
  `content/Farmacologia/cardiotoxicidade-da-cocaina-reavaliacao-do-
  betabloqueador-e-miocardiopatia-cronica-2023-2024.md` resolve fisicamente
  para `content/Farmacologia/`, pasta fora do escopo permitido para
  `related_document_slugs` pela regra Tudo com Tudo — apesar de
  tematicamente muito relevante (reavaliação 2018-2024 da contraindicação ao
  betabloqueador com o estudo observacional RUTI-Cocaine, atualização AHA
  2023 sobre intoxicação, e miocardiopatia crônica com dado quantitativo da
  Alawoè 2024). Verificação feita por mim, lendo o documento completo antes
  de excluí-lo. O conteúdo qualitativo essencial desse documento (a
  contraindicação relativa ao betabloqueador puro isolado no agudo, a
  reversibilidade da cardiomiopatia crônica com abstinência, e a manutenção
  de betabloqueador fora da fase aguda) já está coberto de forma equivalente
  pelos 6 documentos válidos e por literatura verificada independentemente —
  nenhum PMID exclusivo do documento excluído precisou ser usado.
- `patient_material_slug`: nenhuma correspondência em
  `material-paciente/metadados.json` para cocaína/estimulantes, mantido
  `null` — documentado no `review_note` e testado.
- Nenhum overlap de `related_document_slugs` com outras fichas de doenças já
  compostas (verificado programaticamente contra todos os 118 registros de
  `doencas/metadados.json`, incluindo `sindrome-coronariana-aguda` e
  `cardiomiopatias`, que não referenciam nenhum dos 6 slugs escolhidos).

## Decisão de category

`category='toxicologia_cardiovascular'` é categoria **nova**. Categorias
existentes avaliadas e descartadas:

- `toxicidade_por_tratamento`: semanticamente específica para toxicidade
  **iatrogênica de tratamento médico** (ex.: `cardiotoxicidade-por-
  antraciclinas`), não para toxicidade por substância recreativa/ilícita —
  usá-la aqui distorceria o sentido da categoria para quem a lê depois.
- `emergencia_cardiovascular`: captura só a faceta aguda (única ficha
  atualmente na categoria é `choque-cardiogenico`), mas este verbete cobre
  igualmente a cardiomiopatia crônica reversível por metanfetamina/cocaína e
  o uso terapêutico prescrito de estimulantes no TDAH, que não são
  emergência — forçaria a categoria a cobrir mais do que seu nome sugere.
- `doenca_coronariana`: cobre só o eixo isquêmico/vasoespasmo, não a
  arritmia por bloqueio de canal de sódio nem a cardiomiopatia crônica.

Segue o precedente aberto por `disturbio_de_conducao` (verbete
`bloqueio-atrioventricular`, criado horas antes nesta mesma rodada, 29/08/2026):
introduzir categoria nova quando nenhuma existente encaixa sem forçar o
sentido.

Nenhuma dose de fármaco em nenhum campo — confirmado por varredura de regex
(`mg`, `mg/kg`, `mcg`, `j/kg`) sobre o registro serializado inteiro, sem
nenhum resultado.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até revisão
  humana.
- Gate `test_canonical_content_review_status.py` **falha intencionalmente**
  em `test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_
  para_rc` (política vigente desde 28/08/2026: qualquer `review_status !=
  revisado` quebra esse gate específico, sem mecanismo de allowlist para
  pendência declarada — só para exceções já `revisado` com pendência
  documentada). Isso é esperado e correto, não foi contornado. A allowlist
  em `PENDENTES_LOTES_TUDO_COM_TUDO` foi atualizada apenas para satisfazer
  `test_disease_fragments_canonical.py` (que aceita pendência declarada
  independentemente do status), replicando exatamente o padrão já usado nos
  verbetes `cardiomiopatia-hipertrofica`, `bloqueio-atrioventricular` e
  `estenose-mitral` desta mesma rodada de produção.
- `category` nova (`toxicologia_cardiovascular`) — vale confirmação
  editorial de que o nome é adequado à taxonomia do sistema.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `SpecialtyDisease.related_document_slugs`
  resolvido 1099/1099 (após inclusão desta ficha); `review_status.pendente_
  revisao: 1` (só esta ficha).
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_novo_verbete_cardiotoxicidade_por_cocaina_e_
  estimulantes.py`: 12 testes, todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes, todos
  passando.
- `backend/tests/test_canonical_content_review_status.py`: 2 passando, **1
  falha esperada e documentada** acima.
- `app.main` importa sem erro.
- Sem drift contra `origin/main` no momento da abertura da PR.
