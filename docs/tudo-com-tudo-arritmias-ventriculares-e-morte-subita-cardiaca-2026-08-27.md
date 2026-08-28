# Tudo com Tudo — novo verbete-hub de Arritmias ventriculares e morte súbita cardíaca (geral) — 27/08/2026

## Lacuna identificada

Auditoria de **cobertura real** (documentos efetivamente ligados em
`related_document_slugs` de qualquer hub, não presumida por existência de
hub principal) confirmou que não havia hub geral de **arritmias
ventriculares e morte súbita cardíaca**. `content/Arritmias/` tinha 54
documentos, apenas 1 coberto. Após subtrair os clusters já consumidos
pelos hubs em PR aberto `taquicardia-supraventricular` (PR #581) e
`canalopatias-cardiacas-hereditarias` (PR #585), restava um cluster
coerente de arritmias ventriculares/cardiomiopatia arritmogênica/morte
súbita sem nenhum verbete. Este é o vigésimo ciclo Tudo com Tudo do dia,
após endocardite infecciosa (PR #553), pericardite (PR #554), hipertensão
pulmonar (PR #555), síncope (PR #560), valvopatias (PR #563),
cardiomiopatias (PR #565), miocardite (PR #568), dislipidemia (PR #570),
diabetes mellitus tipo 2 (PR #572), tromboembolismo venoso (PR #574),
doença arterial periférica de membros (PR #578), doença da aorta (PR #580),
taquicardia supraventricular (PR #581), canalopatias cardíacas
hereditárias (PR #585), choque cardiogênico (PR #590), insuficiência
cardíaca avançada (PR #594), cardiopatia congênita do adulto (PR #596),
hipertensão resistente e refratária (PR #597) e dispositivos cardíacos
implantáveis (PR #599).

## Descoberta relevante do ciclo: hubs fantasma

A mesma metodologia de auditoria por cobertura real revelou que **quatro
hubs gerais já existentes e publicados** — `fibrilacao-atrial`,
`insuficiencia-cardiaca`, `sindrome-coronariana-aguda`/`sindrome-coronariana-cronica`,
`hipertensao-arterial-sistemica` — têm apenas 2 a 7 `related_document_slugs`
cada, apesar de suas pastas terem 65 a 97 documentos. Juntos, representam
cerca de 250 documentos publicados e não conectados nas condições mais
prevalentes do corpus. Esse achado **não é elegível para novo verbete**
(colidiria com slug existente) e representa enriquecimento de registros
já `revisado`/publicados — reportado ao Rafael separadamente, sem edição
unilateral.

## Escopo e cuidado com duplicação

Novo slug `arritmias-ventriculares-e-morte-subita-cardiaca`, área `geral`.
Cobre TV idiopática, TV na cardiopatia estrutural, cardiomiopatia
arritmogênica, RIVA e torsades de pointes/QT longo adquirido — distinto de
canalopatias hereditárias primárias e de taquicardia supraventricular,
ambos com hub próprio.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (2817 caracteres),
   `presentation` (9 itens), `diagnostic_approach` (estruturado em 5
   subtópicos: diferencial de QRS largo ESC 2019, RIVA vs. TV verdadeira,
   extrassístole frequente/cardiomiopatia induzida, torsades/escore de
   Tisdale, estratificação etiológica/estrutural), `differentials` (7),
   `tests` (7), `red_flags` (8), `source_refs` (23).
2. **Tratamento e fluxos** — `treatment_summary` (3103 caracteres,
   cobrindo manejo agudo de torsades, ablação de TV idiopática/estrutural,
   radioablação estereotáxica, princípio CAST/SWORD), `ambulatory_flow`
   (8), `emergency_flow` (6), `monitoring` (7), `assistant_questions` (8),
   `assistant_rules` (8, com 2 regras de prioridade máxima 100: TV
   instável/torsades e tempestade elétrica).
3. **Populações especiais e conexões** — `special_populations` (6:
   cardiomiopatia arritmogênica com restrição de exercício, Chagas com
   escore de Rassi, atleta com extrassistolia, mulher com QT longo
   adquirido, gestante/puérpera, tempestade elétrica), `related_document_slugs`
   (26), `patient_material_slug` (null — nenhum material genuinamente
   geral encontrado).

## Correção feita na montagem

Um documento (`parada-cardiorrespiratoria-no-adulto-suporte-avancado-sbc-2019`),
proposto pelo agente de pesquisa 3 entre os 9 documentos adicionais por
busca ampla, foi **removido** por já pertencer integralmente ao hub
existente `parada-cardiorrespiratoria-e-morte-subita-abortada` —
sobreposição não detectada pelo agente e identificada apenas na montagem,
verificando os `related_document_slugs` completos desse hub-irmão.

Nenhuma dose de fármaco foi incluída em nenhum campo — verificado
programaticamente. Estrutura de perguntas e regras validada com o motor
de regras real (`clinical_rule_engine`) antes da montagem.

## Fontes primárias

23 referências, todas com PMID/DOI verificado via NCBI E-utilities,
incluindo diretriz ESC 2022 de arritmia ventricular/morte súbita, diretriz
ESC 2019 de taquicardia de QRS largo, critérios de Padua 2020 para
cardiomiopatia arritmogênica, CAST e SWORD.

## Relações Tudo com Tudo

26 `related_document_slugs`: 18 do núcleo pré-selecionado mais 9
encontrados por busca ampla (cardiomiopatia arritmogênica/critérios de
Padua, CDI fundamentos, escore de Rassi, CDI extravascular, morte
súbita/extrassistolia/cardiomiopatia arritmogênica no atleta, decisão
compartilhada de retorno ao esporte), menos 1 removido por sobreposição
com o hub de PCR. Todos verificados individualmente fora de
Farmacologia/Calculadoras/Exames, sem sobreposição com os hubs
`canalopatias-cardiacas-hereditarias`, `taquicardia-supraventricular` e
`parada-cardiorrespiratoria-e-morte-subita-abortada`.

## Coordenação com Codex

Nenhum PR aberto cria o slug `arritmias-ventriculares-e-morte-subita-cardiaca`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não é publicado até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug` deliberadamente omitido — nenhum material
  genuinamente geral sobre arritmia ventricular/morte súbita existe hoje
  no corpus.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  `total_records: 9497`, `total_files: 2193` (nenhum documento novo criado).
- `backend/tests/test_tudo_com_tudo_arritmias_ventriculares_e_morte_subita_cardiaca.py`:
  9 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py`: passando com
  `arritmias-ventriculares-e-morte-subita-cardiaca` na allowlist
  `PENDENTES_LOTES_TUDO_COM_TUDO`.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-20-20260827`, baseada em `origin/main`
sem drift no momento do commit.
