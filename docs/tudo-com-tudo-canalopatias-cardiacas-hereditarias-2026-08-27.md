# Tudo com Tudo — novo verbete-hub de Canalopatias cardíacas hereditárias (geral) — 27/08/2026

## Lacuna identificada

Auditoria do corpus confirmou que não havia nenhum verbete-hub geral de
**canalopatias cardíacas hereditárias do adulto** no Guia de Doenças —
apenas `canalopatias-pediatricas` (área cardiopediatria) e
`qt-longo-terapia-oncologica` (forma ADQUIRIDA por quimioterapia, entidade
distinta). `content/Arritmias/` e pastas adjacentes (Cardiologia do
Esporte, Comunicação clínica, Gravidez, Geral) reuniam 19 documentos
coerentes sobre QT longo congênito, síndrome de Brugada, QT curto, CPVT,
síndrome de Andersen-Tawil e fibrilação ventricular idiopática. Este é o
décimo quarto ciclo Tudo com Tudo do dia, após endocardite infecciosa
(PR #553), pericardite (PR #554), hipertensão pulmonar (PR #555), síncope
(PR #560), valvopatias (PR #563), cardiomiopatias (PR #565), miocardite
(PR #568), dislipidemia (PR #570), diabetes mellitus tipo 2 (PR #572),
tromboembolismo venoso (PR #574), doença arterial periférica de membros
(PR #578), doença da aorta (PR #580) e taquicardia supraventricular
(PR #581).

## Escopo e cuidado com duplicação

Novo slug `canalopatias-cardiacas-hereditarias`, área `geral`. Nenhum dos
5 documentos pediátricos-específicos do hub-irmão `canalopatias-pediatricas`
foi duplicado — verificação programática dedicada
(`test_nao_duplica_documentos_pediatricos_especificos_do_hub_irmao`). O
documento `canalopatias-sindrome-do-qt-longo-e-sindrome-de-brugada-diagnostico-e-manejo`
está deliberadamente vinculado também ao hub pediátrico — inclusão dupla
legítima, pois é documento de diagnóstico/manejo geral sem recorte etário
no título, análogo ao caso do documento VIBORG compartilhado entre os hubs
de aorta e DAP de membros em ciclo anterior.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology`, `presentation` (10
   itens), `diagnostic_approach` (estruturado em dict: critérios de
   Schwartz para QT longo, padrão eletrocardiográfico de Brugada tipo 1
   espontâneo vs. induzido, critérios diagnósticos de CPVT, avaliação
   genética e rastreio familiar em cascata, investigação de QT
   curto/Andersen-Tawil/FV idiopática), `differentials` (7), `tests` (8),
   `red_flags` (8), `source_refs` (17).
2. **Tratamento e fluxos** — `treatment_summary` (4146 caracteres,
   cobrindo betabloqueador como primeira linha em QT longo/CPVT, evitar
   QT-prolongadores, CDI por estratificação de risco, ablação do substrato
   epicárdico em Brugada refratário, manejo de tempestade elétrica, e
   decisão sobre participação esportiva), `ambulatory_flow` (7),
   `emergency_flow` (5), `monitoring` (7), `assistant_questions` (9),
   `assistant_rules` (9, com 2 regras de prioridade máxima 100: parada
   cardíaca abortada e choque de CDI/tempestade elétrica).
3. **Populações especiais e conexões** — `special_populations` (5:
   gestante/puérpera, atleta competitivo, criança/adolescente com
   referência ao hub-irmão, familiar assintomático/rastreio em cascata, QT
   longo adquirido por quimioterapia com referência ao hub próprio),
   `related_document_slugs` (19), `patient_material_slug`.

Nenhuma dose de fármaco foi incluída em nenhum campo — verificado
programaticamente por varredura de padrões de dose (aprendizado do ciclo
anterior de TSV, aplicado preventivamente aqui desde o início dos prompts
dos agentes).

## Correção de PMID feita pelo agente de pesquisa 1

O agente identificou uma divergência: uma referência já usada no corpus
citava PMID 24011539 para o consenso HRS/EHRA/APHRS 2013 na Europace, mas
esse PMID na verdade pertence à publicação irmã (Heart Rhythm, volume/
páginas diferentes). O PMID correto da versão Europace é 23994779 —
verificado e usado.

## Fontes primárias

17 referências, todas com PMID/DOI verificado via NCBI E-utilities,
incluindo: Schwartz et al. 1993 (critérios de QT longo) — PMID 8339437;
Zeppenfeld et al. 2022, ESC Guidelines — PMID 36017572; Mazzanti et al.
2014, coorte de QT curto — PMID 24291113; Kannankeril et al. 2017, ensaio
randomizado de flecainida em CPVT — PMID 28492868; Haïssaguerre et al.
2008, NEJM (repolarização precoce) — PMID 18463377; Krahn et al. 2009,
registro CASPER — PMID 19597050; Sieira et al. 2017, escore de risco de
Brugada — PMID 28379344.

## Relações Tudo com Tudo

19 `related_document_slugs`, todos verificados individualmente fora de
Farmacologia/Calculadoras/Exames, sem sobreposição com os documentos
pediátricos-específicos do hub-irmão.

`patient_material_slug`: `qt-longo-o-que-significa-e-cuidados-com-medicamentos`
(confirmado existente em `material-paciente/metadados.json`).

## Coordenação com Codex

Nenhum dos 200+ PRs abertos verificados cria o slug
`canalopatias-cardiacas-hereditarias`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não é publicado até
  revisão humana.
- Nenhuma dose de fármaco é citada — verificado programaticamente.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  `total_records: 9497`, `total_files: 2193` (nenhum documento novo criado).
- `backend/tests/test_tudo_com_tudo_canalopatias_cardiacas_hereditarias.py`:
  9 testes, todos passando (inclui varredura de dose e não-duplicação com
  o hub-irmão pediátrico).
- `backend/tests/test_canonical_content_review_status.py`: passando com
  `canalopatias-cardiacas-hereditarias` na allowlist
  `PENDENTES_LOTES_TUDO_COM_TUDO`.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-14-20260827`, baseada em `origin/main`
sem drift no momento do commit.
