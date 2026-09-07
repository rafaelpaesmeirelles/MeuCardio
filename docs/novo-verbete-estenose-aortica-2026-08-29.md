# Verbete novo — Estenose aórtica — 29/08/2026

## Contexto

O Guia de Doenças já tinha a ficha `estenose-aortica-tavi-idoso`
(área `cardiogeriatria`), explicitamente geriátrica — Heart Team,
fragilidade, cognição e futilidade no idoso —, mas não tinha uma ficha
geral de **estenose aórtica** cobrindo diagnóstico, gravidade e decisão
de intervenção em todas as idades. A pasta `content/Valvopatias/` já
tinha corpus rico e específico sobre o tema (diretrizes ESC/EACTS
2021/2025, três fluxogramas de decisão, metanálise de 4 RCTs de
intervenção precoce e dois estudos de durabilidade valvar de longuíssimo
prazo), mas nenhuma ficha do Guia de Doenças cobria o espectro geral.

Criado via `doencas/fragmentos/estenose-aortica.json` — **não** via
edição direta de `doencas/metadados.json` — para minimizar colisão com
outras frentes de produção concorrentes (mecanismo já usado por outros
verbetes-hub recentes do sistema; nesta mesma sessão havia dezenas de
outras frentes rodando em paralelo no mesmo checkout).

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: prevalência crescente com a idade, calcificação
  degenerativa senil em idosos versus degeneração de valva bicúspide em
  adultos jovens (1-2% da população, principal causa de EA abaixo de 65
  anos), etiologia reumática histórica.
- `presentation` (9), `diagnostic_approach` (4 eixos — critérios de
  gravidade e discordância de 20-30%, baixo fluxo e baixo gradiente com
  os dois subtipos, avaliação por imagem e funcional, valva bicúspide no
  adulto jovem com aortopatia associada), `differentials` (8, incluindo
  amiloidose cardíaca no subtipo de baixo fluxo/baixo gradiente com FEVE
  preservada), `tests` (8), `red_flags` (8).
- `treatment_summary`: só troca valvar é definitiva (TAVI ou SAVR),
  critérios objetivos de intervenção precoce no assintomático grave,
  decisão do Heart Team pelos 4 eixos, valva bicúspide favorecendo
  cirurgia, corte etário de 70 anos condicionado a anatomia (não
  isolado), dados de durabilidade de longuíssimo prazo relevantes para o
  paciente jovem, sem doses.
- `ambulatory_flow` (8), `emergency_flow` (5), `monitoring` (7).
- `special_populations` (8): adulto jovem bicúspide, idoso (com
  referência cruzada à ficha geriátrica), baixo fluxo/baixo gradiente
  (dois subtipos), assintomático grave com critério de intervenção
  precoce, cirurgia concomitante, expectativa de vida curta, gestante.
- `assistant_questions` (17), `assistant_rules` (11, priority 98 para
  choque/baixo débito).
- `related_document_slugs` (7, do zero — ver seção de verificação).
- `patient_material_slug` preenchido: `estenose-aortica-e-troca-de-valva`
  (material geral, distinto do material específico de TAVI já usado pela
  ficha geriátrica).

## Verificação de citações

Todos os 6 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils (esummary) antes da montagem — título, revista e data conferidos
e batendo com os `source_refs`: diretriz ESC/EACTS 2021 (PMID 34453165),
diretriz ESC/EACTS 2025 (PMID 40878295), metanálise dos 4 RCTs de
intervenção precoce (PMID 40831305), durabilidade PARTNER 3 em 7 anos
(PMID 42340728), durabilidade Evolut Low Risk em 6-7 anos (PMID
41697183) e PARTNER 2A em 10 anos, risco intermediário (PMID 42300821).

## Verificações feitas na montagem

- Os 8 documentos mapeados na missão foram lidos por completo (incluindo
  o fluxograma de timing versão 2021, não listado explicitamente mas
  encontrado ao explorar a pasta). Os 7 `related_document_slugs`
  escolhidos como mais centrais — as duas diretrizes de base, os três
  fluxogramas de decisão (via de intervenção, timing no assintomático
  versão 2025, escolha de modalidade), a metanálise dos 4 RCTs e o
  estudo de durabilidade TAVI em baixo risco — foram verificados
  individual e programaticamente quanto à resolução, ao escopo e à
  menção explícita ao tema no texto. `partner-2a-10-anos-tavr...` foi
  lido por completo mas não entrou na lista final de 7 (risco
  intermediário/idoso, menos central que o estudo de baixo
  risco/durabilidade para o recorte geral desta ficha) — ainda assim
  citado em `source_refs` pela relevância de seguimento de muito longo
  prazo.
- **Overlap com `estenose-aortica-tavi-idoso` (instrução explícita da
  missão)**: nenhum dos 7 `related_document_slugs` deste verbete novo é
  reaproveitado da ficha geriátrica (que usa documentos distintos:
  bloqueio AV pós-TAVI, obstrução coronária pós-TAVI, choque no idoso e
  futilidade). Confirmado por teste dedicado.
- **Overlap com o hub geral `valvopatias` (achado durante a montagem, não
  antecipado na missão)**: o hub geral já publicado (`prevalence_rank`
  5) referencia quase toda a pasta `content/Valvopatias/` (~40
  documentos, incluindo os 8 mapeados nesta missão). Os 7
  `related_document_slugs` desta ficha são, por construção, subconjunto
  do hub — mesmo padrão hub-e-folha já presente no corpus antes desta
  rodada (outras fichas específicas de valvopatia, incluindo a própria
  `estenose-aortica-tavi-idoso`, já compartilham ao menos 1 documento com
  o hub). O teste de não-sobreposição foi ajustado para comparar apenas
  fichas específicas irmãs entre si, excluindo explicitamente o hub
  geral desse comparativo — decisão documentada em teste dedicado
  (`test_overlap_com_hub_valvopatias_e_esperado_e_documentado`) e no
  `review_note` do próprio registro.
- `patient_material_slug` confirmado por correspondência exata em
  `material-paciente/metadados.json`.
- `prevalence_rank` deixado `null`, mesma lógica já usada em verbetes
  anteriores desta frente: o hub fechado de prevalência em área `geral`
  (ranks 1-9) já tem o slot 5 ocupado pelo hub `valvopatias`; esta ficha
  específica não concorre por rank próprio.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Overlap total dos `related_document_slugs` com o hub geral
  `valvopatias` é esperado e documentado, mas fica registrado aqui para
  visibilidade explícita do revisor humano.
- Baixo fluxo e baixo gradiente e valva bicúspide foram descritos com
  base nas diretrizes ESC/EACTS 2021/2025 e no corpus já existente da
  pasta; nenhum RCT dedicado a esses dois subgrupos específicos foi
  citado nesta rodada além do que já constava nos documentos-fonte.

## Gates

- `scripts/audit_tudo_com_tudo.py`: ver saída anexada ao PR.
- `scripts/content_inventory.py --strict`: ver saída anexada ao PR.
- `backend/tests/test_novo_verbete_estenose_aortica.py`: 15 testes.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `backend/tests/test_canonical_content_review_status.py`: **1 falha
  esperada e documentada** (`doencas/metadados.json:estenose-aortica:pendente_revisao`)
  — o gate principal de publicação não aceita `pendente_revisao` mesmo
  com entrada na allowlist de fragmentos; é o comportamento correto e
  intencional, igual ao já usado nos verbetes novos anteriores desta
  frente (cardiomiopatia hipertrófica, 28/08/2026).
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/novo-verbete-estenose-aortica-20260829`, baseada em
`origin/main`.
