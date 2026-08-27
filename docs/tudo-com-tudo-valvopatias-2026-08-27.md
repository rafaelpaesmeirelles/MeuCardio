# Tudo com Tudo — Valvopatias (novo verbete-hub) — 27/08/2026

Quinto ciclo independente do dia de produção Tudo com Tudo (após endocardite
infecciosa PR #553, pericardite PR #554, hipertensão pulmonar PR #555 e
síncope PR #560, já mesclado e revisado).

## Lacuna identificada

O corpus já tinha 37 documentos publicados e revisados em
`content/Valvopatias/` (diretriz ESC/EACTS 2021→2025, registros/ensaios
PARTNER, EVOLUT, COAPT, MITRA-FR, EVEREST II, TRILUMINATE, TRISCEND II,
ALIGN-AR, SUMMIT-MAC), mas **nenhum verbete-hub geral de valvopatia do
adulto** em `doencas/metadados.json` — só entries de subpopulação já
existentes (`valvopatias-na-gravidez`, `estenose-aortica-tavi-idoso`).
Confirmado sem colisão com nenhum PR aberto via `gh pr diff <N> --
doencas/metadados.json`.

## Escopo e cuidado com duplicação

O hub cobre estenose/regurgitação aórtica, mitral e tricúspide no adulto
geral, prótese valvar (mecânica/biológica, disfunção VARC-3), trombose de
prótese, calcificação anular mitral, doença carcinoide e leak paravalvular.
Deliberadamente NÃO duplica o escopo de `valvopatias-na-gravidez`,
`estenose-aortica-tavi-idoso`, `fragilidade-pre-procedimento-cardiovascular`
nem `endocardite-infecciosa` — esses verbetes-irmãos são citados por nome em
`special_populations` (texto), nunca incluídos em `related_document_slugs`.

## Conteúdo produzido

Registro novo `valvopatias` (área geral): epidemiologia com dados de carga
global (Nkomo 2006, GBD 2020), apresentação por lesão (9 itens),
`diagnostic_approach` estruturado (objeto com sub-chaves por lesão —
critérios ecocardiográficos de gravidade, ecocardiograma sob estresse,
angiotomografia, VARC-3), diferenciais (8), testes (9, com limitações),
red flags (8), tratamento (~9.000 caracteres cobrindo TAVI vs. SAVR,
COAPT/MITRA-FR, TRILUMINATE/TRISCEND II, escolha mecânica vs. biológica,
trombose de prótese), fluxo ambulatorial (10) e de emergência (7),
monitorização (8), populações especiais (6), 15 perguntas e 12 regras de
assistente determinístico.

## Fontes primárias

Diretriz ESC/EACTS de valvopatia 2021 (PMID 34453165), atualização 2025
(PMID 40878295) e corrigendum 2026 (PMID 42452857); estudos de carga
epidemiológica (Nkomo 2006, Yadgir/GBD 2020, Chen/GBD reumática 2020);
ensaios PARTNER 2/3, Evolut Low Risk, COAPT, MITRA-FR, EVEREST II,
TRILUMINATE, TRISCEND II; classificação VARC-3 (Généreux 2021); Diretriz
Brasileira de Ergometria SBC 2024. Lista completa em `source_refs` (16
referências).

## Relações Tudo com Tudo

41 `related_document_slugs`: 37 de `content/Valvopatias/` mais 4 de outras
pastas (`Cardiologia_geriátrica/`, `Febre_reumática/`, `Gravidez/`) com
menção direta e explícita a valvopatia no corpo do texto — vínculo direto,
não proximidade temática. `patient_material_slug` omitido deliberadamente:
não há, em `material-paciente/metadados.json`, um material verdadeiramente
geral sobre doença valvar (todos são específicos a uma lesão/procedimento) —
recomenda-se avaliar a criação de um material geral em ciclo futuro.

## Riscos e limitações

- Ficha nasce com `review_status: pendente_revisao`.
- Nenhum documento, checklist, trilha ou material novo foi criado — lote
  puramente de conexão sobre conteúdo já publicado e revisado.
- Nenhuma dose de fármaco foi incluída.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9496`
  (+1 sobre baseline de main, nenhum documento novo).
- `scripts/content_inventory.py --strict`: contagens exatas, `invalid: []`, `missing: []`.
- `backend/tests/test_tudo_com_tudo_valvopatias.py` (novo) +
  `test_canonical_content_review_status.py`: todos passando.
- `python -c "import app.main"`: importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-5-20260827`, base `main` (ciclo
independente, não empilhado). Rebaseado sobre o main atual em 27/08/2026,
após main avançar com a mesclagem dos PRs #559 (lote 4) e #560 (síncope).
Sem merge, deploy ou publicação automática.


## Revisão clínica dirigida pelo Codex

Em 27/08/2026, o hub foi revisado e marcado como revisado após corrigir o uso da dobutamina no baixo fluxo/baixo gradiente, considerar a posição da bioprótese, consumir planejamento gestacional e idade em decisão compartilhada, ajustar o seguimento da regurgitação mitral primária grave e normalizar a categoria valvopatia.
