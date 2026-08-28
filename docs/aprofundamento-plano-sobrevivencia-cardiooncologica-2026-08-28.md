# Aprofundamento Tudo com Tudo — Plano de sobrevivência cardio-oncológica — 28/08/2026

## Contexto

Quadragésimo primeiro lote de conteúdo do dia. A ficha
`plano-sobrevivencia-cardiooncologica` (área `cardiooncologia`, categoria
`sobrevivencia`, subtype `seguimento_longo_prazo`, `prevalence_rank: 15`)
estava `completeness: basico`, só catalogação (1 `source_ref`: ESC 2022
Cardio-Oncology), zero campos clínicos, zero `related_document_slugs`.
Sexta e última ficha desbloqueada hoje pela reavaliação de escopo da PR
#551.

## Conteúdo produzido

- `epidemiology`: risco cardiovascular elevado a longo prazo em
  sobreviventes de câncer, latência de anos a décadas entre exposição e
  evento, lacuna estrutural no seguimento pós-alta oncológica.
- `presentation` (11), `diagnostic_approach` (3 eixos — registro
  estruturado de exposições prévias, estratificação de risco residual,
  cronograma de rastreio ajustado por perfil de exposição), `differentials`
  (7), `tests` (8), `red_flags` (8).
- `treatment_summary`: registro de exposições sem doses numéricas,
  estratificação de risco residual combinando exposição oncológica e
  fatores tradicionais, cronograma de rastreio, controle intensivo de
  fatores de risco tradicionais, educação sobre sintomas tardios, e
  divisão explícita de responsabilidades entre cardiologia/oncologia/
  atenção primária.
- `ambulatory_flow` (12), `emergency_flow` (6), `monitoring` (8).
- `special_populations` (6).
- `assistant_questions` (11), `assistant_rules` (10, priority 100 para
  dor torácica em sobrevivente exposto).
- `related_document_slugs` criado do zero: 6.

## Verificação de citações

Todos os 6 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem (Lyon et al. ESC Guidelines 2022, Armenian et
al. ASCO 2017, van Nimwegen et al. JAMA Intern Med 2015, Mulrooney et al.
Ann Intern Med 2016, Armstrong et al. NEJM 2016, Darby et al. NEJM 2013).

## Verificações feitas na montagem

- Os 6 `related_document_slugs` foram encontrados do zero (ficha não tinha
  nenhum vínculo pré-existente). Cada um verificado por mim, de forma
  independente do agente de pesquisa: confirmação de que o arquivo resolve
  fisicamente no repositório e leitura direta do frontmatter/corpo para
  confirmar centralidade ao tema de seguimento cardiovascular tardio/
  sobrevivência oncológica.
- Um dos 6 (`ic-os-mascc-2026-padrao-minimo-de-cuidado-cardiovascular-no-
  adulto-com-cancer`) é um documento de escopo mais amplo (toda a
  trajetória oncológica), mas contém um pilar de recomendação dedicado
  (item 5) e uma seção de "erros comuns" especificamente sobre
  planejamento de vigilância pós-tratamento e definição de responsável
  pela continuidade — avaliado como suficientemente central, distinto do
  padrão de "menção de passagem" que levou à rejeição da diretriz-mãe ESC
  2022 como candidato.
- 3 candidatos adicionais encontrados por busca textual ampla foram
  descartados por tratarem de prevenção durante o tratamento ativo (técnica
  de radioterapia com inspiração profunda sustentada) ou de monitorização
  aguda durante terapia anti-HER2 — não de seguimento pós-alta oncológica.
- `patient_material_slug` permanece vazio: existe um material
  `cardio-oncologia` já usado por outra ficha, mas seu conteúdo é voltado
  ao acompanhamento durante o tratamento ativo, não à vida após a alta —
  decisão consciente de não reutilizá-lo apenas por proximidade temática.
- **Overlap pré-existente e legítimo**: 5 dos 6 documentos também
  vinculados pela ficha irmã `efeitos-cardiovasculares-tardios-
  radioterapia` (foco em espectro fisiopatológico da doença cardíaca
  induzida por radiação, distinto do foco desta ficha em coordenação/
  processo de seguimento) — documentado no teste dedicado. Overlaps
  pontuais adicionais com `cardiotoxicidade-por-antraciclinas`,
  `doenca-pericardica-oncologia` e `pericardite`.

Nenhuma dose numérica de fármaco ou radioterapia em nenhum campo. Todas as
perguntas usam a chave `label` corretamente.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração. `source_refs`/`source_urls`
originais preservados e complementados (1 → 7).

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose numérica de fármaco/radioterapia é citada.
- Overlap significativo mas documentado com a ficha irmã de efeitos
  tardios de radioterapia — justificado pela proximidade clínica real dos
  dois temas.
- `patient_material_slug` permanece não preenchido por falta de
  correspondência temática confiável — decisão consciente de não
  reutilizar um material de encaixe parcial.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_plano_sobrevivencia_cardiooncologica.py`:
  12 testes, todos passando (1 correção durante desenvolvimento, para
  documentar overlap pré-existente descoberto pelo próprio teste).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando, 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-plano-sobrevivencia-cardiooncologica-20260828`,
rebaseada em `origin/main` após avanço da base durante o desenvolvimento
(commits de outras sessões, sem tocar `plano-sobrevivencia-
cardiooncologica`).
