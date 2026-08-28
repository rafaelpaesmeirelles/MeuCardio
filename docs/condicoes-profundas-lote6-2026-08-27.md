# Lote 6 de profundidade especializada — 27/08/2026

Sexto lote de aprofundamento do Guia de Doenças, produzido a partir do
`main` atual (já com os lotes 1-5 e os hubs Tudo com Tudo anteriores
mesclados e revisados). Nenhum slug novo foi criado.

## Fichas aprofundadas

| Slug | Área | Categoria |
|---|---|---|
| `taquicardia-supraventricular-fetal` | cardiopediatria | cardiologia_fetal |
| `sindrome-coracao-esquerdo-hipoplasico-fetal` | cardiopediatria | cardiologia_fetal |
| `arritmias-na-gravidez` | gravidez | arritmia |
| `comunicacao-interatrial` | cardiopediatria | cardiopatia_congenita |
| `isquemia-mesenterica-aguda-cardioembolica` | cardiogeriatria | emergencia_vascular |

`comunicacao-interatrial` reaproveita deliberadamente o documento conjunto e
o material para pais já publicados para `comunicacao-interventricular`
(lote5, PR #562, já mesclado) — recurso genuinamente compartilhado entre as
duas condições, com conteúdo clínico escrito especificamente para CIA.

## Fontes primárias

Tsokkou et al. (J Pers Med 2025) e Jaeggi et al. (Circulation 2011) para TSV
fetal; Bokhari et al. (World J Cardiol 2025) e Feinstein et al. (JACC 2012)
para SCEH fetal; De Backer et al./ESC 2025 para arritmias na gravidez;
Rao (Diagnostics 2022), Muroke et al. (2023/2024) e Koutroulou et al. (Front
Neurol 2020) para CIA; Bala et al./WSES 2022, ESVS 2025 e Chamseddine et al.
(J Vasc Surg 2026) para isquemia mesentérica aguda cardioembólica — entre
outras listadas em `source_refs` de cada registro.

## Riscos e limitações

- Todas as fichas permanecem `review_status: pendente_revisao`.
- Nenhuma dose de fármaco foi incluída.
- Duas fichas (SCEH fetal, TSV fetal) sinalizam explicitamente números
  citados de segunda mão dentro de revisões (não conferidos no artigo
  primário original nesta sessão) como "VERIFICAÇÃO HUMANA NECESSÁRIA" no
  `review_note`.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9496`
  (inalterado — lote de edição, sem slug/documento novo).
- `scripts/content_inventory.py --strict`: contagens exatas, `invalid: []`, `missing: []`.
- `backend/tests/test_condicoes_profundas_lote6.py` (novo) +
  `test_canonical_content_review_status.py`: todos passando.
- `python -c "import app.main"`: importa sem erro.

## Branch e PR

Branch `claude/condicoes-profundas-lote6-20260827`, base `main`. Sem merge,
deploy ou publicação automática.
