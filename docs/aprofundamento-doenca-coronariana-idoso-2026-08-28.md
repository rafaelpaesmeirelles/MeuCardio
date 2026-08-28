# Aprofundamento Tudo com Tudo — Doença coronariana no idoso — 28/08/2026

## Pivô do dia

O gap-finding de hubs gerais novos (21º ciclo do dia, iniciado em 27/08)
foi declarado esgotado para o momento: o único candidato restante,
**cardiopatia reumática crônica do adulto** (18 documentos não cobertos em
`content/Febre_reumática/`), tinha sobreposição conceitual real com o PR
aberto `#567` (Codex, `codex/guia-febre-reumatica-20260827`), que já
amplia os aliases do hub pediátrico existente `febre-reumatica-cardite`
para termos adultos/crônicos mantendo área pediátrica. Diante do risco,
perguntei ao Rafael como prosseguir; a decisão foi **pivotar para um lote
de aprofundamento** de ficha já existente, em vez de abrir esse hub.

## Escolha da ficha

Um agente auditou os 26 PRs abertos que tocam `doencas/metadados.json`
(15 hubs Claude conhecidos + 11 lotes de aprofundamento Codex/Claude não
mapeados antes) para excluir qualquer ficha já em edição, e revisou
`doencas/metadados.json` em busca de entradas rasas. `doenca-coronariana-idoso`
(área `cardiogeriatria`) foi a mais rasa entre as clinicamente relevantes
e livre de qualquer PR aberto: tinha apenas `slug/name/aliases/area/
category/subtype/prevalence_rank/completeness=básico/summary (1 frase)/
tags/source_refs (1 referência genérica)/source_urls/review_status/
review_note/version` — nenhum campo clínico.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (dados reais de
   prevalência/mortalidade/apresentação atípica no idoso), `presentation`
   (10 itens), `diagnostic_approach` (estruturado em 4 subtópicos: ECG/
   troponina de alta sensibilidade ajustada à função renal, estratificação
   de risco isquêmico vs. hemorrágico, papel da fragilidade na decisão
   diagnóstica, angiografia vs. estratégia conservadora conforme ESC/AHA),
   `differentials` (10), `tests` (9), `red_flags` (8), `source_refs` (10).
2. **Tratamento e assistente** — `treatment_summary` (3371 caracteres,
   cobrindo estratégia de revascularização guiada por fragilidade, DAPT
   individualizada por risco hemorrágico sem citar doses, reabilitação
   cardíaca adaptada, manejo de comorbidades), `ambulatory_flow` (9),
   `emergency_flow` (8), `monitoring` (8), `assistant_questions` (11),
   `assistant_rules` (10, priority até 95 para SCA com supra + instabilidade
   hemodinâmica).
3. **Populações especiais e conexões** — `special_populations` (8: muito
   idoso multimórbido, fragilidade avançada, DRC concomitante, demência/
   decisão compartilhada, polifarmácia, mulher idosa, institucionalizado,
   cuidados paliativos), `related_document_slugs` (21 propostos),
   `patient_material_slug`.

## Correções feitas na montagem

- **Operador inválido**: a regra `demencia_avancada_ou_neoplasia_ativa`
  usava `"op": "includes"`, inexistente no motor de regras real
  (`ALLOWED_OPERATORS` não o contém) — corrigido para `"contains"`, que
  produz o comportamento correto de checagem de pertencimento em lista
  (campo `comorbidades` é `multiselect`).
- **2 documentos removidos** dos 21 propostos: `sintomas-prodromicos-e-
  agudos-de-infarto-em-mulheres-o-que-perguntar-na-anamnese` e
  `limiar-de-transfusao-no-cardiopata-mint-reality-e-trics-iii` tratam de
  DAC/infarto em geral, mas não mencionam população idosa/geriátrica no
  próprio texto (o primeiro tem idade média 66±12 anos na amostra, não é
  foco etário do documento) — não passam no critério de vínculo direto e
  explícito exigido pelo "Tudo com Tudo" para uma ficha especificamente
  geriátrica. Ficaram 19 `related_document_slugs`.
- **2 documentos compartilhados** com outras fichas (`fragilidade-como-
  modificador-de-decisao-cardiovascular`, já em `fragilidade-pre-
  procedimento-cardiovascular` e `anticoagulacao-idoso`; `reabilitacao-
  cardiaca-no-muito-idoso-seguranca-fragilidade-e-adesao`, já em
  `fragilidade-pre-procedimento-cardiovascular` e `plano-alta-
  cardiogeriatria`) mantidos por serem genuína e centralmente sobre DAC no
  idoso — mesmo padrão de pertencimento múltiplo legítimo já usado nos
  hubs de doença da aorta e cardiopatia congênita do adulto.

Nenhuma dose de fármaco foi incluída em nenhum campo — verificado
programaticamente. Estrutura de perguntas e regras validada com o motor
de regras real (`clinical_rule_engine`) antes da montagem.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype` e `prevalence_rank`
originais foram preservados sem alteração — só o conteúdo clínico e os
campos editoriais (`completeness: básico → completo`, `review_status`,
`version: 1 → 2`, `review_note`) mudaram.

## Fontes primárias

11 referências (1 original + 10 novas), todas com PMID/DOI verificado,
incluindo diretriz ESC 2023 de SCA, After Eighty (Lancet 2016),
SENIOR-RITA (NEJM 2024), FIRE trial (NEJM 2023), POPular AGE (Lancet
2020), MASTER DAPT (NEJM 2021).

## Coordenação com Codex

Nenhum dos 26 PRs abertos que tocam `doencas/metadados.json` edita
`doenca-coronariana-idoso`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não é publicado até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `patient_material_slug`: `doenca-coronariana-e-infarto` — material
  existente sobre DAC em geral (não exclusivamente geriátrico, mas com
  parágrafo dedicado à apresentação atípica em idosos); nenhum material
  exclusivamente geriátrico sobre DAC foi encontrado no corpus hoje.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9496` (sem criação de documento ou registro novo).
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`,
  `total_records: 9496`, `total_files: 2193`.
- `backend/tests/test_aprofundamento_doenca_coronariana_idoso.py`: 10
  testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py`: passando com
  `doenca-coronariana-idoso` na allowlist `PENDENTES_LOTES_TUDO_COM_TUDO`.
- `app.main` importa sem erro.

## Branch e PR

Branch `claude/aprofundar-doenca-coronariana-idoso-20260828`, rebaseada
em `origin/main` sem drift no momento do commit (um commit intermediário
não relacionado — `#598`, padrão BRASH em UCO — foi absorvido pelo
rebase sem conflito).
