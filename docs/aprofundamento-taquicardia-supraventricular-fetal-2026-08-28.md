# Aprofundamento Tudo com Tudo — Taquicardia supraventricular fetal — 28/08/2026

## Contexto

Vigésimo sexto lote de conteúdo do dia. A ficha
`taquicardia-supraventricular-fetal` (área `cardiopediatria`, categoria
`cardiologia_fetal`, subtype `arritmia_fetal`, `prevalence_rank: 9`) já
tinha `patient_material_slug` e 1 `related_document_slug` preenchidos,
além de `presentation`/`differentials`/`tests`/`red_flags` básicos em
bullet (`completeness: intermediario`), mas zero `epidemiology`,
`diagnostic_approach`, `treatment_summary` ou máquina do assistente
(1 `source_ref`).

## Pivôs deste ciclo (transparência)

Dois alvos foram descartados antes de qualquer dispatch de pesquisa:

1. **`extrassistoles-fetais`** — um agente de busca de lacunas propôs
   este slug, mas verificação independente minha (leitura real dos
   arquivos, não apenas grep) mostrou que os "3 candidatos" tinham
   menção zero, tangencial (1 linha, como gatilho de outra arritmia),
   ou eram uma **negação explícita** de conexão (o próprio documento
   avisa o leitor a não confundir os dois temas). Corpus insuficiente
   confirmado — mesmo status de `tumores-cardiacos-fetais`.
2. **`cardiotoxicidade-inibidor-proteassoma`** — um segundo agente
   propôs este slug como livre de colisão, mas eu confirmei via
   `gh pr diff 551 | grep` que a PR #551 (aberta) já toca esse slug
   exato. Descartado por colisão real.

Uma terceira tentativa de busca, com a lista completa de exclusões
conhecidas e reforço para leitura real de documentos, concluiu que
**todas as 41 fichas `completeness=basico`** do corpus já estavam
esgotadas (completadas hoje, em colisão com PR aberta, ou de corpus
insuficiente já confirmado). Ampliei então a busca para fichas
`completeness=intermediario`, onde encontrei `taquicardia-
supraventricular-fetal` — verificação própria confirmou ausência de
colisão real com as PRs #564 e #581 (que aparecem em buscas por
palavra-chave, mas cujos diffs não tocam este slug exato) e 2 novos
vínculos genuínos por leitura direta dos documentos.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (TSV é a
   taquiarritmia sustentada fetal mais comum, 60-70% dos casos;
   mecanismo predominante é reentrada AV por via acessória; risco de
   hidropisia correlaciona com frequência e duração sustentada),
   `presentation` expandida de 4 para 11 itens (por mecanismo:
   reentrada, flutter, taquicardia atrial ectópica, juncional),
   `diagnostic_approach` (diferenciação ecocardiográfica dos
   mecanismos por relação atrioventricular via Doppler pulsado
   simultâneo/M-mode/Doppler tecidual), `differentials` expandido de 3
   para 7, `tests` expandido de 3 para 9, `red_flags` expandido de 4
   para 8, `source_refs` (6, todos os PMIDs verificados individualmente
   via NCBI e-utils).
2. **Conduta e assistente** — `treatment_summary` (terapia
   farmacológica transplacentária como primeira linha, sem doses;
   hidropisia reduz eficácia e aumenta urgência; monitorização materna
   obrigatória; parto antecipado é conduta de exceção, não trata a
   arritmia), `ambulatory_flow` (10), `emergency_flow` (8),
   `monitoring` (8), `assistant_questions` (13), `assistant_rules` (9,
   priority 95 para TSV sustentada + hidropisia).
3. **Populações especiais e conexões** — `special_populations` (7:
   sem hidropisia, com hidropisia, intermitente, flutter associado,
   gestante em uso de antiarrítmico, recém-nascido pós-conversão,
   refratária próxima ao termo), `related_document_slugs` (3, união do
   original com 2 novos, confirmados por trecho citado).

## Verificação de citações

Todos os 6 PMIDs desta rodada foram verificados individualmente via
NCBI e-utils antes da montagem — todas as 6 referências corretas
quanto a título/periódico/ano/volume/páginas. Nenhuma correção
necessária.

## Verificações feitas na montagem

- Os 3 `related_document_slugs` finais (piso mínimo da regra Tudo com
  Tudo) verificados individual e programaticamente quanto à resolução,
  ao escopo e à menção explícita de TSV/taquiarritmia fetal no texto.
- **Piso exatamente atingido, não excedido**: busca ampla (própria e
  do agente da Parte 3, independentemente) não encontrou um quarto
  candidato genuíno — os 2 novos vínculos foram confirmados por trecho
  citado antes da montagem, sem fabricar uma conexão adicional para
  parecer mais robusto.
- **Overlap pré-existente e legítimo** (não introduzido por este
  lote): `arritmias-fetais-taquicardia-supraventricular-e-bloqueio-
  atrioventricular-total-tratamento-transplacentario` também vinculado
  por `bloqueio-atrioventricular-fetal`, `flutter-atrial-fetal` e
  `hidropisia-fetal-cardiovascular`; `planejamento-do-parto-na-
  cardiopatia-fetal-...` também vinculado por `tetralogia-de-fallot` e
  `planejamento-parto-cardiopatia-fetal` — documentado no teste
  dedicado.
- `patient_material_slug` original preservado sem alteração —
  reconfirmado como existente.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente; antiarrítmicos (digoxina, flecainida, sotalol)
citados apenas por nome. Estrutura de perguntas e regras validada com
o motor de regras real — todos os operadores usados pertencem ao
conjunto permitido, nenhuma regra usa a chave `monitoring` (não
permitida) dentro de `add`.

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
2014 sobre diagnóstico e tratamento de cardiopatia fetal, o estudo
comparativo de Jaeggi et al. (2011, Circulation) sobre eficácia de
digoxina/flecainida/sotalol, e revisões sobre mecanismos e predição de
hidropisia.

## Coordenação com Codex

PRs #564 e #581 (ambas abertas) aparecem em buscas por palavra-chave
relacionadas a este tema, mas `gh pr diff` confirmou que nenhuma toca
o slug exato `taquicardia-supraventricular-fetal`.

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- `related_document_slugs` no piso mínimo (3) — corpus não permite
  mais vínculos genuínos no momento.
- Overlap parcial mas documentado com 4 fichas do mesmo cluster.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_taquicardia_supraventricular_fetal.py`:
  12 testes, todos passando (1 correção durante desenvolvimento, para
  documentar overlap pré-existente descoberto pelo próprio teste).
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-taquicardia-supraventricular-fetal-20260828`,
baseada em `origin/main` sem drift no momento do commit.
