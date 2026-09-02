# Verbete novo — Estenose mitral — 29/08/2026

## Contexto

Rodada de reconhecimento sistêmico identificou que **estenose mitral** —
a valvopatia mais associada à febre reumática e causa importante de
morbimortalidade em países de baixa e média renda — não tinha ficha
própria em `doencas/metadados.json`, apesar de corpus rico já existente
(~7 documentos dedicados: diagnóstico e manejo ESC/EACTS 2025, fluxograma
comissurotomia vs. cirurgia, rastreamento WHF e valvuloplastia por balão,
INVICTUS na fibrilação atrial valvar reumática, formas na gestação e no
idoso, doença degenerativa por calcificação anular).

Criado via `doencas/fragmentos/estenose-mitral.json` para minimizar
colisão com outras frentes de produção concorrentes.

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: febre reumática como causa mais comum em escala global e
  principal causa de morte por valvopatia no mundo; declínio em países de
  alta/média renda vs. persistência como problema grave de saúde pública
  em regiões de baixa renda; longo período de latência (20-40 anos) entre
  o episódio de febre reumática e os sintomas; distinção da estenose
  mitral degenerativa por calcificação do anel mitral (MAC).
- `presentation` (11), `diagnostic_approach` (planimetria da área valvar
  mitral, corte de gravidade ≤1,5 cm², escore de Wilkins com seus quatro
  componentes e pontos de corte, avaliação pré-valvuloplastia por
  ecocardiograma transesofágico, teste de esforço, tomografia na MAC),
  `differentials` (8), `tests` (8), `red_flags` (8).
- `treatment_summary`: vigilância clínica na doença leve assintomática,
  valvuloplastia mitral por balão percutânea como primeira escolha em
  anatomia favorável, avaliação cirúrgica (comissurotomia ou troca
  valvar) em anatomia desfavorável, decisão em heart team, anticoagulação
  obrigatória com antagonista de vitamina K (não DOAC) na EM reumática
  com fibrilação atrial ou evento embólico prévio, profilaxia secundária
  de febre reumática — sem doses.
- `ambulatory_flow` (12), `emergency_flow` (7), `monitoring` (8).
- `special_populations` (8).
- `assistant_questions` (13), `assistant_rules` (11, priority 100 para
  edema agudo de pulmão precipitado por taquiarritmia em estenose grave;
  duas regras de priority 95 sinalizando uso inadequado de DOAC em EM
  reumática com FA ou evento embólico prévio).
- `related_document_slugs` (7, do zero).

## Verificação de citações

Todos os 6 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem: Praz et al. (ESC/EACTS 2025, PMID 40878295),
Wilkins et al. (Br Heart J 1988, PMID 3190958 — artigo de origem do
escore de Wilkins), Reményi et al. (critérios WHF, PMID 22371105),
Connolly et al. (INVICTUS, N Engl J Med 2022, PMID 36036525), Baumgartner
et al. (EAE/ASE quantificação de estenose valvar, PMID 19130998) e
Vahanian et al. (ESC/EACTS 2021, PMID 34453165).

## Verificações feitas na montagem

- Os 7 `related_document_slugs` finais foram verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema — todos lidos por completo antes da inclusão, confirmando que
  cada um discute estenose mitral centralmente (não tangencialmente):
  - `estenose-mitral-diagnostico-e-manejo-esc-eacts-2025` (Valvopatias)
  - `fluxograma-estenose-mitral-grave-comissurotomia-vs-cirurgia-esc-eacts-2025`
    (Valvopatias)
  - `rastreamento-ecocardiografico-whf-e-valvuloplastia-por-balao-na-estenose-mitral-reumatica`
    (Febre reumática)
  - `estenose-mitral-descompensada-na-gestacao-e-edema-pulmonar`
    (Gravidez)
  - `estenose-mitral-reumatica-no-idoso-diagnostico-diferencial-e-estrategia-terapeutica-por-faixa-etaria`
    (Cardiologia geriátrica)
  - `doenca-valvar-mitral-degenerativa-no-idoso-calcificacao-anular-e-opcoes-percutaneas`
    (Cardiologia geriátrica — mecanismo degenerativo distinto,
    explicitamente contrastado com o mecanismo reumático nos dois
    documentos)
  - `fibrilacao-atrial-valvar-reumatica-e-escolha-do-anticoagulante-invictus`
    (Fibrilação atrial — população do ensaio INVICTUS definida por
    estenose mitral reumática com FA, tema central do documento, não
    tangencial)
  - Nenhum candidato resolveu para `content/Farmacologia`,
    `content/Calculadoras` ou `content/Exames`; nenhum candidato foi
    descartado nesta rodada — os 7 propostos passaram no critério de
    centralidade.
- `patient_material_slug` confirmado por correspondência exata em
  `material-paciente/metadados.json`
  (`estenose-mitral-entendendo-a-valvula-estreitada`).
- `category='valvopatia'` já existe na convenção do corpus.
- Overlap legítimo e pré-existente documentado no teste dedicado
  (`DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS`): 3 dos 7 documentos
  também estão em `related_document_slugs` da ficha-hub `valvopatias`
  (área geral) — `estenose-mitral-diagnostico-e-manejo-esc-eacts-2025`,
  `fluxograma-estenose-mitral-grave-comissurotomia-vs-cirurgia-esc-eacts-2025`
  e `doenca-valvar-mitral-degenerativa-no-idoso-calcificacao-anular-e-opcoes-percutaneas`
  — e 1 também está em `valvopatias-na-gravidez`
  (`estenose-mitral-descompensada-na-gestacao-e-edema-pulmonar`).
  Confirmado programaticamente contra os 119 registros compostos via
  `load_disease_records()`; nenhuma sobreposição não documentada foi
  encontrada.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Gate `test_canonical_content_review_status.py` falha intencionalmente
  (política vigente desde 28/08/2026: allowlists ficam vazias, qualquer
  status diferente de `revisado` quebra o gate sem exceção). A falha foi
  confirmada isolada — exatamente 1 teste falhando
  (`test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`),
  os outros dois testes do mesmo arquivo passam.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_novo_verbete_estenose_mitral.py`: 11 testes, todos
  passando.
- `backend/tests/test_disease_fragments_canonical.py`: 3 testes, todos
  passando.
- `backend/tests/test_canonical_content_review_status.py`: 1 falha
  esperada e documentada acima, 2 testes passando.
- `app.main` importa sem erro.
- `load_disease_records()` carrega os 119 registros compostos
  (`doencas/metadados.json` + fragmentos + correções) sem erro, incluindo
  o novo registro `estenose-mitral`.
