# Verbete novo — Bloqueio atrioventricular — 29/08/2026

## Contexto

Rodada de reconhecimento sistêmico identificou que **bloqueio
atrioventricular do adulto** não tinha ficha própria em
`doencas/metadados.json` — a ficha `dispositivos-cardiacos-implantaveis`
cobre a indicação de marca-passo em geral, mas não a doença/etiologia do
BAV em si, e `bloqueio-atrioventricular-fetal` é ficha distinta,
exclusivamente fetal. Corpus com ~8 documentos dedicados (bloqueio
bifascicular, cardite de Lyme, síndrome BRASH, BAV pós-TAVI).

Criado via `doencas/fragmentos/bloqueio-atrioventricular.json` para
minimizar colisão com outras frentes de produção concorrentes.

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: prevalência crescente com idade, causa mais comum é
  degeneração idiopática (Lenègre/Lev), causas reversíveis a excluir
  sistematicamente (ACC/AHA/HRS 2018).
- `presentation` (12), `diagnostic_approach` (classificação por grau,
  localização nodal vs. infra-hissiana pela largura do QRS, estudo
  eletrofisiológico com intervalo HV, investigação etiológica),
  `differentials` (9), `tests` (12), `red_flags` (10).
- `treatment_summary`: observação em bloqueios de baixo grau
  assintomáticos, marca-passo definitivo em alto grau/completo,
  exclusão obrigatória de causas reversíveis (síndrome BRASH, doença de
  Lyme) antes de indicar dispositivo, sem doses.
- `ambulatory_flow` (10), `emergency_flow` (7), `monitoring` (8).
- `special_populations` (6).
- `assistant_questions` (14), `assistant_rules` (11, priority 100 para
  instabilidade hemodinâmica aguda).
- `related_document_slugs` (6, do zero).

## Verificação de citações

Todos os 7 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem (ACC/AHA/HRS 2018, ESC 2021 cardiac pacing, ESC
2025 conduction system pacing, McAnulty NEJM 1982, Scheinman Circulation
1977, Lyme carditis JACC 2019, síndrome BRASH J Emerg Med 2020).

## Verificações feitas na montagem

- Os 6 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema — todos lidos por completo antes da inclusão.
- **Descartado 1 dos 7 candidatos propostos pelo agente de pesquisa**
  (`sindrome-brash-...`) por resolver para `content/Farmacologia`, fora
  do escopo permitido pela regra Tudo com Tudo — verificação feita por
  mim, corrigindo a proposta inicial do agente.
- `patient_material_slug`: nenhuma correspondência específica de BAV
  adulto (não fetal) encontrada, mantido `null`.
- `category='disturbio_de_conducao'` é categoria **nova** — nenhuma
  categoria existente de área geral encaixava uma bradiarritmia/distúrbio
  de condução (`arritmia_supraventricular` é semanticamente específica
  para taquiarritmias, ficaria errado aqui).
- Overlaps legítimos e pré-existentes documentados com `arritmias-na-
  gravidez`, `estenose-aortica-tavi-idoso`, `endocardite-infecciosa` e
  `dispositivos-cardiacos-implantaveis`.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Gate `test_canonical_content_review_status.py` falha intencionalmente
  (política vigente desde 28/08/2026).
- `category` nova (`disturbio_de_conducao`) — vale confirmação editorial
  de que o nome é adequado à taxonomia do sistema.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_novo_verbete_bloqueio_atrioventricular.py`: 14
  testes, todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `backend/tests/test_canonical_content_review_status.py`: 1 falha
  esperada, documentada acima.
- `app.main` importa sem erro.
