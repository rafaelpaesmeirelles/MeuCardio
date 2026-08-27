# Tudo com Tudo — Endocardite Infecciosa (verbete-hub adulto), 27/08/2026

## Lacuna identificada

Auditoria do corpus (`scripts/audit_tudo_com_tudo.py` + `scripts/content_inventory.py` sobre `origin/main`, commit `d3aad9d6`) mostrou o corpus estruturalmente saudável: 9.467 itens, zero referência quebrada em qualquer coleção, 100% de cobertura de tópico. A lacuna não era de integridade, mas de **cobertura temática num ponto de altíssima densidade já publicada**: `content/Endocardite/` reúne 28 documentos narrativos já `review_status: revisado` (diretriz completa ESC 2023, critérios Duke-ISCVID 2023, esquemas antibióticos por agente, timing cirúrgico, POET, populações especiais — prótese, TAVI, uso de droga injetável, dispositivo, fúngica, recidiva, gravidez), mais 1 protocolo de emergência e 1 material ao paciente já publicados sobre o tema — mas `doencas/metadados.json` só tinha `endocardite-pediatrica`; não existia nenhum verbete-hub de doença para o adulto. Esse acervo ficava, na prática, sem porta de entrada pela função Guia de Doenças.

Dois outros candidatos foram avaliados e descartados: cardiomiopatia hipertrófica (zero verbete, mas base de conexão já publicada bem menor — 5 checklists, 4 trilhas, 2 materiais) e tamponamento cardíaco (lado agudo já bem coberto por 2 protocolos de emergência dedicados, ganho marginal menor). Endocardite venceu pela razão descoberta/esforço: um único verbete novo destrava ~28 itens já publicados e hoje invisíveis pela falta de hub central.

## PRs abertos evitados

