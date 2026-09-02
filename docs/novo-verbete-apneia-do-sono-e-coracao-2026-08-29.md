# Verbete novo — Apneia do sono e doença cardiovascular — 29/08/2026

## Contexto

Rodada de reconhecimento sistêmico identificou que **apneia do sono como
fator de risco/comorbidade cardiovascular** não tinha ficha própria em
`doencas/metadados.json`, apesar de corpus já rico e existente (7
documentos dedicados: CPAP e hipertensão resistente — HIPARCO/SAVE, CPAP e
recorrência de fibrilação atrial pós-ablação, SERVE-HF, respiração de
Cheyne-Stokes na ICFEr, STOP-BANG pré-operatório em cirurgia cardíaca,
apneia obstrutiva no idoso cardiopata, estimulação transvenosa do nervo
frênico/sistema remedē).

Criado via `doencas/fragmentos/apneia-do-sono-e-coracao.json` — **não**
via edição direta de `doencas/metadados.json` — para minimizar colisão
com outras frentes de produção concorrentes.

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: AOS clinicamente relevante (IAH ≥15/h) em ~10-17% dos
  homens e 3-9% das mulheres de meia-idade, associação bidirecional com
  hipertensão resistente, FA e IC; respiração de Cheyne-Stokes em 30-40%
  da ICFEr avançada, marcador prognóstico independente.
- `presentation` (13), `diagnostic_approach` (rastreio STOP-BANG/Epworth
  seguido de confirmação por polissonografia/poligrafia, distinção
  obstrutiva vs. central por esforço toracoabdominal), `differentials`
  (9), `tests` (9), `red_flags` (9).
- `treatment_summary`: distingue AOS (CPAP primeira linha por alívio
  sintomático, sem redução comprovada de desfecho duro — SAVE) de apneia
  central/Cheyne-Stokes na ICFEr (servoventilação adaptativa
  **contraindicada** — SERVE-HF, priorizar otimização de IC), STOP-BANG
  no pré-operatório, sem doses.
- `ambulatory_flow` (11), `emergency_flow` (6), `monitoring` (8).
- `special_populations` (7).
- `assistant_questions` (16), `assistant_rules` (10, priority 95 para
  uso de servoventilação adaptativa em apneia central + ICFEr).
- `related_document_slugs` (7, do zero).
- `patient_material_slug` preenchido: `apneia-do-sono-e-o-coracao`.

## Verificação de citações

Todos os 9 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem, incluindo os dois ensaios pivotais que definem
a conduta (SAVE, NEJM 2016, PMID 27571048 — CPAP não reduz desfecho
cardiovascular duro; SERVE-HF, NEJM 2015, PMID 26323938 — servoventilação
adaptativa aumenta mortalidade em ICFEr com apneia central), o ensaio
HIPARCO de CPAP em hipertensão resistente (JAMA 2013, PMID 24327037), o
estudo pivotal de estimulação transvenosa do nervo frênico (Costanzo et
al., Lancet 2016, PMID 27598679), a validação do STOP-BANG (Chung et al.,
Anesthesiology 2008, PMID 18431116), a escala de Epworth (Johns, Sleep
1991, PMID 1798888), o estudo de valor prognóstico da respiração de
Cheyne-Stokes (Lanfranchi et al., Circulation 1999, PMID 10086966), a
Sleep Heart Health Study (Gottlieb et al., Circulation 2010, PMID
20625114) e a metanálise de duração do sono e desfechos cardiovasculares
(Cappuccio et al., Eur Heart J 2011, PMID 21300732).

## Verificações feitas na montagem

