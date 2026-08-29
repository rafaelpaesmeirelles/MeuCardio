# Verbete novo — Insuficiência mitral — 29/08/2026

## Contexto

Rodada de reconhecimento sistêmico identificou que **insuficiência
mitral** — a valvopatia mais prevalente no mundo ocidental — não tinha
ficha própria em `doencas/metadados.json`, apesar de corpus rico já
existente (~10 documentos dedicados: fluxograma ESC/EACTS 2025,
EVEREST II, COAPT vs. MITRA-FR, disjunção anular mitral, falha aguda de
TEER, prolapso arrítmico no atleta).

Criado via `doencas/fragmentos/insuficiencia-mitral.json` para minimizar
colisão com outras frentes de produção concorrentes.

## Conteúdo produzido (verbete completo, do zero)

- `epidemiology`: prevalência populacional (Nkomo et al., Lancet 2006),
  distinção primária vs. secundária, valor prognóstico independente da
  IM funcional em ICFEr (Rossi et al., Heart 2011).
- `presentation` (11), `diagnostic_approach` (quantificação de gravidade
  por múltiplos parâmetros, classificação de Carpentier, avaliação de
  remodelamento de VE), `differentials` (8), `tests` (8), `red_flags`
  (8).
- `treatment_summary`: terapia guiada por diretriz para IM secundária,
  reparo cirúrgico preferencial à troca na IM primária, TEER para IM
  secundária refratária (COAPT positivo vs. MITRA-FR negativo — diferença
  por seleção de pacientes), sem doses.
- `ambulatory_flow` (10), `emergency_flow` (7), `monitoring` (8).
- `special_populations` (7).
- `assistant_questions` (13), `assistant_rules` (12, priority 100 para
  suspeita de IM aguda grave).
- `related_document_slugs` (7, do zero).

## Verificação de citações

Todos os 8 PMIDs desta rodada foram verificados individualmente via NCBI
e-utils antes da montagem (Nkomo Lancet 2006, ACC/AHA 2020, ESC/EACTS
2025, COAPT, MITRA-FR, Grayburn framework conceitual, EVEREST II 5 anos,
Rossi Heart 2011). Uma 9ª referência (Niarchou et al., disjunção anular
mitral) mantida apenas com DOI, sem PMID disponível.

## Verificações feitas na montagem

- Os 7 `related_document_slugs` verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  ao tema — todos lidos por completo antes da inclusão.
- `patient_material_slug` confirmado por correspondência em
  `material-paciente/metadados.json`.
- `category='valvopatia'` já existe na convenção do corpus.
- Overlap legítimo e pré-existente documentado com `valvopatias` (hub
  geral com 41 `related_document_slugs`) — 4 dos 7 documentos também
  vinculados lá.

Nenhuma dose de fármaco em nenhum campo. Todas as perguntas usam a chave
`label` corretamente.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Gate `test_canonical_content_review_status.py` falha intencionalmente
  (política vigente desde 28/08/2026).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_novo_verbete_insuficiencia_mitral.py`: 14 testes,
  todos passando.
- `backend/tests/test_disease_fragments_canonical.py`: passando.
- `backend/tests/test_canonical_content_review_status.py`: 1 falha
  esperada, documentada acima.
- `app.main` importa sem erro.
