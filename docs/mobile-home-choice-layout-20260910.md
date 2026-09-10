# Cabeçalho e escolha de modo mobile — 10/09/2026

Base: produção `4c58de6f`. Correção restrita ao CSS final de Home/escolha e aos testes relacionados. Nenhum asset, movimento de galáxia, tela de login ou comportamento da busca foi alterado.

## Causas identificadas

O commit `7125f116`, de 05/09/2026 às 06:06:58 +02:00, acrescentou ao bloco mobile do CSS final uma regra que escondia `.spaces-brand > span` apenas no tema claro. A marca escura permanecia completa. Isso explica tanto o desaparecimento de “CorVIA” quanto a diferença da posição da busca nos prints.

A escolha de modo usava uma grade com coluna implícita e tamanho mínimo automático. O cabeçalho somava cluster sem encolhimento (`width:max-content`, marca e galáxia) e avatar. A largura intrínseca desse conteúdo podia expandir a coluna além do celular; a região de cartões herdava essa largura. O corte horizontal do ancestral escondia o excesso sem resolvê-lo.

A verificação visual anterior media `documentElement.scrollWidth` com tolerância e a visibilidade do contêiner `.spaces-brand`. Ela não exigia a visibilidade do wordmark nem comparava os retângulos individuais de cartões, texto, galáxia e conta. A captura mobile principal era de 390px no tema escuro e no modo Completo. Logo, marca parcialmente oculta e conteúdo cortado dentro de um ancestral podiam passar.

## Correção

- Wordmark visível em ambos os temas.
- Grade de escolha com `minmax(0,1fr)` e mínimos de largura explícitos; textos dos cartões podem quebrar linha.
- Marca e galáxia da escolha recebem as dimensões compactas já usadas na Home; avatar permanece dentro do cabeçalho.
- Até 600px, a busca ocupa uma linha própria e os três modos permanecem logo abaixo. Isso mantém a identidade completa e um campo de busca utilizável em 320px, sem ocultar conteúdo para encobrir overflow.

## Evidência e regressão

O workflow Visual QA já existente recebeu 32 combinações: larguras 320/360/393/430 × temas claro/escuro × escolha/Completo/Essencial/Ciência. Cada combinação gera screenshot e medidas individuais. O gate verifica wordmark, limites de cabeçalho/cartões/avatar, texto cortado, sobreposições, alvo de toque da galáxia, largura útil do input e paridade geométrica entre temas. Não depende apenas da largura do documento.

Execução local focal: o teste novo detecta wordmark oculto, cartão fora da viewport, texto cortado e sobreposição; passou. O contrato geral de Home inicialmente passou 14/15 e falhou em `/admin/atividade`; a mesma falha foi reproduzida com o teste original de HEAD. A rota já é acessível por `Admin.tsx`, portanto foi classificada como subpágina e passou a exigir também o link da central administrativa. Os dois casos afetados foram reexecutados e passaram. Sintaxe do helper e do runner visual válida; `git diff --check` sem erro.

A matriz visual real será executada pelo workflow isolado. Ainda não há aprovação visual dos 32 resultados neste registro; as capturas devem ser inspecionadas antes do merge. Não foi usada sessão autenticada de produção nem execução externa improvisada de navegador.


Revisão final: cada captura falha se o tema renderizado divergir do solicitado; ambos ficam registrados separadamente. O azul VIA escuro aprovado `#5f8fe8` recebeu precedência sobre o azul global `#17335d`, que estava apagando a palavra no fundo escuro. No fundo-base `#06142b`, o contraste calculado passa de 1,46:1 para 5,76:1 (gradientes reais ainda serão inspecionados nas capturas). A marca clara conserva suas cores. A imagem da galáxia da escolha agora respeita o botão compacto, vencendo uma largura legada de118px; o gate também detecta imagem sobreposta ou fora da tela.
