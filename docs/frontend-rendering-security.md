# Política de renderização segura no frontend

## Regra geral

Conteúdo clínico, resultados de busca, respostas de IA e mensagens de e-mail são
tratados como dados, nunca como HTML confiável. O frontend não insere strings
remotas diretamente na árvore DOM.

A CI executa `frontend/scripts/check-rendering-security.mjs` e bloqueia:

- inserção direta de HTML no React;
- atribuição a `innerHTML` e APIs equivalentes;
- parsing manual de HTML no navegador;
- `rehype-raw` em renderização Markdown;
- Mermaid com `securityLevel: loose`;
- `srcDoc`, protocolo `javascript:` e links `_blank` sem isolamento.

## Markdown clínico

`react-markdown` e `remark-gfm` permanecem porque são usados no assistente, casos
clínicos, biblioteca e modo emergência. HTML bruto não é habilitado. A política
de CI proíbe a introdução de `rehype-raw`, que seria a mudança capaz de converter
marcação HTML presente no Markdown em elementos executáveis.

## Fluxogramas Mermaid

O Mermaid roda com:

- `securityLevel: strict`;
- rótulos HTML desativados;
- validação do SVG contra scripts, `foreignObject`, event handlers, protocolos
  executáveis e referências externas.

O SVG aprovado é colocado em um `Blob` do tipo `image/svg+xml` e exibido em
`<img>`. Ele não é inserido como marcação na página. Se a geração ou validação
falhar, o componente mostra o código-fonte do fluxograma como texto.

## Busca

O PostgreSQL devolve snippets com delimitadores `<mark>`. O frontend reconhece
somente a abertura e o fechamento exatos desse marcador. Todo o restante é
renderizado como texto React escapado, inclusive qualquer tag que eventualmente
exista no conteúdo de origem.

## E-mail externo

HTML recebido por e-mail não é renderizado no contexto autenticado da Corvia.
A interface usa o corpo textual quando disponível; quando só existe HTML,
remove marcação e mostra texto simples. Recursos remotos, pixels de rastreamento,
formulários e scripts não são carregados.

Essa decisão privilegia confidencialidade e integridade sobre fidelidade visual.
Uma futura visualização HTML exigiria sanitização dedicada, isolamento por
sandbox e política explícita de recursos externos — não uma exceção local ao
gate atual.
