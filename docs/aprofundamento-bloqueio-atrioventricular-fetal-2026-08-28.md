# Aprofundamento Tudo com Tudo — Bloqueio atrioventricular fetal — 28/08/2026

## Contexto

Décimo oitavo lote de conteúdo do dia, segundo do cluster de
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
`indicacoes-ecocardiograma-fetal`, PR #630). A ficha
`bloqueio-atrioventricular-fetal` (área `cardiopediatria`, categoria
`cardiologia_fetal`, `prevalence_rank: 32`) já tinha
`patient_material_slug` e 2 `related_document_slugs` preenchidos, mas
zero campos clínicos.

## Conteúdo produzido

Produzido por 3 agentes de pesquisa em paralelo:

1. **Epidemiologia e diagnóstico** — `epidemiology` (risco de 1-2% na
   primeira gestação afetada em mãe anti-Ro/SSA positiva, recorrência
   de 12-18% em gestação subsequente, mortalidade de 15-30% quando há
   hidropisia), `presentation` (11 formas), `diagnostic_approach` (6
   subtópicos: determinação do grau de bloqueio por Doppler mecânico,
   sorologia materna, avaliação de cardiopatia estrutural/isomerismo,
   avaliação hemodinâmica/hidropisia, vigilância seriada, monitoramento
   de resposta terapêutica), `differentials` (7), `tests` (8),
   `red_flags` (8), `source_refs` (8, incluindo AHA 2014, o estudo
   PRIDE de Friedman et al. 2008, e o registro nacional de lúpus
   neonatal de Buyon et al. 1998).
2. **Conduta e assistente** — `treatment_summary` (vigilância seriada
   semanal na janela de 18-24 semanas, corticosteroide transplacentário
   em bloqueio incompleto, imunoglobulina/hidroxicloroquina profilática
   em alto risco, beta-agonista em frequência muito baixa, planejamento
   de parto em centro com marcapasso disponível), `ambulatory_flow`
   (11), `emergency_flow` (7), `monitoring` (8), `assistant_questions`
   (14), `assistant_rules` (11, priority 98 para bloqueio completo com
   frequência muito baixa e hidropisia).
3. **Populações especiais e conexões** — `special_populations` (6:
   anti-Ro/anti-La positivo sem BAV ainda, lúpus/Sjögren materno,
   gestação anterior com BAV, BAV incompleto/janela de
   reversibilidade, BAV completo com hidropisia, BAV associado a
   cardiopatia estrutural não autoimune), `related_document_slugs` (4,
   união dos 2 originais com 2 novos).

## Verificações feitas na montagem

- Os 4 `related_document_slugs` finais verificados individual e
  programaticamente quanto à resolução, ao escopo e à menção de
  bloqueio atrioventricular/bloqueio cardíaco congênito/anti-Ro no
  texto.
- O agente da Parte 3 confirmou por grep direto que os 2 slugs
  originais existem no frontmatter dos arquivos correspondentes antes
  de reutilizá-los.
- **Overlap pré-existente** com 4 fichas irmãs do cluster fetal ainda
  não aprofundadas hoje (`taquicardia-supraventricular-fetal`,
  `flutter-atrial-fetal`, `extrassistoles-fetais`,
  `hidropisia-fetal-cardiovascular`) — não introduzido por este lote
  (os documentos já estavam nos `related_document_slugs` dessas
  fichas antes deste PR), documentado no teste dedicado como
  legítimo.
- `patient_material_slug` original
  (`gravidez-com-anticorpo-anti-ro-ssa-vigilancia-do-coracao-do-bebe`)
  preservado sem alteração — reconfirmado como existente.

Nenhuma dose de fármaco em nenhum campo — verificado
programaticamente; fármacos citados apenas por nome (dexametasona,
imunoglobulina intravenosa, hidroxicloroquina, beta-agonista), sem
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

8 referências com PMID verificado, incluindo a diretriz científica da
AHA 2014 sobre cardiopatia fetal, o estudo PRIDE de Friedman et al.
(2008) sobre vigilância com Doppler mecânico, o estudo de Jaeggi et
al. (2004) sobre tratamento transplacentário, o estudo de Izmirly et
al. (2012) sobre hidroxicloroquina profilática, e o registro nacional
de lúpus neonatal de Buyon et al. (1998).

## Coordenação com Codex

Nenhum dos PRs abertos que tocam `doencas/metadados.json` (ou
fragmentos/correções) edita `bloqueio-atrioventricular-fetal`.
Reconfirmado que a branch `codex/guia-atresia-tricuspide-20260827`
não colide (esteira distinta, sem tocar fichas do cluster fetal desta
lista).

## Riscos e limitações

- Registro fica `review_status: pendente_revisao` — não publica até
  revisão humana.
- Nenhuma dose de fármaco é citada.
- Overlap de 2 documentos com 4 fichas irmãs ainda não aprofundadas
  hoje, documentado e pré-existente.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`,
  `total_items: 9497`.
- `scripts/content_inventory.py --strict`: `invalid: []`, `missing: []`.
- `backend/tests/test_aprofundamento_bloqueio_atrioventricular_fetal.py`:
  12 testes, todos passando de primeira.
- `backend/tests/test_canonical_content_review_status.py` e
  `test_disease_fragments_canonical.py`: passando (allowlist
  unificada), 6 testes.
- `app.main` importa sem erro.
- Total: 18 testes executados, 18 passando.

## Branch e PR

Branch `claude/aprofundar-bloqueio-atrioventricular-fetal-20260828`,
baseada em `origin/main` sem drift no momento do commit.
