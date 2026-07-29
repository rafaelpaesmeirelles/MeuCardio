# Cobertura da base científica — Corvia

Estado em 29/07/2026. Todos os números são medidos diretamente sobre os arquivos do
repositório — `theme:` do front matter em `content/`, e os `metadados.json` das outras
quatro frentes. Nenhum número é estimado.

## Resumo

| Frente | Itens | Publicados | Situação |
|---|---:|---:|---|
| `content/` — biblioteca científica | 241 | 235 | 27 temas cobertos; 29 são fluxogramas, 23 publicados |
| `galeria/` — achados de imagem | 36 | 36 | ✅ verificada item a item |
| `exames/` — marcadores e exames | 17 | 17 | ✅ verificada item a item |
| `evidencias/` — recomendações pontuais | 32 | 32 | 20 verificadas item a item; 12 novas em 29/07 |
| `estudos/` — ensaios e metanálises | 18 | 18 | 15 verificados item a item; 3 novos em 29/07 |
| **Medicamentos** (tabela `drugs`) | **100** | **88** | reconstruída de `content/Farmacologia`; em conferência contra bula brasileira |

## `content/` — 241 documentos

| Tema | Docs | Pend. revisão |
|---|---:|---:|
| Farmacologia | 96 | 68 |
| Cardiomiopatias | 11 | 8 |
| Calculadoras | 8 | 3 |
| Aorta e doença arterial periférica | 7 | 1 |
| Dispositivos | 7 | 2 |
| Doença coronariana | 7 | 5 |
| Gravidez | 7 | 0 |
| Terapia intensiva | 7 | 4 |
| Arritmias | 6 | 1 |
| Cardio-oncologia | 6 | 1 |
| Febre reumática | 6 | 1 |
| Pericárdio | 6 | 2 |
| Prevenção e lipídios | 6 | 4 |
| Síncope | 6 | 2 |
| Valvopatias | 6 | 4 |
| Cardiopatias congênitas | 5 | 1 |
| Diabetes e cardiologia | 5 | 0 |
| Endocardite | 5 | 2 |
| Fibrilação atrial | 5 | 2 |
| Hipertensão | 5 | 3 |
| Hipertensão pulmonar | 5 | 1 |
| Insuficiência cardíaca | 5 | 3 |
| Perioperatório | 5 | 1 |
| Saúde mental e cardiologia | 4 | 1 |
| Tromboembolismo | 3 | 2 |
| Comunicação clínica | 1 | 0 |
| Geral | 1 | 1 |

**Total: 241 documentos, 123 pendentes de revisão** — 68 deles em Farmacologia, que
concentra mais da metade da fila.

A queda de 250 para 241 não é perda de conteúdo: são as **11 fusões de pares
complementares** descritas no fim deste arquivo, mais as duplicatas de metoprolol,
varfarina e HAS-BLED, menos os 6 fluxogramas escritos em 29/07. Todo documento
removido do disco foi **despublicado** no banco — conferido em 29/07/2026 comparando
os 235 slugs publicados contra os 241 arquivos: **nenhum órfão publicado**. Os 22
registros que sobram no banco sem arquivo estão todos fora do ar.

"Pend. revisão" conta documentos com `review_status` diferente de `revisado`. Não
significa que estejam errados: significa que ninguém confirmou a fonte. A Fase B mostrou
que essa distinção importa — ver abaixo.

## As quatro frentes JSON

| Frente | Itens | Temas cobertos |
|---|---:|---|
| `galeria/` | 36 | 23 |
| `exames/` | 17 | 16 |
| `evidencias/` | 32 | 18 |
| `estudos/` | 18 | 15 |

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

1. **Medicamentos saiu do zero, mas não está conferida.** A base foi reconstruída de
   `content/Farmacologia` pelo `extrair_drugs_de_markdown.py` — **100 registros, 88
   publicados** em 29/07/2026. O que falta é conferência contra bula brasileira, em
   andamento, e resolver o `drug_class` com quase um valor distinto por fármaco, que
   serve para ler e é inútil como filtro — e é por ele que a API filtra.
2. **A busca não cobre as quatro frentes JSON.** `app/api/search.py` consulta só a
   tabela `documents`. Os 103 itens de galeria, exames, evidências e estudos são
   invisíveis para quem pesquisa. A lacuna cresceu junto com o conteúdo.
