# Aprofundamento Tudo com Tudo — Fisiologia de ventrículo único — 28/08/2026

## Contexto

Vigésimo quinto lote de conteúdo do dia. A ficha
`fisiologia-ventriculo-unico` (área `cardiopediatria`, categoria
`cardiopatia_congenita`, subtype `coracao_univentricular`,
`prevalence_rank: 21`) já tinha `patient_material_slug` e 3
`related_document_slugs` preenchidos, mas zero campos clínicos
(`completeness: basico`, 1 `source_ref`).

Este ciclo encerra o trabalho no cluster de cardiologia fetal (8
fichas concluídas hoje) e migra para o grupo mais amplo
`cardiopatia_congenita` dentro de `cardiopediatria`, seguindo o mesmo
processo de busca de lacunas.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (grupo heterogêneo
   de cardiopatias univentriculares — SCEH, atresia tricúspide, VU de
   dupla entrada — incidência de 2-3/10.000 nascidos vivos, sobrevida
   pós-Fontan >85-90% em 20 anos com atrito progressivo após 20-25
   anos), `presentation` (10 fases/formas: diagnóstico pré-natal/
   neonatal, fases pré-Glenn/pós-Glenn/pós-Fontan, sinais de falência
   tardia), `diagnostic_approach` (4 subtópicos: avaliação pré-natal/
   neonatal, pré-Glenn, pré-Fontan, seguimento pós-Fontan no adulto),
   `differentials` (tratados como cenários anatômicos de base),
   `tests` (8), `red_flags` (8), `source_refs` (6, todos os PMIDs
   verificados individualmente via NCBI e-utils).
2. **Conduta e assistente** — `treatment_summary` (lógica da
   estratégia univentricular em 3 estágios cirúrgicos, seguimento
   multidisciplinar vitalício com ACHD/hepatologia/hematologia,
   reconhecimento explícito de que a falência de Fontan é trajetória
   natural em longo prazo para parte dos pacientes e exige vigilância
   ativa), `ambulatory_flow` (12), `emergency_flow` (8), `monitoring`
   (8), `assistant_questions` (14), `assistant_rules` (10, priority 98
   para falência aguda de Fontan: cianose progressiva + edema/ascite +
   arritmia nova).
3. **Populações especiais e conexões** — `special_populations` (10:
   pré-estágio-1, interestágios, pós-Glenn, Fontan estável, falência
   de Fontan, gestante com Fontan, arritmia atrial, enteropatia/
   bronquite plástica, avaliação esportiva, disfunção do nó sinusal),
   `related_document_slugs` (7, união dos 3 originais com 4 novos,
   após avaliação de 22 candidatos do corpus, 18 descartados por
   menção apenas tangencial ao tema, documentados individualmente).

## Verificação de citações

Todos os 6 PMIDs desta rodada foram verificados individualmente via
NCBI e-utils antes da montagem — todas as 6 referências corretas
quanto a título/periódico/ano/volume/páginas. Como o `esummary.fcgi`
retorna apenas o primeiro autor, listas de autores completas que o
agente havia sugerido para 3 referências (AHA 2019, Feinstein 2012,
d'Udekem 2014) foram substituídas por "Autor Principal, et al." antes
da montagem, para não fabricar nomes de coautores não confirmados —
prática preventiva, não uma correção de erro já publicado.

## Verificações feitas na montagem

- Os 7 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  de ventrículo único/Fontan no texto.
- **Overlap parcial mas legítimo, pré-existente** (não introduzido por
  este lote): `circulacao-de-fontan-e-transposicao-das-grandes-
  arterias-no-adulto` também vinculado por `transposicao-das-grandes-
  arterias`; `ventriculo-unico-e-estadiamento-de-fontan-fisiologia-
  cirurgica-em-tres-estagios-e-complicacoes` também vinculado por
  `atresia-tricuspide` — documentado no teste dedicado.
- O agente da Parte 3 documentou explicitamente 18 candidatos
  descartados por menção apenas tangencial (ex.: Fontan citado em
  meio a listas extensas de outras lesões, ou como referência lateral
  fora do escopo central do documento).
- `patient_material_slug` original (`fisiologia-ventriculo-unico`)
  preservado sem alteração — reconfirmado como existente.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente. Estrutura de perguntas e regras validada com o
motor de regras real — todos os operadores usados pertencem ao
conjunto permitido, nenhum uso de "includes", nenhuma regra usa a
chave `monitoring` (não permitida) dentro de `add`.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

6 referências com PMID verificado individualmente via NCBI e-utils
(dupla checagem: agente + eu), incluindo o Scientific Statement da AHA
2019 sobre avaliação e manejo da circulação de Fontan, a revisão de
fisiologia de Gewillig & Brown (2016), e estudos sobre sobrevida de
longo prazo, mortalidade e enteropatia perdedora de proteína.

## Coordenação com Codex

Nenhum PR aberto (busca por título/nome de branch entre 308 PRs
abertos no repositório) toca `fisiologia-ventriculo-unico` ou os
termos "ventriculo-unico"/"fontan"/"univentricular".

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap parcial mas documentado com 2 fichas do mesmo tema (TGA
  adulto, atresia tricúspide).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_fisiologia_ventriculo_unico.py`:
  12 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-fisiologia-ventriculo-unico-20260828`,
baseada em `origin/main` sem drift no momento do commit.
