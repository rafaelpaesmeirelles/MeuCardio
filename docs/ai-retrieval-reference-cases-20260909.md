# Referência amostral de recuperação de conteúdo — 9 de setembro de 2026

Conjunto preparado por agente antes de observar os resultados da comparação lexical/híbrida. São 16 perguntas em oito pares: uma consulta com nomes/siglas e uma formulação clínica em linguagem natural por assunto. Cada pergunta tem duas ou três entidades previamente rotuladas. A amostra busca jornadas comuns e não pretende representar a prevalência de todas as perguntas reais.

## Escopo e interpretação

- Rótulos atribuídos por agente a partir dos arquivos fonte existentes no repositório, com leitura dos trechos pertinentes. Não houve certificação clínica humana nem nova revisão externa das recomendações contidas nesses arquivos.
- Todos os arquivos selecionados declaram `review_status: revisado` no front matter; nenhum declara `published: false`. A ausência de `published` não foi tratada como prova de publicação no banco. Nenhuma consulta à produção foi executada para preparar este conjunto.
- As chaves usam a frente do catálogo: `documento:slug`. Um Markdown com `kind: estudo` ou `kind: fluxograma` continua sendo um documento do catálogo; não foi inventada uma linha de `scientific_studies` ou uma chave alternativa com base no kind. O adaptador do avaliador deve normalizar os tipos reais retornados pelo RAG antes da comparação.
- Esta amostra foca recuperação de documentos, incluindo protocolos, referências farmacológicas e fluxogramas. Não mede cobertura integral de exames, calculadoras, entidades estruturadas ou demais frentes do Tudo com Tudo.
- `required_any` é um conjunto de referências alternativas pertinentes: acertar uma satisfaz somente um limiar mínimo de recuperação. Não prova completude. Nenhum conteúdo fora da lista deve ser automaticamente classificado como irrelevante, pois os rótulos não são exaustivos.
- Não foram acrescentados `required_all`: obrigar referências alternativas simultâneas poderia penalizar uma recuperação útil apenas por redundância documental. Para medir cobertura parcial do conjunto, pode-se reportar a fração dos rótulos elegíveis recuperados separadamente.
- Nas perguntas abertas, encontrar uma fonte pertinente não demonstra que a resposta clínica gerada é correta, suficiente, atual ou segura. Essa avaliação exige outro protocolo e revisão humana.

## Protocolo para reduzir viés

1. Congelar este arquivo e registrar seu SHA256 antes de executar qualquer modo de busca.
2. Fazer uma única verificação de elegibilidade por tipo/slug e publicação, usando consulta de existência com filtros pelos slugs; verificar também a disponibilidade no índice/chunks que cada modo realmente utiliza. Fonte ausente ou não publicada deve ser relatada como inelegível, nunca convertida silenciosamente em erro de recuperação nem substituída por um resultado visto depois.
3. Usar a mesma fotografia do acervo, top-k, regras de publicação e orçamento de contexto nos dois modos. Se a busca híbrida incluir também catálogo lexical, esse recurso deve ser declarado; não comparar arquiteturas diferentes como se apenas embeddings tivessem mudado.
4. Guardar a lista completa de resultados e escores de cada modo. Apurar Hit@k, primeiro acerto/MRR@k e cobertura dos rótulos elegíveis; separar `exact` e `paraphrase`. A precisão não pode ser calculada tratando todos os itens não rotulados como negativos.
5. Medir latência e custo incremental com instrumentação real; separar embedding de consulta, recuperação, reranking e geração. Este fixture não exige nem autoriza por si só chamadas pagas.
6. Se houver falha de provedor, fallback, timeout, índice ausente ou fonte inelegível, reportar explicitamente. Uma execução sem embeddings efetivos não mede contribuição semântica.
7. Manter perguntas e rótulos originais. Qualquer correção posterior deve gerar nova versão, registrar o motivo e repetir ambos os modos; não escolher referências após conhecer qual modo as recupera.

## Congelamento

- Arquivo: `scripts/fixtures/ai_retrieval_cases.json`
- SHA256: `80d2b45d94b0bee4d914aa365ab5f30793a4731ee444258d8418ed0c34c166ea`
- Casos: 16 (8 exact; 8 paraphrase).
- Entidades únicas rotuladas: 18.
- Estado: fontes verificadas offline; publicação/indexação ainda devem ser verificadas pelo avaliador.

## Fontes e fotografia dos rótulos