Confirmado via `gh pr list --state open` que nenhum dos PRs abertos toca `doencas/metadados.json` com um verbete geral de endocardite. PRs de conteúdo de endocardite hoje abertos (#192, #209, #260, #264, #296, #323, #351, #354, #388, #390, #435) propõem checklists/materiais ao paciente adicionais — coleções que este lote **não toca**. Também evitados por instrução direta do usuário: #543 (SCA), #544 (embolia pulmonar), #545 (exportação), #536/#535 (colapso/PCR), #534 (sangramento anticoagulado), e os próprios #540/#542 (já meus).

## Conteúdo produzido

Um único registro novo em `doencas/metadados.json`:

- **slug**: `endocardite-infecciosa` — **name**: Endocardite infecciosa — **area**: geral — **category**: cardiopatia_adquirida — **subtype**: infecciosa — **completeness**: completo — **fonte_producao**: claude — **review_status**: pendente_revisao — **version**: 1

Campos preenchidos, todos com fonte primária citada inline: `epidemiology`, `presentation` (8 itens), `diagnostic_approach`, `differentials` (6), `tests` (7, cada um com finalidade e limitação), `red_flags` (6), `treatment_summary`, `ambulatory_flow` (6), `emergency_flow` (5), `monitoring` (6), `special_populations` (8 subpopulações: prótese precoce/tardia, pós-TAVI, uso de droga injetável, dispositivo cardíaco, fúngica, recidiva/reinfecção, gravidez, cardiopatia congênita), `assistant_questions` (6) e `assistant_rules` (6, validados pelo motor `clinical_rule_engine`), `tags`, `source_refs` (12), `source_urls`.

Nenhum documento, checklist, trilha, material ao paciente ou protocolo de emergência novo foi criado — o lote inteiro é a criação de um único hub que se conecta ao acervo já existente.

## Fontes primárias

- Delgado V, Ajmone Marsan N, de Waha S, et al.; ESC Scientific Document Group. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44(39):3948-4042. PMID 37622656.
- Fowler VG Jr, Durack DT, Selton-Suty C, et al. The 2023 Duke-ISCVID Criteria for Infective Endocarditis. Clin Infect Dis. 2023;77(4):518-526. PMID 37138445.
- Habib G, Erba PA, Iung B, et al.; EURO-ENDO Investigators. Eur Heart J. 2019;40(39):3222-3232. PMID 31504413.
- Pries-Heje MM, et al. Five-Year Outcomes of the POET Trial. N Engl J Med. 2022;386(6):601-602. PMID 35139280.
- Duval X, et al. TEPvENDO/AEPEI — PET-CT em suspeita de EI. PMID 32488236.
- DeSimone DC, Garrigos ZE, Marx GE, et al. Blood culture-negative IE. J Am Heart Assoc. 2025;14(8):e040218. PMID 40094211.
- Shishido AA, et al. Microbial cell-free DNA sequencing in IE. Open Forum Infect Dis. 2025. PMID 40046887.
- Regueiro A, et al. TAVI e endocardite subsequente — registro internacional. JAMA. 2016;316(10):1083-1092. PMID 27529557.
- Mais 4 fontes de populações especiais (prótese precoce/tardia, uso de droga injetável, dispositivo cardíaco) — ver `source_refs` completo no registro.

Todas as fontes secundárias já publicadas no acervo (`content/Endocardite/*.md`) foram usadas como ponto de partida, mas os fatos-chave (incidência, mortalidade, critérios diagnósticos, classes de recomendação cirúrgica) foram conferidos diretamente contra a fonte primária (PMID/DOI) por 3 agentes de pesquisa independentes nesta sessão, não apenas parafraseados.

## Relações Tudo com Tudo

**28 vínculos diretos** (`related_document_slugs`), todos verificados por script como slugs existentes de `content/**/*.md` e, adicionalmente, testados (`test_related_document_slugs_sao_todos_sobre_endocardite`) para conter a palavra "endocardite" no próprio texto do documento — evitando vínculo por proximidade temática disfarçado de vínculo direto. **1 material ao paciente** (`patient_material_slug`): `endocardite-infecciosa-o-que-esperar-do-diagnostico-e-do-tratamento`, já publicado e revisado.

**Relação recusada e documentada**: `profilaxia-antibiotica-de-endocardite-infecciosa-especifica-por-lesao-congenita-aha-2007-2021` foi avaliada e **não promovida** a vínculo direto — trata de indicação de profilaxia pré-procedimento em lesões congênitas específicas, não do diagnóstico/tratamento da endocardite já instalada; classificada como proximidade temática (mesma doença como desfecho a prevenir, não o mesmo objeto do verbete).

## Riscos e limitações declaradas no `review_note`

- Inconsistência já presente na própria diretriz ESC 2023 entre a definição de "endocardite protética precoce" na seção de epidemiologia (corte de 1 ano) e na tabela formal de recomendação cirúrgica (corte de 6 meses) — registrada explicitamente no `special_populations`, não resolvida por decisão própria.
- Dado do registro pós-TAVI é de até outubro/2015, sinalizado como potencialmente desatualizado frente à evolução das próteses transcateter.
- Critério clínico/de imagem para diferenciar endocardite de dispositivo (eletrodo/valva) de infecção de bolsa isolada não foi encontrado nas fontes revisadas — declarado como lacuna explícita, não preenchido por extrapolação.
- Nenhuma dose de antibiótico específica por agente foi incluída — o `treatment_summary` referencia por nome o documento já existente no acervo (`esquemas-antibioticos-na-endocardite-infecciosa-por-agente-esc-2023`), evitando duplicar ou divergir de dose já publicada.

## Gates

- `python3 scripts/audit_tudo_com_tudo.py`: `total_items` 9.467 → 9.468 (+1), `broken_references` zero em todas as coleções, `SpecialtyDisease.related_document_slugs` 76/76 → 104/104 (+28, todos resolvidos), `SpecialtyDisease.patient_material_slug` 42/42 → 43/43.
- `python3 scripts/content_inventory.py --minimum-records 9468 --minimum-files 2187 --strict`: `exit 0`, 93 registros em `doencas/metadados.json` (+1), 2.187 arquivos (inalterado — nenhum documento novo).
- `backend/tests/test_canonical_content_review_status.py`: allowlist ampliada com o novo slug `endocardite-infecciosa`.
- `backend/tests/test_tudo_com_tudo_endocardite_infecciosa.py` (novo, 6 testes): slug genuinamente novo, marcação editorial, profundidade mínima de conteúdo, assistente determinístico validado pelo `clinical_rule_engine` (sem `mwho`/`hfa-icos`), todos os vínculos resolvem e são documentos narrativos (não medicamento/exame/calculadora), todo documento vinculado menciona "endocardite" no próprio texto.
- `python3 -c "import app.main"`: OK.
- `git diff --check`: sem espaço em branco/conflito.

## Branch e PR

Branch: `claude/tudo-com-tudo-lacuna-20260827`, criada a partir de `origin/main` (commit `d3aad9d6`) via `git worktree`, independente das branches `claude/condicoes-profundas-especializadas-lote2-20260827` (PR #542) e `claude/condicoes-profundas-lote3-20260827` (lote 3, em preparação) — este lote não depende de nenhuma delas. Sem merge, sem deploy, sem publicação automática. Revisão clínica humana obrigatória antes de `review_status: revisado`.
