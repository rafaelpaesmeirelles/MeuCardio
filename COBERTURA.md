# Cobertura da base científica — Corvia

Estado em 29/07/2026, **remedido às 20h** pela sessão da Biblioteca. Todos os números
são medidos diretamente sobre os arquivos do repositório — `theme:` do front matter em
`content/`, e os `metadados.json` das outras quatro frentes; a coluna "Publicados" vem
do banco. Nenhum número é estimado.

## Resumo

| Frente | Itens | Publicados | Situação |
|---|---:|---:|---|
| `content/` — biblioteca científica | 253 | 252 | 27 temas cobertos; 29 são fluxogramas, **todos publicados** |
| `galeria/` — achados de imagem | 36 | 36 | ✅ verificada item a item |
| `exames/` — marcadores e exames | 40 | 0 | crescida de 17 para 40 pela sessão da Biblioteca em 29/07 à noite; **zero temas com 1 item só**; aguardando publicação |
| `evidencias/` — recomendações pontuais | 103 | 100 | 3 novas (anti-IL-1 na pericardite, ILR na síncope, rastreio de AAA), ainda `published: false` |
| `estudos/` — ensaios e metanálises | 45 | 41 | 4 novos (BREATHE-5, profilaxia da febre reumática, AMBITION, EINSTEIN-PE); ainda `published: false` |
| **Medicamentos** (tabela `drugs`) | **100** | **88** | reconstruída de `content/Farmacologia`; gestação e lactação fechadas em 88/88 |

O banco tem **275 registros** em `documents` contra 253 arquivos no disco: os 22
excedentes são as fusões e duplicatas já removidas do disco, todas despublicadas.
Nenhum órfão está no ar.

## `content/` — 253 documentos

| Tema | Docs | Pend. revisão |
|---|---:|---:|
| Farmacologia | 96 | 66 |
| Cardiomiopatias | 12 | 8 |
| Calculadoras | 8 | 3 |
| Doença coronariana | 8 | 5 |
| Gravidez | 8 | 0 |
| Terapia intensiva | 8 | 4 |
| Aorta e doença arterial periférica | 7 | 1 |
| Arritmias | 7 | 1 |
| Dispositivos | 7 | 2 |
| Febre reumática | 7 | 1 |
| Prevenção e lipídios | 7 | 4 |
| Cardio-oncologia | 6 | 1 |
| Endocardite | 6 | 2 |
| Hipertensão | 6 | 3 |
| Pericárdio | 6 | 2 |
| Perioperatório | 6 | 1 |
| Síncope | 6 | 2 |
| Valvopatias | 6 | 4 |
| Cardiopatias congênitas | 5 | 1 |
| Diabetes e cardiologia | 5 | 0 |
| Fibrilação atrial | 5 | 2 |
| Hipertensão pulmonar | 5 | 1 |
| Insuficiência cardíaca | 5 | 3 |
| Saúde mental e cardiologia | 4 | 1 |
| Tromboembolismo | 4 | 2 |
| Comunicação clínica | 2 | 0 |
| Geral | 1 | 1 |

**Total: 253 documentos, 121 pendentes de revisão** — 66 deles em Farmacologia, que
concentra mais da metade da fila.

A queda de 250 para 241, registrada na medição anterior, não foi perda de conteúdo:
foram as **11 fusões de pares complementares** descritas no fim deste arquivo, mais as
duplicatas de metoprolol, varfarina e HAS-BLED. Os 12 documentos que entraram depois
disso são conteúdo novo dos lotes de 29/07. Todo documento removido do disco foi
**despublicado** no banco — conferido de novo às 20h: 252 publicados contra 253
arquivos, e **nenhum órfão publicado**. Os 22 registros que sobram no banco sem
arquivo estão todos fora do ar.

"Pend. revisão" conta documentos com `review_status` diferente de `revisado`. Não
significa que estejam errados: significa que ninguém confirmou a fonte. A Fase B mostrou
que essa distinção importa — ver abaixo.

## As quatro frentes JSON

| Frente | Itens | Temas cobertos (de 27) | Temas com 1 item só |
|---|---:|---:|---:|
| `galeria/` | 36 | 23 | 12 |
| `exames/` | 40 | 20 | **0** |
| `evidencias/` | 103 | 19 | 6 |
| `estudos/` | 45 | 24 | 9 |

A prioridade é **profundidade** — temas com 1 item só —, não mais zerar temas. Duas
leituras que a tabela deixa explícitas:

