# Novo verbete: Insuficiência tricúspide (29/08/2026)

## O que foi criado

`doencas/fragmentos/insuficiencia-tricuspide.json` — verbete novo, slug
`insuficiencia-tricuspide`, cobrindo insuficiência tricúspide grave (primária
e secundária/funcional) e, como diferencial dentro da mesma ficha, a estenose
tricúspide reumática. A biblioteca já tinha corpus rico em
`content/Valvopatias/`, `content/Cardiologia_geriátrica/` e
`content/Insuficiência_cardíaca/`, mas nenhuma ficha própria em
`doencas/metadados.json`.

## Fontes usadas (todas lidas por completo)

- `content/Valvopatias/insuficiencia-tricuspide-grave-triluminate-e-reparo-transcateter-borda-a-borda.md`
- `content/Valvopatias/insuficiencia-tricuspide-grave-triscend-ii-e-a-troca-valvar-transcateter-com-o-sistema-evoque.md`
- `content/Valvopatias/fluxograma-insuficiencia-tricuspide-secundaria-grave-quando-intervir-esc-eacts-2025.md`
- `content/Valvopatias/troca-valvar-tricuspide-transcateter-no-mundo-real-registro-sts-acc-tvt.md`
- `content/Valvopatias/estenose-tricuspide-reumatica-diagnostico-e-manejo.md`
- `content/Cardiologia_geriátrica/insuficiencia-tricuspide-funcional-grave-no-idoso-fragil-teer-tricuspide-e-o-triluminate.md` (encontrado via grep, extra)
- `content/Insuficiência_cardíaca/insuficiencia-cardiaca-direita-isolada-por-doenca-tricuspide-fisiopatologia-da-congestao-e-manejo-clinico.md` (encontrado via grep, extra)

Todos os 7 viraram `related_document_slugs` (dentro do teto de 3-7 da regra
Tudo com Tudo), confirmados centrais ao tema por leitura direta e completa.
Dois candidatos adicionais mapeados por grep foram lidos e deliberadamente
excluídos por tratarem de subtipos etiológicos específicos, não do tema geral
desta ficha: `regurgitacao-tricuspide-induzida-por-eletrodo-mecanismo-
prognostico-e-manejo.md` (Dispositivos) e `displasia-congenita-isolada-da-
valva-tricuspide-nao-ebstein-...md` (Cardiologia pediátrica).

## PMIDs verificados individualmente (NCBI e-utils, esummary, 29/08/2026)

| PMID | Estudo | Status |
|---|---|---|
| 36876753 | TRILUMINATE Pivotal (Sorajja 2023, NEJM) | conferido, sem divergência |
| 40159089 | TRILUMINATE 2-year outcomes (Kar 2025, Circulation) | conferido, sem divergência |
| 39475399 | TRISCEND II pivotal (Hahn 2025, NEJM) | conferido, sem divergência |
| 42470411 | TRISCEND II substudo ecocardiográfico (Sannino 2026, JACC CV Imaging) | conferido, epub sem vol/páginas ainda |
| 41973411 | Registro STS/ACC TVT (Makkar 2026, JAMA) | conferido, sem divergência |
| 40878295 | ESC/EACTS 2025 valvopatias | **CORRIGIDO**: páginas 4635-4736 (registro oficial), não 4635-4747 como citado nos documentos-fonte |
| 15013122 | Nath 2004, sobrevida por gravidade da IT | conferido, sem divergência |
| 29241483 | Zack 2017, mortalidade cirúrgica tricúspide isolada | conferido, sem divergência |

A referência de estenose tricúspide reumática (StatPearls, NCBI Bookshelf
NBK499990) não tem PMID por não ser indexada no PubMed — mantida como já
verificada em sessão anterior desta biblioteca, conforme já registrado no
documento-fonte.

## Schema

`SpecialtyDisease` completo: `slug`, `name`, `aliases` (6), `area="geral"`,
`category="valvopatia"`, `subtype=null`, `cyanosis_class=null`,
`prevalence_rank=null`, `completeness="completo"`, `summary`, `epidemiology`
(2.124 caracteres), `presentation` (11 itens), `diagnostic_approach` (dict
aninhado com 5 chaves, 6.344 caracteres serializados, incluindo subseção
dedicada `estenose_tricuspide_reumatica_como_diferencial`), `differentials`
(8), `tests` (9), `red_flags` (8), `ambulatory_flow` (8), `emergency_flow`
(5), `treatment_summary` (3.378 caracteres, sem dose de fármaco),
`monitoring` (7), `special_populations` (6), `assistant_questions` (17,
todas com chave `label`), `assistant_rules` (18, `op` sempre em
`{eq,neq,in,not_in,gt,gte,lt,lte,truthy,falsy,contains,exists,missing}`,
`risk` sempre em `{informativo,rotina,prioritario,urgente,emergencia}`, `add`
nunca usa `monitoring`), `tags`, `source_refs`/`source_urls` (9), 7
`related_document_slugs`, `patient_material_slug`, `review_status
="pendente_revisao"`, `review_note` detalhado, `version=1`,
`fonte_producao="claude"`.

`patient_material_slug` resolvido para
`insuficiencia-tricuspide-a-terceira-valvula-e-o-reparo-por-cateter`, já
existente em `material-paciente/metadados.json` e vinculado ao
`documento_slug` do TRILUMINATE.

Nenhuma dose de fármaco em nenhum campo — verificado por padrão regex
(mg/mg-kg/mcg/J-kg) contra o registro serializado inteiro.

## Gates executados

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_novo_verbete_insuficiencia_tricuspide.py`: teste
  dedicado novo, cobrindo profundidade mínima, diferencial de estenose
  reumática, assistente determinístico seguro, ausência de dose, vínculos
  Tudo com Tudo e `patient_material_slug`.
- `backend/tests/test_disease_fragments_canonical.py`: passa (allowlist
  compartilhada funciona corretamente para status pendente).
- `backend/tests/test_canonical_content_review_status.py`: entrada
  `insuficiencia-tricuspide` adicionada a `PENDENTES_LOTES_TUDO_COM_TUDO
  ["doencas/metadados.json"]`, seguindo exatamente o padrão do PR #698
  (`claude/novo-verbete-cardiomiopatia-de-takotsubo-20260829`). O teste
  `test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_
  para_rc` **FALHA para este registro, como esperado** — `review_status
  ="pendente_revisao"` e conteúdo novo não revisado por humano não se
  autoaprova nesse gate. Não contornado.
- `python -c "import app.main"`: sanidade de import.

Resultado esperado do conjunto: **exatamente 1 falha documentada**
(`test_canonical_content_review_status.py`), todos os demais gates
passando.

## Decisões editoriais registradas no `review_note`

- `category="valvopatia"` segue a convenção dos 3 registros já existentes
  dessa categoria (`estenose-aortica-tavi-idoso`, `valvopatias-na-gravidez`,
  `valvopatias`).
- `area="geral"` e `subtype=null`: a ficha cobre o adulto em geral, com
  população geriátrica coberta em `special_populations`, sem modificador
  populacional fechado equivalente a `heart_team`/`gestacao`/
  `multiplas_lesoes`.
- `prevalence_rank=null`: fora do hub fechado de doenças de altíssima
  prevalência em área "geral" (ranks 1-9), mesma convenção do verbete
  `cardiomiopatia-de-takotsubo`.
