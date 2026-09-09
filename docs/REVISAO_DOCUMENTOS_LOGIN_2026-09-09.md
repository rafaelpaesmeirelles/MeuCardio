# Revisão de documentos e login — 09/09/2026

## Documentos ao paciente

- Corrigida a quebra de linhas e a restauração da fonte após cada página. Textos longos, URLs, títulos, posologias, quantidades, observações e orientações passam a respeitar as margens e continuar nas páginas seguintes.
- Cabeçalho clínico unificado: CorVIA à esquerda, logo profissional no centro e identificação pessoal/profissional à direita. Aplicado aos PDFs clínicos, receitas comuns e controladas, materiais ao paciente, exportações pessoais em PDF/Word e impressão HTML.
- Receitas controladas preservam as duas vias, campos e validações existentes. Itens extensos continuam em páginas adicionais sem cobrir o quadro de assinatura.
- Rodapés e conteúdo dos PDFs assináveis reservam a área do carimbo digital.
- Documentos gerados e seu histórico apresentam a escolha explícita de assinatura. A assinatura pendente impede o envio, também no backend; falhas permitem nova tentativa. Arquivos já emitidos mantêm método e bytes originais.
- A impressão legada identifica a assinatura manual e oferece encaminhamento para revisão e assinatura digital no receituário.
- Orientações de medicamentos são preservadas na resolução, no snapshot e no PDF.
- Exportações PowerPoint foram verificadas quanto à retenção do texto editável; sua composição visual existente foi preservada.

## Login aprovado

- Formulário desktop claro/escuro em faixa horizontal fina na parte inferior; adaptação própria para notebooks.
- Universo reduzido, coração discretamente ampliado, galáxia clara suave e fundo escuro sem pontilhado.
- Disco galáctico normalizado antes da rotação, mantendo sua inclinação e proporção. Login claro gira no sentido anti-horário; miniuniversos internos giram lentamente no sentido horário. Preferência de movimento reduzido respeitada.
- Conferência visual em desktop e celular, nos dois temas. Versão aprovada pelo solicitante.

## Validação concluída antes da autorização de deploy

- 43 testes isolados de backend aprovados: geometria, paginação, retenção de texto, cabeçalhos, exportações, regras do receituário, assinatura criptográfica e bloqueios de envio.
- 4 testes do componente real de finalização aprovados: assinatura A1, falha de assinatura, assinatura externa pendente e reabertura de documento assinado.
- TypeScript e build de produção aprovados. Permanece o aviso de tamanho de alguns chunks.
- Dois PDFs demonstrativos, com duas páginas cada, renderizados e inspecionados visualmente. Sem dados reais, medicamentos ou validade clínica.
- Não houve envio a pacientes nem teste com certificado pessoal real. Os testes locais foram isolados, sem uso do banco de produção.

## Publicação autorizada

O solicitante autorizou publicar após concluir os ajustes, sem CI de backend e sem repetir testes. A publicação usa o fluxo direto existente, acionado manualmente para o SHA aprovado, com backup, build e checagens de disponibilidade do próprio deploy. O commit usa `[skip ci]` para esta publicação; a política normal de CI não foi desativada.

## Revisão visual após a primeira publicação

- Fundo, campos e cartões claros em azul gelo, azul acinzentado e ciano, sem superfícies rosadas ou lilases. Pequenos acentos cromáticos da marca e dos ícones preservados.
- Nova coloração da galáxia clara: azul, ciano e lilás, preservando a estrutura da imagem. Dimensões ampliadas em aproximadamente 10% nos dois temas e tamanhos de tela.
- Projeção da galáxia separada da inclinação original da imagem: disco horizontal fixo, com textura girando no próprio plano em 120 segundos. Sentido anti-horário no claro e horário no escuro. Verificação das duas imagens em oito fases: razão vertical constante de 0,34 e desvio do centro inferior a 0,002 pixel.
- Superfície única para campos de login, ícones e preenchimento automático do navegador. Contorno de foco no campo externo, sem retângulo de outra cor dentro do input; campos mobile com 44 px e texto de 16 px.
- Estrelas estáticas, discretas e em posições irregulares no login e nos fundos dos ambientes internos e formulários públicos. A camada não recebe cliques e é ocultada na impressão.
- Conferência visual dos dois temas em desktop/celular, sem envio de formulário. Compilação do frontend; nenhuma alteração adicional de backend e nenhuma repetição das suítes anteriores.
# Carregamento da galáxia — correção após vídeo de 09/09

O vídeo mostrou o PNG claro sendo pintado em faixas durante o download, seguido
pela troca da fotografia original para o disco projetado no canvas. O login agora
revela apenas o primeiro quadro completo, depois de `HTMLImageElement.decode()`.
Foi removida a imagem progressiva de fallback, junto com o download duplicado.

- Textura clara otimizada de 1.860.719 para 137.220 bytes (92,6% menor), com largura
  de 1366 px para o canvas de 683 px. WebP qualidade 95; diferença média no quadro
  de renderização inferior a 1 nível por canal RGB, em escala de 0 a 255.
- Textura escura preservada byte a byte. Ambas recebem URLs com hash em `/assets`,
  usando o cache HTTP imutável já configurado no servidor.
- Downloads e decodificação reutilizados ao alternar temas; animação pausada em
  aba oculta e sem reescrita de atributos/estilos a cada quadro.
- Geometria, sentido/velocidade do giro, paletas e layout aprovados preservados.
- Verificação focada do componente real: download lento, troca de tema antes de
  terminar, reutilização do arquivo, movimento reduzido e limpeza ao desmontar.
  Comando: `node --test scripts/check-login-galaxy-loading.test.mjs` (1 aprovado).
- TypeScript e build Vite aprovados; conferência visual dos dois temas realizada.
  Nenhuma suíte de CI/backend executada nesta correção.
# Galáxia escura visível durante falha ou demora de rede — 09/09

O canvas ficava oculto até a textura terminar de baixar/decodificar. Se o arquivo
atrasasse ou falhasse, restavam apenas o coração e as órbitas. Agora os dois temas
incluem um primeiro quadro completo no próprio módulo do login (data URI), com a
mesma projeção da animação. A troca ocorre de uma vez, só depois do primeiro
quadro animado estar pronto. Falhas transitórias têm uma nova tentativa limitada;
se persistirem, a imagem completa continua visível.

- Textura escura reduzida de 304.046 para 191.498 bytes, mantendo a transparência.
  Diferença média por canal, composta no fundo escuro: inferior a 0,63/255.
- Imagem inicial escura mantém canal alfa; a clara usa o branco neutro da
  composição multiply existente. Layout, cores e geometria aprovados mantidos.
- Verificação do componente ampliada para cobrir duas falhas de download,
  tentativa limitada e permanência da galáxia inicial: aprovada.
- Conferência visual do build real em servidor local que responde 503 aos
  arquivos da animação: galáxias visíveis e completas nos dois temas.
- Conferência visual da animação escura com download normal: canvas pronto e
  imagem inicial retirada corretamente. TypeScript e build Vite aprovados.
- Nenhuma suíte de CI/backend executada.
