# Cobertura da base científica — MeuCardio

Estado em 28/07/2026. Todos os números são medidos diretamente sobre os arquivos do
repositório — `theme:` do front matter em `content/`, e os `metadados.json` das outras
quatro frentes. Nenhum número é estimado.

## Resumo

| Frente | Itens | Publicados | Situação |
|---|---:|---:|---|
| `content/` — biblioteca científica | 250 | 249 | 26 temas cobertos; 16 são fluxogramas |
| `galeria/` — achados de imagem | 36 | 36 | ✅ verificada item a item |
| `exames/` — marcadores e exames | 17 | 17 | ✅ verificada item a item |
| `evidencias/` — recomendações pontuais | 20 | 19 | ✅ verificada item a item |
| `estudos/` — ensaios e metanálises | 15 | 15 | ✅ verificada item a item |
| **Medicamentos** (tabela `drugs`) | **0** | **0** | **zerada — sem fonte de dados** |

## `content/` — 250 documentos

| Tema | Docs | Pend. revisão |
|---|---:|---:|
| Farmacologia | 100 | 78 |
| Calculadoras | 10 | 10 |
| Cardiomiopatias | 10 | 9 |
| Doença coronariana | 9 | 8 |
| Fibrilação atrial | 8 | 7 |
| Aorta e doença arterial periférica | 7 | 1 |
| Gravidez | 7 | 0 |
| Terapia intensiva | 7 | 6 |
| Dispositivos | 6 | 2 |
| Endocardite | 6 | 3 |
| Hipertensão | 6 | 4 |
| Hipertensão pulmonar | 6 | 2 |
| Insuficiência cardíaca | 6 | 4 |
| Síncope | 6 | 2 |
| Tromboembolismo | 6 | 5 |
| Valvopatias | 6 | 5 |
| Arritmias | 5 | 1 |
| Cardio-oncologia | 5 | 1 |
| Diabetes e cardiologia | 5 | 0 |
| Febre reumática | 5 | 1 |
| Pericárdio | 5 | 2 |
| Prevenção e lipídios | 5 | 4 |
| Cardiopatias congênitas | 4 | 1 |
| Perioperatório | 4 | 1 |
| Saúde mental e cardiologia | 4 | 1 |
| Geral | 2 | 2 |

**Total: 250 documentos, 160 pendentes de revisão** — 78 deles em Farmacologia, que
concentra quase metade da fila.

"Pend. revisão" conta documentos com `review_status` diferente de `revisado`. Não
significa que estejam errados: significa que ninguém confirmou a fonte. A Fase B mostrou
que essa distinção importa — ver abaixo.

## As quatro frentes JSON

| Frente | Itens | Temas cobertos |
|---|---:|---|
| `galeria/` | 36 | 23 |
| `exames/` | 17 | 16 |
| `evidencias/` | 20 | 17 |
| `estudos/` | 15 | 14 |

As quatro cobrem os temas clínicos com pelo menos 1 item cada, exceto lacunas pontuais
(ex.: `estudos/` não tem item de Cardio-oncologia nem de Cardiopatias congênitas). A
prioridade agora é **profundidade** — temas com 1 item só —, não mais zerar temas.

## Verificação (Fase B) — concluída nas quatro frentes JSON

Os 88 itens das quatro frentes foram verificados contra a fonte, um a um. O que se
confirmou e o que não:

**Nenhuma fabricação.** 15/15 DOIs resolvem no Crossref, todos os PMIDs existem no
PubMed, 36/36 licenças de imagem conferem com o Wikimedia Commons, e **nenhuma imagem
está sob licença NC ou ND** — relevante porque o produto é assinatura paga.

**Os defeitos eram de outra natureza**, e o padrão vale para conteúdo futuro:

| Tipo | Exemplos |
|---|---|
| Número errado | PEITHO (desfecho primário errado nos dois grupos e no n) |
| Dado principal ausente | DAPA-HF (faltava o desfecho primário); POST 2 (omitia o resultado primário e mostrava só análises favoráveis) |
| Fonte apontando para o artigo errado | CLEAR SYNERGY citando o braço da espironolactona num registro sobre colchicina |
| Atribuição a diretriz errada | iSGLT2 na ICFEr creditado ao update de 2023 (é da ESC 2021); colchicina na DAC misturando classe de uma diretriz com a ressalva de outra |
| Fonte inaceitável | 7 no total: site de estudante, material de operadora de saúde, calculadoras, Medscape/eMedicine e um site de respostas geradas por IA |
| Imagem descrita como o que não é | ECG rotulado como infarto anterior sendo inferior; tira de monitor e trecho de 2 derivações apresentados como ECG completo |
| **Contradição entre telas** | ITB com 1,3 no verbete de exames e 1,40 no fluxograma de DAP |

