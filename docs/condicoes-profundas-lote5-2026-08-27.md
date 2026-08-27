# Lote 5 de profundidade especializada — 27/08/2026

Quinto lote de aprofundamento do Guia de Doenças, produzido a partir do
`main` atual (já com os lotes 1-4 e os hubs Tudo com Tudo anteriores
mesclados e revisados). Nenhum slug novo foi criado: as oito fichas abaixo
já existiam na coleção `doencas/metadados.json`, com `completeness:
intermediario`, e este lote as leva a `completeness: completo`.

## Fichas aprofundadas

| Slug | Área | Categoria |
|---|---|---|
| `sincope-pediatrica` | cardiopediatria | sintoma_e_sindrome |
| `comunicacao-interventricular` | cardiopediatria | cardiopatia_congenita |
| `coarctacao-da-aorta` | cardiopediatria | cardiopatia_congenita |
| `fragilidade-pre-procedimento-cardiovascular` | cardiogeriatria | avaliacao_pre_procedimento |
| `hipertensao-por-inibidor-vegf` | cardiooncologia | toxicidade_por_tratamento |
| `efeitos-cardiovasculares-tardios-radioterapia` | cardiooncologia | sobrevivencia |
| `protese-mecanica-na-gravidez` | gravidez | valvopatia_e_anticoagulacao |
| `aortopatia-na-gravidez` | gravidez | aortopatia |

`sincope-pediatrica` foi deliberadamente construída para NÃO duplicar o hub
geral de síncope do adulto (PR #560, ainda não mesclado): foca em espasmo do
choro, canalopatias com gatilho específico (LQT1-exercício/natação,
LQT2-estímulo auditivo, LQT3-sono) e ECG obrigatório em toda síncope
pediátrica — eixos ausentes no verbete adulto.

## Fontes primárias

Rao PS (Rev Cardiovasc Med 2024, CIV), Doshi & Chikkabyrappa (Cureus 2018) e
Raza et al. (Diagnostics 2023, coarctação), Afilalo et al./FRAILTY-AVR (JACC
2017, fragilidade), Chalk et al. (Obstet Med 2026, aortopatia na gravidez),
van der Zande et al./ROPAC III (Eur Heart J 2025, prótese mecânica na
gravidez), Quintero-Martinez et al. e Varvara et al. (radioterapia tardia),
Lyon et al./ESC 2022 cardio-oncologia (hipertensão por inibidor de VEGF),
entre outras listadas em `source_refs` de cada registro.

## Conexões Tudo com Tudo

Todos os `related_document_slugs` foram verificados para resolver
exclusivamente contra `content/**/*.md`, nunca contra
Farmacologia/Calculadoras/Exames.

## Riscos e limitações

- Todas as oito fichas permanecem `review_status: pendente_revisao`.
- Nenhuma dose de fármaco foi incluída em nenhum campo novo.
- Cotas de WebSearch se esgotaram durante a produção de várias fichas;
  pesquisa complementar foi feita via WebFetch direto (PMC/Europe PMC/DOI),
  sem prejuízo relevante à cobertura — limitações pontuais de acesso a
  texto integral de diretriz estão documentadas no `review_note` de cada
  registro específico.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9494`
  (inalterado — lote de edição, sem slug/documento novo).
- `scripts/content_inventory.py --strict`: contagens exatas, `invalid: []`, `missing: []`.
- `backend/tests/test_condicoes_profundas_lote5.py` (novo) +
  `test_canonical_content_review_status.py`: todos passando.
- `python -c "import app.main"`: importa sem erro.

## Branch e PR

Branch `claude/condicoes-profundas-lote5-20260827`, base `main` (lotes
anteriores já mesclados, portanto sem empilhamento). Sem merge, deploy ou
publicação automática.


## Revisão clínica dirigida pelo Codex

Em 27/08/2026, os oito registros foram revisados e marcados como revisados após correção dos bloqueios de segurança: faixa etária do espasmo do choro, escalonamento da CIV sintomática, limites da CFS, procedimentos urgentes, lesão aguda de órgão-alvo sob anti-VEGF, dispneia e dose radioterápica desconhecida, anticoagulação da prótese mecânica e estratificação indexada da aorta na síndrome de Turner.
