# Aprofundamento Tudo com Tudo — Toxicidade cardiovascular por inibidores de proteassoma — 28/08/2026

## Contexto

Trigésimo sétimo lote de conteúdo do dia. A ficha
`cardiotoxicidade-inibidor-proteassoma` (área `cardiooncologia`,
categoria `terapia_alvo`, `prevalence_rank: 8`) estava
`completeness: basico`, só catalogação (1 `source_ref`: ESC 2022), zero
campos clínicos.

## Nota de transparência: desbloqueio tardio

Esta ficha esteve bloqueada o dia todo por suspeita de colisão com a
PR #551 aberta (junto com mais 5 fichas de cardiooncologia/
cardiogeriatria). Uma reavaliação no fim do dia confirmou que o escopo
real da PR #551 mudou ao longo do dia — ela não toca mais nenhuma
dessas 6 fichas hoje, tocando em vez disso outras 8 fichas diferentes.
Isso liberou `cardiotoxicidade-inibidor-proteassoma` e outras 5 fichas
para processamento (as demais ficam para lotes futuros).

## Conteúdo produzido

- `epidemiology`: incidência de eventos cardiovasculares com
  carfilzomibe (CVAE 18,1% qualquer grau, 8,2% grau ≥3) vs. bortezomibe
  (bem menor), mecanismo de disfunção endotelial e estresse oxidativo.
- `presentation` (10 itens).
- `diagnostic_approach` (3 subtópicos: avaliação basal pré-terapia,
  monitorização durante o tratamento, diferenciação de causa renal vs.
  cardíaca — relevante pela nefropatia frequente no mieloma múltiplo).
- `differentials` (7), `tests` (8), `red_flags` (7).
- `treatment_summary`: controle pressórico agressivo pré-ciclo como
  medida preventiva central (sem doses), manejo de IC guiado por
  diretriz, decisão compartilhada com hematologia sobre manter/pausar/
  trocar terapia, diferença de perfil carfilzomibe vs. bortezomibe,
  alerta explícito contra suspensão desnecessária de tratamento
  oncológico eficaz.
- `ambulatory_flow` (10), `emergency_flow` (7), `monitoring` (7).
- `special_populations` (6).
- `assistant_questions` (13), `assistant_rules` (9, priority 95-96
  para hipertensão grave/IC aguda/evento isquêmico).
- `related_document_slugs` (4, do zero).

## Verificação de citações

Todos os 7 PMIDs desta rodada foram verificados individualmente via
NCBI e-utils antes da montagem — todas as referências corretas quanto
a título/periódico/ano/volume/páginas, incluindo a metanálise de
Waxman et al. (JAMA Oncol 2018), a diretriz ESC 2022 de cardio-
oncologia, e estudos de segurança cardiovascular do carfilzomibe.

## Verificações feitas na montagem

- Os 4 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema no texto.
- **Candidato descartado por negação de conexão**: um 5º candidato
  (`amiloidose-cardiaca-por-cadeia-leve-al-e-o-ensaio-andromeda-
  daratumumabe`) foi proposto pelo agente de pesquisa, mas o trecho
  citado era, na verdade, parte da seção "Armadilhas" do próprio
  documento, avisando explicitamente para não confundir os dois temas
  — mesmo padrão de "negação de conexão" já identificado hoje em
  outros ciclos (extrassistoles-fetais). Verifiquei pessoalmente o
  documento fonte antes de excluir.
- **Overlap pré-existente e legítimo**: `hipertensao-induzida-por-
  terapia-antineoplasica-...` também vinculado por
  `hipertensao-por-inibidor-vegf`; `lista-de-quimioterapicos-de-risco-
  de-prolongamento-do-qt-...` também vinculado por
  `cardiotoxicidade-bcr-abl` — documentado no teste dedicado.

Nenhuma dose de fármaco em nenhum campo. Estrutura de perguntas e
regras validada com o motor de regras real — todas usam a chave
`label` corretamente (bug de `text`/`label` corrigido mais cedo hoje,
prevenido desde o início neste lote).

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `prevalence_rank` originais
preservados sem alteração.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap parcial mas documentado com 2 fichas do mesmo tema
  (cardiotoxicidade oncológica).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_cardiotoxicidade_inibidor_proteassoma.py`:
  11 testes, todos passando (1 correção durante desenvolvimento, para
  documentar overlap pré-existente descoberto pelo próprio teste).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando, 6 testes.
- `app.main` importa sem erro.
- Total: 17 testes executados, 17 passando.

## Branch e PR

Branch `claude/aprofundar-cardiotoxicidade-inibidor-proteassoma-20260828`,
baseada em `origin/main` sem drift no momento do commit.
