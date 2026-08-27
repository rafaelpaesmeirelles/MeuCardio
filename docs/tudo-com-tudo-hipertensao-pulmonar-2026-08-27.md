# Tudo com Tudo — Hipertensão Pulmonar (verbete-hub adulto), 27/08/2026

## Lacuna identificada

Terceiro ciclo independente Tudo com Tudo do dia (os dois primeiros produziram os PRs #553 — endocardite infecciosa — e #554 — pericardite). `content/Hipertensão_pulmonar/` é a **maior pasta de content/ sem verbete geral adulto** entre todas as auditadas nos três ciclos: **61 documentos** já publicados e revisados — diretriz ESC/ERS 2022 completa, Diretriz Brasileira 2026 (GRADE), e uma extensa série de ensaios de ponta (STELLAR, ZENITH, SOTERIA, HYPERION, GRIPHON, TRITON, INCREASE, PATENT-1/CHEST-1, MERIT-1, BREATHE-5, MAESTRO) — mais **10 materiais ao paciente** já publicados e o protocolo de emergência "falência aguda de ventrículo direito". Mesmo assim, `doencas/metadados.json` só tinha `hipertensao-pulmonar-pediatrica` (cardiopediatria) e `hipertensao-pulmonar-gravidez` (gravidez) — nenhum verbete cobrindo o adulto geral com a classificação em 5 grupos que amarra o restante do acervo.

Dois candidatos alternativos (síncope, 31 documentos; cardiomiopatia hipertrófica, 5-6 documentos centrais dentro de uma pasta fragmentada de 27) ficaram atrás por volume/estrutura.

## PRs abertos evitados

Confirmado via `gh pr list --state open` (274 PRs) e `gh pr diff <N> -- doencas/metadados.json` em cada PR relevante: nenhum toca `doencas/metadados.json` com slug de hipertensão pulmonar, síncope, cardiomiopatia hipertrófica, valvopatia ou aorta. Único PR que toca `doencas/` além dos hubs já anunciados é o #543 (slug `sindrome-coronariana-aguda`, sem sobreposição).

## Escopo e cuidado com duplicação

O verbete geral **não duplica** `hipertensao-pulmonar-pediatrica` nem `hipertensao-pulmonar-gravidez`: o único documento da pasta especificamente sobre HAP na gestação (`hipertensao-arterial-pulmonar-na-gestacao-risco-manejo-e-desfechos`) foi **deliberadamente excluído** do `related_document_slugs` — pertence ao registro de gravidez, testado explicitamente (`test_nao_duplica_conteudo_de_gravidez_ou_pediatria`).

## Conteúdo produzido

Um único registro novo em `doencas/metadados.json`:

- **slug**: `hipertensao-pulmonar` — **name**: Hipertensão pulmonar — **area**: geral — **category**: circulacao_pulmonar — **subtype**: cinco_grupos_esc_ers_2022 — **completeness**: completo — **fonte_producao**: claude — **review_status**: pendente_revisao — **version**: 1

Campos: epidemiologia (com dado histórico de sobrevida pré/pós terapia moderna), apresentação (7 itens), abordagem diagnóstica (limiar PAPm>20mmHg de 2022, classificação em 5 grupos, via diagnóstica sequencial, critérios de diferenciação entre grupos), diferenciais (6), exames (6), red flags (6), tratamento (grupo 1 completo — 4 classes farmacológicas, estratificação de risco, reavaliação periódica — mais princípios de manejo dos grupos 2-5), fluxo ambulatorial (7) e de emergência (5, coordenado com o protocolo já existente de falência de VD), monitorização (7), **11 populações especiais/subtipos etiológicos** (BMPR2 hereditária, esclerose sistêmica, esquistossomose, HIV, drogas/toxinas, portopulmonar, sarcoidose, cardiopatia congênita, Eisenmenger, PVOD, perioperatório), assistente determinístico (5 perguntas, 5 regras validadas), tags, 18 `source_refs`.

**60 `related_document_slugs`** — o maior lote de conexão dos três ciclos do dia. Nenhum documento, checklist, trilha, material ou protocolo de emergência novo foi criado.

## Correção factual durante a síntese

Um dos agentes de pesquisa identificou e corrigiu um dado que estava invertido na minha própria instrução de pesquisa: a taxa de operabilidade cirúrgica em CTEPH é de aproximadamente **60% operável / 40% inoperável** (não o inverso, como uma leitura inicial de fonte secundária sugeria) — corrigido com base em Kim NH et al., Eur Respir J 2024, PMID 39209473, verificado de forma independente em duas fontes.

## Fontes primárias

- Humbert M, Kovacs G, Hoeper MM, et al. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. PMID 36017548.
- Hoeper MM et al. A global view of pulmonary hypertension. Lancet Respir Med. 2016. PMID 26975810.
- Humbert M et al. Registro francês de HAP. Am J Respir Crit Care Med. 2006. PMID 16456139.
- D'Alonzo GE et al. Sobrevida pré-terapia moderna (NIH). Ann Intern Med. 1991. PMID 1863023.
- Sitbon O et al. Critério de vasorreatividade. Circulation. 2005. PMID 15939821.
- Bermejo J et al. SIOVAC (sildenafila no grupo 2). Eur Heart J. 2018. PMID 29281101.
- Waxman A et al. INCREASE (treprostinil inalado no grupo 3). NEJM. 2021. PMID 33440084.
- Kim NH et al. CTEPH contemporâneo. Eur Respir J. 2024. PMID 39209473.
- Rajagopal S et al. AHA Scientific Statement, HP perioperatória. Circulation. 2023. PMID 36924225.
- Mais 9 fontes de populações especiais (BMPR2, esclerose sistêmica/DETECT, HIV, drogas/toxinas, Eisenmenger BREATHE-5/MAESTRO, PVOD, congênita/CONCOR) — ver `source_refs` completo no registro.

## Relações Tudo com Tudo

**60 vínculos diretos**, verificados por script (existem, são documento narrativo, não medicamento/exame/calculadora) e por teste automatizado (mencionam "pulmonar" no próprio texto). **1 material ao paciente** já publicado (`hipertensao-pulmonar`).

**Relação recusada e documentada**: `hipertensao-arterial-pulmonar-na-gestacao-risco-manejo-e-desfechos` — pertence ao registro `hipertensao-pulmonar-gravidez`, não ao verbete geral do adulto.

## Riscos e limitações declarados

- Correção de dado invertido (operabilidade CTEPH) documentada explicitamente no `review_note`.
- Não foi encontrada fonte primária citável para "tempo médio até diagnóstico" em anos/meses — usado, em vez disso, o dado robusto de 75% dos pacientes já em classe funcional III/IV ao diagnóstico como evidência de atraso diagnóstico.
- Nenhuma dose de fármaco específica foi incluída — apenas classe farmacológica e princípio terapêutico.

## Gates

- `audit_tudo_com_tudo.py`: 9.467 → 9.468 itens (+1), zero referência quebrada.
- `content_inventory.py --minimum-records 9468 --minimum-files 2187 --strict`: exit 0, 93 doenças (+1), 2.187 arquivos inalterados.
- Novo `backend/tests/test_tudo_com_tudo_hipertensao_pulmonar.py` (7 testes) + conjunto ampliado (7 arquivos, 60 testes): **59 passaram, 1 falha** — a mesma falha pré-existente de frontend já identificada nos PRs #553/#554.
- `python -c "import app.main"`: OK.

## Branch e PR

Branch: `claude/tudo-com-tudo-lacuna-3-20260827`, criada a partir de `origin/main` via `git worktree`, independente de todas as outras branches em andamento. Sem merge, sem deploy, sem publicação automática. Revisão clínica humana obrigatória antes de `review_status: revisado`.
