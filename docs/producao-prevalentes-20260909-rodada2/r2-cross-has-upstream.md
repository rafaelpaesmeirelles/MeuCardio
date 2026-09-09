# Revisão cruzada do documento legado HAS — rodada 2

Data: 09/09/2026. Agente revisor r2_fa, independente da frente produtora HAS. Documento integral lido, com confronto de `r2-has-upstream.diff` e auditoria da frente. Correções focais autorizadas pelo coordenador aplicadas somente em `round2/content/Hipertensão/hipertensao-resistente-verdadeira-versus-pseudorresistente-tecnica-adesao-avental-branco.md`.

**Resultado:** denominador Jung resolvido em fonte primária, interpretação quantitativa Kallioinen corrigida e quatro links internos tornados navegáveis. `review_status: revisado` atribuído conforme autorização, com nota explícita de revisão assistida por IA e ausência de revisão humana/leitura integral dos artigos.

## Correções aplicadas

1. **Jung 2013:** o resumo original permite reconstruir a amostra: 375 encaminhados, 108 após otimização/exclusão do avental branco, 15 com causas secundárias e 17 controlados com quatro medicamentos. A avaliação urinária dos 76 restantes encontrou 40 não aderentes, correspondentes a 53%. Corrigido o parágrafo para explicitar **40/76**, e retirada a generalização de “mais da metade” a todos os encaminhados. Também corrigida a retomada desse percentual no fechamento. Nenhuma necessidade de excluir o dado: a ambiguidade foi resolvida. [Resumo primário, PMID 23337469](https://pubmed.ncbi.nlm.nih.gov/23337469/).
2. **Kallioinen 2017:** confirmado no resumo primário que os intervalos são efeitos significativos de fontes **individuais** de erro. A redação “somando as fontes individuais analisadas” foi substituída por “os efeitos significativos de fontes individuais variaram”. Não alterados os limites numéricos, que correspondem ao resumo. [Artigo primário, PMID 27977471](https://pubmed.ncbi.nlm.nih.gov/27977471/), PMCID PMC5278896; resumo recuperado pela API Europe PMC devido a resposta vazia/recaptcha do navegador.
3. **Links:** quatro referências em formato de nome de arquivo foram convertidas para `/biblioteca/slug`, após confirmar cada arquivo em `round2-paths.txt`: automedida TASMINH4/HOME BP; hipertensão por alcaçuz; espironolactona/PATHWAY-2; aldosteronismo/rastreio ARR.

## Demais conferências

- **De la Sierra 2011:** resumo primário recuperado pela API Europe PMC confirma 68.045 tratados, 8.295 com resistência pela definição do estudo, 62,5%/37,5% após MAPA. O resultado não foi transformado em soma com a coorte Jung. [PMID 21444835](https://pubmed.ncbi.nlm.nih.gov/21444835/).
- **AHA 2018:** definição, medidas externas e adesão confrontadas previamente nesta revisão cruzada com a [síntese oficial](https://professional.heart.org/en/science-news/resistant-hypertension-detection-evaluation-and-management/top-things-to-know).
- **Endocrine Society 2025:** investigação etiológica/rastreio diante de hipocalemia, sem esperar falha da quarta droga, coerentes com a [recomendação 3 e observações técnicas](https://www.endocrine.org/clinical-practice-guidelines/primary-aldosteronism-2), reabertas pelo revisor nesta rodada.
- Mantida a seleção de diurético conforme função renal/volemia, sem regra de alça para qualquer TFG reduzida, e a avaliação de segurança antes de antagonista mineralocorticoide.

## Limites editoriais, sem edição fora do escopo

Há formulações legadas que podem ser aperfeiçoadas em revisão estilística posterior: chamar triagem bioquímica de “único” método independente do relato é excessivo; registros de dispensação também fornecem informação independente, embora não comprovem ingestão. Também é preferível usar “efeito do avental branco” uniformemente em tratados, e atribuir as categorias “verdadeiramente resistentes” explicitamente à definição operacional do estudo de 2011. Esses pontos não foram ampliados em novas recomendações e não mudam os gabaritos nem o algoritmo corrigido; mantidos fora da edição autorizada focal.

Não houve commit, alteração dos catálogos globais ou publicação. Caches dos resumos estão em `round2/overlay-cache/` apenas para rastreabilidade temporária, sem inclusão sugerida no commit. A revisão não comprova completude de todo o tema HAS.