| Chave | Arquivo fonte | published no fonte | SHA256 do fonte |
|---|---|---|---|
| `documento:apixabana` | `content/Farmacologia/apixabana.md` | não declarado | `73ac50e60a016c4a3676b23d2291169b02e1cf3387a6c84096f943e36dc2d94a` |
| `documento:apixabana-rivaroxabana-dose-bula-brasil-2025-arvore-de-decisao` | `content/Farmacologia/apixabana-rivaroxabana-dose-bula-brasil-2025-arvore-de-decisao.md` | não declarado | `edced38bdf30705b992e7273bf05a1aa7173cfd28306fb776472840b89af1afe` |
| `documento:colchicina-na-pericardite-o-que-esperar` | `content/Pericárdio/colchicina-na-pericardite-o-que-esperar.md` | true | `042034d2e78bb9478bdf1782b7141f7b42214edca2e91b6d4160ad544856dbbb` |
| `documento:colchicina-na-pericardite-recorrente-o-que-o-ensaio-mostra` | `content/Pericárdio/colchicina-na-pericardite-recorrente-o-que-o-ensaio-mostra.md` | true | `4686a057c3681e082cde46ef4042cef2897c44862ed677be1e50541e610ae4f8` |
| `documento:esc-2024-diretriz-fibrilacao-atrial-af-care` | `content/Fibrilação_atrial/esc-2024-diretriz-fibrilacao-atrial-af-care.md` | não declarado | `e5555f1503933c001dbfc9dacc60f201652b40e9a2601cbcee1ea75065d3a12d` |
| `documento:fluxograma-anticoagulacao-cha2ds2-va-esc-2024` | `content/Fibrilação_atrial/fluxograma-anticoagulacao-cha2ds2-va-esc-2024.md` | true | `022a9728d40bdc2d7ee17a13d40df63031a556b8844835cd631d7f086c9e3e03` |
| `documento:fluxograma-hipertensao-resistente-quarta-droga` | `content/Hipertensão/fluxograma-hipertensao-resistente-quarta-droga.md` | não declarado | `7828f37ca54520f36e63c35cfd52386a7d888ca69d13ab4f9aaf2ae6c1524203` |
| `documento:fluxograma-intolerancia-a-estatina-definicao-e-protocolo-de-reexposicao` | `content/Prevenção_e_lipídios/fluxograma-intolerancia-a-estatina-definicao-e-protocolo-de-reexposicao.md` | não declarado | `cae1f7798712726668028a86b72334dd0b19459ac4d758004e7852006841ee03` |
| `documento:fluxograma-minoca-investigacao-diagnostica` | `content/Doença_coronariana/fluxograma-minoca-investigacao-diagnostica.md` | não declarado | `737e4a4a95980ae12c08963bff3e4f26c7d29d90aba8094d9bdd43b8f08b6f40` |
| `documento:fluxograma-palpitacoes-avaliacao-inicial-ambulatorial` | `content/Geral/fluxograma-palpitacoes-avaliacao-inicial-ambulatorial.md` | não declarado | `cdd885450ba353623404ac4cb110b3b26e9a9f35f34a413740887128f7e70cc5` |
| `documento:hipertensao-resistente-espironolactona-como-quarta-droga-o-ensaio-pathway-2` | `content/Hipertensão/hipertensao-resistente-espironolactona-como-quarta-droga-o-ensaio-pathway-2.md` | não declarado | `1eacf43025e392c256c405db65c3a865f3e49a8fdce91ff16f860454cf5c6767` |
| `documento:hipertensao-resistente-verdadeira-versus-pseudorresistente-tecnica-adesao-avental-branco` | `content/Hipertensão/hipertensao-resistente-verdadeira-versus-pseudorresistente-tecnica-adesao-avental-branco.md` | não declarado | `3d30c741f44aa88d45ca53ab47cf1f0371249ebe86ef23f666cf234d106bdaf2` |
| `documento:holter-nao-e-ilr-nao-e-cdi` | `content/Dispositivos/holter-nao-e-ilr-nao-e-cdi.md` | true | `566243bf8c93c7bd2fa058a41f06b5ef08cb5859d05a77d741add2d91aab5f21` |
| `documento:icfer-classificacao-diagnostico-quatro-pilares` | `content/Insuficiência_cardíaca/icfer-classificacao-diagnostico-quatro-pilares.md` | não declarado | `a201b4b777caa10f423a908e19326c346723778ea5e077c8efb82ad9d497ca0c` |
| `documento:icfer-doses-iniciais-alvo-quatro-pilares-arvore` | `content/Farmacologia/icfer-doses-iniciais-alvo-quatro-pilares-arvore.md` | não declarado | `3e64002518673e07d7e0424f476abe3fd0b3a39946bbdb9d2e9bdddacbde5352` |
| `documento:inibidores-de-sglt2-na-icfer-dapa-hf-e-emperor-reduced` | `content/Insuficiência_cardíaca/inibidores-de-sglt2-na-icfer-dapa-hf-e-emperor-reduced.md` | não declarado | `3ee610655900d47114f52356d5d386639553057375b8388d2df07476c396503d` |
| `documento:intolerancia-a-estatina-definicao-operacional-e-protocolo-de-reexposicao-eas-2015` | `content/Prevenção_e_lipídios/intolerancia-a-estatina-definicao-operacional-e-protocolo-de-reexposicao-eas-2015.md` | não declarado | `a95fb1b3cb063b482007d237e01a5298f4d3ec907c64eb16533210ecbb2229b6` |
| `documento:minoca-e-scad-infarto-sem-doenca-coronariana-obstrutiva-e-dissecção-espontânea` | `content/Doença_coronariana/minoca-e-scad-infarto-sem-doenca-coronariana-obstrutiva-e-dissecção-espontânea.md` | não declarado | `29ee9611b8d6df00cfbcc166cc4687b03afa74df40cf5359f238b6909b4a7804` |