- **`exames/` cresceu de 17 para 40 na noite de 29/07**, pela sessão da Biblioteca,
  ainda com `published: false` em todo o lote — falta o aval do Rafael para publicar.
  **Zerou os temas com um item só** (eram 15, depois 6, agora nenhum) e foi de 16
  para **20 temas cobertos**. Sem nenhum exame ainda: Comunicação clínica, Geral,
  Farmacologia, Gravidez, Dispositivos, Prevenção e lipídios e Calculadoras — os
  sete são temas da faixa de Medicamentos ou de menor rendimento por hora
  (Comunicação clínica, Geral). Próximo passo natural nesta frente: aprofundar os
  20 temas cobertos (a maioria ainda com só 2 itens) ou avançar nos sete zerados
  que não são da faixa de Medicamentos (Comunicação clínica, Geral).
- **`evidencias/` cresceu em volume, não em amplitude.** Passou de 32 para 103 itens
  mas cobre 19 temas — o crescimento se concentrou em Cardiomiopatias, Doença
  coronariana e Cardio-oncologia. Síncope saiu de "uma recomendação só" com a
  entrada do ILR (ESC 2018); Pericárdio ganhou uma segunda entrada (anti-IL-1,
  ESC 2025); Aorta e doença arterial periférica ganhou uma segunda (rastreio de
  AAA, ESC 2024). Saúde mental, Arritmias, Dispositivos, Farmacologia, Hipertensão
  e Tromboembolismo seguem com uma só.
- **`estudos/` zerou Cardiopatias congênitas e Febre reumática** (BREATHE-5 e o
  ensaio de profilaxia secundária com penicilina benzatina a cada 3 semanas) e
  aprofundou Hipertensão pulmonar (AMBITION) e Tromboembolismo (EINSTEIN-PE), que
  tinham só 1 item. Resta só Comunicação clínica, Geral e Farmacologia sem nenhum
  estudo — os
  dois primeiros são de baixo rendimento por hora para este formato (ensaio
  clínico), o terceiro é turno da sessão de Medicamentos.

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
   tabela `documents`. Os **194 itens** de galeria, exames, evidências e estudos são
   invisíveis para quem pesquisa. A lacuna quase dobrou em 29/07, junto com o conteúdo:
   eram 103 pela manhã.
3. **Farmacologia concentra 66 dos 121 pendentes** de revisão. Segue sendo o maior bloco
   de conteúdo não verificado do sistema. O método que funciona: bula do detentor do
   registro no Brasil, baixada com `curl` e User-Agent de browser — o `WebFetch` toma
   403 na maioria dos sites de laboratório.
4. **"Geral" (1 documento) segue mal classificado.** Era 2; o de diabetes foi movido na
   fusão de pares. Resta o de gestação, que usa diretriz mais recente que a dos
   documentos atuais de Gravidez — reclassificar exige conciliar conteúdo, não só mover
   arquivo.
5. **Marcações de verificação: 47, em 38 arquivos de `content/`.** Cada uma é uma
   pergunta específica e respondível, não incerteza genérica. Zero nas quatro frentes
   JSON. Distribuição medida às 20h: **24 em Farmacologia**, 3 em Calculadoras, 2 em
   Terapia intensiva, 2 em Fibrilação atrial, e 1 em cada um de Valvopatias, Prevenção
   e lipídios, Perioperatório, Insuficiência cardíaca, Doença coronariana,
   Cardiomiopatias e Arritmias.
6. **Fluxogramas: 29 escritos, 29 publicados — frente zerada.** Os 6 temas que faltavam
   foram cobertos em 29/07/2026 (dislipidemia, amiloidose cardíaca, avaliação
   perioperatória, cardio-oncologia, febre reumática e cardiopatia congênita do adulto)
   e os 6 que aguardavam aval — síndrome coronariana crônica, regurgitação mitral,
   bradiarritmia e marcapasso, taquicardia de QRS largo, pericardite aguda e miocardite
   aguda — **entraram no ar**. Não há tema de fluxograma em aberto.
7. **`exames/` cresceu de 17 para 40 na noite de 29/07** (sessão da Biblioteca), ainda
   `published: false` esperando o aval do Rafael. Ver a leitura na seção acima: os 20
   temas cobertos não têm mais nenhum com um item só, e sete temas seguem sem nenhum
   exame (Comunicação clínica, Geral e os cinco da faixa de Medicamentos: Farmacologia,
   Gravidez, Dispositivos, Prevenção e lipídios, Calculadoras).
8. **Comunicação clínica é o tema mais fraco do acervo**: 2 documentos e **zero nas
   quatro frentes JSON**.

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