- Os 7 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema — todos lidos por completo antes da inclusão (leitura direta
  do arquivo `.md` de cada um, confirmando discussão central de apneia
  do sono/CPAP/Cheyne-Stokes em cada documento, e frontmatter confirmando
  pasta de destino fora de `content/Farmacologia`, `content/Calculadoras`
  e `content/Exames`):
  - `apneia-obstrutiva-do-sono-e-hipertensao-quanto-o-cpap-realmente-baixa-a-pressao`
    (`content/Hipertensão/`)
  - `apneia-obstrutiva-do-sono-e-recorrencia-de-fibrilacao-atrial-apos-ablacao-o-que-o-cpap-realmente-muda`
    (`content/Fibrilação_atrial/`)
  - `servoventilacao-adaptativa-na-apneia-central-com-icfer-o-ensaio-serve-hf`
    (`content/Insuficiência_cardíaca/`)
  - `respiracao-de-cheyne-stokes-na-icfer-marcador-prognostico-independente`
    (`content/Insuficiência_cardíaca/`)
  - `aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca`
    (`content/Cardiologia_do_Esporte_e_do_Exercício/`)
  - `apneia-obstrutiva-do-sono-no-idoso-cardiopata-prevalencia-risco-modificado-pela-idade-e-limites-do-cpap`
    (`content/Cardiologia_geriátrica/`)
  - `estimulacao-transvenosa-do-nervo-frenico-na-apneia-central-do-sono-sistema-remede`
    (`content/Dispositivos/`)
  Nenhum dos 7 candidatos precisou ser descartado — todos discutem
  centralmente o tema e resolvem para pastas de documento narrativo.
- `patient_material_slug` confirmado por correspondência exata em
  `material-paciente/metadados.json` (`apneia-do-sono-e-o-coracao`).
- `category='prevencao_e_risco'` já existe na convenção do corpus (área
  geral) — não foi necessário criar categoria nova.
- Overlaps legítimos e pré-existentes documentados no teste dedicado
  (`DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS`), verificados
  programaticamente contra todo o catálogo de 119 doenças:
  - `apneia-obstrutiva-do-sono-no-idoso-cardiopata-prevalencia-risco-modificado-pela-idade-e-limites-do-cpap`
    também é `related_document_slug` de `doenca-coronariana-idoso`.
  - `apneia-obstrutiva-do-sono-e-hipertensao-quanto-o-cpap-realmente-baixa-a-pressao`
    também é `related_document_slug` de `hipertensao-resistente-e-refrataria`.
  Nenhuma outra sobreposição encontrada.
- `assistant_rules` usa apenas operadores válidos (`truthy`, `falsy`,
  `eq`, `neq`, `gte`, `contains` — nunca `includes`) e apenas chaves
  válidas em `add` (`risk`, `red_flags`, `opposing`, `messages`,
  `suggested_tests`, `missing_information`, `supporting`,
  `ambulatory_flow` — nunca `monitoring`), validado com
  `validate_question_definitions`/`validate_rule_definitions` de
  `app.services.clinical_rule_engine`. Todas as 16 perguntas usam a
  chave `label` (nenhuma usa `text`).

Nenhuma dose de fármaco em nenhum campo.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Gate `test_canonical_content_review_status.py::test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  falha intencionalmente (política vigente desde 28/08/2026: exige
  `revisado` em todos os registros canônicos, sem exceção via
  allowlist — `PENDENTES_LOTES_TUDO_COM_TUDO` só reconhece pendência com
  `status == "revisado"`, nunca `pendente_revisao`, portanto não existe
  mecanismo de bypass desse teste específico). A entrada adicionada a
  `PENDENTES_LOTES_TUDO_COM_TUDO["doencas/metadados.json"]` neste PR é
  usada exclusivamente por `test_disease_fragments_canonical.py`
  (allowlist compartilhada, ver comentário no próprio arquivo) e não
  afeta o resultado do teste acima.
- Nome do slug do fragmento (`apneia-do-sono-e-coracao`) e da branch
  (`claude/novo-verbete-apneia-sono-e-coracao-20260829`) diferem
  ligeiramente na ordem das palavras — sem impacto técnico, apenas nota
  de rastreabilidade.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_novo_verbete_apneia_do_sono_e_coracao.py`: 12
  testes, todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes, todos
  passando.
- `backend/tests/test_canonical_content_review_status.py`: 3 testes — 1
  falha esperada e documentada acima
  (`test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`),
  2 passando.
- `app.main` importa sem erro.
- Total: 18 testes executados, 17 passando, 1 falha esperada e
  documentada.

## Branch e PR

Branch `claude/novo-verbete-apneia-sono-e-coracao-20260829`, rebaseada
sobre `origin/main` sem conflitos no momento do commit (drift de 8
commits não relacionados, fora do escopo de `doencas/` e dos testes
editados).