3. **Farmacologia concentra 68 dos 123 pendentes** de revisão. Segue sendo o maior bloco
   de conteúdo não verificado do sistema. O método que funciona: bula do detentor do
   registro no Brasil, baixada com `curl` e User-Agent de browser — o `WebFetch` toma
   403 na maioria dos sites de laboratório.
4. **"Geral" (1 documento) segue mal classificado.** Era 2; o de diabetes foi movido na
   fusão de pares. Resta o de gestação, que usa diretriz mais recente que a dos
   documentos atuais de Gravidez — reclassificar exige conciliar conteúdo, não só mover
   arquivo.
5. **Marcações de verificação: 47, em 38 arquivos de `content/`.** Cada uma é uma
   pergunta específica e respondível, não incerteza genérica. Zero nas quatro frentes
   JSON.
6. **Fluxogramas: 29 escritos, 23 publicados.** Os 6 temas que faltavam foram cobertos
   em 29/07/2026 — dislipidemia, amiloidose cardíaca, avaliação perioperatória,
   cardio-oncologia, febre reumática e cardiopatia congênita do adulto. **Os 6 que
   seguem fora do ar** são os escritos na sessão anterior e ainda sem aval do Rafael:
   síndrome coronariana crônica, regurgitação mitral, bradiarritmia e marcapasso,
   taquicardia de QRS largo, pericardite aguda e miocardite aguda.
7. **Profundidade, não amplitude, é o gargalo das frentes JSON.** `estudos` cobre 15
   temas dos 27 de `content/`; `evidencias`, 18. Cardiopatias congênitas, febre
   reumática e comunicação clínica não têm estudo nenhum.

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

## Duplicatas de tema: 11 pares complementares — RESOLVIDO em 29/07/2026

Os 11 pares abaixo **foram fundidos**, e os documentos absorvidos foram removidos do
disco e despublicados no banco. A tabela fica como registro do que foi feito e do
critério usado — é a mesma varredura que vale repetir quando a base crescer.

Varredura por sobreposição de assunto entre todos os documentos, filtrada por
`kind` para não confundir fluxograma com protocolo do mesmo tema — esse par é
legítimo e foi excluído. Sobraram **11 pares reais, todos complementares**:
em nenhum deles um documento contém o outro. As seções se dividem entre os
dois, de modo que **nenhum dos dois está completo**.

| tema | documentos | seções em comum |
|---|---|---|
| Síndrome coronariana aguda (ESC 2023) | estrutura-detalhada × diagnostico-e-tratamento | 2 de 13 e 9 |
| Endocardite infecciosa (ESC 2023) | versao-completa × base | 1 de 14 e 6 |
| Ablação de FA (ESC 2024) | versao-completa × base | 0 de 8 e 7 |
| Hipertensão pulmonar (ESC/ERS 2022) | versao-completa × base | 0 de 7 e 13 |
| IC — atualização focada 2023 | atualizacao-focada × complemento | 1 de 10 e 8 |
| SCAI shock | complemento × classificacao | 0 de 7 e 11 |
| Choque cardiogênico | drogas-vasoativas × esc-2023-acs | 2 de 5 e 9 |
| TEP agudo (ESC 2019) | esc-2019 × escers-2019 | 2 de 9 e 14 |
| TVP aguda | aguda-diagnostico × diagnostico-e-tratamento | 3 de 11 e 12 |
| Valvopatia (ESC/EACTS) | 20212025 × vhd | 4 de 13 e 9 |
| DCV no diabetes (ESC 2023) | estratificacao-de-risco × esc-2023 | 1 de 10 e 13 |

Por que isso importa mais do que parece: quem procura "endocardite" encontra
dois documentos e lê um deles. Se pegar o errado, perde os critérios de Duke
modificados ou perde os esquemas de antibiótico — **cada um está num arquivo
diferente**. A fusão é o mesmo trabalho já feito em losartana, metoprolol,
varfarina e HAS-BLED, e pelo mesmo motivo.

Dois falsos positivos foram descartados na conferência, porque compartilhavam
palavras sem compartilhar assunto: síndrome aórtica aguda × síndrome
coronariana aguda, e cardiomiopatia arritmogênica × cardiomiopatia dilatada.