A última é a mais insidiosa: só aparece quando alguém compara duas páginas — que é
exatamente o que um assinante faz. Um caso análogo foi corrigido agora nesta revisão:
um documento de `content/` tinha `theme: "Febre_reumática"` com underscore, o que
dividia o tema em dois no filtro da biblioteca.

**Lição que vale para todo conteúdo novo:** DOI que resolve não prova nada sobre o
conteúdo. É preciso abrir e conferir se o artigo é o que o registro descreve.

## Lacunas conhecidas

1. **Medicamentos é a única seção zerada.** Não é falta de importação: **não existe
   fonte de dados**. O `popular_drugs.py` lê de `knowledge/medicamentos/*.md`, formato
   do ZIP original que não está mais no repositório, e os 100 documentos de
   `content/Farmacologia/` são prosa — o comparador precisa de campos estruturados
   (`dosing` como dict, contraindicações como lista). Exige JSON escrito do zero.
2. **A busca não cobre as quatro frentes JSON.** `app/api/search.py` consulta só a
   tabela `documents`. Os 88 itens de galeria, exames, evidências e estudos são
   invisíveis para quem pesquisa.
3. **Farmacologia concentra 78 dos 160 pendentes** de revisão. É o maior bloco de
   conteúdo não verificado do sistema.
4. **"Geral" (2 documentos) segue mal classificado** — são "Doença Cardiovascular e
   Gestação (ESC 2025)" e "Doença Cardiovascular em Pacientes com Diabetes (ESC 2023)",
   que deveriam estar em Gravidez e Diabetes e cardiologia. O de gestação usa uma
   diretriz mais recente que a dos documentos atuais de Gravidez, então reclassificar
   exige conciliar conteúdo, não só mover arquivo.
5. **Colchicina na pericardite aguda** (`evidencias`) é o único item fora do ar,
   aguardando conferência de classe e nível na tabela da ESC 2015 — ver `CLAUDE.md`.
6. **Fluxogramas:** 16 publicados. Ainda sem fluxograma: regurgitação mitral,
   miocardite, amiloidose cardíaca, bradiarritmia e marcapasso, taquicardia de QRS
   largo e TV, síndrome coronariana crônica, pericardite, cardiopatia congênita do
   adulto, cardio-oncologia, avaliação perioperatória, febre reumática, dislipidemia.

## Como carregar e publicar conteúdo

Não precisa de rebuild — conteúdo entra por rota, com o token de admin:

```
POST /api/admin/import                       # documentos de content/
POST /api/admin/conteudo/carregar            # as quatro frentes JSON
GET  /api/admin/conteudo/pendentes           # o que aguarda publicação
POST /api/admin/conteudo/publicar            # publica; publicar:false despublica
```

**Publicar é decisão humana e mora no banco, nunca no arquivo.** O campo `published` do
JSON é ignorado pelos carregadores de propósito — antes dessa guarda, qualquer recarga
despublicava em silêncio tudo que já estava no ar.

## Histórico desta base

1. Migração do ZIP do corpus legado (`migrar_corpus_legado.py`): 164 documentos.
2. Extração do módulo de CDI a partir de um arquivo texto mal identificado como PDF
   (layout em duas colunas reconstruído manualmente).
3. Extração de `Faça___3_.md` (225 módulos adicionais, `migrar_perplexity_md.py`).
4. Consolidação entre temas (`consolidar_temas.py`): as migrações 1 e 3 usavam uma lista
   de palavras-chave cuja ordem causava falso positivo (ex.: "FA não valvar" lido como
   Valvopatias por conter "valvar"), produzindo 53 documentos duplicados em dois temas.
5. Três rodadas de expansão autônoma em `content/` (44 documentos) e duas nas quatro
   frentes JSON (24 itens), cobrindo temas ausentes e insuficientes.
6. Fluxogramas clínicos: 16 documentos, todos convertidos para árvore de decisão estrita
   (formato obrigatório descrito no `CLAUDE.md`).
7. **Carga inicial das quatro frentes JSON no banco.** Elas apareciam vazias na interface
   desde sempre — não por falta de conteúdo, mas porque os carregadores nunca tinham
   rota que os chamasse. 88 itens publicados de uma vez.
8. **Fase B — verificação item a item** das quatro frentes contra a fonte, com correção
   de 20 defeitos e remoção de 7 fontes inaceitáveis.

**Limitação conhecida:** a consolidação do item 4 corrige duplicatas (mesmo documento em
dois temas). Documentos que existem em um único tema mas foram classificados errado —
sem duplicado para revelar o erro — podem não ter sido pegos. O caso do
`Febre_reumática` com underscore, encontrado agora, é exemplo disso.
