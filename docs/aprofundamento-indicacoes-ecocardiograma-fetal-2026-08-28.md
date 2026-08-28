# Aprofundamento Tudo com Tudo — Indicações de ecocardiograma fetal — 28/08/2026

## Contexto

Décimo sétimo lote de conteúdo do dia, primeiro fora do cluster de
gravidez pós-parto (após `doenca-coronariana-idoso`, PR #603;
`valva-aortica-bicuspide-pediatrica`, PR #604;
`hipotensao-ortostatica-no-idoso`, PR #606; `sopros-na-infancia`,
PR #608; `hipertensao-arterial-pediatrica`, PR #609;
`dor-toracica-pediatrica`, PR #610; `dislipidemias-pediatricas`,
PR #611; `arritmias-pediatricas`, PR #612;
`avaliacao-multidimensional-cardiogeriatrica`, PR #613;
`cuidados-paliativos-cardiovasculares`, PR #615;
`cardiopatia-congenita-gravidez`, PR #616;
`hipertensao-pulmonar-gravidez`, PR #621;
`cardiotoxicidade-bcr-abl`, PR #624;
`medicamentos-cardiovasculares-gestacao-lactacao`, PR #625;
`plano-parto-cardiopatia-materna`, PR #626;
`seguimento-cardiovascular-pos-parto`, PR #628). A ficha
`indicacoes-ecocardiograma-fetal` (área `cardiopediatria`, categoria
`cardiologia_fetal`, `prevalence_rank: 31`) já tinha
`patient_material_slug` e 1 `related_document_slug` preenchidos, mas
zero campos clínicos.

Quarta ficha do dia em formato framework/protocolo (não uma doença
única) — triagem de indicações para ecocardiograma fetal direcionado
— mesmo padrão de adaptação de campos já usado em
`avaliacao-multidimensional-cardiogeriatrica` (PR #613),
`cuidados-paliativos-cardiovasculares` (PR #615) e
`plano-parto-cardiopatia-materna` (PR #626).

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Cenários e diagnóstico** — `epidemiology` (prevalência de
   cardiopatia congênita na população geral vs. grupos de risco,
   sensibilidade limitada do rastreamento obstétrico de rotina),
   `presentation` (17 categorias de indicação: 7 maternas, 7 fetais, 3
   familiares/genéticas), `diagnostic_approach` (6 subtópicos:
   indicações maternas, fetais, familiares/genéticas detalhadas,
   janela gestacional ideal, diferença rastreamento vs. direcionado,
   seguimento e periodicidade), `differentials` (7), `tests` (9),
   `red_flags` (8), `source_refs` (6, incluindo ASE 2023, AHA 2014,
   ISUOG 2013 e estudos sobre translucência nucal e cardiopatia).
2. **Conduta e assistente** — `treatment_summary` (indicações
   maternas/fetais/familiares, janela gestacional 18-24 semanas,
   qualificação do examinador, conduta pós-confirmação, investigação
   genética associada, reforço de que rastreamento de rotina não
   substitui o exame direcionado), `ambulatory_flow` (10),
   `emergency_flow` (8), `monitoring` (8), `assistant_questions` (14),
   `assistant_rules` (12, priority 98 para hidropisia fetal nova).
3. **Populações especiais e conexões** — `special_populations` (6:
   diabetes pré-gestacional, anti-Ro/anti-La positivo, cardiopatia
   congênita materna própria, gestação monocoriônica, exposição a
   teratógeno, translucência nucal aumentada), `related_document_slugs`
   (3, dentro do intervalo permitido — busca exaustiva não encontrou
   mais candidatos genuinamente centrais ao tema).

## Correção de compliance feita na montagem

Uma `assistant_rule` do agente da Parte 2
(`gestacao_monocorionica_rastreio`) usava a chave `monitoring` dentro
de `add` — chave não pertencente ao conjunto permitido pelo motor de
regras real (`monitoring` é campo de nível de ficha, não de resultado
de regra). O conteúdo foi preservado e movido para a chave
`supporting`, mantendo o sentido clínico original.

## Verificações feitas na montagem

- Os 3 `related_document_slugs` finais (1 já existente + 2 novos)
  verificados individual e programaticamente quanto à resolução, ao
  escopo e à menção de ecocardiograma fetal/risco de
  recorrência/indicação no texto.
- O agente da Parte 3 documentou explicitamente que a busca exaustiva
  no corpus encontrou apenas 3 documentos narrativos que tratam
  explicitamente de indicação/realização do exame — vários outros
  documentos mencionam "ecocardiograma fetal" apenas de passagem,
  como ferramenta diagnóstica dentro de uma ficha de doença fetal
  específica (ex.: janela aortopulmonar, taquiarritmia fetal com
  hidropisia, tetralogia de Fallot), e foram corretamente excluídos
  por não serem o foco central do documento nem "documentos" no
  sentido da regra Tudo com Tudo (são outras entradas de doença do
  próprio catálogo, não markdown narrativo em `content/`).
- Overlap com `tetralogia-de-fallot` (2 dos 3 documentos) — legítimo,
  mesma lógica de multi-hub já aplicada em todos os lotes anteriores.
- `patient_material_slug` original (`indicacoes-ecocardiograma-fetal`)
  preservado sem alteração — reconfirmado como existente.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente. Estrutura de perguntas e regras validada com o
motor de regras real — todos os operadores usados pertencem ao
conjunto permitido, nenhum uso de "includes".

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

6 referências com PMID verificado, incluindo a diretriz ASE 2023 já
citada na ficha original, a diretriz científica da AHA 2014 sobre
diagnóstico e tratamento de cardiopatia fetal, as diretrizes ISUOG
2013 de rastreamento cardíaco fetal, e os estudos de Hyett et al.
(1999) e Sotiriadis et al. (2013) sobre translucência nucal e risco de
cardiopatia estrutural.

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `indicacoes-ecocardiograma-fetal`.
Verificada a existência de uma branch remota
`codex/guia-atresia-tricuspide-20260827` (pushed, sem commits de
conteúdo, sem PR aberto) — sinal de trabalho reservado nessa mesma
esteira automatizada; por isso `atresia-tricuspide` foi propositalmente
evitada neste ciclo, mesmo tendo `prevalence_rank` numericamente
melhor.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `related_document_slugs` no limite inferior permitido (3) — corpus
  atual não tem mais documentos narrativos genuinamente centrais ao
  tema; oportunidade de produção futura sinalizada pelo agente da
  Parte 3 (diabetes pré-gestacional e cardiopatia fetal, transfusão
  feto-fetal, teratógenos e cardiopatia fetal, translucência nucal —
  sem documento dedicado no corpus atual).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_indicacoes_ecocardiograma_fetal.py`:
  12 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-indicacoes-ecocardiograma-fetal-20260828`,
baseada em `origin/main` sem drift no momento do commit.
