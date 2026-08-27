# Lote 4 de profundidade especializada — 27/08/2026

Quarto lote consecutivo de aprofundamento do Guia de Doenças (empilhado sobre
o lote 3, PR #551). Nenhum slug novo foi criado: as oito fichas abaixo já
existiam na coleção `doencas/metadados.json`, com `completeness: intermediario`
e conteúdo resumido; este lote as leva a `completeness: completo`, com
conteúdo auditável e fontes primárias verificadas.

## Fichas aprofundadas

| Slug | Área | Categoria |
|---|---|---|
| `insuficiencia-cardiaca-no-idoso` | cardiogeriatria | insuficiencia_cardiaca |
| `pre-eclampsia-e-risco-cardiovascular` | gravidez | hipertensao_na_gestacao |
| `cardiomiopatia-periparto` | gravidez | cardiomiopatia |
| `fibrilacao-atrial-no-idoso` | cardiogeriatria | arritmia |
| `cardiotoxicidade-por-antraciclinas` | cardiooncologia | toxicidade_por_tratamento |
| `miocardite-por-inibidor-checkpoint` | cardiooncologia | toxicidade_por_tratamento |
| `tetralogia-de-fallot` | cardiopediatria | cardiopatia_congenita |
| `transposicao-das-grandes-arterias` | cardiopediatria | cardiopatia_congenita |

Cada ficha recebeu: `epidemiology` com números e referência primária,
`diagnostic_approach` (texto corrido ou, em `insuficiencia-cardiaca-no-idoso`,
objeto estruturado "o que não muda / o que muda no idoso"), `differentials`,
`tests` com limitações explícitas, `red_flags`, `ambulatory_flow`,
`emergency_flow`, `treatment_summary`, `monitoring`, `special_populations`,
`assistant_questions`/`assistant_rules` determinísticos e seguros (sem
reproduzir escore proprietário mWHO/HFA-ICOS), e `related_document_slugs`
expandidos (Tudo com Tudo).

## Fontes primárias

Diretrizes de sociedade e estudos originais citados por ficha, incluindo:
Bailliard & Anderson (Orphanet J Rare Dis 2009, tetralogia de Fallot),
Szymanski et al. (StatPearls 2025, TGA), Gatzoulis et al. (Circulation
1995/Lancet 2000, arritmia pós-Fallot), Slouha et al. (Cureus 2023, timing de
troca valvar pulmonar), ESC 2024 (HAS-BLED classe III, FA no idoso), diretriz
ESC de cardio-oncologia (antraciclinas/inibidores de checkpoint), AHA/ACC
2018/2019 (cardiopatia congênita do adulto — citação sinalizada como
verificação humana pendente por bloqueio de acesso ao texto integral em
`transposicao-das-grandes-arterias`), entre outras listadas em `source_refs`
de cada registro.

## Conexões Tudo com Tudo

Todos os `related_document_slugs` novos foram verificados para resolver
exclusivamente contra `content/**/*.md` (documentos), nunca contra
Farmacologia/Calculadoras/Exames. `patient_material_slug` foi preservado ou
ampliado apenas quando um material mais específico foi encontrado; duas
fichas (`insuficiencia-cardiaca-no-idoso`, `pre-eclampsia-e-risco-cardiovascular`)
deliberadamente não ganharam `patient_material_slug` por não haver material
específico o suficiente para não duplicar/confundir com registros vizinhos.

## Riscos e limitações

- `transposicao-das-grandes-arterias`: a diretriz AHA/ACC 2018/2019 de
  cardiopatia congênita do adulto (PMID 30586767) teve o texto integral
  bloqueado nesta sessão (HTTP 403); as afirmações sobre ccTGA/ventrículo
  direito sistêmico dependem de documento-irmão já verificado em sessão
  anterior desta mesma base — **verificação humana pendente** deste ponto
  específico.
- Nenhuma dose de fármaco foi incluída ou alterada em nenhum campo novo.
- Todas as oito fichas permanecem `review_status: pendente_revisao` —
  aprofundamento editorial não substitui revisão clínica humana.

## Gates

- `scripts/audit_tudo_com_tudo.py`: `broken_references: []`, `total_items: 9494`
  (baseline de `main` em 27/08/2026, já com lote 3 e demais lotes/hubs
  mesclados e revisados — inalterado por este lote de edição, sem
  slug/documento novo).
- `scripts/content_inventory.py --minimum-records 9494 --minimum-files 2193 --strict`:
  contagens exatas, `invalid: []`, `missing: []`.
- `backend/tests/test_condicoes_profundas_lote4.py` (novo): protege apenas
  as 8 fichas deste lote — a proteção dos lotes 2/3 e dos verbetes adultos
  já é responsabilidade dos próprios arquivos de teste desses lotes, hoje
  presentes em `main` (mesclados e revisados).
- `backend/tests/test_condicoes_profundas_lote3.py` e
  `test_canonical_content_review_status.py`: passando sem alteração,
  confirmando que este lote não tocou em nenhum registro fora do seu
  escopo.
- `python -c "import app.main"`: importa sem erro.

## Branch e PR

Branch `claude/condicoes-profundas-lote4-20260827`, empilhada sobre
`claude/condicoes-profundas-lote3-20260827` (PR #551). Sem merge, deploy ou
publicação automática.


## Nota sobre o estado do main

Durante a produção deste lote, `origin/main` avançou substancialmente (mais
de 30 commits) além do ponto em que a branch deste lote 4 havia sido criada
(empilhada sobre o lote 3): o próprio lote 3 (PR #551) e os lotes/hubs
anteriores já foram mesclados e revisados (`review_status: revisado`) em
`main`, junto de features não relacionadas (exportação em PDF/PowerPoint/
Word, Central de Cardiologia Intensiva/UCO). Este lote 4 foi rebaseado sobre
o `main` atual antes do commit final — a branch deixa de estar empilhada
sobre a branch do PR #551 (já mesclada) e passa a ter `main` como base direta.
