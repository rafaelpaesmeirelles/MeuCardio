# Originais científicos no catálogo Tudo com Tudo — PR922

A aquisição de um original licenciado passa a torná-lo localizável como **Publicação original**, sem criar Document ou ScientificStudy, sem marcar revisão humana e sem modificar condutas. A identidade é o `source_key` derivado do DOI; a rota é `/intelligence?fonte=<source_key>`, integrada ao leitor e aos favoritos existentes.

## Elegibilidade e limites

O mesmo predicado atende busca, leitor e favoritos: original armazenado, licença CC BY/CC0 admitida pelo parser, hash e identidade DOI consistentes, ausência de bloqueio de identidade/licença e origem pública atual. A origem exige referência de conteúdo publicado, estudo revisado quando aplicável, referência de calculadora do registro público ou descoberta de organização/domínio confiável do Intelligence. Conteúdo privado, em quarentena ou um asset órfão não estabelece essa origem.

A busca desta entrega cobre **título, autores e DOI**. O arquivo integral permanece cifrado e acessível pelo leitor; seu texto integral não foi incluído no índice de pesquisa. Resumos gerados por IA não entram como texto pesquisável de orientação clínica nesta frente. O RAG léxico clínico exclui linhas da frente `publicacao_original`.

## Representação e descoberta

Um guia ou fluxograma citar o DOI de um artigo não faz esse conteúdo representar o artigo. Por isso a citação não remove o original da busca. A linha de original só é suprimida quando existe estudo publicado/revisado com DOI próprio exato ou documento público com vínculo Intelligence explícito confirmado e DOI correspondente em suas referências. A última exigência garante que o leitor do destino ofereça a fonte.

Os metadados bibliográficos do original também participam da busca do estudo/documento que o representa. Assim, pesquisar o título original em inglês continua encontrando a ficha editorial em português. A identidade, o título e o texto dessa ficha permanecem intactos. DOI prefixado ou semelhante não é considerado o mesmo DOI.

## Validação executada

Quatro testes focais PostgreSQL passaram em **18,90 segundos** no banco isolado `corvia_original_catalog_20260910_backend`:

- Origem pública atual, licença permitida, hash, identidade e bloqueios.
- Guia citante preserva a linha de original; DOI próprio de estudo evita duplicata; prefixos diferentes permanecem distintos.
- Vínculo Intelligence explícito mantém o título inglês localizável no documento em português.
- Seção própria, contagens/paginação consistentes, ausência de promoção a diretriz e exclusão de originais brutos do RAG clínico.

O teste de integração do agente responsável pelo leitor/favoritos também confirmou manifesto, identidade por slug/ID e revogação de acesso quando a origem deixa de estar publicada. Seu resultado inicial foi 1 teste aprovado em 4,48 segundos; os quatro testes acima validaram o predicado SQL final após a otimização.

Um EXPLAIN ANALYZE limitado a 15 segundos, com **12.000 documentos sintéticos e 100 originais sintéticos**, mediu 39,211 ms de planejamento e 521,963 ms de execução, com 0,588 segundo de duração observada. Toda a transação sofreu rollback. Trata-se de medição sintética em QA, não de garantia de latência de produção.

A otimização extrai referências públicas uma vez, materializa os originais elegíveis e normaliza identidades canônicas uma vez, reutilizando joins por DOI. Evita varrer o corpus repetidamente para cada original. A primeira implementação, já substituída, levou 1.803 ms com apenas três originais no mesmo cenário de 12.000 documentos e motivou a correção de desempenho.

Evidências operacionais: `/tmp/corvia-original-catalog-tests.log`, `/tmp/corvia-original-catalog-explain-100.log` e `/tmp/corvia-original-catalog-migration.log`. A preparação de esquema ocorreu exclusivamente no banco QA. Nenhuma chamada paga de IA, teste em produção ou CI backend foi executado nesta verificação. Os gates de corpus e release permanecem exigidos.
