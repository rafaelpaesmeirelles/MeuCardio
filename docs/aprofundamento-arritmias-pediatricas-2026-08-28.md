# Aprofundamento Tudo com Tudo — Arritmias pediátricas — 28/08/2026

## Contexto

Oitavo lote de aprofundamento do dia (após `doenca-coronariana-idoso`,
PR #603; `valva-aortica-bicuspide-pediatrica`, PR #604; `hipotensao-
ortostatica-no-idoso`, PR #606; `sopros-na-infancia`, PR #608;
`hipertensao-arterial-pediatrica`, PR #609; `dor-toracica-pediatrica`,
PR #610; `dislipidemias-pediatricas`, PR #611). A ficha `arritmias-
pediatricas` (área `cardiopediatria`, categoria `arritmia`,
`prevalence_rank: 30`) — hub geral de arritmia pediátrica pós-natal,
distinto do hub adulto `taquicardia-supraventricular` (PR #581) e das
fichas de arritmia fetal/gestante (PR #564) — tinha apenas metadados de
catalogação e 3 `related_document_slugs`.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (TSV incidência
   1:4.500 no 1º ano de vida, recorrência 22% geral vs. 68% em WPW; JET
   pós-operatória em 6,0% das cirurgias cardíacas congênitas; faixas de
   FC normal por idade, Fleming et al. Lancet 2011), `presentation` (10
   itens), `diagnostic_approach` (6 subtópicos: ECG inicial, faixas
   normais de FC, TSV vs. sinusal, reconhecimento de JET, indicação de
   Holter, indicação de EEF), `differentials` (8), `tests` (8),
   `red_flags` (8), `source_refs` (10).
2. **Tratamento e assistente** — `treatment_summary` (manobras vagais,
   cardioversão elétrica/química qualitativa, manejo específico de JET
   com hipotermia leve e marca-passo atrial, critérios de ablação por
   peso corporal, indicação de marca-passo definitivo em BAV), fluxos
   ambulatorial (8) e emergência (7), monitoramento (6), assistente
   clínico determinístico (11 perguntas, 10 regras, priority 95 para
   instabilidade hemodinâmica).
3. **Populações especiais e conexões** — `special_populations` (6:
   TSV no recém-nascido, JET pós-operatória, cardiopatia estrutural com
   via acessória, atleta com bradicardia, canalopatia familiar, BAV
   congênito por anti-Ro materno), `related_document_slugs` (27
   propostos, o maior conjunto entre os aprofundamentos pontuais/
   completos do dia).

## Correções e decisões feitas na montagem

- Todos os 27 `related_document_slugs` verificados individualmente com
  conjunto amplo de termos (arritmia, bradicardia, taquicardia, bloqueio
  atrioventricular, flutter, extrassístole, canalopatia, Brugada, QT
  longo, catecolaminérgica, fibrilação atrial) — evita falso-negativo em
  documentos legitimamente sobre sub-tipos específicos de arritmia que
  não usam a palavra "arritmia" literalmente.
- **10 dos 27 documentos compartilhados** com fichas mais específicas já
  publicadas: `sincope-pediatrica` e `canalopatias-pediatricas` (QT
  longo, CPVT, Brugada, morte súbita em atleta jovem, cardiomiopatia
  arritmogênica), `cardiomiopatias-pediatricas` (cardiomiopatia
  arritmogênica), e as 4 fichas de arritmia fetal (`taquicardia-
  supraventricular-fetal`, `bloqueio-atrioventricular-fetal`, `flutter-
  atrial-fetal`, `extrassistoles-fetais`, `hidropisia-fetal-
  cardiovascular`) — todos mantidos por serem genuína e centralmente
  sobre arritmia/canalopatia pediátrica, mesmo padrão de pertencimento
  múltiplo já usado em ciclos anteriores.
- **Documentos de BAV excluídos por decisão conservadora**: o agente de
  pesquisa identificou documentos de bloqueio atrioventricular congênito
  e pós-operatório clinicamente centrais e alinhados com a população
  especial de BAV/anti-Ro proposta, mas nenhum usa a palavra "arritmia"
  ou "bradiarritmia" em nenhum ponto do texto (só "bloqueio AV" e
  "bradicardia"). Pela regra estrita de menção textual direta usada em
  todo o dia, foram **excluídos** — decisão sinalizada explicitamente
  para o Rafael avaliar se o critério deveria ser relaxado nesse caso
  específico (a `special_populations` já discute BAV/anti-Ro mesmo sem
  o link direto).

Nenhuma dose de fármaco em nenhum campo — verificado programaticamente.
Nenhuma energia de cardioversão/desfibrilação em J/kg citada (parâmetro
de dispositivo, deliberadamente mantido fora do conteúdo, com checagem
de regex dedicada). Estrutura de perguntas e regras validada com o motor
de regras real antes da montagem.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

10 referências novas, com PMID verificado, incluindo a diretriz AHA/AAP
2025 de suporte avançado de vida pediátrico (Lasa et al., Circulation),
o estudo populacional eslovaco de TSV neonatal/infantil (Bjeloševič et
al. 2020) e o registro multicêntrico de JET pós-operatória (Kim et al.,
Annals of Thoracic Surgery 2024).

## Coordenação com Codex

Nenhum dos 32 PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `arritmias-pediatricas`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco nem energia de cardioversão/desfibrilação é
  citada.
- `patient_material_slug` (já existente, `arritmias-pediatricas`)
  reconfirmado.
- Documentos de BAV excluídos por decisão conservadora — ver acima,
  candidatos a reavaliação em ciclo futuro caso o Rafael julgue o
  critério excessivamente estrito.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_arritmias_pediatricas.py`: 12
  testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist unificada).
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-arritmias-pediatricas-20260828`, rebaseada em
`origin/main` sem drift no momento do commit (um commit intermediário
não relacionado — `de72424f`, correção de loop de redirecionamento no
frontend — absorvido pelo rebase sem conflito).
