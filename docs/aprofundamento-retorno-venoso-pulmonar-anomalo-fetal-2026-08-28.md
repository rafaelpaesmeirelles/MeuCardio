# Aprofundamento Tudo com Tudo — Retorno venoso pulmonar anômalo no período fetal — 28/08/2026

## Contexto

Vigésimo quarto lote de conteúdo do dia, oitavo do cluster de
cardiologia fetal (após `doenca-coronariana-idoso`, PR #603;
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
`seguimento-cardiovascular-pos-parto`, PR #628;
`indicacoes-ecocardiograma-fetal`, PR #630;
`bloqueio-atrioventricular-fetal`, PR #631;
`hidropisia-fetal-cardiovascular`, PR #632;
`flutter-atrial-fetal`, PR #633; `coarctacao-aorta-fetal`, PR #636;
`tetralogia-fallot-fetal`, PR #637;
`transposicao-grandes-arterias-fetal`, PR #638). A ficha
`retorno-venoso-pulmonar-anomalo-fetal` (área `cardiopediatria`,
categoria `cardiologia_fetal`, `prevalence_rank: 40`) já tinha
`patient_material_slug` e 1 `related_document_slug` preenchidos, mas
zero campos clínicos.

## Pivô deste ciclo (transparência)

O primeiro alvo escolhido para este ciclo foi `tumores-cardiacos-
fetais`. Após a produção completa dos 3 blocos de conteúdo, a
verificação de `related_document_slugs` (própria e independente, via
`grep` no corpus completo) confirmou apenas **2** documentos
legitimamente sobre tumores cardíacos fetais/rabdomioma no corpus
atual — abaixo do piso de 3 exigido pela regra Tudo com Tudo. Um
terceiro candidato (documento sobre inibidores de mTOR) foi
explicitamente investigado e descartado por mencionar esclerose
tuberosa apenas de forma tangencial, sem discutir tumor cardíaco.
**Decisão: alvo abandonado antes de qualquer commit**, sem fabricar
uma terceira conexão — worktree e branch removidos, nada publicado.
Pivotei então para `retorno-venoso-pulmonar-anomalo-fetal`, com
profundidade de corpus pré-verificada (7+ documentos candidatos) antes
de iniciar a produção.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (baixa taxa de
   detecção pré-natal por câmaras simétricas/septo íntegro/eixo
   normal, exigindo sinais indiretos e incidências dedicadas),
   `presentation` (10 formas: 4 tipos anatômicos, formas obstrutiva/
   não obstrutiva, sinais indiretos, associação com heterotaxia),
   `diagnostic_approach` (5 subtópicos: limitações inerentes ao
   diagnóstico pré-natal, sinais ecocardiográficos indiretos,
   avaliação Doppler de veia vertical e confluência, diferenciação dos
   4 tipos anatômicos, avaliação de heterotaxia), `differentials` (6),
   `tests` (7), `red_flags` (7), `source_refs` (7, todos os PMIDs
   verificados individualmente via NCBI e-utils).
2. **Conduta e assistente** — `treatment_summary` (ausência de
   intervenção intraútero; forma obstrutiva — sobretudo infracardíaca —
   como verdadeira emergência cirúrgica neonatal; **prostaglandina E1
   sem papel terapêutico útil na forma obstrutiva**, ao contrário de
   lesões ducto-dependentes, podendo agravar a congestão pulmonar;
   correção cirúrgica definitiva com reimplante das veias pulmonares;
   baixa detecção pré-natal; importância do planejamento de parto em
   centro terciário), `ambulatory_flow` (10), `emergency_flow` (7,
   reforçando a ausência de benefício da prostaglandina na forma
   obstrutiva), `monitoring` (7), `assistant_questions` (12),
   `assistant_rules` (9, priority 98 para RVPAT obstrutivo com cianose/
   desconforto neonatal, mais uma regra dedicada reforçando a ausência
   de benefício da prostaglandina).
3. **Populações especiais e conexões** — `special_populations` (6:
   infracardíaco/supracardíaco-cardíaco/heterotaxia/diagnosticado no
   pré-natal/não diagnosticado no pós-natal/gestante orientada sobre
   limitações diagnósticas), `related_document_slugs` (4, união do
   original com 3 novos, a partir de uma lista pré-vetada de 6
   candidatos que confirmei via grep antes de dispatch, dos quais 3
   foram corretamente descartados pelo agente por menção apenas
   tangencial).

## Verificação de citações

Todos os 7 PMIDs desta rodada foram verificados individualmente via
NCBI e-utils antes da montagem — tanto pelo agente de pesquisa quanto
de forma independente por mim (segunda checagem via WebFetch direto ao
`esummary.fcgi`) — todas as 7 referências confirmadas corretas
(título, autores, periódico, ano, volume/páginas), incluindo a
diretriz ASE 2023 (Moon-Grady AJ et al.) e um artigo ainda "ahead of
print" (Zeng Y et al., 2026), cujo título completo e lista de autores
foram confirmados em consulta adicional. Nenhuma correção foi
necessária.

## Verificações feitas na montagem

- Os 4 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção explícita
  de RVPA/RVPAT/TAPVR/TAPVC no texto.
- **Overlap parcial mas legítimo** com a ficha adulta
  `retorno-venoso-pulmonar-anomalo` (alvo do PR #576, atualmente
  aberto): 2 dos 4 documentos (`retorno-venoso-pulmonar-anomalo-total-
  obstruido-no-neonato` e seu fluxograma) já eram compartilhados
  **antes** desta edição (overlap pré-existente em `origin/main`, não
  introduzido por este lote) — documentado no teste dedicado. Confirmei
  via `gh pr diff 576 | grep` que a PR #576 não toca a ficha `-fetal`
  trabalhada aqui.
- O agente da Parte 3 documentou explicitamente ter descartado 3
  candidatos com menção apenas tangencial (dupla via de saída de
  ventrículo direito, hipertensão pulmonar pediátrica, síndrome de
  Turner) da lista pré-vetada que forneci.
- `patient_material_slug` original (`retorno-venoso-pulmonar-anomalo-
  fetal`) preservado sem alteração — reconfirmado como existente.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente; prostaglandina E1 citada apenas por nome, sem
posologia. Estrutura de perguntas e regras validada com o motor de
regras real — todos os operadores usados pertencem ao conjunto
permitido, nenhum uso de "includes", nenhuma regra usa a chave
`monitoring` (não permitida) dentro de `add`.

## Catalogação preservada

`name`, `aliases`, `area`, `category`, `subtype`, `prevalence_rank`
originais preservados sem alteração.

## Correção de gate repetida deste PR

Esta branch partiu de `origin/main` antes da branch do PR #606 ser
mesclada. Apliquei aqui a mesma correção de allowlist já aprovada pelo
Rafael no PR #606 em `test_disease_fragments_canonical.py`.

## Fontes primárias

7 referências com PMID verificado individualmente via NCBI e-utils
(dupla checagem: agente + eu), incluindo a diretriz ASE 2023
(Moon-Grady AJ et al.), o estudo multicêntrico de Seale et al. (2012)
sobre impacto do diagnóstico pré-natal, e 5 estudos recentes
(2022-2026) sobre marcadores ultrassonográficos e predição de
obstrução.

## Coordenação com Codex

PR #576 (`codex/guia-retorno-venoso-pulmonar-anomalo-20260827`, aberto)
toca apenas a ficha adulta `retorno-venoso-pulmonar-anomalo` —
confirmado via `gh pr diff 576 | grep -i "retorno-venoso-pulmonar-
anomalo-fetal"` retornando vazio. Nenhum outro PR aberto edita
`retorno-venoso-pulmonar-anomalo-fetal`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap parcial mas documentado com a ficha adulta homônima (PR #576
  em aberto, sem conflito de arquivo).

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_retorno_venoso_pulmonar_anomalo_fetal.py`:
  13 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 19 testes executados, 19 passando.

## Branch e PR

Branch `claude/aprofundar-retorno-venoso-pulmonar-anomalo-fetal-20260828`,
baseada em `origin/main` sem drift no momento do commit.
