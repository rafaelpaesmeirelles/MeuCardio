# Tudo com Tudo — Cardiomiopatias (novo verbete-hub) — 27/08/2026

Sexto ciclo independente do dia de produção Tudo com Tudo (após endocardite
infecciosa PR #553, pericardite PR #554, hipertensão pulmonar PR #555,
síncope PR #560 e valvopatias PR #563).

## Lacuna identificada

O corpus já tinha 27 documentos publicados e revisados em
`content/Cardiomiopatias/` (diretriz ESC 2023 — primeira diretriz abrangente
de cardiomiopatias —, diretriz brasileira 2024 de CMH, ensaios de
inibidores de miosina cardíaca, ATTR-ACT/tafamidis, acoramidis, danicamtiv,
registro InterTAK de Takotsubo, tratamento etiológico de Chagas), mas
**nenhum verbete-hub geral de cardiomiopatia do adulto** — só entries de
subpopulação já existentes (`cardiomiopatia-periparto`,
`cardiomiopatias-pediatricas`, `amiloidose-cardiaca-idoso`). Confirmado sem
colisão com nenhum PR aberto.

## Escopo e cuidado com duplicação

O hub cobre CMH, CMD, cardiomiopatia arritmogênica (ACM/ARVC), amiloidose
cardíaca (ATTR e AL), Takotsubo, cardiomiopatia chagásica, doença de Fabry e
taquicardiomiopatia. Deliberadamente NÃO duplica o escopo de
`cardiomiopatia-periparto`, `cardiomiopatias-pediatricas` nem
`amiloidose-cardiaca-idoso` — esses verbetes-irmãos são citados por nome em
`special_populations` (texto), nunca incluídos em `related_document_slugs`.

## Conteúdo produzido

Registro novo `cardiomiopatias` (área geral): epidemiologia por subtipo com
a reclassificação fenotípica ESC 2023 (NDLVC substituindo "não compactação",
Takotsubo deixando de ser cardiomiopatia primária), apresentação por
fenótipo (8 itens), `diagnostic_approach` estruturado (objeto com sub-chaves
— algoritmo de amiloidose por cintilografia, critérios de Padua para ACM,
HCM Risk-SCD), diferenciais (9), testes (8, com limitações), red flags (9),
tratamento (~5.500 caracteres cobrindo inibidores de miosina, danicamtiv,
tafamidis/acoramidis, restrição esportiva em ACM), fluxo ambulatorial (9) e
de emergência (5), monitorização (6), populações especiais (6), 10
perguntas e 11 regras de assistente determinístico.

## Fontes primárias

Diretriz ESC 2023 de cardiomiopatias (PMID 37622657, primeira diretriz
abrangente do tema); diretriz brasileira 2024 de CMH; HCM Risk-SCD
(O'Mahony 2014, PMID 24126876); registro InterTAK de Takotsubo (Templin
2015, PMID 26332547); algoritmo não invasivo de amiloidose ATTR (Gillmore
2016, PMID 27143678; Garcia-Pavia 2021, PMID 33825853); ATTR-ACT/tafamidis
(Maurer 2018, PMID 30145929); ensaios EXPLORER-HCM/SEQUOIA-HCM de
inibidores de miosina cardíaca. Lista completa em `source_refs` (10
referências).

## Relações Tudo com Tudo

32 `related_document_slugs`: 27 de `content/Cardiomiopatias/` mais 5 de
outras pastas (cardiopediatria, cardiogeriatria, arritmias, esporte,
dispositivos) com menção direta e explícita a cardiomiopatia no corpo do
texto. `patient_material_slug` omitido deliberadamente: não há, em
`material-paciente/metadados.json`, um material verdadeiramente geral sobre
cardiomiopatia (todos os 14 candidatos são específicos a um subtipo) —
recomenda-se avaliar a criação de um material geral em ciclo futuro.

## Riscos e limitações

- Ficha nasce com `review_status: pendente_revisao`.
- Nenhum documento, checklist, trilha ou material novo foi criado.
- Nenhuma dose de fármaco foi incluída.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9497`
  (+1 sobre baseline de main, nenhum documento novo).
- `scripts/content_inventory.py --strict`: contagens exatas, `invalid: []`, `missing: []`.
- `backend/tests/test_tudo_com_tudo_cardiomiopatias.py` (novo) +
  `test_canonical_content_review_status.py`: todos passando.
- `python -c "import app.main"`: importa sem erro.

## Branch e PR

Branch `claude/tudo-com-tudo-lacuna-6-20260827`, base `main` (ciclo
independente, não empilhado). Reconstruído sobre o main atual em 27/08/2026,
após main avançar com a mesclagem dos PRs #562 (lote 5), #560/#563 já
integrados e o lote de AVC (#566). Sem merge, deploy ou publicação
automática.
