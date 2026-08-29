# Verbete novo — Cardiomiopatia dilatada — 29/08/2026

## Contexto

Rodada de reconhecimento sistêmico identificou que **cardiomiopatia
dilatada (CMD)** — a cardiomiopatia não isquêmica mais prevalente na
prática clínica — não tinha ficha própria em `doencas/metadados.json`,
apesar de corpus rico já existente em `content/Cardiomiopatias/`
(diagnóstico genético e manejo ESC 2023, fluxogramas de investigação
etiológica e de risco de morte súbita/CDI, taquicardiomiopatia,
cardiomiopatia periparto) e em `content/Saúde_mental_e_cardiologia/`
(cardiomiopatia alcoólica). A única ficha de cardiomiopatia já existente
era `cardiomiopatia-hipertrofica` (subtype distinto) e o hub geral
`cardiomiopatias`.

Criado via `doencas/fragmentos/cardiomiopatia-dilatada.json` para
minimizar colisão com outras frentes de produção concorrentes.

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology` (1478 caracteres): CMD como cardiomiopatia não isquêmica
  mais prevalente, etiologia heterogênea (genética/familiar, idiopática,
  tóxica, periparto, induzida por taquiarritmia, infecciosa/miocardítica).
- `presentation` (12), `diagnostic_approach` (6 blocos: avaliação inicial,
  exclusão de doença coronariana, ressonância cardíaca, investigação
  etiológica sistemática, teste genético, estratificação de risco e CDI),
  `differentials` (10), `tests` (10), `red_flags` (8).
- `treatment_summary` (3102 caracteres): terapia guiada por diretriz para
  disfunção sistólica, tratamento de causas reversíveis (alcoólica,
  taquicardia-induzida, periparto), estratificação de risco de morte
  súbita e indicação de CDI, sem doses.
- `ambulatory_flow` (10), `emergency_flow` (5), `monitoring` (8).
- `special_populations` (6).
- `assistant_questions` (17), `assistant_rules` (13, priority 100 para
  choque cardiogênico).
- `related_document_slugs` (6, do zero).
- `patient_material_slug`: `cardiomiopatia-dilatada-por-que-o-coracao-
  aumenta-de-tamanho` (confirmado em `material-paciente/metadados.json`).

## Verificação de citações

Todos os 8 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem:

- Arbelo E et al. 2023 ESC Guidelines for the management of
  cardiomyopathies. Eur Heart J. 2023. PMID 37622657.
- Wahbi K et al. Risk score for VT em laminopatias. Circulation. 2019.
  PMID 31155932.
- Bauersachs J et al. Cardiomiopatia periparto — position statement HFA/
  ESC. Eur J Heart Fail. 2019. PMID 31243866.
- Sato N et al. Taquicardiomiopatia — revisão conceitual. Heart Fail
  Rev. 2026. PMID 42412249.
- Lakdawala NK et al. Danicamtiv em CMD (fase 2). J Am Coll Cardiol.
  2025. PMID 41217321.
- Zeppenfeld K et al. 2022 ESC Guidelines — arritmias ventriculares e
  prevenção de morte súbita. Eur Heart J. 2022. PMID 36017572.
- Køber L et al. DANISH — CDI em IC sistólica não isquêmica. N Engl J
  Med. 2016. PMID 27571011.
- Baman TS et al. Carga de extrassístoles ventriculares e função de VE.
  Heart Rhythm. 2010. PMID 20348027.

## Verificações feitas na montagem

- Os 6 `related_document_slugs` finais foram lidos por completo,
  individualmente, antes da inclusão — todos resolvem para documentos em
  `content/Cardiomiopatias/` ou `content/Saúde_mental_e_cardiologia/`
  (nenhum em Farmacologia/Calculadoras/Exames) e todos mencionam
  "cardiomiopatia dilatada" ou "CMD" centralmente no texto.
- **Descartado 1 dos 7 candidatos propostos**
  (`miocardite-diagnostico-estratificacao-de-risco-e-biopsia-endomiocardica-
  esc-2025`) por a menção à cardiomiopatia dilatada ser apenas uma
  progressão minoritária de desfecho dentro de um documento cujo tema
  central é miocardite, não CMD em si — decisão de rigor além da proposta
  inicial do agente de pesquisa, registrada no `review_note` do fragmento.
- Nenhuma colisão de slug com `cardiomiopatia-hipertrofica`: mesma
  `category='cardiomiopatia'` (convenção do hub `cardiomiopatias`),
  `subtype='dilatada'` distinto, e **nenhum** `related_document_slugs`
  compartilhado entre os dois verbetes específicos (confirmado
  programaticamente).
- Overlap legítimo e pré-existente confirmado com 5 dos 6 documentos: o
  hub geral `cardiomiopatias` já referenciava 5 dos 6 documentos
  nucleares de CMD; `cardiomiopatia-periparto` e
  `seguimento-cardiovascular-pos-parto` compartilham o documento de
  cardiomiopatia periparto; `taquicardia-supraventricular` compartilha o
  documento de taquicardiomiopatia. Apenas `cardiomiopatia-alcoolica-...`
  não é compartilhado com nenhuma outra ficha. Todos documentados em
  `DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS` no teste dedicado.
- `patient_material_slug` confirmado por correspondência exata em
  `material-paciente/metadados.json`.
- `category='cardiomiopatia'` e `subtype='dilatada'` seguem a mesma
  convenção já usada por `cardiomiopatia-hipertrofica`. `prevalence_rank`
  deixado `null`.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente (nenhuma usa a chave legada `text`). Todas as regras
usam operadores válidos (`eq`, `truthy`, `falsy`, `contains`, `gte`,
`lte` — nenhuma usa `includes`) e chaves de `add` na allowlist (nenhuma
usa `monitoring`).

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Gate `test_canonical_content_review_status.py` falha intencionalmente:
  o teste `test_manifestos_canonicos_so_tem_pendencias_explicitamente_
  aprovadas_para_rc` exige `review_status=='revisado'` para todos os
  registros sem exceção via allowlist (política vigente desde
  28/08/2026, sem exceção mesmo com entrada no allowlist de
  `PENDENTES_LOTES_TUDO_COM_TUDO`, já que essa allowlist só se aplica a
  registros com `status=='revisado'` marcados como pendência editorial —
  não a registros `pendente_revisao`). Essa falha foi mantida
  deliberadamente, sem contorná-la, conforme instrução recebida.
- Foi adicionada uma entrada em `PENDENTES_LOTES_TUDO_COM_TUDO` (dentro
  de `test_canonical_content_review_status.py`) apenas porque essa
  estrutura é reaproveitada por `test_disease_fragments_canonical.py`
  (import direto) — sem essa entrada, o teste
  `test_catalogo_combinado_tem_slugs_unicos_e_status_editorial_explicito`
  falharia também. A entrada **não** afeta o resultado do gate de
  `test_canonical_content_review_status.py` em si, que continua falhando
  como esperado (confirmado por execução).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_novo_verbete_cardiomiopatia_dilatada.py`: 13
  testes, todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes, todos
  passando.
- `backend/tests/test_canonical_content_review_status.py`: 1 falha
  esperada (`test_manifestos_canonicos_so_tem_pendencias_explicitamente_
  aprovadas_para_rc`), documentada acima; os outros 2 testes do arquivo
  passam.
- `app.main` importa sem erro.
- `DATABASE_URL` apontado para o container Docker `corvia-test-pg`
  (já em execução, confirmado antes dos testes).
