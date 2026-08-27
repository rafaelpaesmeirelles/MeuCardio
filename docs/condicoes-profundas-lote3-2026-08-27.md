# Profundidade especializada — lote 3, 27/08/2026

Empilhado sobre o lote 2 (PR #542, branch `claude/condicoes-profundas-especializadas-lote2-20260827`, commit `948681bc`), continuando a frente "continue aprofundando conteúdo do menu/função Guia de Doenças". Mesma metodologia do lote 2: autoauditoria das fichas mais superficiais e de maior impacto clínico nas áreas cardiopediatria, cardiogeriatria, cardiooncologia e gravidez, sem criar slug novo, sem tocar em condições da área geral, sem alterar contadores globais.

## Fichas aprofundadas (8)

| Slug | Área | Fontes primárias | Documentos vinculados | Material ao paciente |
|---|---|---|---|---|
| `delirium-cardiogeriatria` | cardiogeriatria | 18 (PADIS 2018, AGS 2015, ABCDEF/Pun 2019, HELP/Inouye 1999, CAM-ICU original, 4AT, DECADE) | 4 | `confusao-ou-sonolencia-na-uti-entendendo-o-delirium` |
| `risco-quedas-cardiogeriatria` | cardiogeriatria | 17 (AGS/BGS World Falls Guideline 2022, ESC Síncope 2018, AHA Hipotensão Ortostática 2024, SAFE PACE) | 4 | `cai-ou-desmaiei-por-que-e-dificil-saber-no-idoso-e-por-que-isso-importa` |
| `toxicidade-cardiovascular-car-t` | cardiooncologia | 5 | 3 | `toxicidade-cardiovascular-car-t` |
| `fluoropirimidinas-isquemia` | cardiooncologia | 12 (ESC 2022 Cardio-Oncologia, coortes de incidência por esquema, rechallenge) | 4 | `fluoropirimidinas-isquemia` |
| `sindrome-coronariana-gravidez` | gravidez | 5 | 5 | `sindrome-coronariana-gravidez` |
| `tromboembolismo-gravidez` | gravidez | 3 (ESC 2025 gravidez, ESC 2019 TEP, bula Clexane) | 7 | `tromboembolismo-gravidez` |
| `persistencia-canal-arterial` | cardiopediatria | 6 | 1 | `canal-arterial-persistente-no-bebe-prematuro` |
| `anomalia-ebstein` | cardiopediatria | 13 (AATS 2024/2025, ESC 2020 ACHD, Eckerström et al. JAHA 2024 — história natural) | 3 | `anomalia-de-ebstein-o-que-e-e-como-e-acompanhada` |

Todos: `fonte_producao: claude`, `review_status: pendente_revisao`, `completeness: completo`, `version: 2` (partiam de `basico`/`version: 1`).

## Campos adicionados/expandidos em cada ficha

epidemiology, presentation, diagnostic_approach (uma ficha — `delirium-cardiogeriatria` — usa objeto estruturado em vez de texto corrido, compatível com o schema `Mapped[dict]` do modelo e já usado em 5 registros pré-existentes do acervo), differentials, tests, red_flags, ambulatory_flow, emergency_flow, treatment_summary, monitoring, special_populations, assistant_questions, assistant_rules, tags, source_refs, source_urls, e (quando havia vínculo direto genuíno) related_document_slugs/patient_material_slug.

## Relações Tudo com Tudo — regra aplicada

Todo `related_document_slugs` foi filtrado manualmente para excluir slugs de medicamento/exame/calculadora mesmo quando tecnicamente resolvem como arquivo em `content/**/*.md` (lição herdada do lote 2, com `anticoagulacao-idoso`) — cada candidato foi verificado por caminho de pasta (`content/Farmacologia/`, `content/Calculadoras/`, `content/Exames/` excluídos). Nenhuma flag disparou neste lote: os agentes já receberam a regra explícita no prompt e devolveram apenas documentos narrativos genuínos.

## Diferenciais e riscos declarados

- `delirium-cardiogeriatria`: `diagnostic_approach` é objeto estruturado (rastreio/diferencial-de-demência/investigação-de-causa) em vez de texto único — decisão deliberada, compatível com o schema, testada explicitamente (`test_ficha_atinge_profundidade_minima_e_nao_e_mero_resumo` mede o JSON serializado).
- `fluoropirimidinas-isquemia`: rechallenge com pré-tratamento (nitrato/bloqueador de canal de cálcio) reduz recorrência mas não zera (19,2% mesmo com profilaxia) — declarado explicitamente, sem prometer eficácia total.
- `anomalia-ebstein`: inconsistência de corte temporal (6 meses vs. 1 ano) para "prótese precoce" já presente na própria fonte primária, registrada como tal, não resolvida por decisão própria.
- `risco-quedas-cardiogeriatria`: fonte genérica anterior (declaração AHA sobre UTI cardiológica geriátrica) foi rebaixada a referência de contexto e substituída, para o núcleo do conteúdo, pelas diretrizes específicas de quedas (AGS/BGS 2022) e síncope (ESC 2018) — ambas com recomendação formal de tratar queda inexplicada como síncope inexplicada.

## Testes novos

`backend/tests/test_condicoes_profundas_lote3.py` (novo, análogo ao do lote 2): slug não cria/remove registro (92 fichas mantidas), marcação editorial, profundidade mínima real (incluindo suporte a `diagnostic_approach` como dict), assistente determinístico validado pelo `clinical_rule_engine` (sem `mwho`/`hfa-icos`), vínculos Tudo com Tudo resolvidos, **proteção do lote 2** (as 8 fichas do PR #542 continuam com `version: 2`, não tocadas) e **proteção dos 5 verbetes gerais** do PR #538/#539 (área `geral`, `fonte_producao: chatgpt`).

## Gates

- `python3 scripts/audit_tudo_com_tudo.py`: `total_items` inalterado, zero referência quebrada.
- `python3 scripts/content_inventory.py --minimum-records 9467 --minimum-files 2187 --strict`: exit 0, contagens inalteradas (nenhum slug/arquivo novo, só edição de registros existentes).
- Subconjunto (`test_condicoes_profundas_lote3.py` + `test_condicoes_profundas_especializadas_lote2.py` + `test_canonical_content_review_status.py`): **74 passaram**.
- Suíte completa do backend (1649 testes): **1631 passaram, 18 falharam** — as 18 falhas são de infraestrutura/ambiente, não relacionadas a este lote: módulo Python `qrcode` ausente do venv (afeta 5 testes de assinatura digital PDF/QR), Redis indisponível no momento pontual da execução (afeta 3 testes de readiness), mais 10 falhas em `test_admin_user_delete_real_dependencies.py` e `test_email_conta_padrao_envio.py` — nenhum desses 6 arquivos de teste referencia `doencas`, `SpecialtyDisease` ou `content/`, confirmado por grep.
- `python3 -c "import app.main"`: OK.

## Branch e PR

Branch: `claude/condicoes-profundas-lote3-20260827`, criada a partir de `origin/claude/condicoes-profundas-especializadas-lote2-20260827` (commit `948681bc`, tip do PR #542). PR empilhado sobre #542 — deve ser revisado/mesclado depois dele, ou rebaseado sobre a main quando #542 for mesclado. Sem merge, sem deploy, sem publicação automática. Revisão clínica humana obrigatória antes de qualquer `review_status: revisado`.
